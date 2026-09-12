"""
Etapa 2 del Word→HTML: corrección quirúrgica de tablas con DeepSeek.

Recibe el HTML de la Etapa 1 (`structure.docx_to_html`) y le pide al modelo
que corrija únicamente los patrones de tabla complejos (colspan/rowspan,
colores exactos, columnas) que el motor determinístico no pudo deducir bien.
No reescribe el documento entero.

Degrada con gracia: si `DEEPSEEK_API_KEY` no está seteada o la llamada falla,
se devuelve el HTML de entrada sin modificar — un fallo de IA nunca debe
romper la conversión completa.
"""
import logging
import os
import re

import httpx

logger = logging.getLogger(__name__)

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-v4-pro"
TIMEOUT_SECONDS = 60.0

# Prompt de trabajo real (Jesús) para reconstruir tablas de "cuadros de
# acabados" con colspan/rowspan y colores exactos del documento original.
# Se conserva textual para no perder reglas; los colores son de ejemplo.
_TABLE_PROMPT = """el pdf es la tabla, la estructura que usamos es algo asi
se parte asi:
<style> </style>
-- aqui abajo va defrente el cuerpo, no necesariamente es con "body" puede ser directamente con "div"
<style type="text/css">@page (esta parte siempre ponemos) { margin-top: 2.5cm; margin-bottom: 2.5cm; margin-right: 3cm; margin-left: 3cm; } body (aqui definimos la letra y el tamaño de todo el documento) { font-family: Candara; font-size: 10pt; } --- de aqui en adelante es lo usual-- div, li, td { text-align: justify; } ul li, ol li{ margin-top: 15px; margin-bottom: 15px; } table, thead, tbody { border-collapse: collapse; box-sizing: border-box; vertical-align: top; } -- esta parte es para firmas en las tablas de firmas que usamos pero ahora no es necesario--- .firmas { border-top: 1px solid #000; } </style>
-- aqui viene el detalle de la tabla -- -- align siempre sera "centar" -- border siempre sera "0" -- y lo demas igual
<table align="center" border="0" cellpadding="0" cellspacing="0" style="width:100%;"> <colgroup> -- seccion de medicion mediante porcentaje de columnas, depende la cantidad de columnas agregamos el porcenaje como en este ejemplo hay 3 columnas "td" agregamos 3 "col width = .." -- <col width="48%" /> <--- En esta parte definimos el tamaño con porcentaje de una columna <col width="auto" /> <col width="48%" /> </colgroup> <tbody> <tr> <td> </td> <td> </td> <td> </td> </tr> </tbody> </table>
-- un ejemplo de como seria la tabla
-- primero cuento la cantidad de columnas y segun veo en este caso son 3 columnas en toda la tabla lo agregaria asi --
-- aqui hago 5 "tr" porque quiero 5 filas por ahora, y 3 "td" porque son 3 columnas, en la primera fila veo que coge "cuadro de acabados altanova toda la fila, para ese caso puedo crer una tabla de una fila, algo asi: si te das cuenta solo tiene 1tr y 1td porque solo sera para el titulo de la primera fila de la tabla del pdf
<table align="center" border="1" cellpadding="0" cellspacing="0" style="width:100%;"> <tbody> <tr> <td> cuadro de acabados altanova</td> </tr> </tbody> </table> luego un espacio y viene la siguiente tabla el titulo en cada columna, luego viene la enumeracion q cada enumeracion es un "subtitulo" por lo que veo, y luego vien el rellenado, respecto al color si gutas lo peudes poner en la misma fila enumerada para no complicarnos tanto, ahora el detalle de como juntar las columnas por ejemplo en "1 estructura" y para todos los q son asi seria como el ejemplo aqui <table align="center" border="1" cellpadding="0" cellspacing="0" style="width:100%;"> <colgroup> <col width="2%" /> <col width="25%" /> <col width="73%" /> </colgroup> <tbody> <tr> <td>1</td> <td colspan="2" rowspan="1">Estructura</td> <-- Aqui el "coldspan="2" dice que cogio 2 columnas y rowspan="1" porque es su misma fila, </tr> <tr> <td> </td> <td> </td> <td> </td> </tr> <tr> <td> </td> <td> </td> <td> </td> </tr> <tr> <td> </td> <td> </td> <td> </td> </tr> <tr> <td> </td> <td> </td> <td> </td> </tr> </tbody> </table>

ahora te dare un ejemplo de los rowspan, hay casos que necesitaremos juntar filas largas de muchas columnas como filas de la misma columna, en este caso haremos de la misma columna para que se vea identico como en la seccion "2 sala - comedor" del pdf:
-- aqui tenemos lo mismo que la tabla de arriba excepto el estilo con el color q es backgroun de esta forma: "style="text-align: center;background-color: #6CE6DA;" aqui en el "td" del numero 2 (esto solo es ejemplo mostrando el numero 2 pero cuando rehagas la tabla te tienes que guiar), le digo q el background sera como el color del pdf, y estara centrado solo el titulo, el numero 2 se mantiene en su columna
<table align="center" border="1" cellpadding="0" cellspacing="0" style="width:100%;">
				<colgroup>
					<col width="2%" />
					<col width="25%" />
					<col width="73%" />
				</colgroup>
				<tbody>
					<tr>
						<td>2</td>
						<td colspan="2" rowspan="1" style="text-align: center;background-color: #6CE6DA;">Sala - comedor</td>
					</tr>
					<tr>
						<td> </td> <- aqui no hay enumeracion ya que pertenece al numero 2
						<td>Pisos</td>  <- aqui es lo mismo como en las demas tablas
						<td>Piso laminado con acabado tipo madera o similar</td>  <- aqui igual su informacion en la columna que pertenece
					</tr>
					<tr>
						<td> </td>
						<td>Contrazócalos</td>
						<td>Contrazocalo tipo madera o similar</td>
					</tr>
					<tr>
						<td> </td>
						<td>Pared</td>
						<td>Papel mural</td>
					</tr>
					<tr>
						<td> </td>
						<td>Puerta de ingreso</td>
						<td>Puerta contraplacada con acabado tipo madera o similar con cerradura tipo manija o similar</td>
					</tr>
					<tr>
						<td> </td>
						<td>Mampara</td>
						<td>Vidrio laminado incoloro y carpientería de aluminio o similar. Rejilla lateral de aluminio o similar, altura igual a mampara.<br />
						Baranda metálica o similar</td>
					</tr>
					<tr>
						<td colspan="1" rowspan="5"> </td>  <- aqui vemos algo distinto, la columna dice "coldspan="1" es distinto al ejemplo de arriba, dice 1 porque no modificara en ninguna columna se mantiene en su misma columna" y "rowspan="5" aqui si afecta a las filas pero de su propia columna, le dice q cogera las 5 columnas pero de su propia fila por eso coldspan = "1",
						<td colspan="1" rowspan="5" style="vertical-align: middle;">Otros</td> <- aqui para otros es lo mismo que en el td de arriba, cogera 5 filas de su propia columna por eso indica "colspan="1" rowspan="5" solo de su propia columna,
						<td>Punto de TV-Cable</td> <-- este td le pertenece al td de otros pero de la tercera columna, aqui las columnas no estan afectadas
					</tr>
					<tr>
						<td>Punto de Data</td> <- aqui solo aparece 1td porque el rowspan de "otros" y si afecto a los "td" de las otras columnas por eso solo aparece 1 td para que el diseño tenga sentido y sea igual como el pdf en esta seccion, habran otras secciones con la misma logica pero quizas con mas filas y tendra q ser lo mismo segun las filas se pone en el rowspan y asi sucesivamente
					</tr>
					<tr>
						<td>Placas de interruptor color blanco o similar</td>
					</tr>
					<tr>
						<td>Placas de tomacorriente color blanco o similar</td>
					</tr>
					<tr>
						<td>En el ingreso al departamento 1 pulsador de tiembre en placa color blanco o similar.</td>
					</tr>
				</tbody>
			</table>

con esta informacion realizalo y convierte con los mismo colores del pdf, Excel, word o el archivo que usen y sean exactos, no imagines no alucines, el prompt tiene colores pero son de ejemplo.
revisa bien, aunque los cuadros no se vean las columnas estan sin color tipo "invisible" pero todos estan separados por columnas excepto lso titulos y subtitulos analiza bien"""

# Instrucción explícita: solo corregir lo puntual, no reescribir el documento.
_SYSTEM_APPENDIX = (
    "You will receive HTML already structurally extracted (colspan/rowspan/colors "
    "already present where detectable). Your job is ONLY to fix cases where the "
    "structure looks wrong or incomplete relative to what the rules above describe "
    "— do not rewrite paragraphs of plain text, do not change colors/values that "
    "are already correct, return the full HTML document with only the necessary "
    "table corrections applied."
)

# Refuerzo explícito contra el bug #47: el modelo a veces copia el <style> de
# ejemplo del prompt y envuelve todo en un documento completo. Esto va ANTES de
# la explicación larga para que no quede enterrado.
_OUTPUT_FORMAT_INSTRUCTION = (
    "IMPORTANT — OUTPUT FORMAT: Your output must contain ONLY the content-level "
    "HTML tags (p, table, colgroup, tr, td, etc.) — the exact same tags that were "
    "in the input. NEVER add <!DOCTYPE>, <html>, <head>, <body>, <title>, or any "
    "top-level document wrapper. NEVER copy the <style> block shown in the "
    "formatting examples below into your output — those examples are "
    "reference/context only, describing conventions, not literal content to insert.\n\n"
)

_WRAPPER_RE = re.compile(r"<!doctype|<html\b|<head\b|<body\b|<title\b|<style\b", re.IGNORECASE)


def _has_document_wrapper(html: str) -> bool:
    """True si la salida incluye un wrapper de documento completo (bug #47)."""
    return bool(_WRAPPER_RE.search(html))


def enhance_tables_with_ai(html: str) -> str:
    """Corrige tablas complejas con DeepSeek; degrada a `html` si algo falla."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        logger.warning(
            "DEEPSEEK_API_KEY no está configurada; se devuelve el HTML sin corregir."
        )
        return html

    system_prompt = _OUTPUT_FORMAT_INSTRUCTION + _TABLE_PROMPT + "\n\n" + _SYSTEM_APPENDIX
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": html},
        ],
        "stream": False,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = httpx.post(
            DEEPSEEK_API_URL,
            json=payload,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        logger.warning("Falló la corrección de tablas con DeepSeek: %s", exc)
        return html

    if isinstance(content, str) and content.strip():
        if _has_document_wrapper(content):
            logger.warning(
                "DeepSeek envolvió la salida en un documento completo "
                "(DOCTYPE/html/head/body); se descarta y se devuelve el HTML sin corregir."
            )
            return html
        return content
    return html

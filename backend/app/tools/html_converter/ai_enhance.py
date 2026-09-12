"""
Etapa 2 y Etapa 3 del Word→HTML: corrección de tablas y esqueleto final con DeepSeek.

Etapa 2 recibe el HTML de la Etapa 1 (`structure.docx_to_html`) y le pide al
modelo que corrija únicamente los patrones de tabla complejos (colspan/rowspan,
colores exactos, columnas) que el motor determinístico no pudo deducir bien.
No reescribe el documento entero.

Etapa 3 envuelve el resultado en el esqueleto de salida fijo y verifica que el
texto visible no haya sido alterado (fidelidad textual).

Las dos degradan con gracia: si `DEEPSEEK_API_KEY` no está seteada o la
llamada falla, se devuelve el HTML de entrada sin modificar — un fallo de IA
nunca debe romper la conversión completa.
"""
import logging
import os
import re
from html import unescape
from pathlib import Path

import httpx

from app.tools.html_converter.structure import docx_to_html

logger = logging.getLogger(__name__)

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-v4-pro"
TIMEOUT_SECONDS = 60.0

# Techo de tokens de salida para la pasada de IA (issue #56). El default de
# deepseek-v4-pro al omitir `max_tokens` es 4096, insuficiente para devolver un
# documento largo completo → la respuesta se truncaba y la Etapa 3 la rechazaba.
# Un techo alto no cuesta nada extra: se factura por tokens realmente generados,
# no por el máximo declarado.
MAX_OUTPUT_TOKENS = 32000

# Prompt de trabajo real (Jesús) para reconstruir tablas de "cuadros de
# acabados" con colspan/rowspan y colores exactos del documento original.
# Se conserva textual para no perder reglas; los colores son de ejemplo.
_TABLE_PROMPT = """el pdf es la tabla, la estructura que usamos es algo asi
se parte asi:
<style> </style>
-- aqui abajo va defrente el cuerpo, no necesariamente es con "body" puede ser directamente con "div"
<style type="text/css">@page (esta parte siempre ponemos) { margin-top: 2.5cm; margin-bottom: 2.5cm; margin-right: 3cm; margin-left: 3cm; } body (aqui definimos la letra y el tamaño de todoel documento) { font-family: Candara; font-size: 10pt; } --- de aqui en adelante es lo usual-- div, li, td { text-align: justify; } ul li, ol li{ margin-top: 15px; margin-bottom: 15px; } table, thead, tbody { border-collapse: collapse; box-sizing: border-box; vertical-align: top; } -- esta parte es para firmas en las tablas de firmas que usamos pero ahora no es necesario--- .firmas { border-top: 1px solid #000; } </style>
-- aqui viene el detalle de la tabla -- -- align siempre sera "centar" -- border siempre sera "0" -- y lo demas igual
<table align="center" border="0" cellpadding="0" cellspacing="0" style="width:100%;"> <colgroup> -- seccion de medicion mediante porcentaje de columnas, depende la cantidad de columnas agregamos el porcenaje como en este ejemplo hay 3 columnas "td" agregamos 3 "col width = .." -- <col width="48%" /> <--- En esta parte definimos el tamaño con porcentaje de una columna <col width="auto" /> <col width="48%" /> </colgroup> <tbody> <tr> <td> </td> <td> </td> <td> </td> </tr> </tbody> </table>
-- un ejemplo de como seria la tabla
-- primero cuento la cantidad de columnas y segun veo en este caso son 3 columnas en toda la tabla lo agregaria asi --
-- aqui hago 5 "tr" porque quiero 5 filas por ahora, y 3 "td" porque son 3 columnas, en la primera fila veo que coge "cuadro de acabados altanova toda la fila, para ese caso puedo crer una tabla de una fila, algo asi: si te das cuenta solo tiene 1tr y 1td porque solo sera para el titulo de la primera fila de la tabla del pdf
<table align="center" border="1" cellpadding="0" cellspacing="0" style="width:100%;"> <tbody> <tr> <td> cuadro de acabados altanova</td> </tr> </tbody> </table> luego un espacio y viene la siguiente tabla el titulo en cada columna, luego viene la enumeracion q cada enumeracion es un "subtitulo" por lo que veo, y luego vien el rellenado, respecto al color si gutas lo peudes poner en la misma fila enumerada para no complicarnos tanto, ahora el detalle de como juntar las columnas por ejemplo en "1 estructura" y para todos los q son asi seria como el ejemplo aqui <table align="center" border="1" cellpadding="0" cellspacing="0" style="width:100%;"> <colgroup> <col width="2%" /> <col width="25%" /> <col width="73%" /> </colgroup> <tbody> <tr> <td>1</td> <td colspan="2" rowspan="1">Estructura</td> <-- Aqui el "coldspan="2" dice que cogio 2 columnas y rowspan="1" porque es su misma fila, </tr> <tr> <td> </td> <td> </td> <td> </td> </tr> <tr> <td> </td> <td> </td> <td> </td> </tr> <tr> <td> </td> <td> </td> <td> </td> </tr> <tr> <td> </td> <td> </td> <td> </td> </tr> </tbody> </table>

ahora te dare un ejemplo de los rowspan, hay casos que necesitaremos juntar filas largas de muchas columnas como filas de la misma columna, en este caso haremos de la misma columna para quese vea identico como en la seccion "2 sala - comedor" del pdf:
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


# Esqueleto de salida fijo confirmado como bueno (Ficha de Actualización de
# Datos / Convenio de Separación). Las imágenes de cabecera/pie se agregan por
# proyecto más adelante; acá van como placeholders vacíos.
_SKELETON_TEMPLATE = """<style type="text/css">@page {
    margin: 0;
  }
  body{
    font-family: 'Arial';
	font-size: 11pt;
    margin: 0;
    padding: 0.5cm 1.53cm;
  }
  div, p, li{
    text-align: justify;
  }
  table, thead, tbody
  {
    vertical-align: top;
    border-collapse: collapse;
    box-sizing: border-box;
  }
  .firmas {
    border-top: 1px dotted #000;
  }
  .ajusTabla {
    font-size: 0.8em;
    text-align: center;
  }
  .contenido{
    z-index: 1;
  }
  .cabecera{
    top: 0;
    left: 0;
    right: 0;
    width: 100%;
  }
  .pie_pagina{
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
  }
  .img_cabecera{
    width: 100%;
    display: block;
  }
  .img_pie_pagina{
    width: 100%;
    display: block;
  }
  .cuerpo-texto{}
  @media screen{
    .cabecera, .pie_pagina{
      position: initial;
	}
    .espacio-cabecera, .espacio-pie{
      height: 0;
    }
  }
  @media print{
    .cabecera{
      position: fixed;
	}
    .pie_pagina{
      position: fixed;
    }
    .espacio-cabecera{
      height: 2.3cm;
    }
    .espacio-pie{
      height: 0.5cm;
    }
  }
</style>
<div class="cabecera">
  <!-- banner image goes here later, per-project -->
</div>
<table class="contenido" style="font-size: 10pt;" width="100%">
	<thead>
		<tr class="espacio-cabecera">
			<td> </td>
		</tr>
	</thead>
	<tfoot>
		<tr>
			<td>
			<div class="espacio-pie" style="height: 35px; background-color: white"> </div>
			</td>
		</tr>
		<tr><td> </td></tr>
		<tr><td> </td></tr>
	</tfoot>
	<tbody>
		<tr>
			<td class="cuerpo-texto">
			<!-- content goes here, unchanged -->
			</td>
		</tr>
	</tbody>
</table>
<div class="pie_pagina">
  <!-- footer image goes here later, per-project -->
</div>"""

_SKELETON_PROMPT = (
    "Vas a recibir el HTML del cuerpo de un documento (ya convertido y corregido). "
    "Envuélvelo en el esqueleto de salida fijo que aparece abajo como plantilla "
    "canónica, cumpliendo estas reglas:\n"
    "- El contenido recibido va DENTRO de <td class=\"cuerpo-texto\">, exactamente "
    "igual: no borres, no reescribas, no cambies colores/valores/estructura del "
    "contenido (fidelidad total — solo agregás el envoltorio).\n"
    "- REGLA DE FIDELIDAD CRÍTICA: el texto visible del contenido debe quedar "
    "idéntico carácter por carácter al texto de entrada. Solo podés cambiar la "
    "estructura/wrapping HTML (tags, clases, anidamiento) alrededor del texto; "
    "jamás reformules, mejores ni alteres el texto real. Si cambiás una sola "
    "letra, el resultado es inválido.\n"
    "- El <style> de la plantilla va tal cual. Podés agregar reglas o clases CSS "
    "nuevas si hace falta para que la estructura no quede engorrosa, pero NO "
    "renombres ni elimines las clases ya reconocidas (.ajusTabla, .firmas, "
    ".contenido, .cabecera, .pie_pagina, .cuerpo-texto, .espacio-cabecera, "
    ".espacio-pie, .img_cabecera, .img_pie_pagina).\n"
    "- .cabecera y .pie_pagina quedan como divs placeholder VACÍOS, sin <img src> "
    "todavía (el banner y el pie se rellenan por proyecto después).\n"
    "- Devuelve el documento HTML completo (con su <style> y la estructura "
    "thead/tfoot/tbody), con el contenido dentro de .cuerpo-texto.\n\n"
    "PLANTILLA DE ESQUELETO:\n"
    + _SKELETON_TEMPLATE
)

_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_STYLE_RE = re.compile(r"<style[^>]*>.*?</style>", re.DOTALL | re.IGNORECASE)
_SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.DOTALL | re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]*>")
_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_visible_text(html: str) -> str:
    """Texto visible normalizado (sin tags/comentarios/style, whitespace colapsado).

    Útil para verificar la regla de fidelidad textual: el esqueleto agrega solo
    estructura (tags, clases) y whitespace/comentarios, que acá se descartan,
    así que comparar el texto normalizado de entrada vs salida detecta si la IA
    reformuló o alteró el contenido.
    """
    text = _COMMENT_RE.sub("", html)
    text = _STYLE_RE.sub("", text)
    text = _SCRIPT_RE.sub("", text)
    text = _TAG_RE.sub("", text)
    text = unescape(text)
    text = text.replace("\xa0", " ")
    return _WHITESPACE_RE.sub(" ", text).strip()


def _describe_divergence(a: str, b: str) -> str:
    """Describe el primer punto donde dos textos normalizados difieren.

    Devuelve el índice del primer carácter distinto y ~50 caracteres de contexto
    de cada texto alrededor de ese punto. No vuelca el documento completo: solo
    lo justo para diagnosticar (truncamiento vs. reformulación real).
    """
    limit = min(len(a), len(b))
    idx = next((i for i in range(limit) if a[i] != b[i]), limit)
    window = 50
    start = max(0, idx - window)
    return (
        f"primer desajuste en el índice {idx}: "
        f"entrada=[…{a[start:idx + window]}…] "
        f"salida=[…{b[start:idx + window]}…]"
    )


def _deepseek_chat(system_content: str, user_content: str) -> str | None:
    """POST a DeepSeek y devuelve el content del modelo, o None si falla."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        logger.warning("DEEPSEEK_API_KEY no está configurada; se omite la pasada de IA.")
        return None

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": MAX_OUTPUT_TOKENS,
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
        logger.warning("Falló la llamada a DeepSeek: %s", exc)
        return None

    if isinstance(content, str) and content.strip():
        return content
    return None


def enhance_tables_with_ai(html: str) -> str:
    """Corrige tablas complejas con DeepSeek; degrada a `html` si algo falla."""
    system_content = _OUTPUT_FORMAT_INSTRUCTION + _TABLE_PROMPT + "\n\n" + _SYSTEM_APPENDIX
    result = _deepseek_chat(system_content, html)
    if result is None:
        return html
    if _has_document_wrapper(result):
        logger.warning(
            "DeepSeek envolvió la salida en un documento completo "
            "(DOCTYPE/html/head/body); se descarta y se devuelve el HTML sin corregir."
        )
        return html
    return result


def apply_skeleton_and_verify(html: str) -> str:
    """Envuelve el HTML en el esqueleto fijo y verifica fidelidad (DeepSeek).

    Degrada con gracia: si falta la clave, la llamada falla, o la salida del
    modelo alteró el texto visible del contenido, devuelve `html` sin el
    esqueleto, sin romper la conversión.
    """
    result = _deepseek_chat(_SKELETON_PROMPT, html)
    if result is None:
        return html
    input_text = _normalize_visible_text(html)
    output_text = _normalize_visible_text(result)
    if input_text != output_text:
        logger.warning(
            "DeepSeek alteró el texto del contenido; se descarta su salida y se "
            "devuelve el HTML sin esqueleto. len(entrada)=%d, len(salida)=%d; %s",
            len(input_text),
            len(output_text),
            _describe_divergence(input_text, output_text),
        )
        return html
    return result


def word_to_html_full_pipeline(docx_path: Path) -> str:
    """Pipeline completo: Etapa 1 → Etapa 2 → Etapa 3, en orden."""
    stage1 = docx_to_html(docx_path)
    stage2 = enhance_tables_with_ai(stage1)
    return apply_skeleton_and_verify(stage2)

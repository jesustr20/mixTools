"""
Herramienta 2: Word -> HTML limpio.

word2cleanhtml.com usa un conversor genérico y deja basura de MS Word
(mso-*, spans vacíos, estilos inline redundantes). Aquí usamos mammoth
(ya lo tienes en tu flujo) + una pasada de limpieza real con BeautifulSoup,
en vez de solo un regex superficial.
"""
import re
from pathlib import Path

import mammoth
from bs4 import BeautifulSoup, Comment

# Atributos/estilos que mammoth o Word podrían dejar y que casi nunca
# quieres en un HTML "limpio" para pegar en un CMS/CRM (como Sperant).
JUNK_INLINE_STYLE_PATTERNS = [
    r"mso-[^;:]+:[^;]+;?",
    r"font-family:\s*[^;]+;?",
]

EMPTY_TAGS_TO_UNWRAP = {"span"}  # spans vacíos o sin atributos útiles se eliminan


def word_to_clean_html(docx_path: Path, strip_styles: bool = True) -> str:
    with open(docx_path, "rb") as f:
        result = mammoth.convert_to_html(f)
    html = result.value  # mammoth ya produce HTML semántico (h1, p, strong, etc.)

    soup = BeautifulSoup(html, "lxml")

    # 1. Quitar comentarios
    for c in soup.find_all(string=lambda text: isinstance(text, Comment)):
        c.extract()

    # 2. Quitar estilos inline "basura" de Word si el usuario lo pide
    if strip_styles:
        for tag in soup.find_all(style=True):
            style = tag["style"]
            for pattern in JUNK_INLINE_STYLE_PATTERNS:
                style = re.sub(pattern, "", style, flags=re.IGNORECASE)
            style = style.strip(" ;")
            if style:
                tag["style"] = style
            else:
                del tag["style"]

    # 3. Reemplazar &nbsp; por espacio real (regla que ya sigues en tus
    #    conversiones manuales: nunca dejar &nbsp; suelto)
    for text_node in soup.find_all(string=re.compile("\xa0")):
        text_node.replace_with(text_node.replace("\xa0", " "))

    # 4. Quitar spans vacíos o sin atributos (basura típica de exportadores Word)
    for tag in soup.find_all(list(EMPTY_TAGS_TO_UNWRAP)):
        if not tag.attrs and (not tag.get_text(strip=True)):
            tag.decompose()
        elif not tag.attrs:
            tag.unwrap()  # span sin atributos: dejar solo el texto

    # 5. Quitar atributos de clase que mammoth a veces agrega sin necesidad real
    for tag in soup.find_all(class_=True):
        if not tag["class"]:
            del tag["class"]

    return str(soup)


def word_to_clean_html_file(docx_path: Path, out_path: Path, strip_styles: bool = True) -> Path:
    html = word_to_clean_html(docx_path, strip_styles=strip_styles)
    out_path.write_text(html, encoding="utf-8")
    return out_path

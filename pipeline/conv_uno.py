"""Convierte un PDF a Markdown bruto con pymupdf4llm (mismas opciones que conv.py).

Uso: python -I pipeline/conv_uno.py <pdf> <salida.raw.md>
"""
import sys, site, pathlib
sys.path.append(site.getusersitepackages())  # psutil vive en el site de usuario y -I lo excluye
import pymupdf4llm

pdf, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
md = pymupdf4llm.to_markdown(str(pdf), ignore_images=True, ignore_graphics=True, show_progress=False,
                             use_ocr=False, header=False, footer=False)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(md, encoding='utf-8')
print(pdf.name, len(md), 'caracteres')

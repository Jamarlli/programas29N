"""Convierte a Markdown bruto todos los PDF de una carpeta. Uso: python pipeline/conv.py <dir_pdf> <dir_salida>"""
import sys, pathlib, pymupdf4llm
src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out.mkdir(exist_ok=True)
for p in sorted(src.glob("*.pdf")):
    md = pymupdf4llm.to_markdown(str(p), ignore_images=True, ignore_graphics=True, show_progress=False, use_ocr=False, header=False, footer=False)
    (out / (p.stem + ".raw.md")).write_text(md, encoding="utf-8")
    print(p.name, len(md))

"""Limpia el Markdown bruto de un programa nuevo y lo deja en markdown/<CLAVE>_2026_programa.md.

Uso: python -I pipeline/limpia_uno.py <id_partido> <bruto.raw.md>

Aplica la limpieza genérica de clean.py y, entre medias, la propia del programa:
pipeline/limpia/<id>.py, con una función limpiar(lineas) -> lineas y, opcionalmente,
DROP = (regex, ...) con líneas que se quitan enteras (cabeceras, pies, números de página).
Los datos del partido (nombre, fuente…) salen de data/partidos.json.
"""
import sys, json, hashlib, pathlib, importlib.util
aqui = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(aqui))
from clean import generic_pre, join_broken, generic_post
import pymupdf

raiz = aqui.parent
pid, raw = sys.argv[1], pathlib.Path(sys.argv[2])
P = {p['id']: p for p in json.loads((raiz / 'data' / 'partidos.json').read_text(encoding='utf-8'))}[pid]
spec = importlib.util.spec_from_file_location(f'limpia_{pid}', aqui / 'limpia' / f'{pid}.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

lines = generic_pre(raw.read_text(encoding='utf-8'))
lines = mod.limpiar(lines)
lines = '\n'.join(lines).split('\n')
lines = join_broken(lines)
body = generic_post(lines, getattr(mod, 'DROP', ()))
if not body.startswith('# '):
    sys.exit('El Markdown limpio debe empezar por «# Título del programa».')
titulo = body.split('\n', 1)[0][2:].strip()

pdf = raiz / P['pdf']
sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
pags = pymupdf.open(pdf).page_count
q = lambda s: s.replace('"', "'")
head = f"""---
partido: "{q(P['partido'])}"
titulo: "{q(titulo)}"
eleccion: "Elecciones generales (Congreso y Senado), 29 de noviembre de 2026"
fuente_pdf: "{P['fuente']}"
tipo_fuente: "{q(P['tipo_fuente'])}"
paginas_pdf: {pags}
sha256_pdf: "{sha}"
fecha_descarga: "2026-11-17"
conversion: "pymupdf4llm (sin OCR, sin imagenes) + limpieza: union de palabras y parrafos partidos, indice y cabeceras eliminados, jerarquia de titulos normalizada"
---

"""
dst = raiz / 'markdown' / f"{P['clave']}_2026_programa.md"
dst.write_text(head + body, encoding='utf-8')
print(f'{dst.name}: {len(body.split())} palabras, {pags} páginas del PDF')

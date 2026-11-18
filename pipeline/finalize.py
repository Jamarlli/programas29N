"""Añade la cabecera con la fuente a los Markdown limpios de PP, PSOE, Vox y FA.

Uso: python pipeline/finalize.py <dir_md_limpio> <dir_pdf> <dir_salida>
"""
import sys, pathlib, hashlib
src, pdfs, dst = map(pathlib.Path, sys.argv[1:4])
META = {
 'PP': ('Partido Popular (PP)', 'Reconstrucción Nacional', 'https://www.pp.es/wp-content/uploads/2026/11/PROGRAMA-ELECTORAL-PP-2026-RECONSTRUCCION-NACIONAL.pdf', 'oficial (pp.es)'),
 'PSOE': ('Partido Socialista Obrero Español (PSOE)', 'La fuerza de la gente. La fuerza de seguir avanzando', 'https://www.democrata.es/uploads/s1/35/40/05/6/programapsoe29n26.pdf', 'copia publicada por Demócrata (la web del PSOE no era accesible)'),
 'VOX': ('VOX', 'Es sentido común', 'https://www.voxespana.es/wp-content/uploads/2026/11/Programa-completo-A5-1.pdf', 'oficial (voxespana.es)'),
 'FRENTEAMPLIO': ('Frente Amplio (Movimiento Sumar, IU, Comuns, Más Madrid y otros)', 'Un programa como una casa', 'https://frenteamplio.info/pdf/ProgramaFrenteAmplio.pdf', 'oficial (frenteamplio.info)'),
}
import pymupdf
dst.mkdir(parents=True, exist_ok=True)
for f in sorted(src.glob('*.md')):
    k = f.name.split('_')[0]; partido, titulo, url, tipo = META[k]
    pdf = pdfs / f.name.replace('.md', '.pdf')
    sha = hashlib.sha256(pdf.read_bytes()).hexdigest(); pags = pymupdf.open(pdf).page_count
    body = f.read_text(encoding='utf-8')
    if not body.startswith('# '):
        body = f'# {titulo}\n\n' + body
    head = f"""---
partido: "{partido}"
titulo: "{titulo}"
eleccion: "Elecciones generales (Congreso y Senado), 29 de noviembre de 2026"
fuente_pdf: "{url}"
tipo_fuente: "{tipo}"
paginas_pdf: {pags}
sha256_pdf: "{sha}"
fecha_descarga: "2026-11-17"
conversion: "pymupdf4llm 2.1 (sin OCR, sin imagenes) + limpieza: union de palabras y parrafos partidos, indice eliminado, jerarquia de titulos normalizada"
---

"""
    (dst / f.name).write_text(head + body, encoding='utf-8')
    print(f.name, pags, len(body.split()), 'palabras')

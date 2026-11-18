"""Compara palabras y restos de maquetación entre cada PDF y su Markdown. Uso: python pipeline/verify.py <dir_pdf> <dir_md>"""
import sys, pathlib, re, pymupdf
pdfs, mds = map(pathlib.Path, sys.argv[1:3])
for md in sorted(mds.glob('*.md')):
    t = md.read_text(encoding='utf-8')
    pdf_words = sum(len(p.get_text().split()) for p in pymupdf.open(pdfs / md.name.replace('.md','.pdf')))
    words = len(re.sub(r'[#*_|]', ' ', t.split('---',2)[2]).split())
    hy = len(re.findall(r'[a-záéíóúñ]-\n', t))
    pag = len(re.findall(r'Pág\.|\.{6,}', t))
    tables = sum(1 for l in t.split('\n') if l.startswith('|'))
    h = {n: len(re.findall(rf'^{"#"*n} ', t, re.M)) for n in range(1,6)}
    print(f"{md.name}: md {words} / pdf {pdf_words} palabras ({words/pdf_words:.1%}); guion-fin {hy}; restos indice {pag}; lineas tabla {tables}; titulos {h}")

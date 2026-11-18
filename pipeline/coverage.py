"""Comprueba que cada línea de texto del PDF aparece en el Markdown. Uso: python pipeline/coverage.py <pdf> <md>"""
import sys, re, unicodedata, pymupdf

def norm(s):
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '', s)

pdf, md = sys.argv[1:3]
mdn = norm(re.sub(r'[*_#|]', ' ', open(md, encoding='utf-8').read()))
missing = []
for i, page in enumerate(pymupdf.open(pdf)):
    for line in page.get_text().split('\n'):
        l = line.strip().rstrip('-')
        if len(l.split()) < 4:
            continue
        n = norm(l)
        # tolerar guiones de corte al final/principio
        if n and n not in mdn and n[:-2] not in mdn and n[2:] not in mdn:
            missing.append((i + 1, l))
print(f"{md}: {len(missing)} líneas del PDF no encontradas")
for p, l in missing:
    print(f"  p{p}: {l[:150]}")

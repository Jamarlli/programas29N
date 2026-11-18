"""Reparte los extractos en lotes para clasificarlos.

Uso: python -I pipeline/lotes.py <extractos.json> <dir_lotes> <n_lotes>
"""
import json, sys, pathlib

src, out, n = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), int(sys.argv[3])
d = json.loads(src.read_text(encoding='utf-8'))
out.mkdir(parents=True, exist_ok=True)
total = sum(f['palabras'] for f in d)
objetivo = total / n
lotes, actual, acum = [], [], 0
for f in d:
    actual.append({k: f[k] for k in ('id', 'partido', 'tipo', 'numero', 'ruta', 'texto')})
    acum += f['palabras']
    if acum >= objetivo * (len(lotes) + 1) and len(lotes) < n - 1:
        lotes.append(actual)
        actual = []
if actual:
    lotes.append(actual)
for i, l in enumerate(lotes, 1):
    (out / f'lote-{i:02d}.json').write_text(json.dumps(l, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'lote-{i:02d}: {len(l)} extractos, {l[0]["id"]} … {l[-1]["id"]}')

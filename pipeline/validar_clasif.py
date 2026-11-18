"""Comprueba un fichero de clasificación contra su lote y la taxonomía.

Uso: python -I pipeline/validar_clasif.py <taxonomia.json> <lote.json> <clasif.json>
Sale con código 1 y lista los errores si algo no cuadra.
"""
import json, sys, pathlib

tax = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
lote = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding='utf-8'))
try:
    cl = json.loads(pathlib.Path(sys.argv[3]).read_text(encoding='utf-8'))
except Exception as e:
    print('JSON inválido:', e); sys.exit(1)

subtemas = {s['id'] for b in tax['bloques'] for s in b['subtemas']}
ejes = {e['id']: {p['id'] for p in e['posiciones']} for e in tax['ejes']}
errores = []
ids_lote = [f['id'] for f in lote]
ids_cl = [c.get('id') for c in cl]
faltan = [i for i in ids_lote if i not in ids_cl]
sobran = [i for i in ids_cl if i not in ids_lote]
dup = sorted({i for i in ids_cl if ids_cl.count(i) > 1})
if faltan: errores.append(f'faltan {len(faltan)} ids: {faltan[:10]}')
if sobran: errores.append(f'ids que no son del lote: {sobran[:10]}')
if dup: errores.append(f'ids duplicados: {dup[:10]}')
for c in cl:
    i = c.get('id')
    if c.get('subtema') not in subtemas:
        errores.append(f'{i}: subtema desconocido {c.get("subtema")!r}')
    for s in c.get('otros', []):
        if s not in subtemas:
            errores.append(f'{i}: subtema secundario desconocido {s!r}')
    if len(c.get('otros', [])) > 2:
        errores.append(f'{i}: más de 2 subtemas secundarios')
    t = c.get('titular', '')
    if not t or len(t.split()) > 14:
        errores.append(f'{i}: titular vacío o de más de 14 palabras')
    for e in c.get('ejes', []):
        if e.get('eje') not in ejes:
            errores.append(f'{i}: eje desconocido {e.get("eje")!r}')
        elif e.get('posicion') not in ejes[e['eje']]:
            errores.append(f'{i}: posición {e.get("posicion")!r} no existe en {e["eje"]}')
if errores:
    print(f'{len(errores)} errores'); print('\n'.join(errores[:60])); sys.exit(1)
print(f'OK: {len(cl)} extractos clasificados')

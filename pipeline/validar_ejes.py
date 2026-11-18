"""Comprueba un fichero de marcas de ejes contra sus candidatos.

Uso: python -I pipeline/validar_ejes.py <candidatos-NN.json> <marcas-NN.json>
Cada marca: {"eje", "id", "posicion", "cita"}. La cita debe ser literal del extracto.
"""
import json, re, sys, pathlib


def plano(s):
    s = re.sub(r'[*_]', '', s)
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'\s+', ' ', s).strip()


cands = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
try:
    marcas = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding='utf-8'))
except Exception as e:
    print('JSON inválido:', e); sys.exit(1)
ejes = {p['eje']: {x['id'] for x in p['posiciones']} for p in cands}
textos = {p['eje']: {c['id']: plano(c['texto']) for c in p['candidatos']} for p in cands}
err = []
vistos = set()
for m in marcas:
    e, i, pos, cita = m.get('eje'), m.get('id'), m.get('posicion'), m.get('cita', '')
    if e not in ejes:
        err.append(f'eje que no es de este grupo: {e}'); continue
    if pos not in ejes[e]:
        err.append(f'{e}/{i}: posición desconocida {pos!r}')
    if i not in textos[e]:
        err.append(f'{e}/{i}: el extracto no está entre los candidatos de ese eje'); continue
    if (e, i, pos) in vistos:
        err.append(f'{e}/{i}: marca repetida')
    vistos.add((e, i, pos))
    c = plano(cita)
    if not c or len(c.split()) > 45:
        err.append(f'{e}/{i}: cita vacía o de más de 45 palabras')
    elif c not in textos[e][i]:
        err.append(f'{e}/{i}: la cita no es literal: «{c[:80]}»')
if err:
    print(f'{len(err)} errores'); print('\n'.join(err[:60])); sys.exit(1)
por = {}
for m in marcas:
    por.setdefault(m['eje'], 0)
    por[m['eje']] += 1
print(f'OK: {len(marcas)} marcas en {len(por)} ejes de {len(ejes)}')

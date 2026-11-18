"""Une la clasificación por lotes en data/clasificacion.json, con los ids actuales.

Cada entrada guarda la huella (partido + texto) del extracto. Si se vuelve a trocear un
programa y los ids cambian, build_web.py la recupera por la huella.
También aplica las correcciones de subtema decididas al revisar las notas de los lotes.

Uso: python -I pipeline/fusionar_clasif.py <raiz_proyecto>
"""
import json, re, sys, hashlib, pathlib

raiz = pathlib.Path(sys.argv[1])
data = raiz / 'data'

# Correcciones tras revisar las notas «SIN ENCAJE» (ids de los lotes)
CORRECCIONES = {
    'edu-modelo': ['psoe-0221', 'fa-0189', 'fa-0190', 'psoe-0232', 'psoe-0234'],
    'seg-terrorismo': ['pp-0146', 'vox-0110'],
    'pres-por-anunciar': ['pp-0094', 'pp-0124', 'pp-0148', 'pp-0183', 'pp-0186', 'pp-0192', 'pp-0219', 'pp-0229'],
}


def huella(partido, texto):
    return hashlib.sha1((partido + '\x00' + re.sub(r'\s+', ' ', texto).strip()).encode('utf-8')).hexdigest()


def main():
    por_huella = {}
    for lote in sorted((data / 'lotes').glob('lote-*.json')):
        textos = {f['id']: (f['partido'], f['texto']) for f in json.loads(lote.read_text(encoding='utf-8'))}
        cf = data / 'clasif' / lote.name
        if not cf.exists():
            print(f'{lote.name}: aún sin clasificar')
            continue
        for c in json.loads(cf.read_text(encoding='utf-8')):
            for sub, ids in CORRECCIONES.items():
                if c['id'] in ids:
                    c['otros'] = [x for x in c.get('otros', []) if x != sub]
                    c['subtema'] = sub
            por_huella[huella(*textos[c['id']])] = c

    extractos = json.loads((data / 'extractos.json').read_text(encoding='utf-8'))
    out, faltan = [], []
    for f in extractos:
        h = huella(f['partido'], f['texto'])
        c = por_huella.get(h)
        if not c:
            faltan.append(f['id'])
            continue
        out.append({'id': f['id'], 'huella': h, 'subtema': c['subtema'], 'otros': c.get('otros', []),
                    'titular': c['titular'], 'ejes': c.get('ejes', []), 'nota': c.get('nota', '')})
    (data / 'clasificacion.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{len(out)} clasificados; sin clasificación: {faltan}')


main()

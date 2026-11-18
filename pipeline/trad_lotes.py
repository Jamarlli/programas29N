"""Prepara los lotes de traducción de los programas: data/trad/lotes/<idioma>-NNN.txt.

Uso: python -I pipeline/trad_lotes.py [palabras_por_lote]

Idiomas de la web: es (castellano), ca (catalán), va (valenciano), gl (gallego), eu (euskera).
Cada programa está en su idioma original (campo «idioma» de data/partidos.json, con el nombre del idioma; si no lo tiene, es castellano).
- El texto de un programa se traduce a todos los idiomas salvo al suyo. Catalán y valenciano cuentan como
  el mismo idioma: un programa en catalán (ERC, Junts, Comuns, Convergents) o en valenciano (Compromís)
  se deja tal cual en las dos versiones.
- Los titulares de los extractos son nuestros y están en castellano: se traducen a los demás idiomas.
- Las citas de «Dónde chocan» son trozos literales del texto: se traducen junto con su extracto y tienen que
  salir tal cual dentro de la traducción, para que la web pueda subrayarlas.
- Los títulos de los apartados (rutas) y el título de cada programa van en un lote aparte: <idioma>-rutas.txt.

Formato de un lote (y de su traducción, que es igual, con los textos traducidos):
    @@@ <id del extracto>
    @h
    <titular>
    @t
    <texto del extracto en Markdown, con sus líneas en blanco>
    @q
    <cita>
Ninguna línea de los programas empieza por «@», así que las marcas no se confunden con el texto.
"""
import collections, hashlib, json, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATA = RAIZ / 'data'
IDIOMAS = ['es', 'ca', 'va', 'gl', 'eu']
CODIGO = {'castellano': 'es', 'catalán': 'ca', 'valenciano': 'va', 'gallego': 'gl', 'euskera': 'eu'}
GRUPO = {'es': 'es', 'ca': 'ca', 'va': 'ca', 'gl': 'gl', 'eu': 'eu'}


def clave(partido, texto):  # misma huella que build_web.py y fusionar_clasif.py
    return hashlib.sha1((partido + '\x00' + re.sub(r'\s+', ' ', texto).strip()).encode('utf-8')).hexdigest()


def cargar():
    partidos = json.loads((DATA / 'partidos.json').read_text(encoding='utf-8'))
    idioma = {p['id']: CODIGO[p.get('idioma', 'castellano')] for p in partidos}
    orden_p = {p['id']: k for k, p in enumerate(partidos)}
    ext = json.loads((DATA / 'extractos.json').read_text(encoding='utf-8'))
    ext = [e for e in ext if e['partido'] in idioma]
    ext.sort(key=lambda e: (orden_p[e['partido']], e['orden']))
    clasif = {c['huella']: c for c in json.loads((DATA / 'clasificacion.json').read_text(encoding='utf-8'))}
    por_huella = {clave(e['partido'], e['texto']): e['id'] for e in ext}
    citas = collections.defaultdict(list)
    for mf in sorted((DATA / 'ejes').glob('marcas-*.json')):
        cf = mf.with_name(mf.name.replace('marcas', 'candidatos'))
        tx = {c['id']: (c['partido'], c['texto']) for p in json.loads(cf.read_text(encoding='utf-8')) for c in p['candidatos']}
        for m in json.loads(mf.read_text(encoding='utf-8')):
            i = por_huella.get(clave(*tx[m['id']]))
            if i and m['cita'] and m['cita'] not in citas[i]:
                citas[i].append(m['cita'])
    titular = {e['id']: clasif.get(clave(e['partido'], e['texto']), {}).get('titular', '') for e in ext}
    fm = {}
    for p in partidos:
        md = RAIZ / 'markdown' / f"{p['clave']}_2026_programa.md"
        if md.exists():
            t = md.read_text(encoding='utf-8').split('---', 2)[1]
            fm[p['id']] = re.search(r'^titulo:\s*"?(.*?)"?\s*$', t, re.M).group(1)
    return partidos, idioma, ext, citas, titular, fm


def item(e, h, t, q):
    out = [f"@@@ {e['id']}"]
    if h is not None:
        out += ['@h', h]
    if t is not None:
        out += ['@t', t.strip('\n')]
        for c in q:
            out += ['@q', c]
    return '\n'.join(out)


def main():
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 12000
    partidos, idioma, ext, citas, titular, titulos = cargar()
    dest = DATA / 'trad' / 'lotes'
    dest.mkdir(parents=True, exist_ok=True)
    indice = {}
    for L in IDIOMAS:
        lotes, actual, pal = [], [], 0
        for e in ext:
            traducir_t = GRUPO[idioma[e['partido']]] != GRUPO[L]
            h = titular[e['id']] if L != 'es' and titular[e['id']] else None
            if not traducir_t and h is None:
                continue
            n = (e['palabras'] if traducir_t else 0) + (len(h.split()) if h else 0)
            if actual and pal + n > limite:
                lotes.append(actual)
                actual, pal = [], 0
            actual.append((e, h, e['texto'] if traducir_t else None, citas.get(e['id'], []) if traducir_t else []))
            pal += n
        if actual:
            lotes.append(actual)
        for k, l in enumerate(lotes, 1):
            nombre = f'{L}-{k:03d}'
            (dest / f'{nombre}.txt').write_text('\n'.join(item(*x) for x in l) + '\n', encoding='utf-8')
            indice[nombre] = {'idioma': L, 'origen': sorted({idioma[x[0]['partido']] for x in l if x[2] is not None}),
                              'extractos': len(l), 'palabras': sum((x[0]['palabras'] if x[2] is not None else 0) + (len(x[1].split()) if x[1] else 0) for x in l),
                              'partidos': list(dict.fromkeys(x[0]['partido'] for x in l))}
        # títulos de apartado y título del programa, de los programas que hay que traducir a este idioma
        rutas = []
        vistos = set()
        for p in partidos:
            if GRUPO[idioma[p['id']]] == GRUPO[L] or p['id'] not in titulos:
                continue
            rutas.append(f"@@@ titulo:{p['id']}\n@s\n{titulos[p['id']]}")
            for e in ext:
                if e['partido'] != p['id']:
                    continue
                for s in e['ruta']:
                    if (p['id'], s) not in vistos:
                        vistos.add((p['id'], s))
                        rutas.append(f"@@@ ruta:{p['id']}:{len([v for v in vistos if v[0] == p['id']])}\n@s\n{s}")
        if rutas:
            (dest / f'{L}-rutas.txt').write_text('\n'.join(rutas) + '\n', encoding='utf-8')
            indice[f'{L}-rutas'] = {'idioma': L, 'extractos': len(rutas), 'palabras': sum(len(r.split('\n', 2)[2].split()) for r in rutas)}
        print(L, len(lotes), 'lotes,', sum(v['palabras'] for k, v in indice.items() if v['idioma'] == L), 'palabras')
    (DATA / 'trad' / 'indice.json').write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()

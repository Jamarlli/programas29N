"""Textos de la web que no son de los programas: interfaz, temas, preguntas de «Dónde chocan» y fuentes.

  python -I pipeline/i18n.py catalogo        escribe data/i18n/catalogo.json con todos los textos en castellano
  python -I pipeline/i18n.py validar <idioma> comprueba data/i18n/<idioma>.json contra el catálogo

Formato de data/i18n/<idioma>.json (y del catálogo, que lleva el castellano en los valores):
  "ui":      {frase de app.js en castellano: traducción}   (las frases de t('…') y de plural(n, '…', '…'))
  "html":    {texto de index.html: traducción}
  "temas":   {id de tema o subtema: nombre}
  "ejes":    {id de pregunta: {"pregunta": …, "posiciones": {id: nombre}}}
  "fuentes": {id de partido: tipo de fuente}
Las marcas {n}, {x}… y las etiquetas HTML tienen que seguir en la traducción, las mismas y las mismas veces.
"""
import collections, json, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DIR = RAIZ / 'data' / 'i18n'

# textos de index.html que se traducen; en el HTML aparecen como >texto< o "texto"
HTML = [
    'Qué propone cada partido sobre cada tema y dónde chocan entre sí. No es lo que &quot;dijo&quot; un representante nosedónde, sino lo que pone en su programa electoral.',
    'Qué proponen los partidos para el 29N',
    'Programas 29N: qué proponen los partidos para el 29N, con un ejemplo de «Dónde chocan» sobre el precio del alquiler.',
    'Saltar al contenido', 'Programas 29N, inicio', 'Generales · 29 nov 2026', 'Secciones', 'Temas', 'Dónde chocan', 'Buscar',
    'Programas', 'Buscar en los programas', 'Buscar en los programas…', 'Añadir partidos', 'Partidos', 'Cargando los programas…',
    'Esta web necesita JavaScript para mostrar los programas.',
]

# nota al principio de cada programa traducido en los ZIP de Markdown (la usa build_web.py; va en la sección «ui»)
AVISO_MD = 'Traducción automática y revisada del programa original en {x}, hecha por Programas 29N. El original: {u}'


def literales_t(js):
    """Primer argumento de cada t('…') y segundo y tercero de cada plural(…, '…', '…')."""
    out = re.findall(r"(?<![\w.])t\('((?:[^'\\]|\\.)*)'", js)
    for m in re.finditer(r'(?<![\w.])plural\(', js):
        i, prof, args, actual = m.end(), 1, [], ''
        while prof:
            c = js[i]
            if c == "'":
                j = i + 1
                while js[j] != "'":
                    j += 2 if js[j] == '\\' else 1
                actual += js[i:j + 1]
                i = j + 1
                continue
            if c in '([{':
                prof += 1
            elif c in ')]}':
                prof -= 1
                if not prof:
                    break
            if c == ',' and prof == 1:
                args.append(actual.strip())
                actual = ''
            else:
                actual += c
            i += 1
        args.append(actual.strip())
        for a in args[1:3]:
            if re.fullmatch(r"'(?:[^'\\]|\\.)*'", a):
                out.append(a[1:-1])
            elif m.start() > js.index('const plural'):
                raise ValueError(f'plural sin texto literal: {args}')
    return list(dict.fromkeys(x.replace("\\'", "'") for x in out))


def catalogo():
    js = (RAIZ / 'web' / 'app.js').read_text(encoding='utf-8')
    html = (RAIZ / 'web' / 'index.html').read_text(encoding='utf-8')
    for h in HTML:
        assert f'>{h}<' in html or f'"{h}"' in html, h
    tax = json.loads((RAIZ / 'data' / 'taxonomia.json').read_text(encoding='utf-8'))
    temas = {}
    for b in tax['bloques']:
        temas[b['id']] = b['nombre']
        for s in b['subtemas']:
            temas[s['id']] = s['nombre']
    ejes = {e['id']: {'pregunta': e['pregunta'], 'posiciones': {p['id']: p['nombre'] for p in e['posiciones']}} for e in tax['ejes']}
    fuentes = {}
    for p in json.loads((RAIZ / 'data' / 'partidos.json').read_text(encoding='utf-8')):
        md = RAIZ / 'markdown' / f"{p['clave']}_2026_programa.md"
        if md.exists():
            fuentes[p['id']] = re.search(r'^tipo_fuente:\s*"?(.*?)"?\s*$', md.read_text(encoding='utf-8').split('---', 2)[1], re.M).group(1)
    ui = literales_t(js) + [AVISO_MD]
    cat = {'ui': {s: s for s in ui}, 'html': {h: h for h in HTML}, 'temas': temas, 'ejes': ejes, 'fuentes': fuentes}
    DIR.mkdir(parents=True, exist_ok=True)
    (DIR / 'catalogo.json').write_text(json.dumps(cat, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f"catálogo: {len(ui)} frases de la interfaz, {len(HTML)} de index.html, {len(temas)} temas, {len(ejes)} preguntas, {len(fuentes)} fuentes")


marcas = lambda s: collections.Counter(re.findall(r'\{\w+\}|</?\w+[^>]*>|&\w+;', s))


def validar(idioma):
    cat = json.loads((DIR / 'catalogo.json').read_text(encoding='utf-8'))
    tr = json.loads((DIR / f'{idioma}.json').read_text(encoding='utf-8'))
    err = []
    def par(donde, a, b):
        if not isinstance(b, str) or not b.strip():
            err.append(f'{donde}: falta la traducción')
        elif marcas(a) != marcas(b):
            err.append(f'{donde}: marcas o etiquetas distintas: {dict(marcas(a))} → {dict(marcas(b))}')
    for sec in ('ui', 'html', 'temas', 'fuentes'):
        for k, v in cat[sec].items():
            par(f'{sec} «{k[:60]}»', v, tr.get(sec, {}).get(k))
        for k in tr.get(sec, {}):
            if k not in cat[sec]:
                err.append(f'{sec}: sobra «{k[:60]}» (ya no está en el catálogo)')
    for k, e in cat['ejes'].items():
        te = tr.get('ejes', {}).get(k, {})
        par(f'ejes {k} pregunta', e['pregunta'], te.get('pregunta'))
        for pk, pv in e['posiciones'].items():
            par(f'ejes {k} posición {pk}', pv, te.get('posiciones', {}).get(pk))
    for e in err:
        print('ERROR', e)
    print(f'{idioma}: {len(err)} errores')
    return not err


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1] == 'catalogo':
        catalogo()
    else:
        sys.exit(0 if validar(sys.argv[2]) else 1)

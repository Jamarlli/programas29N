"""Trocea los programas en Markdown en extractos literales.

Cada bloque de texto del programa acaba en exactamente un extracto (cobertura total).
- «medida»: una medida o compromiso numerado (o un punto de lista de primer nivel),
  con todo lo que cuelga de ella hasta la siguiente medida o título.
- «texto»: párrafos de exposición seguidos bajo un mismo título, agrupados hasta ~220 palabras.

Uso: python -I pipeline/segment.py <dir_markdown> <dir_pdf> <salida.json>
     python -I pipeline/segment.py --uno <id_partido> <salida.json>   (solo un programa nuevo, para revisarlo)

Salvo PP, PSOE y Vox, que numeran sus medidas a su manera, cada programa marca sus medidas
como puntos de lista de primer nivel («- » o «N. »). La lista de partidos sale de data/partidos.json.
"""
import json, re, sys, pathlib, unicodedata
import pymupdf

# Cómo empieza una medida numerada en cada programa
MEDIDA = {
    'PSOE': re.compile(r'^\*\*(\d+)\.'),
    'PP': re.compile(r'^\*\*(\d+)[ *]'),
    'VOX': re.compile(r'^(\d+)\.\s'),
    'FRENTEAMPLIO': None,
}
PARTIDO_ID = {'PSOE': 'psoe', 'PP': 'pp', 'VOX': 'vox', 'FRENTEAMPLIO': 'fa'}
MAX_TEXTO = 220
RAIZ = pathlib.Path(__file__).resolve().parent.parent
NUEVOS = [p for p in json.loads((RAIZ / 'data' / 'partidos.json').read_text(encoding='utf-8')) if p['clave'] not in MEDIDA]
for _p in NUEVOS:
    MEDIDA[_p['clave']] = None
    PARTIDO_ID[_p['clave']] = _p['id']


def norm(s):
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '', s)


def bloques(body):
    """Divide en bloques separados por línea en blanco; los subpuntos de lista se pegan a su punto."""
    out = []
    for raw in re.split(r'\n\s*\n', body):
        b = raw.strip('\n')
        if not b.strip():
            continue
        if re.match(r'^\s+[-*]\s', b) and out and not out[-1].startswith('#'):
            out[-1] += '\n' + b  # subpunto
        else:
            out.append(b)
    return out


def paginas(pdf):
    doc = pymupdf.open(pdf)
    return [norm(p.get_text()) for p in doc]


def buscar_pagina(texto, pags, desde):
    """Página (1-based) donde aparece el arranque del extracto; busca a partir de la última encontrada."""
    plano = re.sub(r'[*_#>`]|^\s*[-\d.]+\s', ' ', texto)
    n = norm(plano)
    for largo in (60, 35, 20):
        clave = n[:largo]
        if len(clave) < 12:
            continue
        for i in list(range(desde, len(pags))) + list(range(0, desde)):
            if clave in pags[i]:
                return i + 1
    return None


def segmentar(md_path, pdf_path, clave):
    txt = md_path.read_text(encoding='utf-8')
    body = txt.split('---', 2)[2]
    pags = paginas(pdf_path)
    patron = MEDIDA[clave]
    ruta = {}
    frags, actual = [], None

    def cerrar():
        nonlocal actual
        if actual:
            frags.append(actual)
            actual = None

    for b in bloques(body):
        h = re.match(r'^(#{1,6})\s+(.*)$', b)
        if h and '\n' not in b:
            cerrar()
            nivel = len(h.group(1))
            ruta = {k: v for k, v in ruta.items() if k < nivel}
            ruta[nivel] = h.group(2).strip()
            continue
        es_medida = False
        numero = None
        if patron is not None:
            m = patron.match(b)
            if m:
                es_medida, numero = True, m.group(1)
        else:  # cada punto de lista de primer nivel es una medida
            if re.match(r'^(-|\d+\.)\s', b):
                es_medida = True
        if es_medida:
            cerrar()
            actual = {'tipo': 'medida', 'numero': numero, 'ruta': [ruta[k] for k in sorted(ruta) if k > 1],
                      'bloques': [b]}
            continue
        if actual and actual['tipo'] == 'medida' and (re.match(r'^\s*[-*]\s', b) or patron is not None and clave in ('VOX', 'PP') and not b.startswith('_')):
            # subpuntos de una medida de Vox, o continuación de una medida del PP
            actual['bloques'].append(b)
            continue
        if actual and actual['tipo'] == 'texto':
            palabras = sum(len(x.split()) for x in actual['bloques'])
            if palabras + len(b.split()) <= MAX_TEXTO:
                actual['bloques'].append(b)
                continue
        cerrar()
        actual = {'tipo': 'texto', 'numero': None, 'ruta': [ruta[k] for k in sorted(ruta) if k > 1], 'bloques': [b]}
    cerrar()

    pid = PARTIDO_ID[clave]
    out, desde = [], 0
    for i, f in enumerate(frags, 1):
        texto = '\n\n'.join(f['bloques'])
        pag = buscar_pagina(texto, pags, desde)
        if pag:
            desde = pag - 1
        out.append({
            'id': f'{pid}-{i:04d}',
            'partido': pid,
            'orden': i,
            'tipo': f['tipo'],
            'numero': f['numero'],
            'ruta': f['ruta'],
            'pagina': pag,
            'palabras': len(re.sub(r'[*_#]', ' ', texto).split()),
            'texto': texto,
        })
    return out


def main(md_dir, pdf_dir, salida, solo=None):
    todos = []
    programas = [(c, pdf_dir / f'{c}_2026_programa.pdf') for c in ('PP', 'PSOE', 'VOX', 'FRENTEAMPLIO')]
    programas += [(p['clave'], RAIZ / p['pdf']) for p in NUEVOS if (RAIZ / 'markdown' / f"{p['clave']}_2026_programa.md").exists()]
    if solo:
        programas = [x for x in programas if PARTIDO_ID[x[0]] == solo]
    for clave, pdf in programas:
        md = md_dir / f'{clave}_2026_programa.md'
        frs = segmentar(md, pdf, clave)
        # cobertura: todas las palabras del cuerpo están en algún extracto
        body = md.read_text(encoding='utf-8').split('---', 2)[2]
        cuerpo = [b for b in bloques(body) if not re.match(r'^#{1,6}\s[^\n]*$', b)]
        n_cuerpo = sum(len(re.sub(r'[*_#]', ' ', b).split()) for b in cuerpo)
        n_frag = sum(f['palabras'] for f in frs)
        sin_pag = sum(1 for f in frs if not f['pagina'])
        med = sum(1 for f in frs if f['tipo'] == 'medida')
        largos = sorted((f['palabras'], f['id']) for f in frs)[-3:]
        print(f"{clave}: {len(frs)} extractos ({med} medidas), {n_frag}/{n_cuerpo} palabras, sin página: {sin_pag}, más largos: {largos}")
        todos += frs
    salida.write_text(json.dumps(todos, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    if sys.argv[1] == '--uno':
        main(RAIZ / 'markdown', RAIZ / 'descargas', pathlib.Path(sys.argv[3]), solo=sys.argv[2])
    else:
        main(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3]))

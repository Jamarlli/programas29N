"""Genera web/data.js a partir de los extractos, la taxonomía y la clasificación.

Uso: python -I pipeline/build_web.py <raiz_proyecto>

La clasificación se casa con los extractos por la huella de (partido, texto), no por id,
para que sobreviva a un nuevo troceado que desplace los ids.
"""
import json, re, sys, html, pathlib, hashlib, datetime

raiz = pathlib.Path(sys.argv[1])
data = raiz / 'data'

# El orden de este fichero es el de la web; los marcados como «base» salen por defecto.
PARTIDOS = json.loads((data / 'partidos.json').read_text(encoding='utf-8'))

# Circunscripciones por comunidad, con los nombres del BOE
TERRITORIOS = [
    ('Andalucía', ['Almería', 'Cádiz', 'Córdoba', 'Granada', 'Huelva', 'Jaén', 'Málaga', 'Sevilla']),
    ('Aragón', ['Huesca', 'Teruel', 'Zaragoza']),
    ('Asturias', ['Asturias']),
    ('Canarias', ['Las Palmas', 'Santa Cruz de Tenerife']),
    ('Cantabria', ['Cantabria']),
    ('Castilla-La Mancha', ['Albacete', 'Ciudad Real', 'Cuenca', 'Guadalajara', 'Toledo']),
    ('Castilla y León', ['Ávila', 'Burgos', 'León', 'Palencia', 'Salamanca', 'Segovia', 'Soria', 'Valladolid', 'Zamora']),
    ('Cataluña', ['Barcelona', 'Girona', 'Lleida', 'Tarragona']),
    ('Ceuta', ['Ceuta']),
    ('Comunitat Valenciana', ['Alicante', 'Castellón', 'Valencia']),
    ('Extremadura', ['Badajoz', 'Cáceres']),
    ('Galicia', ['A Coruña', 'Lugo', 'Ourense', 'Pontevedra']),
    ('Illes Balears', ['Illes Balears']),
    ('La Rioja', ['La Rioja']),
    ('Madrid', ['Madrid']),
    ('Melilla', ['Melilla']),
    ('Murcia', ['Murcia']),
    ('Navarra', ['Navarra']),
    ('País Vasco', ['Álava', 'Bizkaia', 'Gipuzkoa']),
]


def candidaturas(con_programa):
    """Candidaturas del BOE con el programa que usan, una fila por programa."""
    lista = json.loads((raiz / 'candidaturas' / 'candidaturas-29N.json').read_text(encoding='utf-8'))
    estado = json.loads((raiz / 'candidaturas' / 'programas-estado.json').read_text(encoding='utf-8'))
    provincias = {p for _, ps in TERRITORIOS for p in ps}
    out = []
    for c in lista:
        e = estado[c['sigla']]
        assert set(c['congreso']) | set(c['senado']) <= provincias, c['sigla']
        prog = e['prog'] if e['prog'] in con_programa else None
        est = e['estado'] if prog or e['estado'] != 'web' else 'pdf'  # programa aún sin incorporar
        out.append({'s': c['sigla'], 'n': e['nombre'], 'c': c['congreso'], 'se': c['senado'],
                    'prog': prog, 'e': 'web' if prog else est, 'nota': e['nota'], 'url': e['url']})
    # Las candidaturas que comparten programa (PSC con PSOE, listas al Senado con el programa de un socio…)
    # se funden en la del partido y suman sus circunscripciones.
    por_sigla = {c['s']: c for c in out}
    def clave_de(c):
        if c['s'] in USA_PROGRAMA_DE:
            return clave_de(por_sigla[USA_PROGRAMA_DE[c['s']]])
        return c['prog'] or ('SDP' if c['n'].startswith('Senado de Progreso') else c['s'])
    grupos = {}
    for c in out:
        grupos.setdefault(clave_de(c), []).append(c)
    fundidas = []
    for clave, l in grupos.items():
        rep = max(l, key=lambda c: (c['s'] not in USA_PROGRAMA_DE, len(set(c['c']) | set(c['se']))))
        rep = dict(rep, c=sorted({p for c in l for p in c['c']}), se=sorted({p for c in l for p in c['se']}))
        if clave == 'SDP':
            rep.update(s='SDP', n='Senado de Progreso')
        fundidas.append(rep)
    return fundidas


# Candidaturas sin programa propio que usan el de otra candidatura (por sigla del BOE)
USA_PROGRAMA_DE = {'C-DEM': 'COMUNS-FRONT AMPLI', 'PAZ,CASA Y TRABAJO': 'PODEMOS', 'EH BILDU-ERC': 'EH BILDU', 'ERC-EH BILDU': 'ERC'}


def front_matter(p):
    t = p.read_text(encoding='utf-8').split('---', 2)[1]
    return {m.group(1): m.group(2).strip().strip('"') for m in re.finditer(r'^(\w+):\s*(.*)$', t, re.M)}


def clave(partido, texto):  # misma huella que fusionar_clasif.py
    return hashlib.sha1((partido + '\x00' + re.sub(r'\s+', ' ', texto).strip()).encode('utf-8')).hexdigest()


def inline(s):
    s = re.sub(r'\*\* ([,.;:)])', r'**\1', s)  # «**negrita** ,» → «**negrita**,» (resto del conversor)
    s = re.sub(r' \*\*([,.;:])\*\*', r'\1', s)  # «gestión **.**» → «gestión.»
    s = re.sub(r' \*\*([,.;:]) ', r'\1 **', s)  # «asequible **, que…**» → «asequible, **que…**»
    s = re.sub(r'</?su[pb]>', '', s)
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = s.replace('**', '')
    s = re.sub(r'(?<![\w/])_(?!\s)(.+?)(?<!\s)_(?!\w)', r'<em>\1</em>', s)
    return s


def md_html(texto):
    """Markdown mínimo: párrafos, listas con un nivel de subpuntos, negrita y cursiva."""
    piezas = []  # ('p', [líneas]) | ('ul', [[texto, [subpuntos]]])
    for bloque in re.split(r'\n\s*\n', texto.strip()):
        for l in bloque.split('\n'):
            if not l.strip():
                continue
            m = re.match(r'^(\s*)[-*]\s+(.*)$', l)
            if m:
                if not piezas or piezas[-1][0] != 'ul':
                    piezas.append(('ul', [], 0))
                items = piezas[-1][1]
                # subpunto: sangrado, o lista que cuelga de un párrafo previo dentro del mismo bloque
                sangria = len(m.group(1))
                if not items:
                    piezas[-1] = ('ul', items, sangria)
                if sangria > piezas[-1][2] and items:
                    items[-1][1].append(m.group(2))
                else:
                    items.append([m.group(2), []])
            else:
                if piezas and piezas[-1][0] == 'p' and piezas[-1][2] is bloque:
                    piezas[-1][1].append(l.strip())
                else:
                    piezas.append(('p', [l.strip()], bloque))
        # un bloque nuevo cierra el párrafo en curso
        if piezas and piezas[-1][0] == 'p':
            piezas[-1] = ('p', piezas[-1][1], None)
    out = []
    for pz in piezas:
        if pz[0] == 'p':
            out.append('<p>' + '<br>'.join(inline(x) for x in pz[1]) + '</p>')
        else:
            li = []
            for t, subs in pz[1]:
                sub = ''.join(f'<li>{inline(x)}</li>' for x in subs)
                li.append(f'<li>{inline(t)}' + (f'<ul>{sub}</ul>' if sub else '') + '</li>')
            out.append('<ul>' + ''.join(li) + '</ul>')
    return ''.join(out)


def main():
    tax = json.loads((data / 'taxonomia.json').read_text(encoding='utf-8'))
    extractos = json.loads((data / 'extractos.json').read_text(encoding='utf-8'))

    clasif = {c['huella']: c for c in json.loads((data / 'clasificacion.json').read_text(encoding='utf-8'))}

    # marcas revisadas de los ejes, con cita literal
    marcas_h = []
    for mf in sorted((data / 'ejes').glob('marcas-*.json')):
        cf = mf.with_name(mf.name.replace('marcas', 'candidatos'))
        tx = {c['id']: (c['partido'], c['texto']) for p in json.loads(cf.read_text(encoding='utf-8')) for c in p['candidatos']}
        for m in json.loads(mf.read_text(encoding='utf-8')):
            marcas_h.append((m['eje'], clave(*tx[m['id']]), m['posicion'], m['cita']))
    ejes_revisados = {m[0] for m in marcas_h}

    subtemas = {s['id'] for b in tax['bloques'] for s in b['subtemas']}
    rutas, ruta_idx = [], {}
    salida, sin = [], []
    for f in extractos:
        r = ' › '.join(f['ruta'])
        if r not in ruta_idx:
            ruta_idx[r] = len(rutas)
            rutas.append(r)
        c = clasif.get(clave(f['partido'], f['texto']), {})
        s = c.get('subtema') if c.get('subtema') in subtemas else None
        if not s:
            sin.append(f['id'])
        salida.append({
            'i': f['id'], 'p': f['partido'], 'o': f['orden'], 'k': 'm' if f['tipo'] == 'medida' else 't',
            'n': f['numero'], 'r': ruta_idx[r], 'g': f['pagina'], 'w': f['palabras'],
            's': s, 'x': [x for x in c.get('otros', []) if x in subtemas and x != s],
            'h': c.get('titular', ''),
            'c': md_html(f['texto']),
        })

    # en los ejes revisados, las marcas revisadas sustituyen a las del primer clasificador
    por_huella = {clave(f['partido'], f['texto']): f['id'] for f in extractos}
    marcas = [[e, por_huella[h], pos, cita] for e, h, pos, cita in marcas_h if h in por_huella]
    for f in extractos:
        c = clasif.get(clave(f['partido'], f['texto']), {})
        for e in c.get('ejes', []):
            if e['eje'] not in ejes_revisados:
                marcas.append([e['eje'], f['id'], e['posicion'], ''])
    print(f'marcas de ejes: {len(marcas)} ({len(ejes_revisados)} ejes revisados con cita)')

    partidos = []
    con_extractos = {f['partido'] for f in extractos}
    for pt in PARTIDOS:
        md = raiz / 'markdown' / f"{pt['clave']}_2026_programa.md"
        if pt['id'] not in con_extractos or not md.exists():
            print(f"{pt['id']}: sin extractos todavía, no entra en la web")
            continue
        fm = front_matter(md)
        partidos.append({'id': pt['id'], 'corto': pt['corto'], 'nombre': fm['partido'], 'titulo': fm['titulo'],
                         'fuente': fm['fuente_pdf'], 'tipoFuente': fm['tipo_fuente'],
                         'paginas': int(fm['paginas_pdf']), 'descarga': fm['fecha_descarga'],
                         'color': pt['color'], 'base': pt['base']})
    ids = {p['id'] for p in partidos}
    salida = [x for x in salida if x['p'] in ids]
    marcas = [m for m in marcas if m[1].split('-')[0] in ids]

    out = {'generado': datetime.date.today().isoformat(), 'eleccion': 'Elecciones generales, 29 de noviembre de 2026',
           'partidos': partidos, 'candidaturas': candidaturas(ids),
           'territorios': [{'ccaa': c, 'provincias': ps} for c, ps in TERRITORIOS], 'bloques': tax['bloques'], 'ejes': tax['ejes'], 'marcas': marcas, 'rutas': rutas, 'extractos': salida}
    # mapa de circunscripciones para «Añadir partidos»; lo genera pipeline/mapa_ccaa.cjs
    mapa_f = data / 'mapa-ccaa.json'
    if mapa_f.exists():
        out['mapa'] = json.loads(mapa_f.read_text(encoding='utf-8'))
        assert {z['n'] for z in out['mapa']['zonas']} == {p for _, ps in TERRITORIOS for p in ps}, 'el mapa no casa con TERRITORIOS'
    web = raiz / 'web'
    web.mkdir(exist_ok=True)
    (web / 'data.js').write_text('window.PROGRAMAS=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n',
                                 encoding='utf-8')
    print(f'{len(salida)} extractos, {len(salida) - len(sin)} clasificados, sin clasificar: {len(sin)}')
    print(f'web/data.js: {(web / "data.js").stat().st_size // 1024} KB')


main()

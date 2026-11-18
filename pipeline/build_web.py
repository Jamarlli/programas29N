"""Genera web/data.js a partir de los extractos, la taxonomía y la clasificación.

Uso: python -I pipeline/build_web.py <raiz_proyecto>

La clasificación se casa con los extractos por la huella de (partido, texto), no por id,
para que sobreviva a un nuevo troceado que desplace los ids.
"""
import copy, json, re, sys, html, pathlib, hashlib, datetime, zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from i18n import AVISO_MD

# Los ZIP de «Programas»: los de Markdown (uno por idioma) van en la web; el de PDF pasa de los 25 MB que
# admite Cloudflare y se sube aparte a la release «programas» de GitHub:
#   gh release upload programas dist/programas-29n-pdf.zip --clobber -R Jamarlli/programas29N
ZIP_MD = 'descargas/programas-29n-markdown-{}.zip'
ZIP_PDF = 'https://github.com/Jamarlli/programas29N/releases/download/programas/programas-29n-pdf.zip'
SITIO = 'https://programas29n.jamarlli.workers.dev'

# Idiomas de la web. Cada programa está en su idioma original (campo «idioma» de partidos.json; si no lo tiene,
# castellano) y se traduce a los demás; catalán y valenciano cuentan como el mismo idioma. Las traducciones
# salen de pipeline/trad_fusionar.py (data/trad/<idioma>.json) y los textos de la interfaz, de data/i18n/<idioma>.json.
IDIOMAS = ['es', 'ca', 'va', 'gl', 'eu']
CODIGO = {'castellano': 'es', 'catalán': 'ca', 'valenciano': 'va', 'gallego': 'gl', 'euskera': 'eu'}
GRUPO = {'es': 'es', 'ca': 'ca', 'va': 'ca', 'gl': 'gl', 'eu': 'eu'}
BCP = {'es': 'es', 'ca': 'ca', 'va': 'ca-ES-valencia', 'gl': 'gl', 'eu': 'eu'}
OG = {'es': 'es_ES', 'ca': 'ca_ES', 'va': 'ca_ES', 'gl': 'gl_ES', 'eu': 'eu_ES'}
RUTA = {'es': '/', 'ca': '/ca/', 'va': '/va/', 'gl': '/gl/', 'eu': '/eu/'}
FECHA_ZIP = (2026, 11, 29, 0, 0, 0)


def escribe_zip(destino, ficheros):
    """ZIP con fechas fijas, para que no cambie si no cambia el contenido; devuelve su tamaño en MB."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for nombre, datos in ficheros:
            z.writestr(zipfile.ZipInfo(nombre, FECHA_ZIP), datos, zipfile.ZIP_DEFLATED)
    return round(destino.stat().st_size / 1e6, 1)


def fuentes_txt(raiz, pts):
    fuentes = ['Programas electorales de las elecciones generales del 29 de noviembre de 2026', SITIO, '']
    for pt in pts:
        fm = front_matter(raiz / 'markdown' / f"{pt['clave']}_2026_programa.md")
        fuentes.append(f"programa-29n-{pt['id']}: {fm['partido']} · {fm['titulo']}\n  {fm['fuente_pdf']} ({fm['tipo_fuente']}; descargado el {fm['fecha_descarga']})")
    return ('\n'.join(fuentes) + '\n').encode('utf-8')


def zip_pdf(raiz, pts):
    pdf = [(f"programa-29n-{pt['id']}.pdf", (raiz / pt['pdf']).read_bytes()) for pt in pts]
    return {'url': ZIP_PDF, 'mb': escribe_zip(raiz / 'dist' / 'programas-29n-pdf.zip', pdf + [('fuentes.txt', fuentes_txt(raiz, pts))])}


def md_traducido(raiz, pt, L, tr, extractos, aviso):
    """El programa entero en Markdown en el idioma L, montado con los extractos traducidos en su orden."""
    f_md = raiz / 'markdown' / f"{pt['clave']}_2026_programa.md"
    cab = f_md.read_text(encoding='utf-8').split('---', 2)[1].strip('\n')
    titulo = tr['titulos'].get(pt['id'], front_matter(f_md)['titulo'])
    cab += f'\nidioma: "{L}"\nidioma_original: "{CODIGO[pt["_idioma"]]}"\ntraduccion: "automática, revisada"'
    out = ['---', cab, '---', '', f'# {titulo}', '', f'> {aviso}', '']
    prev = []
    mapa = tr['rutas'].get(pt['id'], {})
    for e in extractos:
        r = e['ruta']
        for k, seg in enumerate(r):
            if k < len(prev) and prev[k] == seg and r[:k] == prev[:k]:
                continue
            out += ['#' * min(k + 2, 6) + ' ' + mapa.get(seg, seg), '']
        prev = r
        out += [tr['extractos'][e['id']]['t'], '']
    return '\n'.join(out).encode('utf-8')

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
        # programa publicado solo como página web: la web sirve el PDF que se generó a partir de ella,
        # para que las citas puedan enlazar a una página concreta
        copia = {}
        if pt.get('solo_web'):
            destino = raiz / 'web' / 'descargas' / f"programa-29n-{pt['id']}.pdf"
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes((raiz / pt['pdf']).read_bytes())
            copia = {'pdfCopia': f"descargas/{destino.name}"}
        partidos.append({'id': pt['id'], 'corto': pt['corto'], **({'sigla': pt['sigla']} if 'sigla' in pt else {}), 'nombre': fm['partido'], 'titulo': fm['titulo'],
                         'fuente': fm['fuente_pdf'], 'tipoFuente': fm['tipo_fuente'],
                         'paginas': int(fm['paginas_pdf']), 'descarga': fm['fecha_descarga'],
                         'color': pt['color'], 'base': pt['base'], 'idioma': CODIGO[pt.get('idioma', 'castellano')], **copia})
    ids = {p['id'] for p in partidos}
    descargas = {'pdf': zip_pdf(raiz, [pt for pt in PARTIDOS if pt['id'] in ids])}
    salida = [x for x in salida if x['p'] in ids]
    marcas = [m for m in marcas if m[1].split('-')[0] in ids]

    out = {'generado': datetime.date.today().isoformat(), 'eleccion': 'Elecciones generales, 29 de noviembre de 2026',
           'partidos': partidos, 'descargas': descargas, 'candidaturas': candidaturas(ids),
           'territorios': [{'ccaa': c, 'provincias': ps} for c, ps in TERRITORIOS], 'bloques': tax['bloques'], 'ejes': tax['ejes'], 'marcas': marcas, 'rutas': rutas, 'extractos': salida}
    # mapa de circunscripciones para «Añadir partidos»; lo genera pipeline/mapa_ccaa.cjs
    mapa_f = data / 'mapa-ccaa.json'
    if mapa_f.exists():
        out['mapa'] = json.loads(mapa_f.read_text(encoding='utf-8'))
        assert {z['n'] for z in out['mapa']['zonas']} == {p for _, ps in TERRITORIOS for p in ps}, 'el mapa no casa con TERRITORIOS'
    print(f'{len(salida)} extractos, {len(salida) - len(sin)} clasificados, sin clasificar: {len(sin)}')
    web = raiz / 'web'
    web.mkdir(exist_ok=True)
    versiones = {}
    for L in IDIOMAS:
        o = version(L, out, extractos, [pt for pt in PARTIDOS if pt['id'] in ids])
        if o is None:
            print(f'{L}: sin textos de la interfaz (data/i18n/{L}.json), no se publica')
            continue
        versiones[L] = o
    publicados = list(versiones)
    # el selector de idioma, el hreflang y el sitemap solo ofrecen los idiomas completos (todos los programas,
    # titulares y citas en ese idioma); los demás se generan igual, para verlos, pero sin enlazar ni indexar
    completos = [L for L, o in versiones.items() if o.pop('_completo')]
    print(f'idiomas completos: {", ".join(completos)}')
    for L, o in versiones.items():
        o['idiomas'] = completos
        nombre = 'data.js' if L == 'es' else f'data-{L}.js'
        (web / nombre).write_text('window.PROGRAMAS=' + json.dumps(o, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
        print(f'web/{nombre}: {(web / nombre).stat().st_size // 1024} KB')
    paginas_idioma(raiz, publicados, completos)


def version(L, out, extractos, pts):
    """La web en el idioma L: los textos de la interfaz, los temas y las preguntas traducidos, y los programas
    en ese idioma (su original si ya lo está; si no, su traducción, solo si está entera)."""
    i18n = {}
    if L != 'es':
        f = data / 'i18n' / f'{L}.json'
        if not f.exists():
            return None
        i18n = json.loads(f.read_text(encoding='utf-8'))
    f = data / 'trad' / f'{L}.json'
    tr = json.loads(f.read_text(encoding='utf-8')) if f.exists() else {'extractos': {}, 'rutas': {}, 'titulos': {}}
    te = tr['extractos']
    o = copy.deepcopy(out)
    o['idioma'] = L
    o['ui'] = i18n.get('ui', {})
    por_partido = {}
    for e in extractos:
        por_partido.setdefault(e['partido'], []).append(e)
    # un programa se muestra traducido solo si están traducidos todos sus extractos
    traducidos, pendientes = set(), []
    for p in o['partidos']:
        if GRUPO[p['idioma']] != GRUPO[L]:
            if all('t' in te.get(e['id'], {}) for e in por_partido[p['id']]) and p['id'] in tr['titulos']:
                traducidos.add(p['id'])
                p['traducido'] = True
                p['tituloOriginal'] = p['titulo']
                p['titulo'] = tr['titulos'][p['id']]
            else:
                pendientes.append(p['id'])
        if L != 'es':
            p['tipoFuente'] = i18n['fuentes'].get(p['id'], p['tipoFuente'])
    if L != 'es':
        for b in o['bloques']:
            b['nombre'] = i18n['temas'][b['id']]
            for s in b['subtemas']:
                s['nombre'] = i18n['temas'][s['id']]
        for e in o['ejes']:
            t = i18n['ejes'][e['id']]
            e['pregunta'] = t['pregunta']
            for pos in e['posiciones']:
                pos['nombre'] = t['posiciones'][pos['id']]
    sin_titular = 0
    rutas, idx = [], {}
    ruta_de = {e['id']: e['ruta'] for e in extractos}
    for x in o['extractos']:
        t = te.get(x['i'], {})
        if L != 'es':
            if 'h' in t:
                x['h'] = t['h']
            elif x['h']:
                sin_titular += 1
        r = ruta_de[x['i']]
        if x['p'] in traducidos:
            x['c'] = md_html(t['t'])
            x['t'] = 1
            mapa = tr['rutas'].get(x['p'], {})
            r = [mapa.get(seg, seg) for seg in r]
        r = ' › '.join(r)
        if r not in idx:
            idx[r] = len(rutas)
            rutas.append(r)
        x['r'] = idx[r]
    o['rutas'] = rutas
    sin_cita = 0
    for m in o['marcas']:
        pid = m[1].split('-')[0]
        if pid in traducidos and m[3]:
            c = te[m[1]].get('q', {}).get(m[3])
            if c:
                m[3] = c
            else:
                sin_cita += 1
    o['_completo'] = not (pendientes or sin_titular or sin_cita)
    if pendientes:
        print(f'  {L}: {len(pendientes)} programas aún sin traducir enteros, salen en su idioma original: {", ".join(pendientes)}')
    if sin_titular or sin_cita:
        print(f'  {L}: {sin_titular} titulares y {sin_cita} citas aún sin traducir')
    # el Markdown de todos los programas en este idioma
    aviso = o['ui'].get(AVISO_MD, AVISO_MD)
    md = []
    for pt in pts:
        f_md = raiz / 'markdown' / f"{pt['clave']}_2026_programa.md"
        if pt['id'] in traducidos:
            pt = dict(pt, _idioma=pt.get('idioma', 'castellano'))
            nombre_original = pt['_idioma']
            txt = aviso.replace('{x}', o['ui'].get(nombre_original, nombre_original)).replace('{u}', pt.get('fuente') or front_matter(f_md)['fuente_pdf'])
            md.append((f"programa-29n-{pt['id']}.md", md_traducido(raiz, pt, L, tr, por_partido[pt['id']], txt)))
            md.append((f"originales/programa-29n-{pt['id']}.md", f_md.read_bytes()))
        else:
            md.append((f"programa-29n-{pt['id']}.md", f_md.read_bytes()))
    url = ZIP_MD.format(L)
    o['descargas'] = dict(o['descargas'], md={'url': '/' + url, 'mb': escribe_zip(raiz / 'web' / url, md + [('fuentes.txt', fuentes_txt(raiz, pts))])})
    for p in o['partidos']:
        if 'pdfCopia' in p:
            p['pdfCopia'] = '/' + p['pdfCopia']
    return o


def paginas_idioma(raiz, idiomas, completos):
    """web/<idioma>/index.html a partir de web/index.html, y el sitemap. Los hreflang y el sitemap solo llevan
    los idiomas completos (si solo lo está el castellano, ninguno); las páginas de los demás llevan noindex."""
    web = raiz / 'web'
    base = (web / 'index.html').read_text(encoding='utf-8')
    alt = ''
    if len(completos) > 1:
        alt = ''.join(f'<link rel="alternate" hreflang="{BCP[L]}" href="{SITIO}{RUTA[L]}">\n' for L in completos)
        alt += f'<link rel="alternate" hreflang="x-default" href="{SITIO}/">\n'
    base, n = re.subn(r'(?:<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n)*(<link rel="icon")', lambda m: alt + m.group(1), base, count=1)
    assert n == 1
    (web / 'index.html').write_text(base, encoding='utf-8')
    for L in idiomas:
        if L == 'es':
            continue
        i18n = json.loads((data / 'i18n' / f'{L}.json').read_text(encoding='utf-8'))
        h = base.replace('<html lang="es">', f'<html lang="{BCP[L]}">')
        if L not in completos:
            h = h.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">')
        h = h.replace('<script src="data.js"></script>', f'<script src="data-{L}.js"></script>')
        h = re.sub(r'(href|src)="(?!https?:|#|/)([^"]+)"', r'\1="../\2"', h)
        h = h.replace(f'<link rel="canonical" href="{SITIO}/">', f'<link rel="canonical" href="{SITIO}/{L}/">')
        h = h.replace(f'<meta property="og:url" content="{SITIO}/">', f'<meta property="og:url" content="{SITIO}/{L}/">')
        h = h.replace('<meta property="og:locale" content="es_ES">', f'<meta property="og:locale" content="{OG[L]}">')
        for es, tr in sorted(i18n['html'].items(), key=lambda kv: -len(kv[0])):
            n = h.count(f'>{es}<') + h.count(f'"{es}"')
            assert n, (L, es)
            h = h.replace(f'>{es}<', f'>{tr}<').replace(f'"{es}"', f'"{tr}"')
        (web / L).mkdir(exist_ok=True)
        (web / L / 'index.html').write_text(h, encoding='utf-8')
    alt = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{BCP[L]}" href="{SITIO}{RUTA[L]}"/>' for L in completos) if len(completos) > 1 else ''
    urls = ''.join(f'\n  <url>\n    <loc>{SITIO}{RUTA[L]}</loc>\n    <lastmod>{datetime.date.today().isoformat()}</lastmod>{alt}\n  </url>' for L in (completos or ['es']))
    (web / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">{urls}\n</urlset>\n', encoding='utf-8')


sys.stdout.reconfigure(encoding='utf-8')
main()

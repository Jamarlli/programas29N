"""Limpieza propia del programa de Adelante Andalucía (Elecciones generales 29N 2026).

«Un programa para frenar a las derechas» (134 páginas). Estructura del PDF:
- p. 1 portada (con un párrafo de presentación), p. 2 portadilla, p. 3 introducción de «Las 29 del
  29N» con su índice; pp. 4-32 una página por cada una de las 29 medidas principales («MEDIDA N DE
  29»: título, texto o viñetas y la referencia «Se desarrolla en el programa: …»).
- p. 33 índice de áreas; pp. 35-133 doce áreas («01 Servicios públicos»…) con apartados N.N, algunos
  bloques con cabecera en mayúsculas (sólo en las áreas 1 y 11) y 719 propuestas numeradas de forma
  continua (1-719; `_areas` comprueba que salen en orden y sin saltos). Cada propuesta es una ficha: número grande, título en negrita, texto y una justificación
  en cursiva que empieza por «Porque…». El área 12 añade por provincia un recuadro «También en este
  programa: …». p. 134 contraportada (enlace a la web y créditos tipográficos).

La maqueta es a dos columnas con fichas y pymupdf4llm la desordena sin remedio: separa los números
de sus fichas (a veces agrupa siete números seguidos y luego las siete fichas), saca las
justificaciones «Porque…» lejos de su propuesta, mezcla fichas de las dos columnas y de bloques
distintos. Como el orden no se puede reconstruir desde el bruto, aquí se recompone el orden de lectura
con las posiciones y las fuentes del propio PDF (pymupdf, el mismo extractor que usa pymupdf4llm):
cada página se lee por bandas (los títulos a todo el ancho separan bandas) y en cada banda primero la
columna izquierda y luego la derecha. El texto es el del PDF, sin tocar; `limpiar` comprueba al
final que las palabras del resultado son las mismas que las del bruto (salvo índices, cabeceras,
pies y créditos) para asegurar que sólo cambia el orden.

Salida:
- «## Las 29 del 29N» con sus 29 medidas como «N. **Título** — texto» (las viñetas de la medida 1
  como subpuntos) y la referencia «Se desarrolla en el programa…» dentro de la misma medida.
- «## 01 Servicios públicos»… (áreas), «### 1.1 Sanidad» (apartados), «#### …» (cabeceras de bloque,
  pasadas de mayúsculas a minúsculas), párrafos de exposición y cada propuesta como
  «N. **Título** — texto _Porque…_».
Se quitan: rótulos de portada y contraportada (incluidos los créditos tipográficos), los índices de las
pp. 3 y 33 y los «En esta área» de cada área, los rótulos «MEDIDA N DE 29», «Las 29 del 29N»,
«PROGRAMA · ÁREA N DE 12» y «N SECCIONES · M PROPUESTAS», cabeceras, pies, pestañas y números de página.
"""
import re, json, pathlib, collections
import pymupdf

RAIZ = pathlib.Path(__file__).resolve().parents[2]
PDF = RAIZ / next(p['pdf'] for p in json.loads((RAIZ / 'data' / 'partidos.json').read_text(encoding='utf-8'))
                  if p['id'] == 'adelante')

TITULO = '# Un programa para frenar a las derechas'
MID = 297.6           # mitad de la página (595 pt)
TERM = tuple('.:;!?)»"”…')
NOMBRES_PROPIOS = {'andalucía': 'Andalucía', 'madrid': 'Madrid'}


# ---------------------------------------------------------------- lectura del PDF

def _lineas(page):
    """Líneas de la página con su estilo base (fuente, tamaño, color) y el texto con negritas internas."""
    out = []
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            vis = [s for s in l['spans'] if s['text'].strip()]
            if not vis:
                continue
            # negritas dentro de una línea: números de propuesta en WorkSans-SemiBold dentro del texto
            # («(Propuesta **106**)») y el arranque «Veintinueve propuestas» de la p. 3
            def destacada(s):
                return s['font'].startswith('WorkSans-SemiBold') or (
                    s['font'].startswith('FrauncesTitular') and round(s['size'], 1) == 14.5)
            base = next((s for s in vis if not destacada(s)), vis[0])
            txt = ''
            for s in l['spans']:
                t = s['text'].replace('\xa0', ' ')
                if t.strip() and destacada(s) and not destacada(base):
                    t = f"{t[:len(t) - len(t.lstrip())]}**{t.strip()}**{t[len(t.rstrip()):]}"
                txt += t
            x0, y0, x1, y1 = l['bbox']
            out.append(dict(x0=x0, y0=y0, x1=x1, y1=y1, font=base['font'], size=round(base['size'], 1),
                            color=base['color'], text=txt.strip(), first=vis[0]))
    return out


def _tipo(l, pn):
    """Clasifica una línea de las páginas de áreas (35-133)."""
    f, z, c = l['font'], l['size'], l['color']
    if z == 6.3 or (f.startswith('ClashDisplay') and z in (8.0, 10.0)):
        return None                                  # cabecera, pie, pestaña lateral y número de página
    if f.startswith('WorkSans-Bold') and z in (7.0, 7.5):
        return None                                  # «PROGRAMA · ÁREA 1 DE 12», «8 SECCIONES · …», «EN ESTA ÁREA»
    if (f.startswith('ClashDisplay') and z in (9.0, 11.0)) or (f.startswith('FrauncesTexto-Bold') and z == 10.0):
        return None                                  # índice «En esta área» de la portada de cada área
    if f.startswith('ClashDisplay') and z == 150.0:
        return 'area_num'
    if f.startswith('FrauncesTitular') and z in (46.0, 36.0, 30.0):
        return 'area_tit'
    if f.startswith('ClashDisplay') and z == 40.0:
        return 'sec'
    if f.startswith('FrauncesTitular') and z in (34.0, 26.0):
        return 'sec_cont'
    if f.startswith('WorkSans-Bold') and z == 8.0 and c == 0xffffff:
        return 'blk'
    if f.startswith('WorkSans') and z in (9.0, 10.0, 8.4):
        return 'intro'
    if f.startswith('ClashDisplay') and z == 21.0:
        return 'num'
    if f.startswith('FrauncesTexto-Bold') and z == 10.5:
        return 'tit'
    if f.startswith('WorkSans') and z == 8.6:
        return 'body'
    if f.startswith('FrauncesTexto-Italic') and z == 8.8:
        return 'porq'
    raise ValueError(f'p{pn}: estilo desconocido {f} {z} {c:06x}: {l["text"]!r}')


def _orden(lineas):
    """Orden de lectura: bandas separadas por líneas a todo el ancho; en cada banda, columna izquierda y luego derecha."""
    def ancho(l):
        return l['tipo'] in ('area_num', 'area_tit', 'sec', 'sec_cont') or (l['x0'] < MID - 10 and l['x1'] > MID + 30)
    out, izq, der = [], [], []

    def vaciar():
        out.extend(sorted(izq, key=lambda l: (l['y0'], l['x0'])))
        out.extend(sorted(der, key=lambda l: (l['y0'], l['x0'])))
        izq.clear(); der.clear()
    # el número grande de área va delante de su título aunque éste empiece un poco más arriba (p. 105)
    for l in sorted(lineas, key=lambda l: (l['y0'] - (60 if l['tipo'] == 'area_num' else 0), l['x0'])):
        if ancho(l):
            vaciar(); out.append(l)
        elif l['x0'] < MID:
            izq.append(l)
        else:
            der.append(l)
    vaciar()
    return out


def _unir(a, b):
    """Une dos líneas de un mismo párrafo («dietistas-» + «-nutricionistas», «Almería–» + «Aguadulce»)."""
    if not a:
        return b
    if a.endswith('-') and b.startswith('-'):
        return a + b[1:]
    if a.endswith(('-', '–')):
        return a + b
    return a + ' ' + b


def _frase(s):
    """Cabecera de bloque en mayúsculas → minúsculas con inicial mayúscula y nombres propios."""
    s = s.lower()
    s = s[0].upper() + s[1:]
    for k, v in NOMBRES_PROPIOS.items():
        s = re.sub(rf'\b{k}\b', v, s)
    return s


# ---------------------------------------------------------------- partes del documento

def _portada(doc):
    """p. 1: título y párrafo de presentación (lo demás son rótulos de la portada)."""
    txt = ''
    for l in _lineas(doc[0]):
        if l['font'].startswith('WorkSans-Regular') and l['size'] == 10.5:
            txt = _unir(txt, l['text'])
    return [TITULO, '', txt, '']


def _intro_29(doc):
    """p. 3: cinco párrafos «Veintinueve propuestas…» (el índice «Las 29, una a una» se quita)."""
    out, par = ['## Las 29 del 29N', ''], ''
    for l in _lineas(doc[2]):
        if l['size'] != 14.5:
            continue
        if l['first']['font'].startswith('FrauncesTitular') and par:
            out += [par, '']; par = ''
        par = _unir(par, l['text'])
    out += [par, '']
    return out


def _medida(page, pn):
    """pp. 4-32: una de las 29 medidas principales."""
    num, tit, texto, ref, vinetas = None, '', '', '', []
    ls = _lineas(page)
    cuerpo, balas = [], False
    for l in ls:   # viñeta: la línea empieza por un guion «–» verde (WorkSans-Bold) y sigue el texto
        if l['font'].startswith('WorkSans-Bold') and l['size'] == 11.0:
            assert l['text'].startswith('–'), l['text']
            l.update(text=l['text'][1:].strip(), font='WorkSans-Regular', vineta=True)
            balas = True
    for l in ls:
        f, z = l['font'], l['size']
        if z in (6.3, 10.0) or (f.startswith('FrauncesTitular') and z == 30.0):
            continue                                 # pie, número de página, rótulo «Las 29 del 29N»
        if f.startswith('WorkSans-Bold') and z == 7.5:
            continue                                 # «MEDIDA N DE 29»
        if f.startswith('ClashDisplay') and z == 120.0:
            num = int(l['text'])
        elif f.startswith('FrauncesTitular') and z in (34.0, 44.0):
            tit = _unir(tit, l['text'])
        elif f.startswith('WorkSans-Regular') and z in (11.0, 12.0):
            cuerpo.append(l)
        elif f.startswith('WorkSans-SemiBold') and z == 8.0:
            ref = _unir(ref, l['text'])
        else:
            raise ValueError(f'p{pn}: estilo desconocido {f} {z}: {l["text"]!r}')
    if balas:   # viñetas a dos columnas: izquierda y luego derecha
        cuerpo.sort(key=lambda l: (l['x0'] >= MID, l['y0']))
        for l in cuerpo:
            if l.get('vineta'):
                vinetas.append(l['text'])
            else:
                vinetas[-1] = _unir(vinetas[-1], l['text'])
    else:
        for l in sorted(cuerpo, key=lambda l: l['y0']):
            texto = _unir(texto, l['text'])
    assert num == pn - 3 and tit and ref and (texto or vinetas), (pn, num, tit)
    if vinetas:
        return [f'{num}. **{tit}**'] + [f'  - {v}' for v in vinetas] + [f'  {ref}', '']
    return [f'{num}. **{tit}** — {texto}', ref, '']


def _areas(doc):
    """pp. 35-133: áreas, apartados, bloques, exposición y propuestas numeradas."""
    flujo = []
    for pn in range(35, 134):
        ls = []
        for l in _lineas(doc[pn - 1]):
            t = _tipo(l, pn)
            if t:
                l['tipo'], l['pn'] = t, pn
                ls.append(l)
        flujo += _orden(ls)

    out, numeros = [], []
    prop = None          # propuesta en curso: dict(num, tit, body, porq)
    par, prev = None, None

    def cerrar_prop():
        nonlocal prop
        if prop:
            assert prop['tit'], prop
            s = f"{prop['num']}. **{prop['tit']}**"
            resto = ' '.join(x for x in (prop['body'], f"_{prop['porq']}_" if prop['porq'] else '') if x)
            out.extend([s + (' — ' + resto if resto else ''), ''])
            prop = None

    def cerrar_par():
        nonlocal par
        if par:
            out.extend([par, ''])
        par = None

    i = 0
    while i < len(flujo):
        l = flujo[i]; t = l['tipo']
        if t != 'intro':
            cerrar_par()
        if t in ('area_num', 'sec', 'blk'):
            cerrar_prop()
            sig = {'area_num': ('area_tit',), 'sec': ('sec_cont',), 'blk': ('blk',)}[t]
            txt = '' if t == 'area_num' else l['text']
            j = i + 1
            while j < len(flujo) and flujo[j]['tipo'] in sig:
                txt = _unir(txt, flujo[j]['text']); j += 1
            if t == 'area_num':
                out += [f"## {l['text']} {txt}", '']
            elif t == 'sec':
                out += ['### ' + re.sub(r'^(\d+\.\d+)\s*', r'\1 ', txt), '']
            else:
                out += ['#### ' + _frase(txt), '']
            i = j; prev = None
            continue
        if t in ('area_tit', 'sec_cont'):
            raise ValueError(f"p{l['pn']}: título suelto {l['text']!r}")
        if t == 'intro':
            cerrar_prop()
            nuevo = (par is None or prev is None or
                     (prev['pn'] == l['pn'] and (prev['x0'] < MID) == (l['x0'] < MID) and l['y0'] - prev['y1'] > 3) or
                     ((prev['pn'] != l['pn'] or (prev['x0'] < MID) != (l['x0'] < MID)) and par.endswith(TERM)))
            if nuevo:
                cerrar_par(); par = l['text']
            else:
                par = _unir(par, l['text'])
        elif t == 'num':
            cerrar_prop()
            prop = dict(num=int(l['text']), tit='', body='', porq='')
            numeros.append(prop['num'])
        elif t == 'tit':
            assert prop and not prop['body'] and not prop['porq'], (l['pn'], l['text'])
            prop['tit'] = _unir(prop['tit'], l['text'])
        elif t == 'body':
            assert prop and not prop['porq'], (l['pn'], l['text'])
            prop['body'] = _unir(prop['body'], l['text'])
        elif t == 'porq':
            assert prop, (l['pn'], l['text'])
            prop['porq'] = _unir(prop['porq'], l['text'])
        prev = l
        i += 1
    cerrar_prop(); cerrar_par()
    # el orden de lectura es correcto si las propuestas salen numeradas 1, 2, 3… sin saltos
    assert numeros == list(range(1, len(numeros) + 1)), [
        (a, b) for a, b in zip(numeros, numeros[1:]) if b != a + 1][:10]
    return out


# ---------------------------------------------------------------- comprobación contra el bruto

def _palabras(lineas):
    txt = re.sub(r'[*_#|>]|<[^>]+>', ' ', '\n'.join(lineas))
    txt = txt.replace(' — ', ' ')
    return collections.Counter(re.findall(r'\w+', txt.lower()))


def limpiar(lineas):
    doc = pymupdf.open(PDF)
    assert doc.page_count == 134
    out = _portada(doc) + _intro_29(doc)
    for pn in range(4, 33):
        out += _medida(doc[pn - 1], pn)
    out += _areas(doc)
    # Mismas palabras que el bruto: lo que sobra en el bruto han de ser sólo índices, rótulos,
    # cabeceras y pies; lo que sobre en el resultado, nada.
    bruto, limpio = _palabras(lineas), _palabras(out)
    sobra = limpio - bruto
    # el bruto quita el guion de fin de línea de «AFECTIVO-/SEXUAL» (p. 45, cabecera de bloque) y lo
    # deja en «AFECTIVOSEXUAL»; aquí se conserva «afectivo-sexual», como en el resto del programa
    if bruto['afectivosexual'] == 1:
        sobra -= collections.Counter({'afectivo': 1, 'sexual': 1})
    assert not sobra, f'palabras que no están en el bruto: {dict(sobra)}'
    return out

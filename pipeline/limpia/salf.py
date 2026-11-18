"""Limpieza propia del «Contrato electoral» de Se Acabó La Fiesta (SALF), 29N 2026.

El PDF es una maqueta de fichas: cada capítulo (I-X) abre con un lema y tres cifras destacadas,
y cada medida es una ficha con número, título en negrita, texto, nota de coste y, en la columna
derecha, una cifra con su pie. pymupdf4llm separa los números de su ficha (a veces los agrupa:
«5», «6», «7» y luego las tres fichas) y saca las cifras de la columna derecha después del texto.

Aquí se recompone cada ficha como:
    N. **Título.** Texto. _Coste…_
      - **cifra** pie de la cifra
Las páginas 2-3 (organigramas del Gobierno) se recomponen a mano a partir del PDF, porque la
conversión mezcla las dos columnas de los organigramas.
"""
import re

ROMANOS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
CAPS = ['VIVIENDA', 'SEGURIDAD', 'IMPUESTOS', 'INMIGRACIÓN', 'PENSIONES', 'SANIDAD',
        'CORRUPCIÓN', 'EMPLEO', 'EDUCACIÓN', 'GEOPOLÍTICA']
NOMBRES = ['Vivienda', 'Seguridad', 'Impuestos', 'Inmigración', 'Pensiones', 'Sanidad',
           'Corrupción', 'Empleo', 'Educación', 'Geopolítica']

# Páginas 2-4: el Gobierno y los 10 compromisos.
# Organigramas (pp. 2-3): la conversión mezcla las dos columnas; se recomponen en el orden del PDF.
GOBIERNO_HOY = [
    'Economía, Comercio y Empresa (VP 1.ª)', 'Trabajo y Economía Social (VP 2.ª)',
    'Transición Ecológica y Reto Demográfico (VP 3.ª)',
    'Asuntos Exteriores, UE y Cooperación', 'Presidencia, Justicia y Relaciones con las Cortes',
    'Defensa', 'Hacienda', 'Interior', 'Transportes y Movilidad Sostenible',
    'Educación, FP y Deportes', 'Trabajo y Economía Social', 'Industria y Turismo',
    'Agricultura, Pesca y Alimentación', 'Política Territorial y Memoria Democrática',
    'Transición Ecológica y Reto Demográfico', 'Vivienda y Agenda Urbana', 'Cultura',
    'Economía, Comercio y Empresa', 'Sanidad', 'Derechos Sociales, Consumo y Agenda 2030',
    'Ciencia, Innovación y Universidades', 'Igualdad', 'Transformación Digital y Función Pública',
    'Juventud e Infancia', 'Inclusión, Seguridad Social y Migraciones',
]
CIFRAS_HOY = [('22', 'ministerios'), ('3', 'vicepresidencias'), ('35', 'secretarías de Estado'),
              ('128', 'direcciones generales'), ('823', 'altos cargos (+22,7 % desde 2017)'),
              ('1.255', 'puestos de confianza: 71,2 M€ al año'), ('452', 'entes del sector público estatal')]
GOBIERNO_SALF = [
    ('Vicepresidencia económica: Hacienda, Economía y Empleo', None),
    ('Presidencia y Administraciones Públicas',
     'Absorbe: Relaciones con las Cortes, Política Territorial, Función Pública y Transformación Digital'),
    ('Hacienda, Economía y Empleo', 'Absorbe: Hacienda; Economía, Comercio y Empresa; Trabajo'),
    ('Interior y Justicia', 'Absorbe: Interior, Justicia y Migraciones'),
    ('Defensa', 'Absorbe: Fuerzas Armadas e industria de defensa'),
    ('Asuntos Exteriores', 'Absorbe: Exteriores, UE y cooperación condicionada'),
    ('Sanidad y Seguridad Social', 'Absorbe: Sanidad; Seguridad Social; Derechos Sociales y Consumo'),
    ('Educación, Ciencia y Cultura', 'Absorbe: Educación y FP; Universidades y Ciencia; Cultura y Deportes; Juventud'),
    ('Infraestructuras, Energía e Industria', 'Absorbe: Transportes; Energía y Medio Ambiente; Industria y Turismo'),
    ('Vivienda', 'Absorbe: Suelo, licencias, Sareb y vivienda en propiedad'),
    ('Agricultura, Pesca y Alimentación', 'Absorbe: Campo, mar y mundo rural'),
]
CIFRAS_SALF = [('22 → 10', 'ministerios'), ('3 → 1', 'vicepresidencias'), ('35 → 15', 'secretarías de Estado'),
               ('128 → 70', 'direcciones generales'), ('823 → 450', 'altos cargos'), ('1.255 → 400', 'asesores'),
               ('452 → 300', 'entes estatales')]


def tabla_cifras(cifras):
    out = [f'| {a} | {b} |' for a, b in cifras]
    out.insert(1, '|---|---|')  # la primera cifra hace de cabecera, como en la conversión
    return out


def portada_y_gobierno(lines):
    """Páginas 1-4: portada, organigramas y los 10 compromisos con la cláusula de penalización."""
    def linea(pref):
        return next(l for l in lines if l.startswith(pref))
    out = ['# Contrato electoral', '']
    out += ['## El Gobierno', '', '### Así está el Gobierno hoy', '',
            '**22** ministerios', '', '**3** vicepresidencias', '',
            linea('823 altos cargos y 1.255 asesores.'), '',
            '| Presidente del Gobierno |', '|---|']
    out += [f'| {m} |' for m in GOBIERNO_HOY]
    out += [''] + tabla_cifras(CIFRAS_HOY) + ['']
    out += ['### Así estará con SALF', '',
            '**22 → 10** ministerios', '', '**3 → 1** vicepresidencia', '',
            linea('La mitad de los altos cargos y 400 asesores.'), '']
    for nombre, absorbe in GOBIERNO_SALF:
        out += [f'- {nombre}' + (f' — {absorbe}' if absorbe else ''), '']
    out += [''] + tabla_cifras(CIFRAS_SALF) + ['']
    out += ['**Ahorro directo mínimo de 300 millones de euros.**', '',
            '> ' + linea('**«Nuestro Gobierno cabe en una mesa.»**'), '']
    # 10 compromisos: tabla de propuestas → un punto por fila
    out += ['## 10 compromisos', '']
    for l in lines:
        m = re.match(r'^\|(\d+)\|\*\*(.+?)\*\*\|(.+)\|$', l)
        if m:
            texto = re.sub(r'\s*<br>\s*', ' ', m.group(3)).strip()
            out += [f'{m.group(1)}. **{m.group(2).capitalize()}** — {texto}', '']
    out += ['', '### Cláusula de penalización', '',
            '> ' + linea('**«El castigo por incumplimiento'), '',
            linea('Desde el 1.º día, el 100 %'), '']
    return out


# Reparaciones de líneas que la conversión rompió (columnas mezcladas, número de ficha pegado
# al título, flechas «antes → después» perdidas). Línea exacta → líneas que la sustituyen.
REPL = {
    # flechas «antes → después» de las cifras (en el PDF son un dibujo)
    '###### **105 1**': ['###### **105 → 1**'],
    '**10 % 100 %**': ['**10 % → 100 %**'],
    '###### **206 € 0 €**': ['###### **206 € → 0 €**'],
    '###### **21 % 4 %**': ['###### **21 % → 4 %**'],
    '###### **29 100**': ['###### **29 → 100**'],
    '**2.900 332 M€**': ['**2.900 → 332 M€**'],
    # Empleo 6: la conversión invierte «1 → −2»
    '**−2**': [],
    # Sanidad 7 y 8: texto y pie de la cifra mezclados
    'Tarjeta para españoles y residentes legales con cotización sin facturar a quien o cobertura. Urgencias para todos, siempre. Facturación debe pagar real a los países y aseguradoras de terceros.': [
        'Tarjeta para españoles y residentes legales con cotización o cobertura. Urgencias para todos, siempre. Facturación real a los países y aseguradoras de terceros.',
        'sin facturar a quien debe pagar'],
    '> **Medicamentos: precios netos públicos y 0 € copago cero para quien no puede.** de copago para quien Subasta nacional de genéricos y biosimilares. Copago cero no puede para pensiones mínimas y enfermos crónicos.': [
        '###### **Medicamentos: precios netos públicos y copago cero para quien no puede.**',
        'Subasta nacional de genéricos y biosimilares. Copago cero para pensiones mínimas y enfermos crónicos.',
        '###### **0 €**', 'de copago para quien no puede'],
    # Educación 5: la cifra «12,8 → 9 %» se coló en el título
    '###### **FP desde los 15 y un tutor para cada 12,8 alumno en riesgo. 9 %**': [
        '###### **FP desde los 15 y un tutor para cada alumno en riesgo.**', '###### **12,8 → 9 %**'],
    # Geopolítica 5 y 7: número de ficha pegado al título
    '###### **Ceuta y Melilla, plaza franca: 0 % de IRPF, 5 0 % de Sociedades y 0 % de cotizaciones. Para siempre.**': [
        '**5**', '###### **Ceuta y Melilla, plaza franca: 0 % de IRPF, 0 % de Sociedades y 0 % de cotizaciones. Para siempre.**'],
    '###### **7 Escudo del Estrecho y del Atlántico: 5.000 militares más en Ceuta y Melilla; antiaérea y antidrón en cada isla.**': [
        '**7**', '###### **Escudo del Estrecho y del Atlántico: 5.000 militares más en Ceuta y Melilla; antiaérea y antidrón en cada isla.**'],
    # cifras que la conversión perdió (están en la capa de texto del PDF)
    'indultos por corrupción': ['**0**', 'indultos por corrupción'],
    'operaciones de espionaje extranjero detectadas en 2025': ['**108**', 'operaciones de espionaje extranjero detectadas en 2025'],
}

# Bloques desordenados: (líneas que se mueven, prefijo de la línea tras la que van).
MOVER = [
    # Geopolítica 4: la cifra de la ficha sale después de la ficha 5
    (['###### **22.757M€**', 'de comercio bilateral: a Rabat le cuesta más que a nosotros'],
     'Bloqueo comercial total a todo puerto marroquí'),
]


def norm_linea(l):
    l = l.strip()
    l = re.sub(r'(\w) ‐ (\w)', r'\1\2', l)  # palabra partida al final de línea («ínte ‐ gro»)
    l = l.replace(' ‐ ', '')
    return l


def es_num(l):
    m = re.match(r'^(?:#+\s*)?(?:\*\*)?(\d{1,2})(?:\*\*)?$', l)
    return int(m.group(1)) if m else None


def bold_h(l):
    """Texto de una línea «###### **X**» o «**X**»."""
    m = re.match(r'^(?:#+\s*)?\*\*(.+?)\*\*$', l)
    return m.group(1).strip() if m else None


def clasificar(l):
    if not l:
        return None
    if re.match(r'^\*\*S A L F', l) or re.match(r'^\*\*C O M P R O M I S O', l) or l == '€':
        return ('drop', l)
    if l.startswith('EN SALF SOMOS'):
        return ('para', f'**{l}**')
    if l.startswith('**Modelo de macrocárcel SALF.**'):
        return ('para', l)
    if re.match(r'^\*\*«.*»\*\*$', l):
        return ('quote', l)
    n = es_num(l)
    if n is not None:
        return ('num', n)
    t = bold_h(l)
    if t is not None:
        if t.endswith('.') and len(t) > 8:
            return ('title', t)
        return ('sval', t)
    m = re.match(r'^\*\*(.+?\.)\*\*\s+(.+)$', l)  # «**MIR docente.** Dos años…»
    if m:
        return ('titlebody', (m.group(1), m.group(2)))
    if l.startswith('_') and l.endswith('_'):
        return ('cost', l)
    if l.endswith(('.', '_')):
        return ('body', l)
    return ('scap', l)


def capitulo(idx, lines):
    """lines: líneas del capítulo sin la cabecera «### NOMBRE»."""
    lines = [l for l in lines if l]
    out = [f'## {ROMANOS[idx]}. {NOMBRES[idx]}', '', lines[0], '']  # lema
    toks = [t for t in (clasificar(l) for l in lines[1:]) if t]
    # cifras de cabecera: hasta el primer número o título
    i = 0
    vals, capts = [], []
    while i < len(toks) and toks[i][0] != 'title' and toks[i] != ('num', 1):
        k, v = toks[i]
        if k in ('sval', 'num'):
            vals.append(str(v))
        elif k == 'scap':
            capts.append(v)
        i += 1
    out += cabecera(idx, vals, capts)
    toks = toks[i:]

    medidas = []      # dicts: n, title, body[], cost[], stats[]
    grupo = []        # medidas del último grupo de números
    cola = []         # números pendientes de asignar
    pend_val = []     # cifras a la espera de su pie
    pend_dest = None  # medida a la que va la cifra pendiente
    cierre = []
    previo_num = False

    def nueva(n, title):
        m = {'n': n, 'title': title, 'body': [], 'cost': [], 'stats': [], 'auto': False}
        medidas.append(m)
        grupo.append(m)
        return m

    def destino_stat():
        for m in grupo:
            if not m['stats'] and not m.get('reserva'):
                return m
        return medidas[-1]

    for k, v in toks:
        if k == 'num':
            ult = medidas[-1]['n'] if medidas else 0
            if medidas and medidas[-1]['auto'] and v == ult and not cola:
                medidas[-1]['auto'] = False   # número de una ficha cuyo título salió antes
                continue
            esperado = (cola[-1] if cola else ult) + 1
            if v == esperado:
                if not previo_num:
                    grupo.clear()
                cola.append(v)
                previo_num = True
                continue
            k, v = 'sval', str(v)
        previo_num = False
        if k == 'title' or k == 'titlebody':
            title, body = (v, None) if k == 'title' else v
            if cola:
                m = nueva(cola.pop(0), title)
            else:
                m = nueva((medidas[-1]['n'] if medidas else 0) + 1, title)
                m['auto'] = True
            if body:
                m['body'].append(body)
        elif k == 'body':
            dest = next((m for m in grupo if not m['body']), medidas[-1])
            dest['body'].append(v)
        elif k == 'cost':
            dest = [m for m in grupo if m['body']][-1] if any(m['body'] for m in grupo) else medidas[-1]
            dest['cost'].append(v)
        elif k == 'sval':
            if not pend_val:
                pend_dest = destino_stat()
                pend_dest['reserva'] = True
            pend_val.append(v)
        elif k == 'scap':
            if pend_val:
                pend_dest['stats'].append(('**' + ' → '.join(pend_val) + '**', v))
                pend_dest['reserva'] = False
                pend_val = []
            else:
                destino_stat()['stats'].append((None, v))
        elif k == 'quote':
            cierre.append('> ' + v)
        elif k == 'para':
            medidas[-1].setdefault('despues', []).append(v)
    assert not pend_val, (NOMBRES[idx], pend_val)

    for m in medidas:
        txt = f"{m['n']}. **{m['title']}**"
        if m['body']:
            txt += ' ' + ' '.join(m['body'])
        if m['cost']:
            txt += ' ' + ' '.join(m['cost'])
        out.append(txt)
        for val, cap in m['stats']:
            out.append(f'  - {val} {cap}' if val else f'  - {cap}')
        out.append('')
        for p in m.get('despues', []):
            out += [p, '']
    out += cierre + ['']
    return out


# Cifras de cabecera: la conversión agrupa primero las cifras y luego los pies, a veces en otro
# orden. Para cada capítulo: lista de (índices de cifras, índice del pie), en el orden del PDF.
CABECERA = {
    0: [((0,), 0), ((1,), 1), ((2, 3), 2)],             # 12 meses → 12 semanas
    2: [((0,), 0), ((1,), 2), ((2,), 1)],
    4: [((0,), 0), ((1,), 1), ((2, 3), 2)],             # 13 % → 17 %
    8: [((0,), 1), ((1,), 2), ((2,), 0)],
    9: [((0,), 2), ((1,), 1), ((2,), 0)],
}


def cabecera(idx, vals, capts):
    plan = CABECERA.get(idx, [((j,), j) for j in range(len(vals))])
    usados_v = sorted(j for js, _ in plan for j in js)
    assert usados_v == list(range(len(vals))) and len(plan) == len(capts), (idx, vals, capts)
    out = []
    for js, c in plan:
        out += ['**' + ' → '.join(vals[j] for j in js) + '** ' + capts[c], '']
    return out


def como_se_paga(lines):
    out = ['### Cómo se paga', '']
    for l in lines:
        if not l:
            continue
        if l.startswith('|'):
            out.append(re.sub(r'\*\*<br>\*\*|<br>', ' ', l))
        else:
            if out[-1].startswith('|'):
                out.append('')
            out += [l, '']
    return out


def limpiar(lineas):
    lines = [norm_linea(l) for l in lineas]
    # reparaciones
    res = []
    for l in lines:
        res.extend(REPL[l] if l in REPL else [l])
    lines = res
    for mover, tras in MOVER:
        for l in mover:
            lines.remove(l)
        j = next(i for i, l in enumerate(lines) if l.startswith(tras))
        lines[j + 1:j + 1] = mover
    # Empleo 6: «**1**» + «normas» van detrás del «1 →» que falta: se rehace como «1 → −2»
    i = lines.index('**1**', lines.index('###### **Protección al trabajador sin encarecer su contratación.**'))
    lines[i] = '**1 → −2**'

    ini = [i for i, l in enumerate(lines) if l in [f'### {c}' for c in CAPS]]
    out = portada_y_gobierno(lines[:ini[0]])
    for n, a in enumerate(ini):
        b = ini[n + 1] if n + 1 < len(ini) else len(lines)
        trozo = lines[a + 1:b]
        if n == 2:  # Impuestos: «Cómo se paga» al final
            c = trozo.index('##### Cómo se paga')
            out += capitulo(n, trozo[:c]) + como_se_paga(trozo[c + 1:])
        elif n == 9:  # Geopolítica: contraportada al final
            c = next(j for j, l in enumerate(trozo) if l.startswith('**SALF S E A C A B'))
            out += capitulo(n, trozo[:c])
        else:
            out += capitulo(n, trozo)
    return out

"""Limpieza propia del programa de Comuns-Front Ampli (Eleccions generals 29N 2026, en catalán).

Estructura del PDF (135 págs.): portada «Un programa com una casa» (pág. 1), índice general
(pág. 2) y seis capítulos («Habitatge», «El cost de la vida i una economia justa», «Transició
Ecosocial», «Drets», «Igualtat», «Plurinacionalitat i democràcia»). Cada capítulo abre con una
página de índice propio (una tabla en la conversión; dos en el último capítulo) y sigue con
apartados en 16 pt y subapartados en 13 pt. Las medidas son viñetas «•» y algunas tienen
subviñetas «›». Contraportada con el lema repetido (pág. 135).

La conversión ya pone los apartados como «##» y los subapartados como «###»: se bajan un nivel
(capítulo «##», apartado «###», subapartado «####»). Lo que hay que arreglar:
- índices de cada capítulo (tablas) y títulos de capítulo repetidos encima de ellos;
- la cabecera de página con el nombre del capítulo, que a veces sale como «## <mark>…</mark>»
  en medio del texto (incluso partiendo un párrafo);
- cuatro subapartados de 13 pt que la conversión deja como párrafo en negrita, y un apartado y
  su subapartado (mismo texto) fundidos en un solo título (pág. 109);
- «Propostes:» (texto normal) tomado por título (pág. 56);
- continuaciones de viñeta partidas por el salto de página (págs. 46, 61-62, 78);
- una negrita rota («obligator**i») (pág. 6);
- párrafos de exposición presentados como viñeta (págs. 59, 65, 125) y compromisos concretos
  escritos como párrafo sin viñeta (págs. 42, 112, 115, 117, 122, 132-134).
Los textos repetidos (párrafos o viñetas duplicados) están así en el PDF y se conservan.
"""
import re

TITULO = '# Un programa com una casa'

CAPITULOS = ('Habitatge', 'El cost de la vida i una economia justa', 'Transició Ecosocial', 'Drets', 'Igualtat',
             'Plurinacionalitat i democràcia')

# subapartados (13 pt) que la conversión deja como párrafo en negrita
SUBAPARTADOS = (
    'Defensa del treball autònom, el petit comerç i les Pime.',
    'Ningú no ha de cuidar sol.',
    'Reformar els requisits legals per facilitar l’impuls de la Iniciativa Legislativa Popular',
    'Ampliar el dret de vot a totes les persones majors de 16 anys',
)

# viñetas del PDF que son exposición: pasan a párrafo (y sus subviñetas, si las hay, a medidas)
EXPOSICION = (
    'Per assolir una societat més justa, ètica i compromesa amb la vida',  # pág. 59
    'La pesca artesana ha perdut prop de la meitat de la flota',  # pág. 65
    'Proposem impulsar:',  # pág. 125
)

# párrafos sin viñeta que son compromisos concretos: pasan a medida «- »
MEDIDAS = (
    'Dotarem de recursos els programes d’adaptació i mitigació',  # pág. 42
    'Desenvoluparem uns pressupostos de carboni',  # pág. 42
    'Per donar un impuls a l’autogovern, de forma unitària, els Comuns proposarem',  # pág. 112
    'Elaborar una nova llei de referèndums',  # pág. 115
    'Un cop aprovada la nova llei, utilitzar els mecanismes de democràcia directa',  # pág. 115
    'Augment de la inversió pública en Justícia',  # pág. 117
    'Complirem amb el compromís de destinar el 0,7%',  # pág. 122
    'Impulsarem una reforma de la legislació bàsica de règim local',  # pág. 132
    'Volem reforçar l’autonomia política i de gestió dels governs locals',  # pág. 132
    'També proposem flexibilitzar les limitacions a la contractació de personal',  # pág. 132
    'Entenem que l’organització supralocal bàsica de Catalunya ha de ser la vegueria',  # pág. 134
    'En aquest sentit, proposem modificar via llei orgànica les delimitacions provincials',  # pág. 134
)


def sin_marcas(s):
    return re.sub(r'\s+', ' ', re.sub(r'^#+\s*', '', s).replace('**', '')).strip()


def siguiente(lineas, i):
    j = i + 1
    while j < len(lineas) and not lineas[j].strip():
        j += 1
    return j


def anterior(lineas, i):
    j = i - 1
    while j >= 0 and not lineas[j].strip():
        j -= 1
    return j


def buscar(lineas, pred, desc):
    hits = [i for i, l in enumerate(lineas) if pred(l)]
    assert len(hits) == 1, (desc, len(hits))
    return hits[0]


def limpiar(lineas):
    # 1) portada, índice general, índices de capítulo (tablas) con el título repetido encima,
    #    cabeceras de página «## <mark>…</mark>» y contraportada
    tablas = sum(1 for k, l in enumerate(lineas) if l.startswith('|') and not lineas[k - 1].startswith('|'))
    assert tablas == 7, tablas
    out = []
    for i, l in enumerate(lineas):
        s = l.strip()
        if l.startswith('|'):
            continue
        if s.startswith('## ') and sin_marcas(s) in CAPITULOS:  # cabecera de página (generic_pre quita <mark>)
            continue
        if s.startswith('# '):
            t = sin_marcas(s)
            if t == 'Índex' or t.startswith('02 Habitatge'):
                continue
            j = siguiente(lineas, i)
            if j < len(lineas) and lineas[j].startswith('|'):  # título encima de un índice de capítulo
                continue
        if s.startswith('**') and 'UN PROGRAMA COM UNA CASA' in s:  # portada y contraportada
            continue
        out.append(l)

    # 2) niveles: capítulo «##», apartado «###», subapartado «####»
    for i, l in enumerate(out):
        s = l.strip()
        if s.startswith('#'):
            m = re.match(r'^(#+)\s', s)
            n = len(m.group(1))
            t = sin_marcas(s)
            if t == 'Propostes:':  # texto normal tomado por título (pág. 56)
                out[i] = t
                continue
            assert n <= 3, s
            out[i] = '#' * (n + 1) + ' ' + t
        elif s.startswith('**') and s.endswith('**') and s[2:].startswith(SUBAPARTADOS):
            out[i] = '#### ' + sin_marcas(s)
    assert sum(1 for l in out if l.startswith('#### ') and sin_marcas(l).startswith(SUBAPARTADOS)) == 4

    # apartado (16 pt) y subapartado (13 pt) con el mismo texto, fundidos en un título (pág. 109)
    t = 'Un nou catalanisme popular per un projecte plurinacional'
    i = buscar(out, lambda l: l == f'### {t} {t}.', 'catalanisme')
    out[i:i + 1] = [f'### {t}', '', f'#### {t}.']

    # 3) subviñetas «›» -> subpuntos
    out = [re.sub(r'^\s+- › ', '  - ', l) for l in out]

    # 4) continuaciones de viñeta partidas por el salto de página
    #    «… tindrà un consell» + «- assessor científic.» (pág. 46)
    i = buscar(out, lambda l: l.strip() == '- assessor científic.', 'assessor')
    k = anterior(out, i)
    assert out[k].rstrip().endswith('i tindrà un consell'), out[k][-40:]
    out[k] = out[k].rstrip() + ' assessor científic.'
    del out[k + 1:i + 1]
    #    párrafo sangrado que sigue la viñeta «Establir costos oficials de referència…» (págs. 61-62)
    i = buscar(out, lambda l: l.startswith('Aquests valors de referència no han de substituir'), 'valors')
    k = anterior(out, i)
    assert out[k].startswith('- Establir costos oficials de referència'), out[k][:50]
    out[k] = out[k].rstrip() + ' ' + out[i].strip()
    del out[k + 1:i + 1]
    #    viñeta partida en dos en el PDF: «… dotant a les administracions.» + «• educatives dels
    #    recursos…» (pág. 78); se une al punto anterior sin tocar el texto
    i = buscar(out, lambda l: l.startswith('- educatives dels recursos necessaris'), 'educatives')
    k = anterior(out, i)
    assert out[k].startswith('- Seguir treballant per la universalitat de l’etapa 0-3'), out[k][:50]
    out[k] = out[k].rstrip() + ' ' + out[i][2:].strip()
    del out[k + 1:i + 1]

    # 5) negrita rota: «**… obligator** i per a» -> «**… obligatori** per a» (pág. 6)
    i = buscar(out, lambda l: '**Garantir el lloguer social obligator** i per a' in l, 'obligatori')
    out[i] = out[i].replace('**Garantir el lloguer social obligator** i per a',
                            '**Garantir el lloguer social obligatori** per a')

    # 6) viñetas que son exposición -> párrafo; sus subviñetas pasan a medidas de primer nivel
    for pre in EXPOSICION:
        i = buscar(out, lambda l: l.startswith('- ' + pre), pre)
        out[i] = out[i][2:]
        for k in range(i + 1, len(out)):
            if out[k].startswith('- ') or out[k].startswith('#'):
                break
            if out[k].startswith('  - '):
                out[k] = out[k][2:]

    # 7) compromisos escritos como párrafo -> medida
    for pre in MEDIDAS:
        i = buscar(out, lambda l: l.startswith(pre), pre)
        out[i] = '- ' + out[i]

    return [TITULO, ''] + out

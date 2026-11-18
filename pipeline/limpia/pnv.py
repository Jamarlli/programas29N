"""Limpieza propia del programa de EAJ-PNV (Elecciones generales 29N 2026), versión en castellano.

Estructura del PDF: portada, índice, introducción («Lo que te importa. Lo que vamos a defender.»),
cuadro «Cinco compromisos para Euskadi» y cinco capítulos («01 / COMPROMISO 1 / PODER CONSTRUIR TU
VIDA AQUÍ»…). Cada capítulo abre con un mini-índice («En este capítulo»), una introducción y, tras el
rótulo «Nuestros compromisos», apartados N.N con una entradilla, el rótulo «Qué proponemos», grupos
temáticos en mayúsculas y medidas numeradas 01, 02… (la numeración se reinicia en cada apartado).

- Capítulos → «## N. Título»; apartados N.N → «### N.N Título»; grupos en mayúsculas → «####».
- Medidas «- **01** texto» / «- **01 arranque en negrita** , resto» → «1. texto» / «1. **arranque**, resto».
- Se quitan los rótulos de diseño que se repiten en cada página o apartado («Euskadi zaindu», «En este
  capítulo» con su mini-índice, «Nuestros compromisos», «Qué proponemos»), el índice y la contraportada.
- El cuadro «Cinco compromisos para Euskadi» (número, título, página y resumen de cada capítulo) es un
  resumen de los capítulos, no una lista de medidas: cada fila queda como un párrafo «**01 — Título** —
  resumen», sin la referencia de página («6 pág.»).
"""
import re
from clean import plain

TITULO = '# Defendemos Euskadi. Programa elecciones generales 2026'

CAPS = {
    '1': 'Poder construir tu vida aquí',
    '2': 'Una Euskadi que trabaja y prospera',
    '3': 'Vivir con tranquilidad y con derechos',
    '4': 'Cuidar lo que hemos conseguido',
    '5': 'Decidir aquí. Hacernos escuchar allí.',
}

# Nombres propios dentro de los rótulos de grupo en mayúsculas
PROPIOS = [
    ('euskadi', 'Euskadi'), ('ertzaintza', 'Ertzaintza'), ('seguridad social', 'Seguridad Social'),
    ('ley ela', 'Ley ELA'), ('del estatuto', 'del Estatuto'), ('derechos históricos', 'Derechos Históricos'),
    ('concierto económico', 'Concierto Económico'), ('concierto político', 'Concierto Político'),
    ('ley de secretos oficiales', 'Ley de Secretos Oficiales'),
]

ROTULOS = ('ÍNDICE', 'EUSKADIZAINDU', 'ENESTECAPÍTULO', 'NUESTROSCOMPROMISOS', 'QUÉPROPONEMOS')

TERM = tuple('.:;!?)»"”…')


def frase(t):
    """Rótulo en mayúsculas → minúsculas normales con nombres propios."""
    s = t.lower()
    for a, b in PROPIOS:
        s = re.sub(r'\b' + re.escape(a) + r'(?!\w)', b, s)
    return s[0].upper() + s[1:]


def es_grupo(s):
    """Rótulo de grupo de medidas: negrita en mayúsculas sin minúsculas."""
    t = plain(re.sub(r'^(-|>)\s+', '', s))
    return (re.match(r'^(#+\s*|-\s+|>\s+)?\*\*[^a-záéíóúñü_]+\*\*$', s) is not None
            and len(t) > 4 and re.search(r'[A-ZÁÉÍÓÚÑ]{3}', t) is not None)


def medida(s):
    """«- **01** texto», «> **01** texto» o «- **01 negrita** , resto» → «1. …»."""
    m = re.match(r'^(?:-|>)\s+\*\*(\d{2})\*\*\s+(.*)$', s)
    if m:
        return f'{int(m.group(1))}. {m.group(2)}'
    m = re.match(r'^(?:-|>)\s+\*\*(\d{2})\s+(.*)$', s)
    if m:
        return f'{int(m.group(1))}. **{m.group(2)}'
    return None


def limpiar(lineas):
    # 1. Portada e índice: todo lo anterior a la introducción
    ini = next(i for i, l in enumerate(lineas) if 'LO QUE TE IMPORTA. LO QUE VAMOS A DEFENDER.' in l and l.startswith('###'))
    # contraportada: desde «HAUTESKUNDE OROKORREN» hasta el final
    fin = next(i for i, l in enumerate(lineas) if l.startswith('**HAUTESKUNDE OROKORREN**'))
    lineas = lineas[ini:fin]

    # 2. Quitar líneas en blanco y trabajar con líneas de contenido
    ls = [l.rstrip() for l in lineas if l.strip()]

    out = [TITULO]
    i = 0
    while i < len(ls):
        s = ls[i].strip()
        compacto = plain(s).replace(' ', '')
        # rótulos de diseño repetidos
        if compacto in ROTULOS:
            i += 1; continue
        # mini-índice del capítulo («- **1.1** Vivienda…»)
        if re.match(r'^- \*\*\d\.\d\*\* ', s):
            i += 1; continue
        # introducción
        if s.startswith('### **LO QUE TE IMPORTA'):
            out.append('## Lo que te importa. Lo que vamos a defender.'); i += 1; continue
        # cuadro «Cinco compromisos para Euskadi»
        if s.startswith('### **CINCO COMPROMISOS PARA EUSKADI'):
            out.append('## Cinco compromisos para Euskadi')
            i += 1
            while not ls[i].startswith('# **01**'):
                num = plain(ls[i])
                assert re.match(r'^0\d$', num), ls[i]
                assert re.search(r'\d+ pág\.$', ls[i + 1]), ls[i + 1]
                res = plain(ls[i + 2])
                out.append(f'**{num} — {CAPS[str(int(num))]}** — {res}')
                i += 3
            continue
        # capítulo: «# **01**» + «**C O M P R O M I S O 1**» + «### **TÍTULO**»
        m = re.match(r'^# \*\*0(\d)\*\*$', s)
        if m:
            n = m.group(1)
            assert plain(ls[i + 1]).replace(' ', '') == f'COMPROMISO{n}', ls[i + 1]
            assert ls[i + 2].startswith('### **'), ls[i + 2]
            out.append(f'## {n}. {CAPS[n]}')
            i += 3; continue
        # apartado N.N
        m = re.match(r'^#+\s*\*\*(\d\.\d)\s+(.+?)\*\*$', s)
        if m:
            out.append(f'### {m.group(1)} {m.group(2).strip()}'); i += 1; continue
        # grupo de medidas en mayúsculas
        if plain(s) == 'DEFENDER. ACORDAR. EXIGIR.':  # lema de la introducción: es texto, no título
            out.append(re.sub(r'^#+\s*', '', s)); i += 1; continue
        if es_grupo(s):
            out.append('#### ' + frase(plain(re.sub(r'^(-|>)\s+', '', s)))); i += 1; continue
        # medida numerada
        md = medida(s)
        if md:
            out.append(md); i += 1; continue
        # párrafo tomado por título (arranque en negrita de un párrafo)
        if s.startswith('#'):
            out.append(re.sub(r'^#+\s*', '', s)); i += 1; continue
        # subpunto que en realidad es la continuación de una negrita partida
        if re.match(r'^-\s+\*\*[a-záéíóúñ]', s):
            out.append(s[2:].strip()); i += 1; continue
        out.append(s); i += 1

    # 3. Negritas partidas entre líneas: «… con el**» + «**inicio de …** , …» → una sola negrita
    res = []
    for l in out:
        if (res and l.startswith('**') and re.match(r'^\*\*[a-záéíóúñ]', l)
                and res[-1].endswith('**') and not res[-1][:-2].rstrip().endswith(TERM)):
            res[-1] = res[-1][:-2].rstrip() + ' ' + l[2:]
            continue
        res.append(l)
    out = res

    # 4. Espacio que la conversión mete entre el cierre de negrita y la puntuación: «**texto** ,»
    out = [re.sub(r'\*\* +([,.;:])', r'**\1', l) for l in out]

    # 5. Línea en blanco entre bloques
    final = []
    for l in out:
        final += [l, '']
    return final

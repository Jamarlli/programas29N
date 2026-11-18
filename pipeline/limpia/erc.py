"""Limpieza propia del programa de ERC (Eleccions al Congrés 2026, en catalán).

Estructura del PDF: portada («Pel país. Per la gent. Pel futur.»), índice (pág. 3), «Preàmbul» y
tres bloques en mayúsculas («A. DEFENSAR EL PAÍS», «B. DEFENSAR LA GENT», «C. DEFENSAR ELS
SERVEIS PÚBLICS»), cada uno con apartados «A.», «B.»… Cada apartado tiene párrafos de exposición
y después las medidas numeradas del 1 al 227 («N. Títol en negreta. Cos…»), que la conversión ya
deja como «N. » en la columna 0. Cabeceras y pies («Eleccions al Congrés 2026 | Programa
electoral», «ESQUERRA REPUBLICANA», número de página) ya los quita pymupdf4llm.
"""
import re

TERM = tuple('.:;!?)»"”…')

BLOQUES = {
    'PREÀMBUL': 'Preàmbul',
    'A. DEFENSAR EL PAÍS': 'A. Defensar el país',
    'B. DEFENSAR LA GENT': 'B. Defensar la gent',
    'C. DEFENSAR ELS SERVEIS PÚBLICS': 'C. Defensar els serveis públics',
}


def sin_marcas(s):
    return re.sub(r'\s+', ' ', re.sub(r'^#+\s*', '', s).replace('**', '')).strip()


def siguiente(lineas, i):
    j = i + 1
    while j < len(lineas) and not lineas[j].strip():
        j += 1
    return j


def limpiar(lineas):
    # 1) portada + índice: todo lo anterior a «PREÀMBUL»
    ini = next(i for i, l in enumerate(lineas) if l.startswith('#') and 'PREÀMBUL' in l)
    lineas = ['# Pel país. Per la gent. Pel futur.', ''] + lineas[ini:]

    out = []
    for l in lineas[2:]:
        s = l.strip()
        if s.startswith('#'):
            t = sin_marcas(s)
            if t in BLOQUES:  # bloques en mayúsculas -> capítulos
                out.append('## ' + BLOQUES[t]); continue
            if s.startswith('## '):  # apartados «A. …» (ya en minúsculas normales)
                out.append('### ' + t); continue
            raise ValueError(f'título inesperado: {s}')
        out.append(l)

    # 2) palabra partida en el salto de página tomada por subviñeta: «legislació edu-» + «- cativa» (pág. 10-11)
    i = next(i for i, l in enumerate(out) if l.rstrip().endswith('Modificar la legislació edu-'))
    j = siguiente(out, i)
    assert out[j].lstrip().startswith('- cativa estatal'), out[j][:40]
    out[i] = out[i].rstrip()[:-1] + out[j].lstrip()[2:]
    del out[i + 1:j + 1]

    # 3) subpuntos de la medida 127 (viñetas «–» en el PDF, pág. 29)
    i = next(i for i, l in enumerate(out) if l.startswith('127. Alinear la política industrial'))
    for k in range(i + 1, len(out)):
        if re.match(r'^\d+\. ', out[k]):
            break
        if re.match(r'^\s+- ', out[k]):
            out[k] = '  - ' + out[k].strip()[2:]

    # 4) medida 218 (pág. 44): en el PDF sigue con cuatro párrafos sangrados que forman parte de la
    #    medida (no son viñetas). La conversión convierte el primero en dos subviñetas partidas y los
    #    otros tres en párrafos sueltos: se unen al punto de la medida para que quede completa.
    i = next(i for i, l in enumerate(out) if l.startswith('218. Cal una reforma de la Llei 39/1988'))
    j = next(j for j in range(i + 1, len(out)) if out[j].startswith('219. '))
    trozos = [re.sub(r'^\s*-\s+', '', l.strip()) for l in out[i + 1:j] if l.strip()]
    assert trozos[0].startswith('Aquesta reforma ha de permetre') and trozos[1].startswith('l’Estat i que'), trozos[:2]
    assert trozos[-1].startswith('I també calen canvis'), trozos[-1][:40]
    texto = out[i].rstrip()
    for t in trozos:
        texto += ' ' + t
    out[i:j] = [texto, '']

    # 5) párrafo partido por el salto de página tras «…Agenda 2030:» (págs. 29-30); join_broken no une tras «:»
    i = next(i for i, l in enumerate(out) if l.rstrip().endswith('amb els objectius globals de l’Agenda 2030:'))
    j = siguiente(out, i)
    assert out[j].startswith('un model sostenible, d’eficiència'), out[j][:40]
    out[i] = out[i].rstrip() + ' ' + out[j].strip()
    del out[i + 1:j + 1]

    return ['# Pel país. Per la gent. Pel futur.', ''] + out

"""Limpieza propia del programa de Falange Española de las JONS (29N 2026).

Estructura del PDF: índice, introducción, seis bloques (portadas en imagen, sin texto) con 25
capítulos numerados («1. INMIGRACIÓN») más el «Anexo I – Plan nacional de remigración», y epílogo.
Las medidas van numeradas «1.1.», «1.2.»…: la conversión ya las deja como «- 1.1. …» (se conservan
así porque «1.1. » no lo reconoce segment.py como punto de lista). Los títulos de bloque solo
están como texto en el índice; se insertan con esa redacción.
"""
import re

TITULO = '# Programa electoral. Elecciones generales 29 de noviembre de 2026'

BLOQUES = {
    '1': 'Bloque I. Emergencias nacionales: remigración y vivienda accesible',
    '3': 'Bloque II. Soberanía y unidad nacional',
    '6': 'Bloque III. Protección y futuro de los españoles: trabajo, familia y vida digna',
    '9': 'Bloque IV. Soberanía económica y reindustrialización',
    '13': 'Bloque V. Ruptura con el Régimen del 78: hacia una nueva España',
    '19': 'Bloque VI. Servicios esenciales y gestión nacional',
}

CAPS = {
    '1': 'Inmigración',
    '2': 'Vivienda',
    '3': 'Soberanía nacional y política exterior',
    '4': 'Unión Europea y euro',
    '5': 'Unidad nacional y modelo territorial',
    '6': 'Trabajo',
    '7': 'Familia, natalidad y vida',
    '8': 'Demografía y vertebración territorial',
    '9': 'Economía y fiscalidad',
    '10': 'I+D+I e industria',
    '11': 'Energía',
    '12': 'Sector primario',
    '13': 'Forma del Estado',
    '14': 'Regímen político',
    '15': 'Seguridad nacional y ciudadana',
    '16': 'Defensa',
    '17': 'Justicia',
    '18': 'Eficiencia administrativa',
    '19': 'Educación',
    '20': 'Sanidad',
    '21': 'Cultura y deporte',
    '22': 'Turismo',
    '23': 'Consumo',
    '24': 'Transportes, movilidad e infraestructuras',
    '25': 'Medio ambiente',
}

FASES = {
    'EN LOS PRIMEROS 5 AÑOS:': 'En los primeros 5 años',
    'EN UN PLAZO DE 10 AÑOS:': 'En un plazo de 10 años',
    'DE 10 AÑOS EN ADELANTE:': 'De 10 años en adelante',
}

PIE = re.compile(r'^(#+\s*)?Falange Española de las JONS\s*$')
TERM = tuple('.:;!?)»"”…')


def limpiar(lineas):
    # 1. Índice: desde «ÍNDICE» hasta el primer párrafo de la introducción
    ini = next(i for i, l in enumerate(lineas) if 'ÍNDICE' in l)
    fin = next(i for i, l in enumerate(lineas) if l.startswith('La nación española debe volver'))
    lineas = [TITULO, '', '## Introducción', ''] + lineas[fin:]

    # 2. Pie de página repetido
    lineas = [l for l in lineas if not PIE.match(l.strip())]

    # 3. Párrafos cortados por el salto de página que siguen en mayúscula
    #    («… bajo el signo de la» + «Hispanidad, siempre …»)
    out = []
    for l in lineas:
        s = l.strip()
        if s and not s.startswith(('#', '- ', '<')) and not re.match(r'^\d', s):
            k = len(out) - 1
            while k >= 0 and not out[k].strip():
                k -= 1
            if k >= 0 and re.match(r'^- \d+\.\d+\.', out[k]) and not out[k].rstrip().endswith(TERM):
                out = out[:k] + [out[k].rstrip() + ' ' + s]
                continue
        out.append(l)
    lineas = out

    # 4. Títulos, fases del anexo, subpuntos y reparaciones puntuales
    out, en_611 = [], False
    for l in lineas:
        s = l.strip()
        m = re.match(r'^##\s*\*\*(\d+)\.\s+.+\*\*$', s)
        if m:
            n = m.group(1)
            if n in BLOQUES:
                out += ['## ' + BLOQUES[n], '']
            out.append(f'### {n}. {CAPS[n]}'); en_611 = False; continue
        if s.startswith('## **ANEXO I'):
            out.append('### Anexo I – Plan nacional de remigración'); continue
        if s in FASES:
            out.append('#### ' + FASES[s]); continue
        if s == '## **¡¡¡ARRIBA ESPAÑA!!!**':
            out.append('¡¡¡ARRIBA ESPAÑA!!!'); continue
        if s.startswith('Este documento no es una promesa electoralista'):
            out += ['## Epílogo', '']
        # arranques de las listas del anexo: son compromisos en sí («Derogación de la actual Ley…»)
        if s.startswith(('Derogación de la actual Ley de Extranjería', 'Incentivación de la vuelta voluntaria',
                         'Y, por otro lado, incentivación del retorno')):
            out.append('- ' + s); continue
        if s.startswith('- 6.1.1.'):
            out.append('  ' + s); en_611 = True; continue
        if en_611:
            if re.match(r'^- \d+\.\d+\.', s):
                en_611 = False
            elif s.startswith('- '):
                out.append('    ' + s); continue
        # guion final de línea perdido en la conversión («necesidades-» + «y priorizando»)
        l = l.replace('según dichas necesidadesy priorizando', 'según dichas necesidades- y priorizando')
        out.append(l)
    return out

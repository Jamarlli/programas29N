"""Limpieza propia del programa de Compromís: Front Valencià (29N 2026, en valenciano).

Estructura del PDF: portada con índice (págs. 1-2), capítulos «N. TÍTOL» en naranja,
apartados en mayúsculas negras y medidas como viñetas «-». No hay cabeceras, pies ni
números de página. Un único bloque de subviñetas (las mesures de Rodalies, págs. 58-59).
"""
import re
from clean import plain

TERM = tuple('.:;!?)»"”…')

# Palabras que mantienen mayúscula al pasar los títulos a minúsculas
PROPIOS = {
    'lgtbiq+': 'LGTBIQ+',
    'd’estat': 'd’Estat',
    'unió europea': 'Unió Europea',
}


def frase(t):
    """«UNA VIDA SEGURA: HABITATGE» -> «Una vida segura: habitatge» (respetando nombres propios)."""
    t = plain(t).lower()
    m = re.match(r'^(\d+\.\s+)?(.*)$', t)
    num, resto = m.group(1) or '', m.group(2)
    for k, v in PROPIOS.items():
        resto = resto.replace(k, v)
    resto = resto[:1].upper() + resto[1:]
    return num + resto


def es_bloque(l):
    return re.match(r'^\s*(-|#|\|)', l) is not None


def limpiar(lineas):
    # 1) portada + índice: todo lo anterior a «0. INTRODUCCIÓ»
    ini = next(i for i, l in enumerate(lineas) if l.startswith('## ') and 'INTRODUCCI' in l)
    lineas = ['# Programa electoral 29N', ''] + lineas[ini:]

    out = []
    rodalies = False
    for l in lineas:
        s = l.strip()
        # capítulos y apartados: a minúsculas normales
        m = re.match(r'^(#{2,3})\s+(.*)$', s)
        if m:
            rodalies = False
            out.append(f'{m.group(1)} {frase(m.group(2))}')
            continue
        # guion de pronombre enclítico perdido en el salto de línea («eliminant-\nla», pág. 18)
        l = l.replace('eliminantla per a rendes', 'eliminant-la per a rendes')
        # viñeta duplicada por la conversión («- - Impulsarem…», pág. 21)
        l = re.sub(r'^- - ', '- ', l)
        # continuación de una medida tomada por subviñeta («   - d’industrialització…», pág. 21)
        mm = re.match(r'^\s+- (?=[a-zàèéíòóúïüç’\'])', l)
        if mm:
            l = l[mm.end():]
        # subviñetas de la medida de Rodalies (págs. 58-59)
        if s.startswith('- Ampliarem la dotació del Fons de Compensació Interterritorial'):
            rodalies = False
        if rodalies and re.match(r'^\s*- ', l):
            l = '  - ' + l.strip()[2:]
        if 'En concret, incorporarem les següents mesures:' in s:
            rodalies = True
        out.append(l)

    # 2) medidas cortadas por el salto de página aunque la continuación empiece en mayúscula
    #    («…no» + «LGTBIfòbics, no masclistes…», pág. 49)
    res = []
    for l in out:
        if l.strip() and not es_bloque(l):
            k = len(res) - 1
            while k >= 0 and not res[k].strip():
                k -= 1
            if k >= 0 and re.match(r'^\s*- ', res[k]) and not res[k].rstrip().endswith(TERM):
                res = res[:k] + [res[k].rstrip() + ' ' + l.strip()]
                continue
        res.append(l)
    return res

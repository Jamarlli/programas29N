"""Limpieza propia del programa de Convergents (Eleccions Generals 2026, en catalán).

Estructura del PDF (PowerPoint, 48 págs.): portada, «Presentació» (págs. 2-3), índice «Els nostres
compromisos» (pág. 4) y diez capítulos «N. TÍTOL» en mayúsculas. Cada capítulo abre con una
introducción a dos columnas que acaba en «Per tot això, des de Convergents proposem:», y sigue con
apartados en negrita azul y medidas como viñetas «✓». No hay cabeceras ni pies con texto; solo el
número de página (que la conversión ya omite salvo uno, pág. 13).

Lo que rompe la conversión:
- en varias introducciones mezcla las dos columnas: se reordenan los párrafos según el PDF;
- las medidas que siguen en otra línea salen como viñetas «- » sin «✓»: se unen a su medida;
- un título partido en dos y desordenado (pág. 14);
- negritas sueltas en la puntuación («capdavantera **,** econòmicament»).
"""
import re
from clean import plain

DROP = (
    r'^\d+<br>$',  # número de página dentro de una imagen (pág. 13)
)

# Párrafos de la introducción de cada capítulo, en el orden del PDF (columna izquierda y luego
# derecha). Se identifican por su arranque; el bloque va desde el título del capítulo hasta el
# primer apartado.
ORDEN = {
    '1.': ['Convergents és un partit que defensa', 'Així mateix, el català',
           'La realitat política catalana', 'en la responsabilitat, l’eficiència',
           'Per fer-ho possible', 'Per tot això, Convergents no donarà'],
    '2.': ['Catalunya ha de renovar', 'L’equitat ha de ser', 'Aquest pacte intergeneracional',
           'Defensem la família', 'Alhora, entenem', 'Tot i que l’article 47',
           'comunitats autònomes i els ens locals', 'A Catalunya hi ha un gran desequilibri',
           'Ens comprometen', 'Cal un nou impuls', 'Rebutgem amb fermesa', 'La resposta a les necessitats',
           'Per tot això'],
    '3.': ['Convergents defensa un model', 'Volem una economia', 'El nostre model productiu',
           'capacitat d’atraure', 'Cal impulsar la indústria', 'Finalment, apostem', 'Per tot això'],
    '4.': ['Catalunya compta amb', 'Actualment, però', 'A aquests factors', 'A més, tant la legislació',
           'recuperació de sols', 'Des de Convergents ens comprometem', 'Per tot això'],
    '6.': ['La igualtat efectiva', 'D’altra banda, la violència', 'Malauradament',
           'Pel que fa a la qüestió migratòria', 'persones que fugen', 'D’altra banda, la diversitat',
           'Per tot això'],
    '9.': ['Apostem pel “bon govern”', 'Una societat democràtica', 'Creiem en el principi',
           'Especialment, cal atendre', 'D’altra banda, no hi ha bon govern', 'Finalment, Catalunya',
           'Per tot això'],
}

PROPIOS = {'catalunya': 'Catalunya', 'europa': 'Europa'}


def frase(t):
    """«1. AVANÇAR CAP A LA SOBIRANIA NACIONAL» -> «1. Avançar cap a la sobirania nacional»."""
    t = plain(t).lower()
    m = re.match(r'^(\d+\.\s+)?(.*)$', t)
    num, resto = m.group(1) or '', m.group(2)
    for k, v in PROPIOS.items():
        resto = re.sub(rf'\b{k}\b', v, resto)
    return num + resto[:1].upper() + resto[1:]


def es_capitulo(l):
    return re.match(r'^##\s+\*\*\d+\.', l) is not None


def es_apartado(l):
    return l.startswith('## ') and not es_capitulo(l)


def reordenar(lineas, num, orden):
    ini = next(i for i, l in enumerate(lineas) if re.match(rf'^##\s+\*\*{re.escape(num)}\s', l))
    fin = next(i for i in range(ini + 1, len(lineas)) if es_apartado(lineas[i]))
    pars = [l for l in lineas[ini + 1:fin] if l.strip()]
    assert len(pars) == len(orden), (num, len(pars), len(orden))
    nuevo = []
    for pre in orden:
        cand = [p for p in pars if p.startswith(pre)]
        assert len(cand) == 1, (num, pre, len(cand))
        nuevo += [cand[0], '']
    return lineas[:ini + 1] + [''] + nuevo + lineas[fin:]


def limpiar(lineas):
    # portada: todo lo anterior a «PRESENTACIÓ»; índice: «ELS NOSTRES COMPROMISOS» hasta el capítulo 1
    ini = next(i for i, l in enumerate(lineas) if l.startswith('## ') and 'PRESENTACI' in l)
    idx = next(i for i, l in enumerate(lineas) if l.startswith('## ') and 'COMPROMISOS' in l)
    cap1 = next(i for i, l in enumerate(lineas) if es_capitulo(l))
    lineas = (['# Programa electoral eleccions generals 2026', '', '## Presentació', '']
              + lineas[ini + 1:idx] + lineas[cap1:])

    # introducciones con las columnas mezcladas
    for num, orden in ORDEN.items():
        lineas = reordenar(lineas, num, orden)

    # título partido en dos y desordenado (pág. 14)
    i = next(i for i, l in enumerate(lineas) if 'Avançar cap a una economia de sostenible' in l)
    j = next(j for j in range(i + 1, len(lineas)) if lineas[j].strip())
    assert 'mercat més competitiva i' in lineas[j]
    lineas[i] = '## **Avançar cap a una economia de mercat més competitiva i sostenible.**'
    del lineas[i + 1:j + 1]

    out = []
    for l in lineas:
        s = l.strip()
        if es_capitulo(s):
            out.append('## ' + frase(s[2:])); continue
        if s.startswith('### '):  # frase del cuerpo tomada por título («Catalunya viu un moment crucial.»)
            out.append(plain(s)); continue
        if es_apartado(s) and s != '## Presentació':
            out.append('### ' + plain(s[3:])); continue
        if s.startswith('- ✓'):
            out.append('- ' + s[3:].strip()); continue
        if s.startswith('- '):
            # continuación de la medida anterior que la conversión tomó por viñeta
            k = len(out) - 1
            while not out[k].strip():
                k -= 1
            assert out[k].startswith('- '), s
            out = out[:k] + [out[k].rstrip() + ' ' + s[2:].strip()]
            continue
        out.append(l)

    # párrafo partido en dos en el PDF que la conversión juntó (pág. 24)
    out = [l.replace('per al progrés col·lectiu. En un país immers',
                     'per al progrés col·lectiu.\n\nEn un país immers') for l in out]
    # negritas sueltas en la puntuación: «capdavantera **,** econòmicament», «social **_._**»
    out = [re.sub(r'\s*\*\*_?([,.])_?\*\*', r'\1', l) for l in out]
    # espacio entre el cierre de la cursiva y la puntuación: «_Big Data_ )»
    out = [re.sub(r'_ +([,.;:)])', r'_\1', l) for l in out]
    return out

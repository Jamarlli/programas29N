"""Limpieza propia del programa de Podemos «Así de básico: Paz, casa y trabajo» (29N 2026).

Estructura del PDF: portada, índice, introducción («Así de básico: paz, casa y trabajo») y seis
capítulos sin numerar, cada uno con una página-portada con el título en minúsculas y, en la página
siguiente, el mismo título en mayúsculas. El capítulo «Vida solo hay una. Planeta solo hay uno»
tiene tres apartados (los del índice). Los títulos se fijan con la redacción del índice.
Las medidas van numeradas del 1 al 442 («**N. Título.** Texto»); se pasan a «N. **Título.** Texto».
La conversión toma por título (######) algunas medidas cuyo título en negrita ocupa dos líneas
y parte la negrita en dos trozos: se reconstruyen. Las viñetas que cuelgan de una medida son
subpuntos («  - »; las «⮡» de segundo nivel, «    - »), igual que los párrafos con arranque en
negrita de la medida 280 (ratios por etapa). Los párrafos sangrados que continúan una medida
(«Esta medida requerirá…») se pegan a ella con un salto de línea simple para que no queden sueltos.
"""
import re

TITULO = '# Así de básico: paz, casa y trabajo'

# Títulos en mayúsculas de la página interior -> (nivel, título)
CAPS = {
    'ASÍ DE BÁSICO: PAZ, CASA Y TRABAJO.': (2, 'Así de básico: paz, casa y trabajo'),
    'LAS CASAS SON PARA VIVIR.': (2, 'Las casas son para vivir'),
    'LOS PRECIOS TIENEN QUE BAJAR': (2, 'Los precios tienen que bajar'),
    'PAZ. PARAR LAS GUERRAS.': (2, 'Paz. Parar las guerras'),
    'TRABAJAR MENOS PARA VIVIR MEJOR.': (2, 'Trabajar menos para vivir mejor'),
    'VIDA SOLO HAY UNA. PLANETA SOLO HAY UNO.': (2, 'Vida solo hay una. Planeta solo hay uno'),
    'VIDAS QUE MEREZCAN LA PENA SER VIVIDAS': (3, 'Vidas que merezcan la pena ser vividas'),
    'SERVICIOS PÚBLICOS PARA GARANTIZAR VIDAS DIGNAS': (3, 'Servicios públicos para garantizar vidas dignas'),
    'PLANETA SOLO HAY UNO': (3, 'Planeta solo hay uno'),
    'ESPAÑA, REPÚBLICA PLURINACIONAL.': (2, 'España, república plurinacional'),
}

# Líneas que no son programa: cabecera de página, números de página, títulos de las páginas-portada
# de cada capítulo (repiten el título interior) y lema y fecha de la contraportada.
FUERA = re.compile(r'^(#+\s*)?(\*\*)?(PROGRAMA ELECTORAL|Las casas son para vivir|Los precios tienen que bajar'
                   r'|Paz\. Parar las guerras\.|Trabajar menos para vivir mejor\.'
                   r'|Vida solo hay una\. Planeta solo hay uno\.|España, república plurinacional\.'
                   r'|Paz, casa y trabajo\.)(\*\*)?$|^\d{1,3}$|^29N$')

TERM = tuple('.:;!?')
MEDIDA = re.compile(r'^\*\*(\d+)\.\s*')


def plano(l):
    return l.replace('*', '').strip()


def limpiar(lineas):
    # 1. Portada e índice: todo lo anterior al título interior de la introducción
    ini = next(i for i, l in enumerate(lineas) if 'ASÍ DE BÁSICO: PAZ, CASA Y TRABAJO.**' in l and l.startswith('###'))
    lineas = lineas[ini:]

    # 2. Cabeceras, números de página y portadas de capítulo
    lineas = [l for l in lineas if not FUERA.match(l.strip())]

    # 3. Títulos de capítulo y apartado; quitar el «######» que la conversión pone a medidas
    out = []
    for l in lineas:
        s = l.strip()
        if s.startswith('#'):
            t = plano(re.sub(r'^#+\s*', '', s))
            if t in CAPS:
                n, txt = CAPS[t]
                out.append('#' * n + ' ' + txt)
                continue
            s = re.sub(r'^#+\s*', '', s)  # medida o trozo de negrita tomado por título
            l = s
        out.append(l)
    lineas = out

    # 4. Negrita del título partida en dos líneas: «**23. … y deudores**» + «**hipotecarios.** Crearemos…»
    out = []
    for l in lineas:
        s = l.strip()
        if s.startswith('**') and not MEDIDA.match(s):
            k = len(out) - 1
            while k >= 0 and not out[k].strip():
                k -= 1
            p = out[k].rstrip() if k >= 0 else ''
            if (re.match(r'^(\*\*\d+\.|\s*- \*\*)', p) and p.endswith('**')
                    and not p[:-2].rstrip().endswith(TERM)):
                p = p[:-2].rstrip()
                cur = s[2:]
                p = p[:-1] + cur if re.search(r'[A-Za-záéíóúñ]-$', p) else p + ' ' + cur
                out = out[:k] + [p]
                continue
        out.append(l)
    lineas = out

    # 5. Medidas, subpuntos y continuaciones
    out, en_medida, prev_medida_titulo = [], False, False
    for l in lineas:
        s = l.strip()
        if not s:
            out.append(l); continue
        if s.startswith('#'):
            en_medida = False
            out.append(l); continue
        m = MEDIDA.match(s)
        if m:
            en_medida = True
            l = m.group(1) + '. **' + s[m.end():]
            # título de medida solo (la conversión lo separó del texto que lo sigue en el mismo párrafo)
            prev_medida_titulo = l.endswith('**') and l[:-2].rstrip().endswith(TERM)
            out.append(l); continue
        if en_medida:
            k = len(out) - 1
            while not out[k].strip():
                k -= 1
            if s.startswith('- ⮡') or s.startswith('⮡'):
                out.append('    - ' + s.lstrip('-⮡ ').strip()); prev_medida_titulo = False; continue
            if s.startswith('- '):
                out.append('  - ' + s[2:].strip()); prev_medida_titulo = False; continue
            if re.match(r'^[a-záéíóúñ(«"]', s):  # continuación tras salto de página: la une join_broken
                out.append(s); continue
            if s.startswith('**'):  # apartados con arranque en negrita dentro de una medida (280)
                out.append('  - ' + s); prev_medida_titulo = False; continue
            if prev_medida_titulo or not out[k].rstrip().endswith(TERM):
                # «250. **Reforma … en España.**» + «Lo actualizaremos …», o párrafo cortado por el
                # salto de página que sigue en mayúscula («… Crearemos un Cuerpo» + «Público de …»)
                out[k] = out[k].rstrip() + ' ' + s
                del out[k + 1:]
                prev_medida_titulo = False
                continue
            # párrafo sangrado que sigue a la medida: mismo bloque, línea aparte
            del out[k + 1:]
            out.append('   ' + s)
            continue
        out.append(l)
    lineas = out

    # 6. Reparaciones de negritas y espacios rotos por la conversión
    fix = [
        ('**Formación Profesiona** l.', '**Formación Profesional**.'),
        ('artificial (** **_deepfakes_ )**', 'artificial (_deepfakes_)**'),
        ('agricultores/as-ganaderos/ as jóvenes', 'agricultores/as-ganaderos/as jóvenes'),
        ('todo el año **.** Por ello', 'todo el año. Por ello'),
    ]
    res = []
    for l in lineas:
        for a, b in fix:
            l = l.replace(a, b)
        l = re.sub(r'(\*\*|_) +([,.;:])', r'\1\2', l)
        res.append(l)
    return [TITULO, ''] + res

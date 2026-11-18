"""Limpieza propia del programa de PACMA (Elecciones generales 29N 2026).

Estructura del PDF: «Presentación» y tres capítulos numerados («1. Nuestro compromiso con los
Animales», «2. … con el Medio Ambiente», «3. … con las Personas») con apartados N.N y
subapartados N.N.N (y N.N.N.N). pymupdf4llm asigna niveles de título al azar (a veces «####»
para un apartado N.N, a veces «- **N.N.**» o una negrita suelta), así que el nivel se deduce
del número: N → ##, N.N → ###, N.N.N y N.N.N.N → ####.
Las propuestas concretas son las viñetas «-» del PDF; el resto es exposición en párrafos.
"""
import re
from clean import plain, drop_range

DROP = (
    r'^[�\s]+$',  # lema «VOTA POR LO QUE CREES» con fuente sin mapear (p. 5)
)

NUM = re.compile(r'^(\d{1,2}(?:\.\d{1,2}){0,3})\.?\s*(.+)$')

# Párrafos cortados por un salto de página cuyo trozo siguiente empieza por mayúscula
# (join_broken solo une si empieza por minúscula): (final del primero, arranque del segundo)
CORTES = [
    ('fronteras de la Unión', 'Europea. A la crueldad'),
    ('en países como Arabia', 'Saudí, Egipto'),
]


def titulo(l):
    """Si la línea es un título numerado del programa, devuelve (nivel, texto)."""
    s = l.strip()
    if not (s.startswith(('#', '- **', '**'))) or len(s) > 260:
        return None
    t = plain(re.sub(r'^-\s+', '', s))
    m = NUM.match(t)
    if not m:
        return None
    # tiene que estar en negrita en el PDF (los títulos lo están; el cuerpo no empieza por número en negrita)
    if '**' not in s:
        return None
    num, txt = m.group(1), m.group(2).strip()
    prof = num.count('.') + 1
    nivel = {1: 2, 2: 3}.get(prof, 4)
    return nivel, f'{num}. {txt}'


def limpiar(lineas):
    # índice: desde «ÍNDICE» hasta «Presentación»
    lineas = drop_range(lineas, lambda l: l.startswith('#') and 'ÍNDICE' in l,
                        lambda l: l.startswith('#') and 'Presentación' in l)
    out = ['# Vota por lo que crees', '']
    for l in lineas:
        s = l.strip()
        if s.startswith('#') and plain(s) == 'Presentación':
            out.append('## Presentación'); continue
        t = titulo(l)
        if t:
            out.append('#' * t[0] + ' ' + t[1]); continue
        if s.startswith('#'):  # párrafo del cuerpo tomado por título
            out.append(re.sub(r'^#+\s*', '', s)); continue
        if re.match(r'^\s+-\s', l):  # el PDF no tiene subniveles: todas las viñetas son de primer nivel
            out.append(l.lstrip()); continue
        out.append(l)
    # punto final en cursiva suelto: «naturaleza _._»
    out = [re.sub(r'\s*_\._\s*$', '.', l) for l in out]
    # espacio que la conversión mete entre el cierre de negrita/cursiva y la puntuación: «**texto** ,»
    out = [re.sub(r'(\*\*|_) +([,.;:])', r'\1\2', l) for l in out]
    # unir párrafos partidos por salto de página que siguen en mayúscula
    for fin, ini in CORTES:
        i = next(i for i, l in enumerate(out) if l.rstrip().endswith(fin))
        j = i + 1
        while not out[j].strip():
            j += 1
        assert out[j].startswith(ini), (fin, out[j][:40])
        out[i] = out[i].rstrip() + ' ' + out[j].strip()
        del out[i + 1:j + 1]
    return out

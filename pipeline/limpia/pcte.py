"""Limpieza propia del «Programa de lucha» del PCTE (versión en castellano, 24 páginas).

Estructura del PDF:
- introducción sin título (p. 3), índice (p. 5), once capítulos numerados (01-11) y un cierre
  «Por el socialismo» (pp. 22-23); contraportada con lema y contacto (p. 24).
- Cada capítulo: párrafos de diagnóstico, rótulo «EJES DE LUCHA» y una rejilla de recuadros a dos
  columnas, cada uno con un título corto y un párrafo. Cada recuadro es una medida:
  «- **Título** — texto».
- pymupdf4llm a veces lee dos títulos de recuadro seguidos y luego sus dos textos en orden
  inverso (título A, título B, texto B, texto A). Se reasignan comprobándolo con el PDF:
  Alquiler de vivienda habitual / Alquiler social, Abastecimiento / Transparencia,
  Espacios juveniles / Salarios por edad, Investigación / Gratuidad cultural.
"""
import re
from clean import plain, norm

CAPS = [
    "Luchar por el trabajo, el salario y el tiempo de vida",
    "Más mecanismos de control obrero en la producción",
    "La vivienda no es un negocio",
    "Defender los servicios públicos y la protección social",
    "Asegurar la cesta de la compra y los derechos en el campo",
    "Defender a la juventud trabajadora",
    "Igualdad real para las mujeres trabajadoras",
    "Por el acceso a la cultura y la ciencia",
    "Por la paz y el internacionalismo",
    "Contra la reacción y el autoritarismo: defender nuestras libertades",
    "Aumentar nuestros derechos políticos y sindicales",
]
CAP_N = {norm(t): i + 1 for i, t in enumerate(CAPS)}

TERM = tuple('.:;!?)»"”…')

# contraportada: contacto
CONTACTO = (r'^\*\*CO N TACTA CO N N O S OT R O S\*\*$', r'^\*\*pcte\.es @_pcte_\*\*$')


def unir(trozos):
    """Une los párrafos de un mismo recuadro partidos por la conversión."""
    acc = ''
    for t in trozos:
        t = t.strip()
        if not acc:
            acc = t
        elif acc.endswith('**') and t.startswith('**') and not acc[:-2].rstrip().endswith(TERM):
            acc = acc[:-2].rstrip() + ' ' + t[2:]
        else:
            acc = acc + ' ' + t
    return acc


def limpiar(lineas):
    # negritas: «**texto** ,» → «**texto**,»
    lineas = [re.sub(r'\*\* +([.,;:?!])', r'**\1', l) for l in lineas]
    out = ['# Programa de lucha', '']
    ejes = False          # dentro de la rejilla de recuadros
    tokens = []           # ('H', título) / ('P', texto) de la rejilla en curso

    def volcar():
        nonlocal tokens
        i = 0
        while i < len(tokens):
            kind, val = tokens[i]
            if kind != 'H':
                raise ValueError(f'texto sin título de recuadro: {val[:60]}')
            # título A, título B, texto B, texto A
            if i + 1 < len(tokens) and tokens[i + 1][0] == 'H':
                a, b = val, tokens[i + 1][1]
                assert tokens[i + 2][0] == 'P' and tokens[i + 3][0] == 'P', (a, b)
                assert i + 4 >= len(tokens) or tokens[i + 4][0] == 'H', (a, b)
                out.extend([f'- **{b}** — {tokens[i + 2][1]}', '', f'- **{a}** — {tokens[i + 3][1]}', ''])
                i += 4
                continue
            j = i + 1
            trozos = []
            while j < len(tokens) and tokens[j][0] == 'P':
                trozos.append(tokens[j][1]); j += 1
            assert trozos, val
            out.extend([f'- **{val}** — {unir(trozos)}', ''])
            i = j
        tokens = []

    for l in lineas:
        s = l.strip()
        if not s:
            continue
        if s.startswith('|') or any(re.match(r, s) for r in CONTACTO):   # índice y contacto
            continue
        if re.match(r'^#+\s*\*\*\d{2}\*\*$', s):    # número de capítulo suelto
            continue
        t = plain(s)
        n = CAP_N.get(norm(t))
        if s.startswith('#'):
            if n:
                volcar(); ejes = False
                out += [f'## {n:02d}. {CAPS[n - 1]}', '']
                continue
            if norm(t) == 'por el socialismo':
                volcar(); ejes = False
                out += ['## Por el socialismo', '']
                continue
            if norm(t) == 'ejes de lucha':
                ejes = True
                out += ['### Ejes de lucha', '']
                continue
            if s.startswith('######'):              # arranque del cap. 10 tomado por título
                out += [f'**{t}**', '']
                continue
            if ejes:
                tokens.append(('H', t))
                continue
            raise ValueError(f'título inesperado: {s}')
        if ejes:
            tokens.append(('P', s))
        else:
            out += [s, '']
    volcar()
    return out

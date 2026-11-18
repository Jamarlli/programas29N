"""Limpieza propia del programa del Frente Obrero («Recuperar España. Programa político»).

- Quita el índice (tabla) del principio.
- Los 21 capítulos salen dos veces (portadilla + cabecera de la página siguiente) con las
  letras partidas por resaltados; se reconocen comparando con los títulos del índice y se
  dejan una sola vez como «## NN. Título».
- Repara la letra capital de cada capítulo: la conversión la deja suelta a media línea
  («l Frente Obrero … servicio de **E** los intereses») y a veces dentro de una palabra
  partida («nues- **L** tros»).
- Medidas «**N.** Texto» → «N. Texto». En Sanidad, las tres medidas sin número que preceden
  a la lista numerada pasan a «- ».
- «Medidas:» (cap. 2) no es un título: queda como párrafo.
"""
import re
from clean import norm

CAPS = [
    "La España que debemos ser",
    "Los trabajadores primero",
    "Soberanía nacional",
    "Recuperemos la industria española",
    "Soberanía energética",
    "Fiscalidad",
    "Educación",
    "Cultura",
    "Juventud",
    "Mujer e igualdad real",
    "Natalidad y familia",
    "En defensa del campo español",
    "Contra la censura",
    "Sanidad",
    "Vivienda",
    "Pensiones",
    "Inmigración",
    "Estructura territorial y administración",
    "Justicia",
    "Fuerzas y Cuerpos de Seguridad del Estado",
    "Ejército",
]
_CLAVE = {re.sub(r'[\s0-9]+', '', norm(t)): i for i, t in enumerate(CAPS)}

SANIDAD_SIN_NUM = (
    "Centralizar, unificar y homogeneizar el sistema nacional de salud.",
    "Acabar con el proceso de externalización y privatización de la sanidad.",
    "Incrementar el gasto e inversión sanitaria con el objetivo",
)

CAP = r'[A-ZÁÉÍÓÚÑ]'


def _capitulo(l):
    """Índice del capítulo si la línea es un título de capítulo (en cualquiera de sus dos formas)."""
    s = l.strip()
    if not (s.startswith('#') or s.startswith('**_')) or len(s) > 160:
        return None
    if re.match(r'^\*\*\d+\.\*\*', s):
        return None
    k = re.sub(r'[\s0-9]+', '', norm(re.sub(r'</?(mark|u)>', '', s)))
    return _CLAVE.get(k)


def _capital(l):
    """«l Frente … de **E** los …» → «El Frente … de los …»."""
    m = re.search(r'(\w)- \*\*(' + CAP + r')\*\* (\w)', l)
    if m:
        letra = m.group(2)
        l = l[:m.start()] + m.group(1) + m.group(3) + l[m.end():]
    else:
        m = re.search(r' \*\*(' + CAP + r')\*\* ', l) or re.search(r' (' + CAP + r') ', l)
        if not m:
            return None
        letra = m.group(1)
        l = l[:m.start()] + ' ' + l[m.end():]
    return letra + l


def limpiar(lineas):
    # índice
    i = next(i for i, l in enumerate(lineas) if 'ÍNDICE' in l)
    j = i + 1
    while j < len(lineas) and (not lineas[j].strip() or lineas[j].startswith('|')):
        j += 1
    lineas = lineas[:i] + lineas[j:]

    out = ['# Recuperar España. Programa político', '']
    vistos = set()
    capitales = 0
    tras_titulo = False
    for l in lineas:
        s = l.strip()
        if not s:
            out.append(l)
            continue
        c = _capitulo(s)
        if c is not None:
            if c not in vistos:
                vistos.add(c)
                out.append(f'## {c + 1:02d}. {CAPS[c]}')
            tras_titulo = True
            continue
        # letra capital del primer párrafo del capítulo (en Cultura va tras la cita)
        if tras_titulo and re.match(r'^[a-záéíóúñ]', s):
            r = _capital(s)
            if r is None:
                raise ValueError(f'capital no encontrada: {s[:80]}')
            out.append(r)
            capitales += 1
            tras_titulo = False
            continue
        if tras_titulo and not s.startswith('_'):
            tras_titulo = False
        if re.match(r'^#+\s*Medidas:\s*$', s):
            out.append('Medidas:')
            continue
        m = re.match(r'^\*\*(\d+)\.\*\*\s*(.*)$', s)
        if m:
            out.append(f'{m.group(1)}. {m.group(2)}')
            continue
        if s.startswith(SANIDAD_SIN_NUM):
            out.append('- ' + s)
            continue
        # punto final suelto en negrita: «gran capital **.**»
        l = re.sub(r'\s*\*\*([.,;:])\*\*', r'\1', l)
        out.append(l)
    if len(vistos) != len(CAPS) or capitales != len(CAPS):
        raise ValueError(f'capítulos {len(vistos)}, capitales {capitales}')
    return out

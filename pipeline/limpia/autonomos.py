"""Limpieza propia del «Programa político 2026» del Partido Autónomos (15 páginas, 100 propuestas).

Estructura del PDF:
- portada con título, subtítulo y lema; «Manifiesto y principios rectores 2026» con una tabla de
  tres pilares (p. 1);
- seis bloques («BLOQUE I · …») con las 100 propuestas numeradas seguidas. Cada propuesta tiene
  un título en negrita, un párrafo y un párrafo «Viabilidad:» en cursiva.
- Cabecera repetida «PARTIDO AUTÓNOMOS · PROGRAMA POLÍTICO 2026 | ELECCIONES GENERALES 29N» y pie
  «Programa Electoral Actualizado 2026 · …» (este último ya no sale en la conversión).

Cada propuesta queda como «N. **Título** — texto» y su viabilidad como subpunto
«  - **Viabilidad:** _…_».
"""
import re
from clean import norm

BLOQUES = {
    'I': 'Las 10 propuestas estrella de campaña 2026',
    'II': 'Fiscalidad justa, energía y reducción de cargas',
    'III': 'Empleo, Seguridad Social y crecimiento empresarial',
    'IV': 'Regeneración democrática, justicia y eficiencia del Estado',
    'V': 'Sanidad, educación, vivienda y bienestar social',
    'VI': 'Infraestructuras, sector primario, movilidad y sostenibilidad',
}

DROP = (
    r'^PARTIDO AUTÓNOMOS · PROGRAMA POLÍTICO 2026 \| ELECCIONES GENERALES 29N$',
)


def limpiar(lineas):
    lineas = [l.strip() for l in lineas]
    lineas = [l for l in lineas if l and not any(re.match(r, l) for r in DROP)]
    out = []
    i = 0
    esperado = 1
    while i < len(lineas):
        s = lineas[i]
        if s.startswith('# **PARTIDO AUTÓNOMOS PROGRAMA POLÍTICO 2026'):
            out += ['# Programa político 2026', '']
            i += 1; continue
        if norm(s) == 'manifiesto y principios rectores 2026':
            out += ['## Manifiesto y principios rectores 2026', '']
            i += 1; continue
        # tabla de los tres pilares: la conversión parte en dos filas la última fila de la tabla
        if s.startswith('|'):
            filas = []
            while i < len(lineas) and lineas[i].startswith('|'):
                filas.append([c.strip() for c in lineas[i].strip('|').split('|')]); i += 1
            assert len(filas) == 5 and filas[1][0] == '---', filas
            ultima = [f'{a} {b}' for a, b in zip(filas[3], filas[4])]
            for f in (filas[0], filas[1], filas[2], ultima):
                out.append('|' + '|'.join(f) + '|')
            out.append('')
            continue
        m = re.match(r'^#+\s*\*\*BLOQUE ([IVX]+) · (.+?)\*\*$', s)
        if m:
            b = BLOQUES[m.group(1)]
            assert norm(b) == norm(m.group(2)), s
            out += [f'## Bloque {m.group(1)} · {b}', '']
            i += 1; continue
        m = re.match(r'^#+\s*\*\*(\d{2,3})\. (.+?)\*\*$', s)
        if m:
            n = int(m.group(1))
            assert n == esperado, (n, esperado)
            esperado += 1
            titulo = m.group(2)
            cuerpo = lineas[i + 1]
            assert not cuerpo.startswith(('#', '**Viabilidad')), cuerpo
            viab = None
            if '**Viabilidad:**' in cuerpo:            # propuesta 98: viabilidad en la misma línea
                cuerpo, viab = cuerpo.split(' **Viabilidad:**', 1)
                viab = '**Viabilidad:**' + viab
                i += 2
            else:
                viab = lineas[i + 2]
                assert viab.startswith('**Viabilidad:**'), viab
                i += 3
            out += [f'{m.group(1)}. **{titulo}** — {cuerpo}', '', f'  - {viab}', '']
            continue
        if s.startswith('#'):
            raise ValueError(f'título inesperado: {s}')
        out += [s, '']
        i += 1
    assert esperado == 101, esperado
    return out

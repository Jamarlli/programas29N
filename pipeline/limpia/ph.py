"""Limpieza propia del programa del Partido Humanista (Elecciones generales 29N 2026, 31 páginas).

Estructura del PDF:
- p. 1: portada con el logo y «ELECCIONES GENERALES 2026» (título del Markdown);
- pp. 2-3: «EL SENTIDO DE NUESTRA PROPUESTA POLÍTICA» (introducción, con una cita en cursiva);
- once capítulos numerados «N. TÍTULO» (pp. 4-27). Casi todos llevan debajo un lema subrayado
  («El reparto de la riqueza como herramienta de igualdad social») y un apartado «Diagnóstico y
  datos de partida»; el 10 tiene un apartado «Modelo de Estado»;
- «MEMORIA DE FINANCIACIÓN GLOBAL Y COHERENCIA FISCAL» con dos tablas de datos (pp. 28-30);
- «EPÍLOGO» (p. 31).
Cabecera repetida: el logo «partidohumanista» (imagen; no llega al bruto). No hay índice.

Las propuestas son viñetas «• Propuesta N: Título» (la numeración empieza en cada capítulo)
seguidas de uno o varios párrafos y, en la RBUI, de subviñetas «○». La conversión pierde a veces
la viñeta y deja el título y el texto en líneas o párrafos distintos: cada propuesta queda como un
punto «- **Propuesta N: Título** texto…» con sus párrafos unidos y las subviñetas como subpuntos.
Lemas → «###»; «Diagnóstico y datos de partida» y «Modelo de Estado» → «####»; las tablas
son de datos y se quedan como tablas (sin los saltos «<br>» de las celdas).
"""
import re

VINETA = '[-●•\uf0b7]'   # \uf0b7: viñeta de la fuente Symbol que la conversión deja como texto
PROPUESTA = re.compile(rf'^(?:{VINETA}\s*)?\*\*Propuesta \d+:')


def frase(t):
    """«ECONOMÍA Y EMPLEO» -> «Economía y empleo»."""
    t = t.strip().strip('*').strip()
    t = t.lower()
    return t[:1].upper() + t[1:]


def celda(c):
    c = c.strip()
    partes = [p.strip() for p in c.split('<br>')]
    if all(p.startswith('**') and p.endswith('**') for p in partes if p):
        partes = [p.strip('*') for p in partes]
    return ' '.join(p for p in partes if p)


def limpiar(lineas):
    b = [l.strip() for l in lineas]
    b = [l for l in b if l]

    out = []
    i = 0
    tras_capitulo = False
    while i < len(b):
        s = b[i]
        # --- portada ---
        if s == '# ELECCIONES':
            assert b[i + 1] == '# GENERALES 2026', b[i + 1]
            out += ['# Elecciones generales 2026', '']
            i += 2; continue
        # --- capítulos ---
        m = re.match(r'^#+\s*(?:\*\*)?(\d+)\. (.+?)(?:\*\*)?$', s)
        if m:
            out += [f'## {m.group(1)}. {frase(m.group(2))}', '']
            tras_capitulo = True
            i += 1; continue
        if s in ('### EL SENTIDO DE NUESTRA PROPUESTA POLÍTICA',
                 '#### MEMORIA DE FINANCIACIÓN GLOBAL Y COHERENCIA FISCAL', '## EPÍLOGO'):
            out += ['## ' + frase(s.lstrip('# ')), '']
            tras_capitulo = False
            i += 1; continue
        # --- lema subrayado bajo el título del capítulo ---
        if tras_capitulo:
            tras_capitulo = False
            m = re.match(r'^(?:#+\s*)?\*\*([^*]+)\*\*$', s)
            if m:
                out += ['### ' + m.group(1).strip(), '']
                i += 1; continue
        if s in ('##### **Diagnóstico y datos de partida**', '###### **Modelo de Estado**'):
            out += ['#### ' + s.lstrip('# ').strip('*'), '']
            i += 1; continue
        if s.startswith('##### **Tabla '):
            out += ['### ' + s.lstrip('# ').strip('*'), '']
            i += 1; continue
        if s.startswith('#'):
            raise ValueError(f'título inesperado: {s}')
        # --- tablas de datos ---
        if s.startswith('|'):
            while i < len(b) and b[i].startswith('|'):
                celdas = b[i].strip('|').split('|')
                out.append('|' + '|'.join(celda(c) for c in celdas) + '|')
                i += 1
            out.append('')
            continue
        # --- totales bajo la última tabla: dos líneas en el PDF ---
        if s.startswith('**TOTAL INGRESOS'):
            a, c = s.split(' **TOTAL INVERSIONES', 1)
            out += [a, '', '**TOTAL INVERSIONES' + c, '']
            i += 1; continue
        # --- propuestas ---
        if PROPUESTA.match(s):
            texto = re.sub(rf'^{VINETA}\s*', '', s)
            subs = []
            i += 1
            while i < len(b) and not b[i].startswith(('#', '|')) and not PROPUESTA.match(b[i]):
                if b[i].startswith('- '):
                    subs.append('  - ' + b[i][2:].strip())
                else:
                    assert not subs, ('párrafo tras las subviñetas', b[i][:50])
                    texto += ' ' + b[i]
                i += 1
            out += ['- ' + texto, '']
            for x in subs:
                out += [x, '']
            continue
        assert not re.match(VINETA, s), s
        out += [s, '']
        i += 1

    # espacio que mete la conversión entre el cierre de la negrita y la puntuación
    out = [re.sub(r'\*\* +(_?[,.;:])', r'**\1', l) for l in out]
    return out

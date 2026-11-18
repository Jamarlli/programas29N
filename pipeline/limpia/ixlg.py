"""Limpieza propia del programa de Iniciativa por La Gomera (Senado, 29N 2026, 11 páginas).

Estructura del PDF:
- p. 1: portada («PROGRAMA ELECTORAL / AL SENADO / Elecciones 29N», el candidato, el lema «DE AQUÍ,
  COMO TÚ.» y la web): queda solo el título;
- pp. 2-10: cabecera «PROGRAMA ELECTORAL / SENADO | 29N» y pie «UN ESCAÑO. UNA ISLA.» con el número
  de página (la conversión ya no los saca). Cada página lleva arriba una etiqueta verde de bloque
  («NUESTRA CANDIDATURA», «COMPROMISOS PARA LA GOMERA», «UNA ECONOMÍA QUE TE AYUDE A VIVIR»,
  «UNA ISLA HABITABLE, PRODUCTIVA Y CUIDADA», «DERECHOS, CUIDADOS Y UNA REPRESENTACIÓN ÚTIL») que se
  repite en las dos páginas de cada bloque: pasa a «##» la primera vez y se quita al repetirse.
  Los títulos grandes de página son los capítulos («###»); seis llevan número 01–06 (la conversión
  lo mete en medio del título, o lo pierde en el 02): «### 01. …». Las medidas van numeradas 01, 02…
  en cada capítulo: «01. …». El bloque de economía (pp. 5-6) es un único texto expositivo sobre el
  REF marcado «01»: se deja como párrafos.
- p. 11: contraportada (foto de la candidatura, QR, lemas «UNA CANDIDATURA COMO TÚ.», «ESCAÑO NO ES EL
  FIN. ES UNA HERRAMIENTA PARA LA ISLA.», «UN ESCAÑO. UNA ISLA. DE AQUÍ, COMO TÚ.» y la web): se quita.
"""
import re

TITULO = '# Programa electoral al Senado'

BLOQUES = {
    'NUESTRA CANDIDATURA': 'Nuestra candidatura',
    'COMPROMISOS PARA LA GOMERA': 'Compromisos para La Gomera',
    'UNA ECONOMÍA QUE TE AYUDE A VIVIR': 'Una economía que te ayude a vivir',
    'UNA ISLA HABITABLE, PRODUCTIVA Y CUIDADA': 'Una isla habitable, productiva y cuidada',
    'DERECHOS, CUIDADOS Y UNA REPRESENTACIÓN ÚTIL': 'Derechos, cuidados y una representación útil',
}

CAPITULOS = {
    'EL SENTIDO DE LA CANDIDATURA': 'El sentido de la candidatura',
    'VIVIENDA Y 01 DERECHO A QUEDARSE': '01. Vivienda y derecho a quedarse',
    'MOVILIDAD Y COSTE DE LA INSULARIDAD': '02. Movilidad y coste de la insularidad',
    'UNA ECONOMÍA AL SERVICIO DE LA CIUDADANÍA, NO DE UNOS POCOS.':
        'Una economía al servicio de la ciudadanía, no de unos pocos.',
    'PUEBLOS VIVOS, 03 EMPLEO Y ECONOMÍA LOCAL': '03. Pueblos vivos, empleo y economía local',
    'AGUA, ENERGÍA Y 04 NATURALEZA PROTEGIDA': '04. Agua, energía y naturaleza protegida',
    'CUIDADOS, SALUD Y 05 SERVICIOS CERCANOS': '05. Cuidados, salud y servicios cercanos',
    'UN ESCAÑO CERCANO 06 Y CON CUENTAS CLARAS': '06. Un escaño cercano y con cuentas claras',
}


def limpiar(lineas):
    b = [l.strip() for l in lineas]
    b = [l for l in b if l]

    def txt(l):
        return re.sub(r'^#+\s*', '', l).replace('**', '').strip()

    # portada: todo lo anterior a la primera etiqueta de bloque
    i = b.index('**NUESTRA CANDIDATURA**')
    b = b[i:]
    # contraportada (p. 11)
    j = b.index('### **UNA CANDIDATURA COMO TÚ.**')
    b = b[:j]

    out, vistos = [TITULO, ''], set()
    for l in b:
        t = txt(l)
        if not l.startswith('#') and t in BLOQUES:
            if t not in vistos:
                vistos.add(t)
                out += ['## ' + BLOQUES[t], '']
            continue
        if l.startswith('#'):
            assert t in CAPITULOS, l
            out += ['### ' + CAPITULOS[t], '']
            continue
        m = re.match(r'^-\s+\*\*(\d\d)\*\*\s+(.*)$', l)
        if m:                                   # medida numerada
            out += [f'{m.group(1)}. {m.group(2)}', '']
            continue
        m = re.match(r'^\*\*01\*\*\s+(Durante décadas.*)$', l)
        if m:                                   # texto del REF, marcado «01» (único punto)
            out += [m.group(1), '']
            continue
        assert not re.match(r'^(-|\*\*\d)', l), l
        out += [l, '']
    return out

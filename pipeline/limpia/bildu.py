"""Limpieza propia del programa de EH Bildu «Posible egin. Garantía y derechos» (29N 2026, versión en castellano).

Estructura del PDF: portada, índice, «Nuestro compromiso» (introducción sin número) y tres capítulos
numerados («1. Derechos y libertades», «2. Reconocimiento de Euskal Herria como nación y autogobierno»,
«3. Paz y convivencia») con apartados N.N y subapartados N.N.N (en versalitas en el PDF).
pymupdf4llm deja los capítulos como «#», los apartados como «##» y los subapartados como «###»; se suben
un nivel (##, ###, ####) y los subapartados se pasan a minúsculas con la redacción del cuerpo (que en
3.2.7-3.2.9 no coincide con la del índice). Dentro de 1.5.1 hay tres rótulos en negrita («Ciudadanía»,
«Profesionales», «Gobernanza») que quedan como «#####».
Las medidas son las viñetas «•» del PDF; los subpuntos «»» van sangrados. El resto es exposición.
No hay cabeceras, pies ni números de página en el bruto (la conversión ya los omite).
"""
import re
from clean import plain, drop_range

TITULO = '# Posible egin. Garantía y derechos'

# Subapartados N.N.N (en versalitas en el PDF): número -> título con la redacción del cuerpo
SUB = {
    '1.5.1': 'Salud, derechos colectivos y bienestar comunitario',
    '1.5.2': 'Educación',
    '1.5.3': 'Cuidados',
    '1.5.4': 'Administración pública',
    '1.9.1': 'Energía y clima',
    '1.9.2': 'Industria y transformación productiva',
    '1.9.3': 'Primer sector, medio rural y territorio',
    '1.9.4': 'Movilidad y transporte',
    '1.9.5': 'Rehabilitación energética y edificación',
    '1.9.6': 'Fiscalidad y financiación de la transición ecosocial',
    '1.10.1': 'LGTBIQ+',
    '3.2.1': 'Por los pueblos, contra las injerencias',
    '3.2.2': 'Por la paz, contra las guerras',
    '3.2.3': 'Seguridad europea, seguridad indivisible',
    '3.2.4': 'No a la OTAN',
    '3.2.5': 'Bases fuera, Bardeak herriarentzat',
    '3.2.6': 'Desarme nuclear',
    '3.2.7': 'Frente al genocidio y la ocupacion, libertad para Palestina',
    '3.2.8': 'En defensa del pueblo saharaui y su derecho a la autodeterminación',
    '3.2.9': 'Acabar con el bloqueo contra Cuba y su pueblo',
    '3.2.10': 'Por el multilateralismo y el derecho internacional',
}

ROTULOS = ('Ciudadanía', 'Profesionales', 'Gobernanza')


def limpiar(lineas):
    # portada (texto de imagen «Garantía y derechos») e índice: hasta «Nuestro compromiso»
    ini = next(i for i, l in enumerate(lineas) if l.startswith('#') and plain(l) == 'Nuestro compromiso')
    lineas = [TITULO, ''] + lineas[ini:]

    out = []
    for l in lineas[2:]:
        s = l.strip()
        if s.startswith('#'):
            t = plain(s).rstrip(' .:').strip()
            m = re.match(r'^(\d+(?:\.\d+)*)\.?\s+(.+)$', t)
            if t == 'Nuestro compromiso':
                out.append('## Nuestro compromiso'); continue
            if t in ROTULOS:
                out.append('##### ' + t); continue
            if m:
                num, txt = m.group(1), m.group(2)
                prof = num.count('.') + 1
                if prof == 1:
                    out.append(f'## {num}. {txt}'); continue
                if prof == 2:
                    out.append(f'### {num}. {txt}'); continue
                out.append(f'#### {num} {SUB[num]}'); continue
            raise ValueError(f'título no previsto: {s}')
        # subpuntos «»» del PDF (a veces la conversión los deja en la columna 0)
        m = re.match(r'^\s*-\s+»\s*(.*)$', l)
        if m:
            out.append('  - ' + m.group(1)); continue
        # en 2.5 el último punto perdió la viñeta en el PDF; es una propuesta más de la lista
        if s.startswith('Reservas de cuotas para la diversidad'):
            out.append('- ' + s); continue
        out.append(l)
    return [TITULO, ''] + out

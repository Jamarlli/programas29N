"""Limpieza propia del programa del Partido Feministas al Congreso (PFAC, generales 29N 2026).

Estructura del PDF (170 pp.): portada (p. 1), índice (pp. 2-3), «Introducción», y seis bloques
«BLOQUE N. TÍTULO» (0 a 5) con apartados en mayúsculas; «Vivienda y transporte con perspectiva
feminista» tiene tres subapartados (Vivienda digna, Planificación urbana, Transporte sostenible).
Las 50 propuestas principales van como «MEDIDA N. TEXTO» (en verde) y, además, cada apartado tiene
listas numeradas propias (1., 2., …) con viñetas «-» y, en dos sitios, viñetas «¬» de tercer nivel.
La contraportada repite el lema «VOTA / TU VOTO ÚTIL…». Cabeceras y pies (lema, «PÁG. N») no
llegan al bruto.

Daños de la conversión que se reparan aquí:
- la sangría de las listas: viñetas de segundo nivel que quedaron en la columna 0, listas
  numeradas de primer nivel que quedaron sangradas y párrafos que quedaron como viñeta;
- las «MEDIDA N.» que perdieron la viñeta y las negritas con espacio antes de los dos puntos;
- tres guiones de fin de línea que eran del texto y la conversión borró;
- párrafos cortados por el salto de página cuando la continuación empieza en mayúscula o cifra,
  y dos párrafos que en el PDF siguen dentro de una viñeta (pp. 49 y 100).
"""
import re
from clean import plain

TITULO = '# Programa electoral elecciones generales 29 nov 2026'

# Título en mayúsculas del PDF -> (nivel, título en minúsculas normales)
TITULOS = {
    'INTRODUCCIÓN: UN PROGRAMA DE IZQUIERDAS Y FEMINISTA PARA TRANSFORMAR LA SOCIEDAD':
        (2, 'Introducción: un programa de izquierdas y feminista para transformar la sociedad'),
    'BLOQUE 0. LA AGENDA FEMINISTA: CUESTIÓN Y PRIORIDAD DE ESTADO':
        (2, 'Bloque 0. La agenda feminista: cuestión y prioridad de Estado'),
    'ERRADICACIÓN DE LA VIOLENCIA MACHISTA': (3, 'Erradicación de la violencia machista'),
    'ABOLICIÓN DE LA PROSTITUCIÓN': (3, 'Abolición de la prostitución'),
    'ABOLICION DE LA PORNOGRAFÍA: PRIORIDAD DE ESTADO': (3, 'Abolicion de la pornografía: prioridad de Estado'),
    'ABOLICIÓN DE LA EXPLOTACIÓN REPRODUCTIVA': (3, 'Abolición de la explotación reproductiva'),
    'ABOLICIÓN DEL GÉNERO COMO CATEGORÍA JURÍDICA': (3, 'Abolición del género como categoría jurídica'),
    'BLOQUE 1. HACIA UN ESTADO QUE INCORPORE LA PERSPECTIVA FEMINISTA':
        (2, 'Bloque 1. Hacia un Estado que incorpore la perspectiva feminista'),
    'DERECHOS FUNDAMENTALES': (3, 'Derechos fundamentales'),
    'MEMORIA DEMOCRÁTICA SIN OLVIDOS NI BORRADOS': (3, 'Memoria democrática sin olvidos ni borrados'),
    'EFICACIA DE LA ADMINISTRACIÓN PÚBLICA': (3, 'Eficacia de la Administración pública'),
    'ÉTICA FEMINISTA EN LAS INSTITUCIONES PÚBLICAS': (3, 'Ética feminista en las instituciones públicas'),
    'DERECHOS LGB': (3, 'Derechos LGB'),
    'POLÍTICA LINGÜÍSTICA': (3, 'Política lingüística'),
    'POLÍTICAS MIGRATORIAS LABORALES': (3, 'Políticas migratorias laborales'),
    'POLÍTICAS MIGRATORIAS DERIVADAS DEL DERECHO AL ASILO': (3, 'Políticas migratorias derivadas del derecho al asilo'),
    'EL INGRESO MÍNIMO VITAL': (3, 'El ingreso mínimo vital'),
    'BLOQUE 2. ECONOMÍA Y EMPLEO PARA EL BIENESTAR': (2, 'Bloque 2. Economía y empleo para el bienestar'),
    'ECONOMÍA': (3, 'Economía'),
    'MERCADO LABORAL JUSTO CON PERSPECTIVA FEMINISTA': (3, 'Mercado laboral justo con perspectiva feminista'),
    'LA MUJER EN EL MEDIO RURAL': (3, 'La mujer en el medio rural'),
    'CIENCIA E INNOVACIÓN PARA LA IGUALDAD': (3, 'Ciencia e innovación para la igualdad'),
    'HACIA UN SISTEMA FISCAL JUSTO Y EQUITATIVO': (3, 'Hacia un sistema fiscal justo y equitativo'),
    'BLOQUE 3. SERVICIOS PÚBLICOS GARANTIZADOS Y DE CALIDAD': (2, 'Bloque 3. Servicios públicos garantizados y de calidad'),
    'SANIDAD PÚBLICA Y UNIVERSAL': (3, 'Sanidad pública y universal'),
    'EDUCACIÓN PÚBLICA, LIBRE Y FEMINISTA': (3, 'Educación pública, libre y feminista'),
    'SISTEMA PÚBLICO DE PENSIONES DIGNO, JUSTO Y CON PERSPECTIVA FEMINISTA':
        (3, 'Sistema público de pensiones digno, justo y con perspectiva feminista'),
    'SERVICIOS SOCIALES GARANTES DEL BIENESTAR DE TODA LA CIUDADANÍA':
        (3, 'Servicios sociales garantes del bienestar de toda la ciudadanía'),
    'DISCAPACIDAD Y DEPENDENCIA: INCLUSIÓN Y AUTONOMÍA': (3, 'Discapacidad y dependencia: inclusión y autonomía'),
    'VIVIENDA Y TRANSPORTE CON PERSPECTIVA FEMINISTA': (3, 'Vivienda y transporte con perspectiva feminista'),
    'VIVIENDA DIGNA': (4, 'Vivienda digna'),
    'PLANIFICACIÓN URBANA': (4, 'Planificación urbana'),
    'TRANSPORTE SOSTENIBLE Y MOVILIDAD INTELIGENTE': (4, 'Transporte sostenible y movilidad inteligente'),
    'CULTURA FEMINISTA PARA FORTALECER LA DEMOCRACIA': (3, 'Cultura feminista para fortalecer la democracia'),
    'DEPORTE FEMINISTA: SALUD, VALORES E IGUALDAD': (3, 'Deporte feminista: salud, valores e igualdad'),
    'JUSTICIA FEMINISTA Y GARANTÍAS PENALES SIN SESGOS PATRIARCALES':
        (3, 'Justicia feminista y garantías penales sin sesgos patriarcales'),
    'BLOQUE 4. UNA SOLA SALUD HUMANA, ANIMAL Y AMBIENTAL': (2, 'Bloque 4. Una sola salud humana, animal y ambiental'),
    'ECOFEMINISMO CRÍTICO Y TRANSICIÓN ECOLÓGICA': (3, 'Ecofeminismo crítico y transición ecológica'),
    'ALIMENTACIÓN SALUDABLE Y SOBERANÍA ALIMENTARIA': (3, 'Alimentación saludable y soberanía alimentaria'),
    'UN MEDIOAMBIENTE SANO COMO GARANTÍA DE SALUD': (3, 'Un medioambiente sano como garantía de salud'),
    'JUSTICIA PARA LA SEGURIDAD CLIMÁTICA': (3, 'Justicia para la seguridad climática'),
    'DERECHO AL AGUA Y LA ENERGÍA, SUMINISTROS ESENCIALES PARA LA VIDA':
        (3, 'Derecho al agua y la energía, suministros esenciales para la vida'),
    'COMPROMISO FEMINISTA CON LA SALUD Y EL BIENESTAR ANIMAL': (3, 'Compromiso feminista con la salud y el bienestar animal'),
    'BLOQUE 5. UN ESTADO FEMINISTA POR LA PAZ': (2, 'Bloque 5. Un Estado feminista por la paz'),
    'SITUACIÓN INTERNACIONAL DE LAS MUJERES': (3, 'Situación internacional de las mujeres'),
    'UNA POLITICA EXTERIOR FEMINISTA POR LA PAZ': (3, 'Una politica exterior feminista por la paz'),
    'DEMOCRACIA FEMINISTA EN LA UNIÓN EUROPEA': (3, 'Democracia feminista en la Unión Europea'),
    'SOLIDARIDAD ANTE LA EMERGENCIA CLIMÁTICA': (3, 'Solidaridad ante la emergencia climática'),
    'MODELO DE ESTADO': (3, 'Modelo de Estado'),
}

# Párrafos cortados por el salto de página que join_broken no une (continuación en mayúscula
# o cifra, o primera parte acabada en «;»):
# (final de la primera línea, arranque de la segunda)
CORTES = (
    ('que se producen en nuestro país;', 'o en el extranjero por personas residentes'),  # sigue en la p. 11
    ('Administración General del', 'Estado (AGE) y de sus organismos'),
    ('fuerzas y cuerpos de seguridad del', 'Estado) en la lucha contra la homofobia'),
    ('un efecto embudo en una', 'Atención Primaria saturada'),
    ('IHAN (Iniciativa para la Humanización de la', 'Asistencia al Nacimiento y la Lactancia)'),
    ('Ley de Garantías y Acceso Universal a la', 'Justicia transformará el servicio público'),
    ('la normativa para el SDDR (Sistema de', 'Devolución y Retorno) que se ha debido'),
    ('coordinar con las', 'CCAA la redacción de los planes'),
    ('registrando más de', '290.00 casos anuales'),
    ('Así como la modificación del artículo', '135 de la Constitución'),
    ('la calidad del agua y la gestión de la escasez.', 'Potenciando la capacidad de diseñar'),  # viñeta «¬» que sigue en la p. 49
    ('en los currículos obligatorios del sistema educativo.', 'Esta medida se complementará con talleres'),  # párrafo dentro de la viñeta (p. 100)
)

# Guiones de fin de línea que la conversión borró aunque eran del texto (pp. 23, 149 y 161)
GUIONES = (
    ('acción positivaexclusivamente', 'acción positiva- exclusivamente'),  # cierre de inciso «-en calidad de …-»
    ('conflicto humanovida silvestre', 'conflicto humano-vida silvestre'),
    ('poder patriarcalcapitalistas', 'poder patriarcal-capitalistas'),
)

# Párrafos que la conversión dejó como viñeta
NO_LISTA = ('Además, consideramos necesario:', 'Y, además:')

# Subpuntos numerados de la MEDIDA 24 (sangrados y en verde dentro de la medida, p. 72)
SUB_MEDIDA_24 = ('Sanidad universal que incluya', 'Un Sistema Educativo que priorice',
                 'Servicios Sociales sin las clamorosas', 'Parque público de viviendas en alquiler',
                 'Transporte público suficiente, económico')


def limpiar(lineas):
    L = [l.rstrip() for l in lineas]

    # portada: los dos títulos del principio; índice hasta la introducción
    ini = next(i for i, l in enumerate(L) if l.startswith('### **INTRODUCCIÓN'))
    assert L[0].startswith('# **VOTA') and L[2].startswith('# **PARTIDO FEMINISTAS'), L[:3]
    L = [TITULO, ''] + L[ini:]
    # contraportada: lema final
    fin = max(i for i, l in enumerate(L) if l.startswith('# **VOTA'))
    assert all('VOT' in l or not l.strip() for l in L[fin:]), L[fin:]
    L = L[:fin]

    out = []
    for l in L:
        s = l.strip()
        h = re.match(r'^(#+)\s+(.*)$', l)
        if h and l is not L[0] and l != TITULO:
            t = plain(h.group(2))
            if t == 'Por todo ello el PFAC propone:':
                out.append(t)
                continue
            assert t in TITULOS, t
            n, titulo = TITULOS[t]
            out.append('#' * n + ' ' + titulo)
            continue
        sang = len(l) - len(l.lstrip(' '))
        if s.startswith('- '):
            cuerpo = s[2:].strip()
            if cuerpo.startswith('MEDIDA '):
                out.append('- ' + cuerpo)
            elif cuerpo in NO_LISTA:
                out.append(cuerpo)
            elif re.match(r'^\d+\. ', cuerpo):  # «- 10. Actualizar…»: punto numerado con guion de más
                out.append(cuerpo)
            elif cuerpo.startswith('¬ '):  # tercer nivel
                out.append('    - ' + cuerpo[2:])
            else:  # viñeta de segundo nivel (en la columna 0 o sangrada)
                out.append('  - ' + cuerpo)
            continue
        m = re.match(r'^(\d+)\. (.*)$', s)
        if m and sang:
            if m.group(2).startswith(SUB_MEDIDA_24):
                out.append('  - ' + s)
            else:  # punto numerado de primer nivel que quedó sangrado
                out.append(s)
            continue
        if s.startswith('MEDIDA '):
            out.append('- ' + s)
            continue
        out.append(s if s else '')

    for malo, bueno in GUIONES:
        k = [i for i, l in enumerate(out) if malo in l]
        assert len(k) == 1, (malo, k)
        out[k[0]] = out[k[0]].replace(malo, bueno)

    # negritas con espacio antes de la puntuación: «**ERRADICAR …** : Garantizar»
    out = [re.sub(r'\*\* +([,.;:])', r'**\1', l) for l in out]

    # párrafos cortados por el salto de página
    for fin_a, ini_b in CORTES:
        a = [i for i, l in enumerate(out) if l.rstrip().endswith(fin_a)]
        b = [i for i, l in enumerate(out) if l.strip().startswith(ini_b)]
        assert len(a) == 1 and len(b) == 1, (fin_a, a, ini_b, b)
        a, b = a[0], b[0]
        assert a < b and all(not x.strip() for x in out[a + 1:b]), (fin_a, ini_b)
        out[a] = out[a].rstrip() + ' ' + out[b].strip()
        out[a + 1:b + 1] = [''] * (b - a)

    return out

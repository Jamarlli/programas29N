"""Limpieza propia del programa de Soria ¡Ya! (Elecciones generales 29N 2026, cartel de 1 página).

Estructura del PDF: un cartel a tres columnas con el rótulo grande «Soria ¡Sí!» arriba (es dibujo, no
texto: la conversión no lo saca), doce bloques temáticos con título en rojo y mayúsculas, y al pie el
lema «Del Olvido al Futuro» y «Tu voto útil para Soria» (este también es dibujo). Al final de la
tercera columna, en rojo y más grande, «SI EL 29 N, SORIA ¡YA! CONSIGUE REPRESENTACIÓN, ESTO ES LO
QUE EXIGIREMOS».

El cartel no tiene un título de programa: se usa el rótulo «Soria ¡Sí!», que es el titular de la
página. La frase «Si el 29 N…, esto es lo que exigiremos» y el lema del pie presentan el conjunto de
exigencias y no son de ningún bloque: van como entrada, tras el título (si fueran al final quedarían
dentro del último bloque).

La conversión mezcla las columnas (títulos de un bloque seguidos del texto de otro, párrafos de
la columna 2 partidos y pegados con los de la 3): se rehace el orden columna a columna, comprobado
con el PDF. Cada bloque es un «##» y cada párrafo del bloque (una exigencia) un «- »; los párrafos que
la conversión fundió en uno («Impulso de las conexiones… / Modernización… / Electrificación…»,
«Reapertura… / Estación de AVE…») se separan donde los separa el PDF.
"""
import re

TITULO = '# Soria ¡Sí!'

# (título en el PDF, título limpio, arranques de sus párrafos en el orden del PDF)
BLOQUES = [
    # columna 1
    ('PLAN EXTRAORDINARIO DE 10 AÑOS CONTRA LA DESPOBLACIÓN',
     'Plan extraordinario de 10 años contra la despoblación',
     ['Impulsar un **programa específico', 'Ayudas al funcionamiento']),
    ('CONECTIVIDAD DIGITAL PARA TODOS', 'Conectividad digital para todos',
     ['Acceso a **internet']),
    ('PLAN DE RELEVO GENERACIONAL', 'Plan de relevo generacional',
     ['Establecer **ayudas directas**']),
    ('PLAN DE VIVIENDA PARA ZONAS DESPOBLADAS', 'Plan de vivienda para zonas despobladas',
     ['**Impulsar un programa nacional']),
    ('IMPULSO A NUESTRO CAMPO, MONTES Y MEDIOAMBIENTE', 'Impulso a nuestro campo, montes y medioambiente',
     ['**Apoyo a agricultores', '**Aprovechamiento de nuestros recursos']),
    # columna 2
    ('AUTOVÍAS Y FERROCARRIL: ACABAR CON EL AISLAMIENTO DE SORIA',
     'Autovías y ferrocarril: acabar con el aislamiento de Soria',
     ['**Finalización de la A-11**', 'Impulso de las conexiones', 'Modernización integral',
      'Electrificación y doble vía', '**Reapertura**', 'Estación de AVE', 'Impulso del corredor ferroviario']),
    ('ENERGÍA DE SORIA PARA EL DESARROLLO DE SORIA', 'Energía de Soria para el desarrollo de Soria',
     ['No podemos seguir generando']),
    ('GARANTÍA DE SERVICIOS PÚBLICOS EN EL MEDIO RURAL', 'Garantía de servicios públicos en el medio rural',
     ['**Garantizar los servicios públicos']),
    ('EDUCACIÓN Y TALENTO: ESTUDIAR FUERA, VOLVER A SORIA', 'Educación y talento: estudiar fuera, volver a Soria',
     ['**Becas especiales']),
    # columna 3
    ('ACCESO SEGURO A LA SANIDAD', 'Acceso seguro a la sanidad',
     ['**Autovía Soria-Burgos:**']),
    ('IMPULSO LOGÍSTICO, INVERSIÓN, EMPRENDIMIENTO Y NÓMADAS DIGITALES',
     'Impulso logístico, inversión, emprendimiento y nómadas digitales',
     ['**Corregir el déficit', '**Establecer incentivos específicos**', 'Implantar una cuota reducida']),
    ('SORIA, SEDE DE ORGANISMOS PÚBLICOS', 'Soria, sede de organismos públicos',
     ['**Descentralización de organismos']),
]

LEMA = 'Del Olvido al Futuro'
EXIGIREMOS = 'SI EL 29 N, SORIA ¡YA! CONSIGUE REPRESENTACIÓN, ESTO ES LO QUE EXIGIREMOS'


def limpiar(lineas):
    b = [l.strip() for l in lineas]
    b = [l for l in b if l]
    # espacio que mete la conversión entre el cierre de la negrita y la puntuación
    b = [re.sub(r'\*\* +([,.;:])', r'**\1', l) for l in b]

    titulos = {re.sub(r'^#+\s*', '', l).replace('**', '').strip(): l for l in b if l.startswith('#')}
    parrafos = [l for l in b if not l.startswith('#')]

    def partir(ini, *cortes):
        """Parte el párrafo que empieza por `ini` antes de cada texto de `cortes`."""
        i = next(k for k, p in enumerate(parrafos) if p.startswith(ini))
        trozos, resto = [], parrafos[i]
        for c in cortes:
            n = resto.index(c)
            trozos.append(resto[:n].strip())
            resto = resto[n:]
        trozos.append(resto.strip())
        parrafos[i:i + 1] = trozos

    # columna 2: tres párrafos del PDF fundidos en uno
    partir('Impulso de las conexiones', 'Modernización integral', 'Electrificación y doble vía')
    # columna 2: «Reapertura…» y «Estación de AVE … directa a» | «**Madrid-Zaragoza-Barcelona.** Impulso del
    # corredor…» (la conversión parte la línea y mete en medio párrafos de la columna 3)
    partir('**Reapertura**', 'Estación de AVE')
    i = next(k for k, p in enumerate(parrafos) if p.startswith('Estación de AVE'))
    j = next(k for k, p in enumerate(parrafos) if p.startswith('**Madrid-Zaragoza-Barcelona.**'))
    ave, corredor = parrafos[j].split(' Impulso del corredor', 1)
    parrafos[i] = parrafos[i] + ' ' + ave
    parrafos[j] = 'Impulso del corredor' + corredor

    usados = set()

    def toma(ini):
        hits = [k for k, p in enumerate(parrafos) if p.startswith(ini)]
        assert len(hits) == 1, (ini, hits)
        assert hits[0] not in usados, ini
        usados.add(hits[0])
        return parrafos[hits[0]]

    out = [TITULO, '']
    assert EXIGIREMOS in titulos and LEMA in titulos, titulos
    # en el orden del PDF: la frase cierra la columna 3 y el lema está al pie
    out += ['**Si el 29 N, Soria ¡Ya! consigue representación, esto es lo que exigiremos**', '',
            '**' + LEMA + '**', '']
    del titulos[EXIGIREMOS]
    del titulos[LEMA]
    for pdf, limpio, inis in BLOQUES:
        del titulos[pdf]
        out += ['## ' + limpio, '']
        for ini in inis:
            out += ['- ' + toma(ini), '']
    assert not titulos, titulos
    assert len(usados) == len(parrafos), [p for k, p in enumerate(parrafos) if k not in usados]
    return out

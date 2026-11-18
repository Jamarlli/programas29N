"""Limpieza propia del programa de Teruel Existe (Elecciones generales 29N 2026, 15 páginas).

Estructura del PDF:
- p. 1: portada con el lema «Vamos a seguir defendiendo nuestra tierra.» («Faltaría más.» es imagen);
- p. 2: «Un programa para transformar Teruel», subtítulo «Ser pocos no resta derechos» y las cinco
  prioridades numeradas 01–05 en dos columnas (la conversión las mezcla: 01, 04, 02, 05, 03);
- pp. 3-15: título repetido «Propuestas» en cada página (se quita) y doce capítulos numerados
  («N. …»); los cinco primeros llevan encima la etiqueta «PRIORIDAD N» (se quita: repite el número
  del capítulo). Apartados «4.1.»–«4.3.» y subapartados sin número («Carreteras», «Agua del siglo
  XXI»…) pasan a «###». Las propuestas son viñetas «•» con arranque en negrita.

El texto va a dos columnas y la conversión desordena varios bloques: se recolocan (comprobado con
el PDF) y se unen los párrafos partidos por salto de columna o de página.
"""
import re

DROP = (
    r'^PROGRAMA ELECTORAL$',
    r'^#+\s*Propuestas$',
    r'^#+\s*\*\*PRIORIDAD \d\*\*$',
)


def limpiar(lineas):
    b = [l.strip() for l in lineas]
    b = [l for l in b if l and not any(re.match(r, l) for r in DROP)]

    def idx(ini):
        """Índice del único bloque que empieza por `ini` (tras quitar marcas de lista/título)."""
        hits = [i for i, l in enumerate(b) if re.sub(r'^(#+|[-•>])\s*', '', l).startswith(ini)]
        assert len(hits) == 1, (ini, hits)
        return hits[0]

    def unir(ini_a, ini_b):
        """Pega el bloque que empieza por ini_b al final del que empieza por ini_a y lo quita."""
        j = idx(ini_b)
        txt = re.sub(r'^-\s+', '', b.pop(j))
        i = idx(ini_a)
        b[i] = b[i] + ' ' + txt

    def mover(ini_desde, ini_hasta, ini_antes):
        """Mueve los bloques [ini_desde, ini_hasta] justo delante del bloque ini_antes."""
        i, j = idx(ini_desde), idx(ini_hasta)
        assert i <= j
        trozo = b[i:j + 1]
        del b[i:j + 1]
        k = idx(ini_antes)
        b[k:k] = trozo

    # p. 2: las cinco prioridades, en el orden de su número
    pri = {}
    for n in ('01', '02', '03', '04', '05'):
        i = next(i for i, l in enumerate(b) if re.match(rf'^(>|#+)\s*{n} \*\*', l))
        tit = re.sub(rf'^(>|#+)\s*{n} ', '', b[i])
        pri[n] = f'{int(n)}. {tit} {b[i + 1]}'
        del b[i:i + 2]
    k = idx('El resto del programa recoge')
    b[k:k] = [pri[n] for n in sorted(pri)]

    # p. 4→5: «… un plan de» | «empleo serio, …»
    unir('**Exigir contrapartidas.**', 'empleo serio, con seguimiento')
    # p. 5: final del «Nuevo Plan estatal…» (arriba de la columna derecha)
    unir('**Nuevo Plan estatal de actuación', 'despoblación, fijación de objetivos')
    # p. 5→6: segunda línea de la viñeta «Atención primaria»
    unir('**Atención primaria.**', 'Con medios adecuados, la primaria')
    # p. 6→7
    unir('**Sistema público de servicios sociales**', 'territorio. Asimismo, defenderemos')
    # p. 8: «Autovía A-40» está al pie de la columna izquierda; su final, arriba de la derecha
    unir('**Autovía A-40.**', 'las Cuencas Mineras, Alcañiz, Reus')
    mover('**Autovía A-40.**', '**Autovía A-40.**', '**Autovía A-25.**')
    # p. 9: «Puerto seco» y «Norte de Teruel» cierran la columna de «Ferrocarril»
    mover('**Puerto seco**', '**Norte de Teruel.**', '**Movilidad y conectividad**')
    # p. 10→11
    unir('**Una PAC más equilibrada.**', 'corregido. Pagar por lo que')
    unir('**Agua en Teruel.**', 'Mantenimiento y uso de la presa')
    # p. 11: «Montes, incendios y custodia del territorio» es la columna izquierda (capítulo 6)
    unir('**Custodia del territorio.**', 'acuerdos, compensaciones y medidas')
    mover('**Montes, incendios y custodia', '**Montes de socios.**', '**7. Economía y empleo')
    # p. 12
    unir('**Talento científico.**', 'programa de ciencia y cohesión')
    unir('**Centro Nacional de Diseño Contemporáneo', 'conservación y creación relacionados')
    # p. 14
    unir('**Protección ambiental.**', 'debe ser retribuido')
    # p. 15: la columna derecha sigue al capítulo 12
    i, j = idx('**Comportamiento de partidos'), idx('**Democracia de proximidad.**')
    trozo = b[i:j + 1]
    del b[i:j + 1]
    k = idx('**Parar la polarización**')
    assert k == len(b) - 1, b[k + 1:]
    b[k + 1:k + 1] = trozo

    out = []
    for l in b:
        if l.startswith('# Vamos a seguir'):
            out.append('# Vamos a seguir defendiendo nuestra tierra')
        elif l == '**TERUEL EXISTE. DESDE TERUEL PARA LOS Y LAS TUROLENSES**':
            out.append('**Teruel Existe. Desde Teruel para los y las turolenses**')
        elif l.startswith('## Un programa para'):
            out.append(l)
        elif l == '###### **Ser pocos no resta derechos**':
            out.append('### Ser pocos no resta derechos')
        elif l == '#### Nuestras cinco prioridades':
            out.append('### Nuestras cinco prioridades')
        elif re.match(r'^#+\s*\*\*\d{1,2}\. ', l):          # capítulo
            out.append('## ' + l.lstrip('# ').strip('*'))
        elif l.startswith('#'):                               # apartado (4.1., Carreteras…)
            t = l.lstrip('# ')
            assert t.startswith('**') and t.endswith('**'), l
            out.append('### ' + t.strip('*'))
        elif l.startswith(('- ', '• ')):
            out.append('- ' + l[2:].strip())
        else:
            out.append(l)
        out.append('')

    # negrita rota: «**Incentivos al alquile** r.»
    out = [l.replace('**Incentivos al alquile** r.', '**Incentivos al alquiler**.') for l in out]
    # espacio que mete la conversión entre el cierre de la negrita y la puntuación
    out = [re.sub(r'\*\* +([,.;:])', r'**\1', l) for l in out]
    return out

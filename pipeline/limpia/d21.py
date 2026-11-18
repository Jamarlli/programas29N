"""Limpieza propia del programa de Democracia para el Siglo 21 (d21), «La España que merecemos»
(Elecciones generales 29N 2026, 108 páginas).

Estructura del PDF (comprobada con las fuentes del PDF):
- p. 1: portada (título, «Programa Electoral · Elecciones Generales · 29N»; el subtítulo se quita);
- cinco capítulos, cada uno con una página-portada en letra enorme («ESPAÑA LIMPIA», «ESPAÑA
  RESUELVE», «ESPAÑA PROSPERA», «ESPAÑA CUIDA», «ESPAÑA LIDERA») -> «##», y una página de
  presentación con dos párrafos y unas viñetas-resumen (●), que se dejan pegadas al párrafo
  anterior (es exposición, no medidas);
- apartados en recuadro negro con letra amarilla -> «###». Suelen abrir con un cuadro «↪ …»
  de diagnóstico (párrafo; se quita la flecha);
- subapartados con el logo d21 en negrita de 13 pt -> «####».
La conversión pone casi todos los títulos como «######» sin distinguir niveles: el nivel sale de
la lista TITULOS (sacada del tamaño y color de letra del PDF). Cabecera repetida «España Limpia»
(y una «Infraestructuras y Crecimiento Sostenibles») y el pie «www.democracia21.es» se quitan.

Medidas: en «España Limpia» cada párrafo bajo un subapartado es un compromiso («Se crearán…»)
y pasa a «- ». Del capítulo 2 en adelante las medidas son párrafos con arranque en negrita
terminado en dos puntos («**Título:** texto») -> «- »; los párrafos sin título que siguen a una
medida la continúan y se pegan a ella en el mismo bloque (salvo los de SEPARAR, que son otra
medida). En subapartados sin títulos de medida, cada párrafo es una medida (salvo CONTINUA).
Las cuatro medidas numeradas del resumen de vivienda conservan su número («1. **…:**»).
"""
import re
from clean import norm

TERM = tuple('.:;!?)»"”…')

TITULO = '# La España que merecemos'

TITULOS = [
    (2, 'España limpia'),
    (3, 'No más redes clientelares'),
    (4, 'Punto y final al tsunami de asesores'),
    (4, 'Fuera cargos de carnet y delito de enchufismo'),
    (4, 'No más impuestos revolucionarios para los partidos políticos'),
    (3, 'Cortar de raíz la corrupción'),
    (4, 'Nuevos juzgados especializados en corrupción'),
    (4, 'El mismo control para el político que para el ciudadano'),
    (4, 'Fiscalía y Oficina Anticorrupción, más fuertes que nunca'),
    (4, 'Los corruptos no tendrán refugio'),
    (4, 'Los partidos políticos no saldrán impunes'),
    (4, 'Quien robe a lo público, no volverá nunca a lo público'),
    (3, 'No más repartos de sillones'),
    (4, 'Un Consejo General del Poder Judicial despolitizado'),
    (4, 'Una Fiscalía independiente'),
    (4, 'Unos organismos de control independientes'),
    (3, 'Punto y final a los aforamientos'),
    (4, 'Todos fuera'),
    (3, 'Devolver el poder al ciudadano'),
    (4, 'Escuchar será obligatorio'),
    (4, 'No más bloqueos'),
    (4, 'Si no trabajan, no cobran'),
    (4, 'No habrá Gobierno sin presupuestos'),
    (4, 'Menos promesas, más resultados'),
    (3, 'Gobernar con ética'),
    (4, 'Código ético de Gobierno obligatorio'),
    (3, 'Con dos mandatos basta'),
    (4, '8 años como máximo'),
    (3, 'Aire fresco en nuestro sistema electoral'),
    (4, 'Adiós listas cerradas, hola listas flexibles'),
    (2, 'España resuelve'),
    (3, 'Vivienda, prioridad nº1'),
    (4, 'Alivio hoy. Solución para siempre: plan de choque en 2 fases'),
    (4, 'Fase 1 - Alivio hoy: 3 medidas excepcionales de emergencia'),
    (4, 'Fase 2 - Solución para siempre: un plan a 10 años'),
    (4, 'Nuestro plan de vivienda, al detalle'),
    (3, 'Fase 1 - Alivio hoy: medidas excepcionales para una crisis excepcional'),
    (4, 'Pacto de reconciliación del alquiler: limitar precios condicionado a proteger la propiedad'),
    (4, 'Fondo soberano de vivienda protegida y cero especulación del Estado'),
    (4, 'Movilización masiva de viviendas vacías'),
    (4, 'Recargo para no residentes y competencia justa en vivienda turística'),
    (3, 'Fase 2 – Plan Nacional de Barrios (10 años)'),
    (4, 'Construir barrios, no bloques de hormigón'),
    (4, 'Responsabilidad municipal vinculante: no más excusas'),
    (4, 'Fin de la parálisis urbanística y desbloqueo de suelo'),
    (3, 'Una Administración moderna y digital que te facilite la vida'),
    (4, 'La Autopista Digital española'),
    (4, 'Nadie se quedará atrás'),
    (4, 'El Estado cumplirá con su palabra'),
    (4, 'Ciberseguridad y protección digital para todos los ciudadanos'),
    (3, 'Un Estado proactivo que llegue antes de que tengas que pedirlo'),
    (4, 'Un Estado al servicio del ciudadano'),
    (4, 'Plataforma estatal de gestión de ayudas ante catástrofes'),
    (4, 'Un Estado innovador y con algoritmos transparentes'),
    (3, 'Impuestos justificados y que se entiendan'),
    (4, 'Entender lo que pagas'),
    (4, 'Pagar lo que es justo'),
    (4, 'Un sistema fiscal que funcione'),
    (3, 'Menos normas, más claras, estables y coordinadas'),
    (4, 'Programa Estatal de Auditoría de Barreras'),
    (4, 'Un país diverso, un mercado sin barreras'),
    (3, 'Una función pública independiente y al servicio del ciudadano'),
    (4, 'Una dirección pública despolitizada y profesionalizada'),
    (4, 'Un modelo de acceso a la altura de nuestra sociedad'),
    (4, 'Una Administración ágil y orientada a resultados'),
    (2, 'España prospera'),
    (3, 'La educación en el centro'),
    (4, 'Una educación para el siglo 21'),
    (4, 'Recuperar todo el potencial educativo del país'),
    (4, 'Fortalecer el prestigio de la docencia'),
    (4, 'Universidad flexible, práctica y conectada al mundo real'),
    (4, 'Apostar por la formación profesional más que nunca'),
    (4, 'Hucha de Formación para Jóvenes'),
    (3, 'Más salario, más productividad'),
    (4, 'Productividad, productividad y más productividad'),
    (4, 'Un marco legal favorable a las subidas salariales'),
    (3, 'Revolución PYME'),
    (4, 'Crecer sin frenos'),
    (4, 'Fuera todas las barreras innecesarias'),
    (4, 'Competir en igualdad de condiciones y con voz propia'),
    (4, 'Escudo digital PYME: ciberseguridad al alcance de todas las empresas'),
    (3, 'Autónomo, estamos contigo'),
    (4, 'Flexibilidad total: cuotas e impuestos a tu medida'),
    (4, 'Nuevo Estatuto del Trabajo Autónomo: derechos del siglo 21'),
    (4, 'Cero obstáculos para negocios pequeños y familiares'),
    (4, 'Despegue de autónomo a empresa mucho más fácil'),
    (3, 'Una política migratoria con cabeza'),
    (4, 'Que el talento entre por la puerta grande'),
    (4, 'El Estado decide: una ley que se cumpla'),
    (4, 'Convivencia: derechos, deberes y cero xenofobia'),
    (4, 'Españoles en el mundo: encontraréis las puertas abiertas'),
    (3, 'Talento científico, confiamos en vuestro trabajo'),
    (4, 'Darles la autonomía y el presupuesto que merecen'),
    (4, 'Talento científico sin fronteras'),
    (4, 'Del laboratorio a la sociedad'),
    (3, 'Infraestructuras y crecimiento sostenibles'),
    (4, 'Planificar con datos, no con promesas'),
    (4, 'Conservar primero: infraestructuras seguras y que duren'),
    (4, 'Infraestructuras para un crecimiento sostenido y sostenible'),
    (2, 'España cuida'),
    (3, 'Sanidad pública: cuidar a quienes nos cuidan'),
    (4, 'Que cada euro salve vidas: gestión inteligente para proteger nuestra sanidad pública'),
    (4, 'Dignidad para todos los profesionales sanitarios'),
    (4, 'Llevar la sanidad pública a lo más alto: especialización + IA'),
    (3, 'Contigo y con tu familia'),
    (4, 'Ni un niño atrás: pobreza infantil a la mitad'),
    (4, 'Tiempo para cuidar, sin frenar tu carrera'),
    (4, 'Un país diseñado para conciliar'),
    (4, 'Todas las familias cuentan'),
    (4, 'Salud mental: prevenir en casa, en familia y en el colegio'),
    (3, 'Redefiniendo el envejecimiento'),
    (4, 'Asegurar las pensiones actuales y futuras'),
    (4, 'Un nuevo enfoque vital para la generación sénior del siglo 21'),
    (3, 'Protección animal con los veterinarios'),
    (4, 'Estatus sanitario pleno para la profesión veterinaria'),
    (4, 'Ley de Bienestar Animal 2.0 y lucha contra el maltrato animal'),
    (3, 'Seguridad y defensa para el mundo de hoy'),
    (4, 'Una policía moderna y cercana'),
    (4, 'Respaldo a quienes nos protegen'),
    (4, 'Dignidad y futuro para nuestras Fuerzas Armadas'),
    (4, 'Justicia ágil y víctimas en el centro'),
    (3, 'Medio ambiente y adaptación climática: anticipar para proteger'),
    (4, 'Gestión forestal frente a los incendios'),
    (4, 'Agua: gestión experta y ni una gota perdida'),
    (4, 'Ciudades frescas y escudos frente al calor'),
    (4, 'Más economía circular, menos residuos'),
    (2, 'España lidera'),
    (3, 'Ser una potencia energética'),
    (4, 'Reglas claras, seguridad jurídica y precios reales'),
    (4, 'Redes modernas, almacenamiento e inteligencia en el sistema'),
    (4, 'Una gran reindustrialización verde para España'),
    (3, 'Construir la Unión Europea del siglo 21'),
    (4, 'Una Europa democrática frente a cualquier amenaza'),
    (4, 'Reinventar el motor económico europeo'),
    (4, 'Defender juntos nuestra paz y seguridad'),
    (4, 'Una Europa que no deje a nadie atrás'),
    (3, 'Ni un paso atrás en derechos sociales'),
    (4, 'Feminismo y violencia machista: un consenso innegociable'),
    (4, 'Derechos reproductivos con libertad'),
    (4, 'Derechos LGTBIQ+: orgullo y barrera contra el odio'),
    (4, 'Discapacidad: autonomía como derecho fundamental'),
    (3, 'Cultura y talento que proyecten a España al mundo'),
    (4, 'España, potencia audiovisual de Europa'),
    (4, 'Instituciones culturales libres de partidismo'),
    (4, 'Crear con derechos en la era de la IA'),
    (4, 'Todas las artes, en toda España'),
    (4, 'Cultura sin barreras ni fronteras'),
    (3, 'Deporte para un país sano y vital'),
    (4, 'Un Estatuto del Deportista para nuestra élite'),
    (4, 'Salud ciudadana a través del deporte'),
]

# Títulos que la conversión parte o desordena: primera línea -> título completo; resto se quita
PARTIDOS = {
    'una direccion profesionalizada': ('una direccion publica despolitizada y profesionalizada', ('publica', 'despolitizada y')),
    'feminismo y violencia machista innegociable': ('feminismo y violencia machista un consenso innegociable', ('un consenso',)),
}

# Líneas que se quitan enteras (cabeceras repetidas y subtítulo de portada)
FUERA = (
    r'^#+\s*España Limpia$',
    r'^#+\s*Infraestructuras y Crecimiento Sostenibles$',
    r'^\*\*Programa Electoral\*\* Elecciones Generales \*\*·\*\* 29N$',
)

# Párrafos sueltos (por su arranque) que son subpuntos de la medida anterior
SUBPUNTO = (
    'Se publicará la lista y coste de todos los nombramientos',
    'Se iniciarán trámites de despido de todos los nombramientos',
    'eliminar **todos** los aforamientos',
    'limitar el aforamiento de los miembros de Gobierno',
)

# Viñetas-resumen de la presentación de capítulo que la conversión dejó sin «- »
INTRO_VINETA = (
    'Con impuestos justos, estables y que se entiendan',
    'Poniendo la educación en el centro',
    'Con sueldos más altos',
    'Con PYMES que crezcan',
    'Con una política migratoria con cabeza',
    'Confiando en nuestros científicos',
)

# Párrafos sin título que continúan la medida anterior (en subapartados sin títulos de medida)
CONTINUA = (
    'Cada línea sectorial contará con la participación directa',
    'El resultado será un programa continuo de simplificación',
    'Desde el comercio de proximidad, la hostelería',
)

# Párrafos sin título que, aunque siguen a una medida con título, son otra medida
SEPARAR = (
    'Culminaremos con urgencia la **Unión de Ahorros e Inversiones**',
    'Impulsaremos la **gratuidad de la entrada a los museos públicos',
)

# Párrafos de exposición dentro de un subapartado
EXPOSICION = (
    'La crisis de la vivienda no puede esperar',
    'Nuestro compromiso es doble',
    'A continuación, detallamos la hoja de ruta',
)

TITULO_MEDIDA = re.compile(r'^\*\*(\d+\.\s*)?[^*]+?(:\*\*|\*\*\s*:)')


def limpiar(lineas):
    b = [l.strip() for l in lineas]
    b = [l for l in b if l and not any(re.match(r, l) for r in FUERA)]
    assert b[0] == '#### La España que merecemos', b[0]
    b = b[1:]

    niveles = {norm(t): (n, t) for n, t in TITULOS}
    vistos = set()

    # 1. Títulos (por su texto) y quitar las marcas de título de lo que no lo es
    items = []          # (tipo, texto): tipo 'h2'..'h4' o 'p'
    quitar = set()
    for l in b:
        t = norm(l.replace('<sup>', ' ').replace('</sup>', ' '))
        if t in quitar:
            quitar.discard(t)
            continue
        if t in PARTIDOS:
            t, resto = PARTIDOS[t]
            quitar.update(resto)
        if t in niveles:
            assert t not in vistos, l
            vistos.add(t)
            n, tit = niveles[t]
            items.append((f'h{n}', tit))
            continue
        assert not l.startswith('>'), l
        l = re.sub(r'^#+\s*', '', l)
        items.append(('p', l))
    falta = set(niveles) - vistos
    assert not falta, falta
    assert not quitar, quitar

    # 2. Arreglos de la conversión en los párrafos
    out = []
    for tipo, l in items:
        if tipo == 'p':
            l = l.replace('<sup>', '').replace('</sup>', '')
            # cuadro de diagnóstico «↪ …» (en p. 4 y p. 10 la conversión lo pone como viñetas)
            l = re.sub(r'^(- )?↪\s*', '↪', l)
            l = l.replace('↪P _ero seamos claros', '↪_Pero seamos claros')
            # «**Nuestro modelo … ideal**» tomado por título; sigue «para activar una red…»
            if l == 'Nuestro modelo de Comunidades Autónomas es una fortaleza arquitectónica ideal':
                l = '**' + l + '**'
            # negrita rota: punto final suelto en negrita
            l = l.replace('con un periodo de adaptación suficiente **.**', 'con un periodo de adaptación suficiente.')
            # espacio que mete la conversión entre el cierre de la negrita y la puntuación
            l = re.sub(r'\*\* +([,.;:])', r'**\1', l)
        out.append((tipo, l))
    items = out

    # 3. Unir los trozos del cuadro «↪» de la p. 4, partido en tres viñetas en cursiva
    out = []
    for tipo, l in items:
        if tipo == 'p' and out and out[-1][0] == 'p' and out[-1][1].startswith('↪_') \
                and not out[-1][1].endswith(TERM + ('._', '?_', '!_')) and l.startswith('- _'):
            prev = out[-1][1]
            out[-1] = ('p', prev[:-1].rstrip() + ' ' + l[3:].lstrip())
            continue
        out.append((tipo, l))
    items = out
    diag = {i for i, (t, l) in enumerate(items) if t == 'p' and l.startswith('↪')}
    items = [(t, l[1:] if i in diag else l) for i, (t, l) in enumerate(items)]

    # 4. Clasificar párrafos: exposición, medida, continuación o subpunto
    res = []            # bloques de salida
    capitulo = ''
    nivel = 0           # nivel del último título
    medida_titulada = False   # la última medida del subapartado tiene «**Título:**»
    hay_medida = False
    for i, (tipo, l) in enumerate(items):
        if tipo != 'p':
            n = int(tipo[1])
            if n == 2:
                capitulo = l
            nivel = n
            medida_titulada = hay_medida = False
            res.append('#' * n + ' ' + l)
            continue
        if i in diag:
            res.append(l)
            continue
        if re.match(r'^[a-záéíóúñ]', l) and not l.startswith(SUBPUNTO):
            res.append(l)  # final de párrafo cortado por el salto de página: lo une join_broken
            continue
        s = re.sub(r'^- ', '', l)
        if nivel < 4:
            # presentación de capítulo o texto bajo un apartado: exposición; las viñetas-resumen
            # (●) de la presentación se dejan en el mismo bloque que el párrafo anterior
            if nivel == 2 and (l.startswith('- ') or s.startswith(INTRO_VINETA)):
                for v in re.split(r'(?<=\.) (?=Con )', s):  # dos viñetas que la conversión juntó
                    res[-1] = res[-1] + '\n- ' + v
            else:
                assert not l.startswith('- '), l
                res.append(l)
            continue
        if l.startswith(EXPOSICION):
            res.append(l)
            continue
        if s.startswith(SUBPUNTO):
            res[-1] = res[-1] + '\n  - ' + s
            continue
        m = re.match(r'^\*\*(\d+)\.\s+', l)
        if m:
            res.append(m.group(1) + '. **' + l[m.end():])
            hay_medida, medida_titulada = True, True
            continue
        if TITULO_MEDIDA.match(l):
            res.append('- ' + l)
            hay_medida, medida_titulada = True, True
            continue
        if l.startswith(CONTINUA) or (capitulo != 'España limpia' and medida_titulada and not l.startswith(SEPARAR)):
            assert hay_medida, l
            res[-1] = res[-1] + '\n' + l
            continue
        res.append('- ' + s)
        hay_medida, medida_titulada = True, False

    out = [TITULO, '']
    for r in res:
        out.append(r)
        out.append('')
    return out

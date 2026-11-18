"""Limpieza propia del programa del BNG (Eleccións xerais 29N 2026, en gallego).

Estructura del PDF: portada (p. 1), índice (pp. 2-3), «Introdución» con tres apartados y once
capítulos numerados «N. TÍTULO» con apartados N.N y subapartados N.N.N. El capítulo 6 tiene
apartados «1) … 6)», el 7 dos bloques sin numerar («Desde o Instituto Cervantes:», «Nas relacións
coa Lusofonía:») y el 4.6 un apartado «Minaría sostíbel». Las propuestas son viñetas dibujadas
(no son texto): pymupdf4llm pierde a veces la viñeta, sobre todo tras un salto de página, y
confunde niveles; las viñetas reales y su sangría se han sacado de los dibujos del PDF.
En el capítulo 8 las propuestas son párrafos con un arranque en negrita («Nube pública galega. …»).
Cabeceras y pies (lema, logo, «CAPÍTULO - NN») no llegan al bruto.
"""
import re
from clean import plain

TERM = tuple('.:;!?)»"”…')

PROPIOS = {
    'galiza': 'Galiza',
    'bng': 'BNG',
    'lgbt': 'LGBT',
}

# Medidas que en el PDF llevan viñeta y la conversión la perdió (arranque de la línea)
SIN_VINETA = (
    'Modificar as axudas do Plan estatal de vivenda destinadas',
    'Impulsar medidas de garantía de abastecemento de medicación',
    'Derrogación íntegra da Lei Mordaza',
    'Derrogación da prisión permanente revisábel',
    'Derrogación do delito de desordes públicas',
    'Transferencia a Galiza das competencias en materia de Institucións Penitenciarias',
    'Derrogar a Lei de Segredos Oficiais',
    'Reformar estruturalmente a normativa electoral',
    'Garantir a plena e exclusiva competencia en xestión do persoal docente',
    'Defender inequivocamente o ensino público',
    'Crear un novo Estatuto Marco',
    'Traspasar as competencias en materia de saúde penal',
    'A exixencia da exclusión da pesca artesanal',
    'Colaborar con Galiza na planificación das tecnoloxías',
    'Impulsar a consideración da electricidade como ben básico',
    'Impulsar o aforro enerxético',
    'Impulsar unha verdadeira axenda para o desenvolvemento do autoconsumo',
    'Impulsar a recuperación para o público das concesións dos encoros',
    'Declarar as materias primas críticas e estratéxicas',
    'Actualizar a rede interior ferroviaria galega',
    'Completar as obras do Corredor Atlántico de Mercadorías',
    'Declarar que o transporte ferroviario sexa a modalidade prioritaria',
    'Promover unha mellor conexión ferroviaria transfronteiriza',
    'Demandar a incorporación dos portos galegos',
    'O status internacional de neutralidade activa',
)

# Viñetas de segundo nivel en el PDF que la conversión dejó en primer nivel
SUBNIVEL = (
    'Permitir a creación de novos impostos ou taxas a nivel municipal',
    'Facilitar a portabilidade das hipotecas',
    'Promover o cooperativismo de propiedade e alugueiro',
    'Adoptar as medidas necesarias para facilitar a aplicación por parte CCAA',
    'Promover as modificacións legais que faciliten a creación de empresas públicas',
    'Transferir á Xunta de Galiza os edificios propiedade do Ministerio de Defensa',
    'Elaborar un Estatuto do Persoal de Investigación',
    'Reducir e simplificar a burocracia',
    'Promover a transparencia, a integridade, a diversidade',
)

# Viñetas partidas por la conversión: la segunda mitad empieza con «- » (fin de la primera, arranque de la segunda)
PARTIDAS = (
    ('Regulación estrita das portas xiratorias e das', 'incompatibilidades; concretamente'),
    ('Rematar as obras pendentes de execución no AVE,', 'particularmente a finalización'),
    ('potencialmente contaminantes na', '“restauración” de canteiras'),
)

# Párrafos cortados por el salto de página que siguen en mayúscula: (final del primero, arranque del segundo)
CORTES = (
    ('recepción dos medios públicos audiovisuais de Portugal en', 'Galiza, no cadro da cooperación'),
)


def frase(t):
    """«2.1 VIVENDA» -> «2.1 Vivenda»; respeta nombres propios. Los títulos ya en minúsculas se dejan."""
    t = plain(t)
    m = re.match(r'^((?:\d+(?:\.\d+)*\.?|\d\))\s+)?(.*)$', t)
    num, resto = m.group(1) or '', m.group(2)
    if resto != resto.upper():
        return num + resto
    resto = resto.lower()
    resto = re.sub(r'\b(\w+)\b', lambda w: PROPIOS.get(w.group(1), w.group(1)), resto)
    return num + resto[:1].upper() + resto[1:]


def nivel(t):
    """Nivel de título según la numeración del propio programa."""
    m = re.match(r'^(\d+(?:\.\d+)*)\.?\s', t)
    if m:
        return {1: 2, 2: 3}.get(m.group(1).count('.') + 1, 4)
    return None


def limpiar(lineas):
    # 1) portada e índice: todo lo anterior a «INTRODUCIÓN»
    ini = next(i for i, l in enumerate(lineas) if l.startswith('#') and 'INTRODUCI' in l)
    lineas = ['# Programa electoral', ''] + lineas[ini:]

    # 2) viñetas partidas en dos por la conversión
    for fin, cont in PARTIDAS:
        i = next(i for i, l in enumerate(lineas) if l.rstrip().endswith(fin))
        j = i + 1
        while not lineas[j].strip():
            j += 1
        assert lineas[j].startswith('- ' + cont), (fin, lineas[j][:50])
        lineas[i] = lineas[i].rstrip() + ' ' + lineas[j][2:].strip()
        del lineas[i + 1:j + 1]

    # 3) medidas cortadas por el salto de página cuya continuación empieza en mayúscula
    #    (join_broken solo une si empieza en minúscula)
    for fin, cont in CORTES:
        i = next(i for i, l in enumerate(lineas) if l.rstrip().endswith(fin))
        j = i + 1
        while not lineas[j].strip():
            j += 1
        assert lineas[j].startswith(cont), (fin, lineas[j][:50])
        lineas[i] = lineas[i].rstrip() + ' ' + lineas[j].strip()
        del lineas[i + 1:j + 1]

    out = []
    cap = None          # capítulo actual (número)
    en8 = False         # dentro de un apartado 8.x
    intro8 = False      # en el cap. 8, el primer párrafo tras cada apartado es exposición
    vistos = set()
    for l in lineas:
        s = l.strip()
        if s.startswith('# '):
            out.append(s); continue
        m = re.match(r'^#{2,4}\s+(.*)$', s)
        t = plain(m.group(1)) if m else s
        # --- títulos ---
        if m and t == 'E cumprimos.':  # frase del cuerpo tomada por título (p. 5)
            out.append(t); continue
        if s == 'A mellor garantía, cumprimos os compromisos':
            out.append('### ' + s); continue
        if s.startswith('8.1 Soberanía dixital'):
            out.append('### ' + s); en8, intro8 = True, False; continue
        if s.startswith('4) En materia de ordenación'):
            out.append('### ' + s); continue
        if s.startswith('2) En materia de tramitación ambiental de plans e proxectos,'):
            # título y primera frase en la misma línea: título según el índice y la frase como medida
            out.append('### 2) En materia de tramitación ambiental de plans e proxectos')
            out.append('')
            out.append('- ' + s); continue
        if m:
            if t.startswith('INTRODUCI'):
                out.append('## ' + frase(t)); continue
            n = nivel(t)
            if n == 2:
                cap = int(t.split('.')[0])
            if n:
                out.append('#' * n + ' ' + frase(t))
                if cap == 8 and n == 3:
                    en8 = intro8 = True
                continue
            if t == 'Minaría sostíbel':
                out.append('#### ' + t); continue
            out.append('### ' + frase(t)); continue  # O BNG…, O valor…, 1)…6), Cervantes, Lusofonía
        # --- viñetas ---
        if re.match(r'^-\s', s) is None and s.startswith(SIN_VINETA) and s[:40] not in vistos:
            vistos.add(s[:40])
            out.append('- ' + s); continue
        if re.match(r'^- ', l) and s[2:].startswith(SUBNIVEL):
            out.append('  ' + s); continue
        if re.match(r'^\s+- ', l):
            out.append('  - ' + s[2:].strip()); continue
        # subpuntos numerados del cap. 11 («1. Saída da OTAN…», «a) Anular…»)
        if cap == 11 and re.match(r'^(\d\.|[a-d]\))\s', s):
            out.append('  - ' + s); continue
        # cap. 8: dentro de los apartados 8.x, los párrafos con arranque en negrita son medidas;
        # el primero tras el título de 8.2-8.9 es la introducción del apartado
        if cap == 8 and en8 and s and not s[0].islower():
            if intro8:
                intro8 = False
                out.append(l); continue
            out.append('- ' + s); continue
        out.append(l)
    return out

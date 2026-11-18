"""Limpieza propia del programa de Nuevo Extremeñismo (Elecciones generales 29N 2026, 15 páginas).

Estructura del PDF:
- p. 1: portada «La única candidatura 100% extremeña» / «150 medidas para que se escuche a
  Extremadura en Madrid» (título del Markdown);
- p. 2: «Lo que llevaremos a Madrid»: un párrafo y la lista de los once bloques «I. Vivienda. Una
  casa para vivir, no para invertir.» (hace de sumario, pero sin páginas: se deja como párrafos,
  no como medidas);
- pp. 3-14: once bloques «I.»–«XI.» con un lema debajo, apartados en versalitas («EMPLEO Y
  SALARIOS») a veces con su propio lema, rótulos «Cómo se paga», «Cómo funciona», «Cuánto
  cuesta»… y las 150 medidas numeradas de forma continua. El título del bloque II se repite en
  la p. 5 (se quita);
- p. 15: contraportada con el lema de la portada (se quita).
Cabecera (logos) y pie («@nuevoext», número de página, «www.nuevoext.es») no llegan al bruto.

Las cifras destacadas de cada bloque («+45 %» y su explicación, en tres columnas) llegan
mezcladas: se recomponen como un párrafo por cifra, en el orden del PDF. Los cuatro pasos de
«Cómo funciona» van en dos columnas y llegan como 1, 3, 2, 4: se ponen en orden. Las cinco
etiquetas de «Qué trabajos» se separan con « · ».
Niveles: bloque → «##»; lema del bloque y apartados → «###»; lemas de apartado y rótulos → «####».
"""
import re

# Cifras destacadas: líneas del bruto -> párrafos recompuestos (comprobado con el PDF)
CIFRAS = (
    (['### **+45 % +37 %**',
      'subida del alquiler en cinco años subida del alquiler en cinco años en la provincia de Cáceres en la provincia de Badajoz',
      '### **+26,5 %**',
      'subida del salario mínimo en el mismo periodo'],
     ['**+45 %** subida del alquiler en cinco años en la provincia de Cáceres',
      '**+37 %** subida del alquiler en cinco años en la provincia de Badajoz',
      '**+26,5 %** subida del salario mínimo en el mismo periodo']),
    (['**13 % 10,2 % 64.600** tasa de paro en Extremadura tasa de paro en España personas en paro en Extremadura'],
     ['**13 %** tasa de paro en Extremadura',
      '**10,2 %** tasa de paro en España',
      '**64.600** personas en paro en Extremadura']),
    (['- **1** Te apuntas en tu oficina de empleo.',
      '- **3** Empiezas a trabajar: SMI y 30 horas.',
      '- **2** Ayuntamientos y entidades proponen proyectos.',
      '- **4** Das el salto al empleo privado o al emprendimiento.'],
     ['**1** Te apuntas en tu oficina de empleo.',
      '**2** Ayuntamientos y entidades proponen proyectos.',
      '**3** Empiezas a trabajar: SMI y 30 horas.',
      '**4** Das el salto al empleo privado o al emprendimiento.']),
    (['Cuidados y acompañamiento Prevención de incendios Rehabilitación de vivienda Arreglo de calles y renaturalización Actividades comunitarias'],
     ['Cuidados y acompañamiento · Prevención de incendios · Rehabilitación de vivienda · '
      'Arreglo de calles y renaturalización · Actividades comunitarias']),
    (['### **0,79 % del PIB**',
      'coste neto en toda España (13.300 M€)',
      '**350 M€**',
      'coste neto en Extremadura'],
     ['**0,79 % del PIB** coste neto en toda España (13.300 M€)',
      '**350 M€** coste neto en Extremadura']),
    (['### **212 de 388**',
      'municipios extremeños sin ninguna gasolinera: 147 en Cáceres y 65 en Badajoz',
      '### **−9 cts**',
      'las cooperativas ya venden la gasolina 95 por debajo de la media',
      '### **−11 cts**',
      'las cooperativas ya venden el diésel por debajo de la media'],
     ['**212 de 388** municipios extremeños sin ninguna gasolinera: 147 en Cáceres y 65 en Badajoz',
      '**−9 cts** las cooperativas ya venden la gasolina 95 por debajo de la media',
      '**−11 cts** las cooperativas ya venden el diésel por debajo de la media']),
    (['#### **−4,0 %**',
      '#### **7,1 %**',
      'producción industrial en peso de la industria Extremadura, frente al +2,5 % de manufacturera en Extremadura, media en España frente al 11,9 % en España',
      '**1,7 %**',
      'del PIB español: la tercera comunidad con menos peso'],
     ['**−4,0 %** producción industrial en Extremadura, frente al +2,5 % de media en España',
      '**7,1 %** peso de la industria manufacturera en Extremadura, frente al 11,9 % en España',
      '**1,7 %** del PIB español: la tercera comunidad con menos peso']),
    (['#### **36,6 %**',
      '#### **8 %**',
      'de empleo temporal en las administraciones el máximo fijado por ley para el empleo temporal públicas de Extremadura público'],
     ['**36,6 %** de empleo temporal en las administraciones públicas de Extremadura',
      '**8 %** el máximo fijado por ley para el empleo temporal público']),
    (['#### **14 días**',
      'puede llegar a tardar la cita en atención primaria en algunos municipios extremeños',
      '#### **24-48 h**',
      'el objetivo acordado por el Ministerio de Sanidad y las comunidades autónomas'],
     ['**14 días** puede llegar a tardar la cita en atención primaria en algunos municipios extremeños',
      '**24-48 h** el objetivo acordado por el Ministerio de Sanidad y las comunidades autónomas']),
)


def frase(t):
    """«EMPLEO Y SALARIOS» -> «Empleo y salarios»; los títulos ya en minúsculas se dejan."""
    if t == t.upper():
        t = t.lower()
        t = t[:1].upper() + t[1:]
    return t


def titulo(s):
    """Texto de un título del bruto sin «#», sin negrita y sin el punto final."""
    t = s.lstrip('#').strip().strip('*').strip()
    return t[:-1] if t.endswith('.') else t


def limpiar(lineas):
    b = [l.strip() for l in lineas]
    b = [l for l in b if l]

    # cifras destacadas, pasos y etiquetas en el orden del PDF
    for viejas, nuevas in CIFRAS:
        k = next((k for k in range(len(b)) if b[k:k + len(viejas)] == viejas), None)
        assert k is not None, viejas[0]
        b[k:k + len(viejas)] = nuevas

    # medida 100 partida por la conversión («… en sanidad» / «- y educación.»)
    k = b.index('100. Incentivos estatales para las plazas rurales de difícil cobertura en sanidad')
    assert b[k + 1] == '- y educación.', b[k + 1]
    b[k:k + 2] = [b[k] + ' y educación.']

    out = []
    capitulos = set()
    tras_capitulo = False
    medida = 0
    for s in b:
        if s == '**La única candidatura 100% extremeña 150 medidas para que se escuche a Extremadura en Madrid**':
            out += ['# La única candidatura 100% extremeña. 150 medidas para que se escuche a Extremadura en Madrid', '']
            continue
        if s == '# **La única candidatura 100% extremeña**':   # contraportada
            continue
        if s == '## **Lo que llevaremos a Madrid**':
            out += ['## Lo que llevaremos a Madrid', '']
            continue
        # sumario de la p. 2: «- **I. Vivienda.** Una casa…» -> párrafo
        if re.match(r'^- \*\*[IVX]+\. ', s):
            out += [s[2:], '']
            continue
        # bloques «I.»–«XI.»
        m = re.match(r'^#+\s*\*\*([IVX]+)\. (.+?)\*\*$', s)
        if m:
            num, t = m.group(1), m.group(2)
            if num == 'VII':   # título y lema en la misma línea
                t, lema = t.split(' Lo que afecta', 1)
                lema = 'Lo que afecta' + lema
            else:
                lema = None
            if num in capitulos:   # título repetido en la página siguiente (bloque II)
                continue
            capitulos.add(num)
            out += [f'## {num}. {t}', '']
            if lema:
                out += ['### ' + titulo(lema), '']
            tras_capitulo = lema is None
            continue
        if s.startswith('#'):
            t = titulo(s)
            if tras_capitulo:            # lema del bloque
                assert s.startswith('##### '), s
                out += ['### ' + t, '']
            elif t == t.upper():         # apartado en versalitas
                out += ['### ' + frase(t), '']
            else:                        # lema de apartado o rótulo («Cómo se paga»)
                out += ['#### ' + t, '']
            tras_capitulo = False
            continue
        tras_capitulo = False
        m = re.match(r'^(\d+)\. ', s)
        if m:
            medida += 1
            assert int(m.group(1)) == medida, (medida, s[:40])
        assert not s.startswith('- '), s
        out += [s, '']
    assert medida == 150, medida
    return out

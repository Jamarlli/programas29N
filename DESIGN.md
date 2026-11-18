---
name: Programas 29N
description: Los programas electorales del 29N, comparados tema a tema con el texto literal de cada partido.
colors:
  fondo: "#f4f5f7"
  superficie: "#ffffff"
  superficie-2: "#f3f4f6"
  superficie-3: "#e8eaee"
  linea: "#e3e5e9"
  linea-fuerte: "#c9ced6"
  tinta: "#15181d"
  tinta-media: "#454d59"
  tinta-suave: "#5c6573"
  rotulador: "#ffe066"
  partido-fa: "#809f1b"
  partido-pp: "#21599e"
  partido-psoe: "#de0612"
  partido-vox: "#065a36"
  partido-compromis: "#e17a0d"
  partido-salf: "#b4902a"
  partido-pacma: "#007e2a"
  partido-fo: "#7e1218"
  partido-mundo: "#8a5c46"
  partido-fe: "#1d1d1b"
  partido-pcte: "#ae2a36"
  partido-autonomos: "#001e5a"
typography:
  display:
    fontFamily: "Schibsted Grotesk, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "clamp(2.25rem, 1.5rem + 2.6vw, 3.5rem)"
    fontWeight: 800
    lineHeight: 1.02
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Schibsted Grotesk, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "clamp(1.875rem, 1.4rem + 1.6vw, 2.625rem)"
    fontWeight: 800
    lineHeight: 1.08
    letterSpacing: "-0.03em"
  title:
    fontFamily: "Schibsted Grotesk, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  item:
    fontFamily: "Schibsted Grotesk, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 600
    lineHeight: 1.38
  body:
    fontFamily: "Schibsted Grotesk, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  literal:
    fontFamily: "Newsreader, Source Serif 4, Georgia, serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Schibsted Grotesk, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.4
  meta:
    fontFamily: "Schibsted Grotesk, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.45
rounded:
  xs: "6px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  pill: "999px"
spacing:
  xs: "6px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "28px"
  2xl: "56px"
  gutter: "clamp(16px, 3vw, 32px)"
components:
  busqueda:
    backgroundColor: "{colors.superficie}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.md}"
    padding: "0 16px 0 46px"
    height: "52px"
  nav-activa:
    backgroundColor: "{colors.superficie}"
    textColor: "{colors.tinta}"
    padding: "0 12px"
  chip-partido:
    backgroundColor: "{colors.superficie}"
    textColor: "{colors.tinta}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0 14px 0 12px"
    height: "36px"
  chip-partido-activo:
    backgroundColor: "{colors.superficie}"
    textColor: "{colors.tinta}"
  segmentado-activo:
    backgroundColor: "{colors.superficie}"
    textColor: "{colors.tinta}"
    rounded: "9px"
    height: "32px"
  tarjeta:
    backgroundColor: "{colors.superficie}"
    rounded: "{rounded.lg}"
    padding: "26px 30px"
  marca-postura:
    backgroundColor: "{colors.superficie}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.xs}"
    padding: "0 8px"
    height: "26px"
  boton:
    backgroundColor: "{colors.tinta}"
    textColor: "{colors.superficie}"
    rounded: "{rounded.md}"
    padding: "0 18px"
    height: "40px"
---

<!-- Los tokens son los de web/styles.css. -->

# Design System: Programas 29N

## Overview

**Creative North Star: "La guía del votante"**

**Lectura de diseño (anti-slop):** herramienta de consulta cívica para cualquier votante, en el estilo de una guía electoral de periódico. Diales: energía 1 (tranquila), ritmo 2 (constante, con alguna ruptura) y movimiento 1 (solo estados al pasar el ratón y el destello de llegada).

La web no tiene color propio: es neutral. El único color que aparece es el de los partidos, y el amarillo de rotulador marca lo que el lector ha buscado. Es solo en tono claro, porque el público general lo espera así y una herramienta cívica no tiene motivo para el oscuro.

La página tiene dos voces. Lo que dicen los partidos va en serif (Newsreader) y es literal. Lo nuestro (titulares, navegación, cifras) va en sans (Schibsted Grotesk). La experiencia va de lo general a lo concreto: primero titulares que se escanean, y el texto completo con un clic.

**Key Characteristics:**
- Tarjetas blancas sobre fondo gris muy claro, con un filo de 1px y esquinas de 16px; sin sombras.
- Interfaz en tinta (casi negro): enlaces, foco, pestaña activa y botón principal.
- **Motivo propio, la franja de partido:** cada partido lleva su punto de color junto al nombre y una franja de su color encima de su columna, su tarjeta o su pestaña, siempre en el mismo orden: de izquierda a derecha, Frente Amplio, PSOE, PP y Vox. Los partidos que añade el lector van detrás, en el orden de `data/partidos.json`.
- Posturas en filas: cada postura de una pregunta lleva pegadas las siglas de quien la defiende.
- **Cada cosa, en un solo sitio, y cada enlace dice adónde lleva.** Desplegar es quedarse en la misma página (chevrón); navegar es ir a otra (flecha y destino escrito).
- En móvil, la navegación va abajo, al alcance del pulgar.

## Colors

### Partidos
- Cada partido lleva el color principal de su marca, sacado de la portada de su programa y de su web. Si dos se confundían, se usa el segundo color del partido:
  - **Frente Amplio** #809f1b: el verde lima de las letras de su portada (su rojo anaranjado era casi igual que el del PSOE).
  - **PSOE** #de0612, **PP** #21599e (el azul de su web) y **Vox** #065a36 (el verde oscuro de su programa del 29N).
  - **Compromís** #e17a0d, **SALF** #b4902a (el dorado de su portada), **PACMA** #007e2a, **Frente Obrero** #7e1218, **Por un Mundo Más Justo** #8a5c46, **Falange** #1d1d1b (el negro de su bandera; su rojo se confundía con los de Frente Obrero y PCTE), **PCTE** #ae2a36 y **P. Autónomos** #001e5a.
- Los colores demasiado claros (el lima de FA y el naranja de Compromís) se oscurecen lo justo para llegar a 3:1 de contraste sobre blanco.
- Los cuatro de la comparación por defecto se distinguen bien entre sí. Con 12 partidos hay pares cercanos (Compromís y SALF, PSOE y PCTE, Vox y PACMA…), y con daltonismo se confunden más; por eso el color nunca identifica solo: siempre lleva al lado el nombre o la sigla, y cada partido ocupa siempre la misma posición.
- Se definen en `data/partidos.json` (y los cuatro de la comparación por defecto también en `web/styles.css`).
- Uso: punto de 8–10px delante del nombre, franja de 3–4px encima de columnas y tarjetas, subrayado de la pestaña activa y barras de la tabla de portada (la columna ya dice de qué partido es).

### Acento
- **Amarillo rotulador** (#ffe066): solo marca lo buscado: coincidencias de búsqueda, selección de texto y el destello del extracto al que se llega desde un enlace. Siempre lleva tinta encima.

### Neutral
- **Fondo** (#f4f5f7) y **superficie** (#ffffff): lienzo y tarjetas.
- **Superficies 2 y 3** (#f3f4f6, #e8eaee): filas de postura, buscador de cabecera, pistas de las barras, hover y pulsado.
- **Línea** (#e3e5e9) y **línea fuerte** (#c9ced6): filos de tarjeta, separación entre extractos, borde de chips y siglas.
- **Tinta** (#15181d), **tinta media** (#454d59) y **tinta suave** (#5c6573): texto, texto secundario y metadatos. La suave da al menos 4,9:1 en todas las superficies (5,4:1 sobre el fondo).

### Named Rules
**The Neutral Interface Rule.** La interfaz no tiene color propio. Todo lo que no es de un partido va en tinta y grises; el amarillo es el único acento y solo marca lo buscado.

**The Party Color Beside the Name Rule.** El color de un partido siempre acompaña a su nombre o a su sigla, nunca lo sustituye, y nunca rellena un fondo ni tiñe el texto. Todos los partidos llevan su marca con el mismo tamaño.

## Typography

**Interfaz:** Schibsted Grotesk (400–800), la grotesca de un grupo de prensa: tono de periódico, legible en tamaños pequeños.
**Texto literal:** Newsreader, con eje óptico, para lo que escriben los partidos.

### Hierarchy
- **Display** (800, clamp 2.25–3.5rem, 1.02, tracking −0.035em): solo el h1 de portada.
- **Headline** (800, clamp 1.875–2.625rem, 1.08): h1 de las demás vistas.
- **Title** (800, 1.5rem, 1.15): subtema, sección, grupo y pregunta destacada.
- **Item** (600, 0.9375rem, 1.38): titular de cada extracto. Es nuestro, así que va en sans.
- **Literal** (400, 1.0625rem, 1.55, máx. 70ch): texto de los partidos en serif. También las citas y los títulos de los programas.
- **Label** (600, 0.875rem): chips, pestañas, navegación y posturas.
- **Meta** (400, 0.8125rem): página del PDF, medida y apartado del programa.

### Named Rules
**The Two Voices Rule.** Todo lo literal de un partido va en serif, y nada nuestro va en serif.

**The Proportional Figures Rule.** No se usan cifras tabulares: en Schibsted separan demasiado las comas y el signo de porcentaje.

## Layout

- **Contenedor:** máximo 1320px, con margen lateral clamp(16px, 3vw, 32px).
- **Cabecera:** fija y de 64px en escritorio, con marca, tres secciones, buscador y el botón «Añadir partidos» con el número de partidos que se comparan. En móvil (≤760px) es una sola línea con la marca y ese botón, y las secciones pasan a una barra fija abajo con cuatro botones con icono y texto: Temas, Dónde chocan, Buscar y Programas.
- **Portada:** titular grande, entradilla y los programas que se comparan con su punto de color. «Añadir partidos» está solo en la cabecera. Con más de cuatro partidos, la tabla de temas se desplaza en horizontal y la columna del tema queda fija.
- **Panel «Añadir partidos»:** diálogo nativo de hasta 1180px (pantalla completa a ≤640px), con solo el título «Añadir partidos». Dos columnas con scroll propio. A la izquierda, un buscador por nombre o sigla y la lista, con una fila por programa (las candidaturas que comparten programa, como el PSC con el PSOE, van fundidas en la del partido). Orden, alfabético dentro de cada grupo: primero los partidos que ya se comparan («Añadido»), luego los que se pueden añadir («Añadir») y al final, en gris y sin botón, los que no tienen programa en la web, con «Aún no está disponible.» o «No se ha encontrado su programa.». Cada fila dice dónde se presenta. A la derecha, el mapa de las 52 circunscripciones (grises de la web, líneas blancas más gruesas entre comunidades, Canarias abajo a la izquierda, Ceuta y Melilla con un círculo): se filtra solo pulsando el mapa; la elegida va en tinta y las que no tienen ninguna candidatura con la búsqueda actual quedan más claras. Debajo, los partidos que se comparan como fichas con × y «Restablecer». A ≤860px se apila: primero el mapa, con «Ver las N candidaturas». Los trazados salen de `data/mapa-ccaa.json` (pipeline/mapa_ccaa.cjs). Una barra fija resume el resultado y ofrece «Añadir los N que faltan» y, con una circunscripción elegida, «Comparar toda la circunscripción». La elección se guarda en el navegador. Debajo, «Elige un tema» con la tabla de peso por tema y, después, «Dónde chocan» con seis preguntas en lista de dos columnas y el botón «Ver las N preguntas».
- **Vistas con lateral** (tema, «Dónde chocan», programa): columna de 216px fija con las secciones y su recuento. Por debajo de 960px desaparece y la sustituye una fila de enlaces que se desplaza en horizontal bajo el h1.
- **Tema:** migas («Temas › Vivienda»), h1 y, como primera tarjeta, «Dónde chocan» con las fichas de pregunta del tema (citas plegadas). Después, una tarjeta por subtema. El lateral empieza por «Dónde chocan».
- **Subtema:** tarjeta con, en «Resumen», una columna por partido visible, con su franja de color y su nombre fijo arriba; cada columna tiene una altura máxima (30rem) y se lee con scroll propio. En «Texto completo» los partidos se apilan en filas. Por debajo de 820px las columnas pasan a pestañas con su recuento; la elegida se mantiene en todos los subtemas.
- **Búsqueda:** vista propia con caja grande (52px) y botón «Buscar». Sin palabras, propone ejemplos que existen en los programas, con su número de extractos. Con resultados, una tarjeta por partido con su franja.
- **Pie:** dos columnas (una en móvil). A la izquierda, «Fuentes» plegado: los programas oficiales con su enlace y páginas, y la fecha de los datos. A la derecha, «¿Has visto un error o quieres comentar algo?»: asunto, correo opcional y mensaje, con «Enviar». Se manda por EmailJS y el resultado se anuncia en la misma línea del botón.
- **Al compartir el enlace:** `web/og.png` (1200×630) con el titular y una pregunta de «Dónde chocan», icono `web/icono.png` (180 px, pantalla de inicio del móvil) y favicon `web/favicon.ico` (a 16 px solo «29», para que se lea). Se generan con capturas de las páginas de `pipeline/og/`; el favicon, además, con `pipeline/og/favicon.py`.
- **Ritmo:** 16px entre tarjetas, 26–30px de relleno interior, más aire encima de un encabezado que debajo.
- **Puntos de corte:** 1080, 960, 820, 760 y 640px. A 640px las tarjetas ocupan todo el ancho.

## Elevation & Depth

Plano: fondo gris, tarjetas blancas con un filo de 1px. No hay sombras; al pasar el ratón por una tarjeta enlazada, el filo se oscurece.

## Shapes

16px en tarjetas, 12px en campos, botones y preguntas, 8px en filas de postura y lateral, 6px en siglas. Los chips de filtro y los ejemplos de búsqueda son píldoras, para distinguirlos de la navegación. Los iconos son trazos de 1.4–1.8px y solo aparecen donde dicen algo: lupa, chevrón, flechas de anterior y siguiente, enlace externo y los cuatro de la barra inferior.

## Components

### Buttons
- **Botón principal** (tinta, texto blanco, 40–52px, radio 12px): «Buscar».
- **Botón secundario** (blanco, filo de línea fuerte): «Ver las N preguntas», «Mostrar 40 más».
- **Control segmentado:** cápsula gris con la opción activa en blanco y en negrita. Solo se usa para «Resumen / Texto completo» en la vista de tema.
- **Al pulsar** (`:active`), botones, chips, navegación y cabeceras de tabla se oscurecen un tono. En pantallas táctiles toda zona pulsable mide al menos 44px.

### Chips
- **Filtro de partidos** («Comparar»): píldora de 36px con el punto del partido. Visible: borde continuo y punto lleno. Oculto: borde discontinuo, punto hueco y texto suave; la forma dice el estado, no solo el color. Siempre queda al menos un partido visible, y el filtro no se guarda entre visitas. En la búsqueda llevan el recuento de resultados. En móvil usan la sigla (FA).

### Inputs / Fields
- **Buscador de cabecera** (escritorio): 40px, fondo superficie 2, lupa y la pista «/». Al enfocar pasa a blanco con borde de tinta. En la vista de búsqueda se oculta, porque la caja grande ocupa su lugar.
- **Caja de búsqueda:** 52px, blanca, borde de línea fuerte; al enfocar, borde de tinta doble.

### Navigation
- **Secciones (escritorio):** texto; la activa en negrita con una barra de tinta de 3px pegada al borde inferior de la cabecera.
- **Barra inferior (móvil):** cuatro botones iguales con icono de 22px y texto de 12px; el activo en negrita con una barra de tinta arriba. Reserva su altura y la zona segura del teléfono.
- **Lateral:** lista con recuentos. El activo es una tarjeta blanca con filo y se actualiza al hacer scroll.
- **Pestañas de partido (móvil):** el nombre con su punto y su recuento; la activa en negrita y subrayada con el color del partido.

### Tabla de peso por tema (signature)
Una fila por tema y una columna por partido, con el nombre y su punto en la cabecera. Cada celda lleva arriba la cifra de extractos; debajo, una barra de 6px del color del partido sobre pista gris, de ancho fijo (88px; 52px en móvil) para que se compare igual con 4 que con 12 partidos, y bajo ella, en pequeño, qué porcentaje de todos los extractos del partido trata ese tema. La barra no muestra esa cifra: reparte entre los partidos de la fila esos porcentajes ya normalizados por la extensión de cada programa, y las barras de una fila suman el 100 %. Así la barra más larga es la del partido que más peso da al tema dentro de su programa, no la del que más escribe. Escala fija de 0 a 100 %; la nota de encima lo explica. Al pulsar el nombre de un partido se ordena por su porcentaje; pulsar una fila abre el tema.

### Extracto plegable (signature)
En «Resumen» muestra el titular en sans, un chevrón y dos líneas del texto literal en serif que se desvanecen; pulsar cualquiera de las dos cosas lo despliega. Abierto, enseña el texto completo, la medida, el enlace a la página del PDF y el apartado del programa. Junto al conmutador se avisa: «Los titulares son nuestros; el texto es literal del partido». Abierto, también lleva «Ver en su programa →». Lo que el partido trata en otros subtemas aparece plegado al pie de su columna («Lo trata también en otros subtemas»), como extractos que se despliegan ahí mismo.

### Llegada al programa (signature)
«Ver en su programa» abre el programa entero del partido (migas «Programas › PSOE») con el extracto en su sitio: caja amarilla muy clara, aviso «Subrayada, la cita de «pregunta»» y botón «Volver». Si se llega desde una pregunta, se subraya en amarillo rotulador la frase exacta de la cita (se compara sin espacios); si no, el extracto entero.

### Ficha de pregunta (signature)
La misma ficha en el tema y en «Dónde chocan», para que el lector no vea dos versiones de lo mismo:
1. La pregunta.
2. Las posturas en filas grises. Las siglas (blancas, con filo y su punto) van pegadas al nombre de la postura y alineadas en columna con subgrid, no al otro extremo. No son enlaces. Si nadie defiende una postura, «Ningún partido».
3. Una barra con «Ver la cita de cada partido» (despliega ahí mismo; abierta dice «Ocultar las citas») y, a la derecha, «Todo lo que dicen sobre «subtema»» (en el tema baja al subtema; en «Dónde chocan» lleva al tema).
4. Las citas: una columna por partido, en el orden fijo y con su franja de color, con la postura, la cita literal y «Ver en su programa · p. N →». Cada columna tiene una altura máxima (20rem) y la cita se lee con scroll dentro de ella; a partir del quinto partido, las columnas siguen debajo. Si no se pronuncia, la columna queda en gris con «Su programa no toma una postura explícita». Pasan a 2 columnas entre 820 y 1080px y a 1 por debajo de 640px.

En «Dónde chocan» las citas salen abiertas; en el tema, plegadas. Lo que el lector abre o cierra se respeta al filtrar partidos. En la portada solo se usan las filas de posturas, y la pregunta enlaza a «Dónde chocan».

## Do's and Don'ts

### Do:
- **Do** poner en serif todo texto literal de un partido.
- **Do** dejar el color a los partidos y usar el amarillo solo para lo buscado.
- **Do** enseñar primero titulares y dejar el texto completo a un clic, con la opción de verlo todo desplegado.
- **Do** acompañar cada extracto de su página del PDF original.
- **Do** redactar los estados vacíos como hechos sobre nuestros datos y con la siguiente acción («Prueba con menos palabras…»).
- **Do** dar el porcentaje junto a la cifra absoluta cuando se comparen programas de extensiones distintas, sin obligar a elegir entre las dos.
- **Do** comprobar con la fórmula de WCAG cada par de color de texto (4,5:1) y no fiarse del ojo.
- **Do** dejar que cada visita empiece con todos los partidos visibles.

### Don't:
- **Don't** usar el color de un partido sin su nombre al lado, ni como fondo o color de texto.
- **Don't** cambiar el orden de los partidos entre vistas o entre preguntas.
- **Don't** añadir un color de interfaz propio, degradados, efecto cristal, sombras ni iconos decorativos.
- **Don't** añadir modo oscuro: la web es solo en tono claro.
- **Don't** poner etiquetas pequeñas en mayúsculas encima de los títulos.
- **Don't** usar cifras tabulares con Schibsted Grotesk.
- **Don't** parafrasear el texto de un partido en serif.
- **Don't** meter cajas dentro de cajas más allá de un nivel: tarjeta, y dentro, como mucho, la caja gris de la pregunta.

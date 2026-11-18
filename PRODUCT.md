# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

delegated: HTML, CSS y JavaScript estáticos, sin framework ni paso de compilación de la interfaz. Los datos se generan con Python desde los PDF oficiales (`pipeline/`) y se sirven como un único fichero de datos. Motivo: se puede abrir en local, se aloja en cualquier sitio estático y añadir un partido es volver a ejecutar el pipeline.

## Users

- **Persona que va a votar el 29N** (elecciones generales del 29 de noviembre de 2026), sobre todo en la Comunitat Valenciana. Quiere saber qué propone cada partido sobre un tema concreto, como vivienda o impuestos, y comparar las propuestas. Lo consulta en el móvil y en el ordenador durante la campaña.
- **Quien mantiene el proyecto**, que añade los programas de más partidos a medida que se publican.

## Product Purpose

Consultar íntegros los programas electorales del 29N, ordenados por bloques temáticos y subtemas. El sitio pone juntos los extractos de cada partido sobre el mismo asunto y señala dónde sus posturas chocan, por ejemplo subir o bajar el IRPF. El éxito tiene dos partes:
- en pocos segundos se llega a lo que cada partido dice de un tema;
- no queda fuera ni una línea de ningún programa.

## Positioning

Todo el texto de los partidos es literal: se cita, no se parafrasea. Cada extracto lleva su página del PDF oficial y su lugar en el índice del programa. Lo único que no es del partido es un titular corto y neutral por extracto, que sirve para orientarse, y se distingue a simple vista del texto citado. La cobertura es total y se puede comprobar: cada programa se puede leer entero en su orden original.

## Operating Context

- Campaña electoral, noviembre de 2026.
- Lectura en el móvil durante ratos sueltos y comparación más reposada en el ordenador.
- Los programas fuente son PDF de extensión muy distinta (de 1 a más de 150 páginas) y no siguen la misma estructura.

## Capabilities and Constraints

- **Ruta de navegación:** 17 bloques → 111 subtemas → extractos. Hay 50 ejes de contraste con posiciones enfrentadas, y cada extracto puede marcar posición en uno o varios.
- **Datos actuales:** 10.265 extractos, unas 563.000 palabras, en 28 programas. Por defecto se comparan PP, PSOE, Vox y Frente Amplio; el resto se añade desde «Añadir partidos».
- **Extensible:** añadir partidos no debe obligar a tocar la interfaz. La lista de partidos sale de los datos.
- **Neutralidad:**
  - todos los partidos se tratan igual en orden, tamaño y peso visual;
  - los titulares no valoran;
  - la clasificación por subtemas y ejes es nuestra y debe poder revisarse.
- El Frente Amplio no concurre en las circunscripciones valencianas; allí la candidatura de izquierdas es Compromís-Front Valencià. Su programa también está en la web.

## Evidence on Hand

- **PDF oficiales:** en `descargas/`. Las fuentes y sus hashes están en el front matter de `markdown/*.md`.
- **Markdown fiel:** en `markdown/`. La cobertura está verificada línea a línea contra el PDF.
- **Extractos literales:** en `data/extractos.json`, con la página de cada uno.
- **Taxonomía:** en `data/taxonomia.json`.
- **Clasificación:** en `data/clasif/`.
- **Lo que no hay:**
  - logotipos de los partidos ni permiso para usarlos;
  - encuestas, resultados o valoraciones.

  No se inventan.

## Product Principles

1. El partido habla con sus propias palabras: el texto citado nunca se edita ni se resume.
2. Nada queda fuera: todo extracto está en algún subtema, y cada programa se puede leer entero.
3. Neutralidad visible: mismo trato, mismo orden y ningún color de partido que pese más que otro.
4. La fuente siempre a mano: página y sección del programa en cada extracto.
5. Comparar es la acción principal: lo que dicen los partidos sobre lo mismo aparece junto.

## Accessibility & Inclusion

Texto largo de lectura: contraste AA como mínimo, medida de lectura cómoda y navegación completa con teclado. Debe funcionar bien en móvil.

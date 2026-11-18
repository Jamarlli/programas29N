# Programas 29N

Los programas electorales de las elecciones generales del 29 de noviembre de 2026, ordenados por temas para comparar qué dice cada partido sobre lo mismo.

- **Temas:** 17 bloques y 111 subtemas. En cada subtema, lo que dice cada partido, uno al lado del otro.
- **Dónde chocan:** 40 preguntas de contraste, como «¿Qué hacer con el IRPF?», con la postura de cada partido y la cita de su programa que la justifica.
- **Programas:** cada programa entero, en su orden original.
- **Buscar** en todos los programas a la vez.

Hay 12 programas, de 4.215 extractos. Por defecto se comparan Frente Amplio, PSOE, PP y Vox; el resto se añade desde «Añadir partidos», que también lista las candidaturas del BOE cuyo programa aún no está.

## Criterios

- **El texto de los partidos es literal.** No se resume ni se corrige. Cada extracto lleva la página del PDF oficial del que sale.
- **No falta nada.** Todo el programa está repartido en extractos, y cada extracto está en algún subtema. `pipeline/coverage.py` comprueba que todo el texto del PDF está en el Markdown.
- **Lo que no es del partido se ve.** Los titulares de los extractos, la clasificación por subtemas y las marcas de «Dónde chocan» son nuestros. Se hicieron con un modelo de IA (Claude) siguiendo las instrucciones de [`data/lotes/INSTRUCCIONES.md`](data/lotes/INSTRUCCIONES.md) y [`data/ejes/INSTRUCCIONES.md`](data/ejes/INSTRUCCIONES.md), y se validan con scripts: por ejemplo, cada cita de «Dónde chocan» tiene que aparecer tal cual en el extracto. Si ves una clasificación o una postura mal puesta, abre una issue.

## Ver la web en local

Abre `dist/programas29N.html` en el navegador: es la web entera en un solo fichero. También puedes servir la carpeta `web/`:

```sh
python -m http.server -d web
```

## Publicar

La web es estática y se sirve con Cloudflare Workers (`wrangler.jsonc` publica la carpeta `web/`; `web/_headers` pone las cabeceras de seguridad):

```sh
npx wrangler deploy
```

## Estructura

| Carpeta | Qué hay |
|---|---|
| `web/` | La web: HTML, CSS y JavaScript sin framework. `data.js` se genera. |
| `dist/` | La web en un único HTML. |
| `pipeline/` | Los scripts que convierten los PDF en los datos de la web. |
| `descargas/` | Los PDF oficiales (y alguna página web) tal como los publicó cada partido. |
| `markdown/` | Cada programa convertido a Markdown. La cabecera dice de dónde sale el PDF, su SHA-256 y la fecha de descarga. |
| `data/` | Extractos, taxonomía de temas, clasificación, marcas de «Dónde chocan» y mapa de circunscripciones. |
| `candidaturas/` | Las 84 candidaturas proclamadas en el BOE y el estado del programa de cada una. |

## Pipeline

Todo se ejecuta desde la raíz con `python -I`. Hace falta Python 3.11 con `pymupdf` y `pymupdf4llm`.

1. `candidaturas/programas-estado.py`: estado del programa de cada candidatura (`programas-estado.json`).
2. `pipeline/conv_uno.py <pdf> <salida.raw.md>`: convierte un PDF a Markdown en bruto.
3. `pipeline/limpia_uno.py <id> <bruto>`: limpieza general más la propia de cada partido (`pipeline/limpia/<id>.py`). Escribe `markdown/<CLAVE>_2026_programa.md`.
4. `pipeline/coverage.py <pdf> <md>`: comprueba que no se ha perdido texto.
5. `pipeline/segment.py`: trocea los programas en extractos con su página (`data/extractos.json`).
6. `pipeline/lotes.py`: reparte los extractos en lotes para clasificarlos.
7. `pipeline/validar_clasif.py`: valida cada lote clasificado contra la taxonomía.
8. `pipeline/fusionar_clasif.py`: une los lotes en `data/clasificacion.json`.
9. `pipeline/ejes_candidatos.py`: prepara los extractos candidatos de cada pregunta de «Dónde chocan».
10. `pipeline/validar_ejes.py`: comprueba las marcas y que cada cita sea literal.
11. `pipeline/mapa_ccaa.cjs`: genera el mapa de circunscripciones (Node; las dependencias están en la cabecera del script).
12. `pipeline/build_web.py .`: genera `web/data.js`.
13. `pipeline/bundle.py`: genera `dist/programas29N.html`.

Los cuatro primeros programas (PP, PSOE, Vox y Frente Amplio) se convirtieron con `conv.py`, `clean.py` y `finalize.py`, y se comprobaron con `verify.py`. Los demás usan `conv_uno.py` y `limpia_uno.py`.

## Licencias

- **Código** (`web/`, `pipeline/` y los scripts): [MIT](LICENSE).
- **Datos propios** (titulares, clasificación por temas, marcas de «Dónde chocan», taxonomía, mapa y listado de candidaturas): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es). Puedes reutilizarlos citando la fuente.
- **Fuentes tipográficas** (Newsreader y Schibsted Grotesk, en `web/fonts/`): [SIL Open Font License 1.1](web/fonts/). Se sirven desde la propia web, sin pasar por Google Fonts.
- **Los programas electorales son de cada partido.** Los PDF de `descargas/`, su conversión en `markdown/` y el texto literal de los extractos no están cubiertos por ninguna de las dos licencias; se incluyen para que todo se pueda comprobar.

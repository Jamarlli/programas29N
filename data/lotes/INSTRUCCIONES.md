# Clasificación de extractos de programas electorales (29N 2026)

Los programas electorales están troceados en extractos literales, y una web los va a mostrar por temas para que se pueda comparar qué dice cada partido sobre cada asunto. El texto de los extractos **no se toca**. Tu trabajo es añadir a cada uno sus metadatos de clasificación.

## Entrada
- `data/taxonomia.json`:
  - `bloques[].subtemas[]` lista los subtemas. Cada uno tiene `id`, `nombre` y `incluye`; este último campo dice qué cae dentro.
  - `ejes[]` son preguntas de contraste. Cada eje tiene sus `posiciones` y un `subtema` asociado.
- `data/lotes/lote-NN.json` es tu lote. Cada extracto trae:
  - `id`, `partido` y `tipo` ("medida" o "texto");
  - `numero`;
  - `ruta`: los títulos del programa bajo los que está;
  - `texto`, el contenido literal.

## Salida
Escribe `data/clasif/lote-NN.json`: un array JSON con **un objeto por extracto del lote**, en el mismo orden.

```json
{"id": "pp-0042", "subtema": "imp-irpf", "otros": ["fam-natalidad"], "titular": "Deflactar el IRPF cada año según la inflación", "ejes": [{"eje": "eje-irpf", "posicion": "bajar"}], "nota": ""}
```

### `subtema` (obligatorio)
Es el id del subtema que mejor describe **de qué trata el extracto**:
- Usa el contenido, no el título de la sección. Una medida fiscal sobre vivienda dentro del capítulo de impuestos va a `vivienda-fiscalidad` si trata de la vivienda.
- Para textos introductorios, diagnósticos o balances generales que no proponen nada concreto, usa `pres-diagnostico`.
- Si el texto introduce un capítulo temático, por ejemplo la entradilla del capítulo de vivienda, usa el subtema general de ese bloque: `vivienda-derecho`, `imp-modelo`, `eco-modelo`, etc.

### `otros`
Pon 0, 1 o 2 ids más, solo si el extracto contiene **una propuesta concreta** de ese otro subtema, no una simple mención.

### `titular` (obligatorio)
Es una frase corta en español, de 4 a 12 palabras como máximo 14, que dice qué propone o qué afirma el extracto. Reglas:
- Es neutral y descriptivo. Usa el vocabulario del propio partido: si el partido escribe «okupación», tú escribes «okupación»; si escribe «personas migrantes», tú también.
- No valores, no adjetives y no añadas nada que el texto no diga.
- Para una medida, empieza en infinitivo o con el sustantivo de la acción: «Bajar el IVA de la luz al 5 %», «Prohibir la compra especulativa de vivienda».
- Para un texto expositivo, resume la idea: «Diagnóstico: la vivienda como principal problema de los jóvenes».
- Escribe en mayúscula solo la inicial y los nombres propios, aunque el partido escriba el título en mayúsculas.
- No nombres al partido.
- Si el extracto trae cifras clave (porcentajes, cantidades, plazos), inclúyelas cuando quepan.

### `ejes`
Añade una posición en un eje **solo si el texto la toma de forma explícita**. Por ejemplo, «derogaremos la Ley de Vivienda» marca `eje-ley-vivienda` como `derogar`. En cambio, una medida de vivienda pública que no habla de la ley no marca nada.
- Un extracto puede marcar varios ejes, también ejes de un subtema distinto al suyo.
- La mayoría de los extractos no marcan ninguno. Ante la duda, no marques.

### `nota`
Normalmente va vacía. Úsala en dos casos:
- Si ningún subtema encaja bien: escribe `"SIN ENCAJE: <qué subtema faltaría>"` y pon igualmente el más cercano en `subtema`.
- Si el texto contiene una postura clara y contrastable que no tiene eje: escribe `"EJE NUEVO: <pregunta> → <posición>"`.

## Comprobación (obligatoria)
Al terminar, ejecuta:

```
python -I pipeline/validar_clasif.py data/taxonomia.json data/lotes/lote-NN.json data/clasif/lote-NN.json
```

desde la raíz del proyecto. Corrige hasta que diga `OK`.

Escribe el fichero con la herramienta Write. Si el lote es largo, escríbelo en varias partes a ficheros temporales `data/clasif/lote-NN.parteK.json` y únelos al final con un pequeño script de Python; luego borra las partes. **Lee todos los extractos de verdad**: no clasifiques por la ruta ni por palabras clave.

## Informe final
Responde con:
- el resultado del validador;
- cuántos extractos marcaron algún eje;
- la lista de notas «SIN ENCAJE» y «EJE NUEVO», agrupadas y deduplicadas;
- tres o cuatro casos dudosos que convenga revisar.

No pegues el JSON en la respuesta.

# Revisión de ejes de contraste (programas del 29N)

Una web compara los programas electorales del 29N. Tiene una sección, «Dónde chocan», que muestra preguntas de contraste, por ejemplo «¿Qué hacer con el IRPF?». Para cada pregunta enseña qué partidos defienden cada posición, **con una cita literal de su programa** que lo justifica.

Tu trabajo es decidir esas marcas para los ejes de tu grupo. La web las va a mostrar como hechos, así que deben ser **exactas, justificadas y neutrales**.

## Entrada
`data/ejes/candidatos-NN.json` es una lista de ejes. Cada eje trae:
- `eje`, `pregunta` y `posiciones` (id y nombre);
- `candidatos`: los extractos que podrían tomar postura. De cada uno vienen `id`, `partido`, `titular` (orientativo, no es del partido), `marca_actual` (lo que propuso un primer clasificador, que puede estar mal o faltar) y `texto` (literal).

## Qué marcar
Lee **todos** los candidatos de cada eje. Marca un extracto con una posición solo si el texto **propone o defiende de forma explícita** algo que encaja en esa posición:
- **Lo que no cuenta.** Mencionar el tema no basta. Una inferencia («si propone X, seguramente quiere Y») tampoco basta.
- **Un mismo partido puede tener varias posiciones en un eje.** Por ejemplo, bajar el IRPF a rentas bajas y subirlo a las altas. Márcalas todas, cada una con su cita.
- **Si varios extractos del mismo partido dicen lo mismo,** márcalos todos. La web los agrupa por partido.
- **Balances de gobierno:** valen si dejan clara una postura sobre el futuro, por ejemplo «seguiremos subiendo el SMI». Si solo describen el pasado, no valen.
- **Medidas limitadas:** si la medida es sectorial o acotada, márcala igual en la posición que corresponda. La cita ya muestra el alcance. Por ejemplo, «IVA superreducido para la primera vivienda» va a `bajar` en `eje-iva`.
- **Ninguna posición encaja bien** pero el texto toma postura clara: no fuerces la marca. Anótalo en el informe final.

## Cita
`cita` es un fragmento **copiado literalmente** del `texto` del extracto, de 5 a 40 palabras. Es la frase que demuestra la postura:
- Puedes cortar por el principio y por el final.
- No puedes cambiar ni saltarte palabras del medio.
- Los asteriscos `**` y guiones bajos `_` de formato se pueden omitir.

## Salida
Escribe `data/ejes/marcas-NN.json` con la herramienta Write. Es un array con una entrada por marca:

```json
[{"eje": "eje-irpf", "id": "fa-0316", "posicion": "bajar", "cita": "Bajaremos el IRPF a quienes cobran menos de 27.000 euros"}]
```

Un eje puede quedar sin ninguna marca si nadie toma postura explícita.

## Comprobación (obligatoria)
Ejecuta desde la raíz del proyecto:

```
python -I pipeline/validar_ejes.py data/ejes/candidatos-NN.json data/ejes/marcas-NN.json
```

Corrige hasta que diga `OK`. El error más frecuente es una cita que no es literal: cópiala tal cual del texto.

## Informe final
- Resultado del validador.
- Una tabla por eje: posición → partidos con número de extractos.
- Las tomas de postura que no encajaban en ninguna posición, si las hay. Indica qué posición o qué reformulación del eje haría falta.
- Ejes que se queden con un solo partido o sin marcas.

No pegues el JSON.

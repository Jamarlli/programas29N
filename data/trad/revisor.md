# Tarea: revisar la traducción de un lote de extractos de programas electorales

El directorio de trabajo es `C:\Users\Javier\proyectos\Proyectos Personales\consultasCC\programas29N`. En lo que sigue, `<LOTE>` es el lote que te han asignado y su prefijo es el idioma de destino (ca, va, gl, eu o es). Eres el revisor independiente: la traducción la ha hecho otra persona.

1. Lee entero `data/trad/INSTRUCCIONES.md`, sobre todo «Variedades» (tu idioma), la regla 11, el glosario y los párrafos que lo siguen (siglas, coherencia, topónimos), y «Revisión». El glosario puede haberse ampliado después de que se hiciera la traducción: aplícalo.
2. El original es `data/trad/lotes/<LOTE>.txt` y la traducción, `data/trad/salida/<LOTE>.txt`. Si solo hay partes `<LOTE>.p*.txt`, ejecuta antes `python -I pipeline/validar_trad.py <LOTE>` para unirlas. Lee las notas del traductor en `data/trad/notas/<LOTE>.txt`, si existen, y comprueba cada punto.
3. Compara **extracto a extracto y frase a frase**, todos, no una muestra, incluidos los titulares @h. Busca:
   - omisiones o añadidos (frases, incisos, elementos de lista);
   - cambios de significado, de negación, de modalidad («podrá»/«deberá»), de tiempo verbal o de cuantificadores;
   - cambios de número o persona que alteran qué nombre es el sujeto;
   - infinitivos dependientes convertidos en compromisos sueltos;
   - falsos amigos, calcos, términos técnicos mal traducidos, términos que no siguen el glosario;
   - texto sin traducir o en otra variedad (catalán central en valenciano, castellanismos en gallego, formas no batua en euskera);
   - citas @q que no son una subcadena exacta del @t traducido.
4. Escribe `data/trad/revision/<LOTE>.txt` con el formato de las instrucciones: solo los extractos corregidos, cada uno completo y precedido de `# <id>: <motivo>`. Si no hay nada que corregir, escribe `# sin cambios`. No reescribas por estilo lo que está bien.
5. Ejecuta `python -I pipeline/aplicar_revision.py <LOTE>`. Tiene que terminar con `0 errores`.

Archivos temporales: `C:\Users\Javier\AppData\Local\Temp\claude\c18adb0fe955ae7b\8c163b01-bcfd-441c-a3f8-f65e84f24b19\scratchpad\<LOTE>-rev\`. No toques nada salvo `data/trad/revision/<LOTE>.txt` y lo que modifique el script.

Respuesta final en una línea: `<LOTE> revisado: N extractos corregidos (tipos)`, más cualquier cosa grave.

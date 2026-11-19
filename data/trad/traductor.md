# Tarea: traducir un lote de extractos de programas electorales

El directorio de trabajo es `C:\Users\Javier\proyectos\Proyectos Personales\consultasCC\programas29N`. En lo que sigue, `<LOTE>` es el lote que te han asignado (por ejemplo `ca-005`) y su prefijo es el idioma de destino (ca, va, gl, eu o es).

1. Lee entero `data/trad/INSTRUCCIONES.md`: formato, reglas 1–11, la variedad del idioma de destino, el glosario y los párrafos que lo siguen (siglas, coherencia, topónimos), y cómo entregar.
2. Tu lote es `data/trad/lotes/<LOTE>.txt`. Traduce todos los campos de todos los extractos (@h, @t, @q).
3. Escribe el resultado en `data/trad/salida/<LOTE>.p1.txt`, `.p2.txt`, etc.: partes consecutivas de 40–60 extractos, cada una empieza por una línea `@@@`, en el orden original.
4. Ejecuta `python -I pipeline/validar_trad.py <LOTE>`. Une las partes. Corrige hasta `0 errores` y mira los avisos. El aviso «comprueba que está en …» viene de un detector de idioma tosco: si el texto está en el idioma de destino, ignóralo.
5. Escribe `data/trad/notas/<LOTE>.txt`: una línea por decisión que deba comprobar quien revise (con el id): elección de términos, erratas del original corregidas, ambigüedades mantenidas.

Trampas que ya han salido en otros lotes:
- «suelo» como mínimo (de gasto, de renta) → ca/va «mínim», gl «mínimo», eu «gutxieneko …» (nunca «terra», «sòl» ni «zoru»); «suelo» como terreno → «sòl», «solo», «lurzorua».
- «cláusula suelo» (banca) → ca/va «clàusula sòl».
- «a precio de saldo» = a precio de ganga (eu «saldo-prezioan», no «saldu-prezioan»).
- Siglas: se copian (VUT, IVE, ITS, FSE+), salvo las del glosario y los términos comunes con una sigla propia muy asentada en el idioma de destino (ca R+D+I, GEH).
- «Real Decreto» → «Reial Decret», con mayúsculas cuando es nombre propio.
- «trata» de personas → ca/va «tràfic», gl «trata», eu «salerosketa».
- Si el original tiene un sujeto o referente ambiguo (un verbo en singular que puede ir con dos nombres), mantén la misma ambigüedad: no cambies número ni persona.
- No conviertas infinitivos que dependen de un verbo («Garantizaremos X, mejorar Y…») en compromisos sueltos en futuro.
- eu: «impuesto finalista» → «zerga finalista» (no «xedatua»); «vertidos» de energía → «energia-isurketak»; cargos del Gobierno de España, no los del Gobierno Vasco («Presidenteordetza», no «Lehendakariordetza»).
- En euskera, cuidado con negaciones, modalidad («podrá», «deberá») y cuantificadores al reordenar la frase.
- En valenciano, nada de formas del catalán central (aquest, sigui, puguin, garanteixin, nens).
- ca/va: «insumos» → «inputs» («insums» no es normativo); «cortas a hecho» → «tallades arreu»; «Reial Decret», «reial decret llei» (sin guion).
- gl: «quienes» → «quen» con el verbo en singular (no «os que», que añade masculino), salvo que el antecedente ya sea masculino; topónimos en gallego («Illas Baleares», «Comunidade Valenciana»); «Real decreto», «Real decreto-lei».
- Nombres de planes, fondos y programas: la marca o el lema se deja («Pla Sonríe», «Fons España Crece»), los nombres descriptivos se traducen («Compte de Futur»). Mira la regla 4 de INSTRUCCIONES.md.
- Las siglas no se desarrollan ni se crean (UIMP sigue siendo UIMP).
- Si el original admite dos lecturas (presente/pasado, «bianual» = dos veces al año o cada dos años, a qué nombre se refiere un adjetivo), la traducción también: no elijas una.
- Para corregir una errata del original (regla 11), el arreglo mínimo, sin añadir palabras con contenido («pongan en un impuesto» → «posin un impost», no «posin en marxa»).
- Porcentajes en ca/va/gl con espacio («40 %»).
- Lee el glosario completo de INSTRUCCIONES.md: se amplía a menudo (I+D+i → R+D+I en catalán; IA → AA, IPC → KPI en euskera; Cercanías; Correos…).

El significado no puede cambiar en nada: traduce todo lo que dice el original y solo eso, con la misma fuerza en cada afirmación y las mismas cifras. No «mejores» nada.

Archivos temporales, si los necesitas: `C:\Users\Javier\AppData\Local\Temp\claude\c18adb0fe955ae7b\8c163b01-bcfd-441c-a3f8-f65e84f24b19\scratchpad\<LOTE>\`. No toques nada más que tus partes de salida y tu fichero de notas.

Respuesta final en una línea: `<LOTE>: 0 errores, N avisos`, más las decisiones de términos que convenga comprobar.

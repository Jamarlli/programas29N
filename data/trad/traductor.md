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
- okupa/ocupa: se respeta la palabra exacta del original. «okupación» → «okupació», «ocupación» → «ocupació», «okupa» → «okupa»; «il·legal» solo si el original dice «ilegal». Nunca añadas calificativos.
- «Ley de Montes» → ca/va «Llei de Forests» (traducción oficial del BOE); «monte» forestal → «mont/monts».
- Léxico valenciano: compruébalo en el DNV de la AVL. Caza: «montería» → «munteria», «rehala» → «gossada»; «galápago» → «tortuga d'aigua».
- Títulos de informes, libros y documentos (en cursiva _…_ o entre comillas, también en anexos de fuentes): se dejan en el idioma original. El validador ya no los cuenta como «sin traducir»; si un extracto queda igual que el original por eso, sale como aviso y está bien.
- «salario/renta mediano/a» (la mediana) → ca/va «salari medià», «renda mediana»; gl «salario mediano»; eu «soldata mediana». Nunca «mitjà/medio/batez bestekoa», que es la media.
- ca/va: «como» para dar ejemplos → «com» o «com ara» (nunca «com a», que es «en calidad de»). «empleo de hogar» → «treball de la llar»; «empleadas de hogar» → «empleades de la llar».
- No añadas palabras para que suene más natural si se puede decir sin ellas.
- ca/va: «quienes» → «qui» con el verbo en PLURAL («qui tenen», «les persones que tenen»), nunca en singular. «a bajo coste» → «a baix cost» (barato), no «per davall del cost».
- «pyme/PYME/Pyme» → «pime/PIME/Pime» (ca/va) con la misma caja que el original: si el original va en minúscula, minúscula; si va en mayúscula, mayúscula.
- Palabras coloquiales o de jerga sin entrada en el diccionario normativo van entre comillas: «pelotazo urbanístico» → «pelotasso urbanístic».
- No cambies el número gramatical (un plural sigue en plural) ni añadas o quites la coma delante de una relativa: «los derivados que son…» (especificativa) no es «los derivados, que son…» (explicativa).
- En valenciano, nada de formas del catalán central (aquest, sigui, puguin, garanteixin, nens).
- ca/va: «insumos» → «inputs» («insums» no es normativo); «cortas a hecho» → «tallades arreu»; «Reial Decret», «reial decret llei» (sin guion).
- gl: «quienes» → «quen» con el verbo en singular (no «os que», que añade masculino), salvo que el antecedente ya sea masculino; topónimos en gallego («Illas Baleares», «Comunidade Valenciana»); «Real decreto», «Real decreto-lei».
- Nombres de planes, fondos y programas: la marca o el lema se deja («Pla Sonríe», «Fons España Crece»), los nombres descriptivos se traducen («Compte de Futur»). Mira la regla 4 de INSTRUCCIONES.md.
- Las siglas no se desarrollan ni se crean (UIMP sigue siendo UIMP).
- Si el original admite dos lecturas (presente/pasado, «bianual» = dos veces al año o cada dos años, a qué nombre se refiere un adjetivo), la traducción también: no elijas una.
- Para corregir una errata del original (regla 11), el arreglo mínimo, sin añadir palabras con contenido («pongan en un impuesto» → «posin un impost», no «posin en marxa»).
- Porcentajes en ca/va/gl con espacio («40 %»).
- va: «paro» → «atur», «desempleo» → «desocupació», «empleo» → «ocupació»; «ocupación» de viviendas → «ocupació» (sin añadir «il·legal» ni nada que no diga el original).
- Nunca añadas calificativos que no están en el original, aunque parezca que aclaran.
- eu: siglas vascas asentadas de términos comunes, ya usadas en eu-001…005: IBI → OHZ, VIH → GIB, AOD → GLO, ONGD → GGKE, OCDE → ELGA, FP → LH. «seguridad humana» → «giza segurtasuna»; «financiación finalista» → «finantzaketa finalista» (no «xedatua»). Las siglas de organismos, leyes y planes se copian (CGPJ, AECID, LOPJ…).
- eu: porcentajes con el signo delante y pegado: «%25», «%2,5».
- eu: abreviaturas con punto declinadas sin guion (Euskaltzaindia, araua 196): «CC. AA.ei», «AA.PP.ekin», no «CC. AA.-ei». Se respeta el espaciado del original.
- eu: ILP se copia (HEL no está asentada); OCDE → ELGA; «Comité Europeo de las Regiones» → «Europako Eskualdeetako Batzordea»; «vigilancia» → «zaintza» («bijilantzia» no es batua); «vapear» → «bapeatu».
- eu: no añadas «emakume» a un nombre que en el original no marca género («niñas y jóvenes» → «neskak eta gazteak»). Sí cuando el original usa el femenino («ganaderas» → «emakume abeltzainak»).
- eu: un subjuntivo no es «poder»: «se ha aceptado que las competencias entren» → «sartzea», no «sar daitezkeela». Pon «ahal»/«-ke» solo donde el original dice «poder».
- eu: «del Fondo», «del SNS» y otros genitivos: no amplíes a qué se refieren al reordenar («ampliado la duración y triplicado el anticipo del Fondo» → la duración no se ata al Fondo).
- eu: la sigla IA → AA también dentro de nombres de planes («Bono IA» → «AA Bonua»): es la sigla del término común, no parte de la marca.
- eu: «País Valencià» → «Valentziako Herrialdea» (no se deja en catalán); València → Valentzia. OMS → OME, ONG → GKE, ESO → DBH, UCI → ZIU (siglas vascas asentadas, como ELGA). Lema de Vox «ES SENTIDO COMÚN» → «ZENTZU KOMUNA DA».
- eu: caza y especies (Ehiza eta Arrantza hiztegia, Elhuyar): «montería» → «mendi-ehiza», «rehala» → «ehiza-txakur saldo», «batida/ojeo» → «uxaldi», «cetrería» → «falkoneria», «galápago» → «apoarmatu», «cotorra argentina» → «papagai argentinarra», «calima» → «hauts-gandu». «Ley de Costas» → «Kosten Legea»; «Ley de Montes» → «Mendien Legea».
- eu: cuidado con el alcance de «bakarrik», «ere» y de los adjetivos al reordenar: un adjetivo que el original aplica a dos nombres («ràtios i llistes d'espera màxims») sigue aplicándose a los dos («gehieneko biztanleria-ratio eta itxaron-zerrenda»).
- eu: CSIC → «Ikerketa Zientifikoen Kontseilu Gorena» (no «Nagusia»); «copago» → «koordainketa»; «lanzamiento» de vivienda → «botatze» (LEC en euskera; «kaleratze» es «despido»); ETT → ABLE; ERE → EEE («enplegu-erregulazioko espedientea»); «diligencia debida» → «behar bezalako arreta»; «desalojo» → «hustuketa»; «sinhogarismo» → «etxegabetasuna»; «fijos discontinuos» → «aldizkako kontratu finkoak»; «mínimo vital de agua» → «bizitzeko gutxieneko ur-kopurua». Títulos de informes sin comillas ni cursiva («Informe Planeta Vivo») también se dejan en el original.
- Lee el glosario completo de INSTRUCCIONES.md: se amplía a menudo (I+D+i → R+D+I en catalán; IA → AA, IPC → KPI en euskera; Cercanías; Correos…).

El significado no puede cambiar en nada: traduce todo lo que dice el original y solo eso, con la misma fuerza en cada afirmación y las mismas cifras. No «mejores» nada.

Archivos temporales, si los necesitas: `C:\Users\Javier\AppData\Local\Temp\claude\c18adb0fe955ae7b\8c163b01-bcfd-441c-a3f8-f65e84f24b19\scratchpad\<LOTE>\`. No toques nada más que tus partes de salida y tu fichero de notas.

Respuesta final en una línea: `<LOTE>: 0 errores, N avisos`, más las decisiones de términos que convenga comprobar.

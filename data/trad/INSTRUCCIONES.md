# Traducción de los programas electorales del 29N

Programas 29N muestra los programas electorales de las elecciones generales del 29 de noviembre de 2026 ordenados por temas. La web está en cinco idiomas: castellano (es), catalán (ca), valenciano (va), gallego (gl) y euskera (eu). Cada programa se muestra en su idioma original y traducido a los demás. Un lector tiene que poder fiarse de que la traducción dice **exactamente lo mismo** que el programa: ni más, ni menos, ni con otro tono.

## Qué hay en cada lote

`data/trad/lotes/<idioma>-NNN.txt` contiene una serie de extractos:

```
@@@ <id>
@h
<titular: lo hemos escrito nosotros, en castellano>
@t
<texto literal del programa, en Markdown>
@q
<cita: un trozo literal del texto de ese mismo extracto>
```

- `@h` falta cuando no hay que traducir el titular; `@t` y `@q` faltan cuando el texto ya está en el idioma de destino.
- `@t` puede estar en castellano, catalán, valenciano o gallego: cada programa está en su idioma.
- En los lotes `<idioma>-rutas.txt` cada entrada tiene un solo campo, `@s`. Es el título de un apartado del programa o, en las entradas `titulo:<partido>`, el título del programa entero.

## Qué hay que entregar

Un fichero con **la misma estructura**: los mismos `@@@ id` en el mismo orden y los mismos campos, cada uno con su traducción. Va en `data/trad/salida/<lote>.txt`.
- Si es largo, escríbelo en partes consecutivas: `data/trad/salida/<lote>.p1.txt`, `.p2.txt`… Cada parte empieza en una línea `@@@`. El validador las une.
- Después ejecuta `python -I pipeline/validar_trad.py <lote>` y corrige **todos** los errores hasta que salga `0 errores`.
- Mira también los avisos. Una longitud distinta puede estar bien, pero compruébalo.

## Reglas de traducción: el significado no se toca

1. **Traduce todo y solo lo que dice el original.**
   - No resumas, no omitas frases ni incisos, no añadas explicaciones.
   - No «mejores» el texto ni corrijas sus errores. Si el original es ambiguo, la traducción también tiene que serlo.
2. **Mantén la fuerza de cada afirmación.**
   - El mismo tiempo y modo verbal: «impulsaremos» → «impulsarem», no «impulsaríamos» ni «proponemos impulsar».
   - La misma negación y la misma modalidad: «podrá», «deberá», «garantizaremos», «estudiaremos».
   - Los mismos cuantificadores: «todos», «algunos», «al menos», «hasta», «más de».
   - Los mismos sujetos, en la misma persona: el partido habla en primera del plural.
3. **Las cifras, tal como están escritas.**
   - Si el original pone «2,5 %», «1.000 millones», «LO 1/2026» o «artículo 47», la traducción lleva las mismas cifras, con el formato del idioma de destino.
   - Si el original escribe un número en letras («dos años»), va en letras. No conviertas letras en cifras ni cifras en letras.
   - Los porcentajes en euskera se escriben con el signo delante: «%25». Las cifras siguen siendo las mismas.
4. **Nombres propios.**
   - Los nombres de partidos, coaliciones y personas no se traducen.
   - Tampoco se traducen las marcas ni los nombres oficiales de entidades que no tienen traducción establecida (SAREB, Casa 47, SEPES, Rodalies, FGC, Osakidetza…).
   - Las instituciones del Estado y las de la UE se traducen con su nombre habitual en el idioma de destino. Mira el glosario.
   - Las leyes: se traduce la parte descriptiva y se mantienen el número y la fecha («Ley 12/2023, de 24 de mayo, por el derecho a la vivienda»).
5. **Lo que ya está en otro idioma se queda como está:** una frase en inglés, en latín o, en un programa en castellano, un lema en catalán o en euskera.
6. **El estilo del original.**
   - Si usa lenguaje inclusivo («vecinas y vecinos», «todas y todos»), mantenlo con el recurso equivalente, y no lo añadas donde no está.
   - Las MAYÚSCULAS, la negrita, la cursiva y las comillas se mantienen.
   - El registro es el de un programa político: formal, claro y natural en el idioma de destino. Que no se note que es una traducción, sin que eso cambie el contenido.
7. **La forma del Markdown, línea a línea.**
   - El texto traducido tiene el mismo número de líneas que el original, con las líneas en blanco en el mismo sitio.
   - Cada línea empieza igual: la misma sangría, la misma marca de lista («- », «* », «12. », «**89 »).
   - Lleva el mismo número de `**` (las negritas se mantienen y cubren lo mismo).
   - No unas ni partas líneas aunque una frase siga en la línea siguiente.
8. **Las citas (`@q`).**
   - Cada cita traducida tiene que ser **copia exacta** del trozo correspondiente de tu traducción del `@t`: el validador lo comprueba.
   - Primero traduce el texto y después copia de él el trozo que corresponde a la cita.
9. **Los titulares (`@h`)** son resúmenes nuestros en castellano. Tradúcelos con naturalidad, igual de cortos y sin añadir ni quitar ideas.
10. **Si dudas de cómo traducir un término**, elige la versión más literal que suene natural. No elijas la más bonita.
11. **Errores del original.**
    - Los datos, nombres, cifras, siglas y referencias legales se copian tal cual, aunque parezcan erróneos («Ley 26/1996», «Sociedad Tenedoras»).
    - Si el original tiene un error puramente gramatical (una concordancia, una palabra repetida, un verbo sin conjugar) y el sentido está claro, tradúcelo en forma correcta, con ese mismo sentido.
    - Si el sentido no está claro, tradúcelo lo más literal posible y no lo interpretes.

Al acabar, apunta en `data/trad/notas/<lote>.txt` las decisiones que conviene revisar: términos dudosos, errores del original que hayas corregido (regla 11) y pasajes oscuros que hayas dejado literales, cada uno con su id. Quien revise el lote lo leerá.

Si necesitas ficheros de trabajo (por ejemplo, una vista intercalada para comparar), créalos en una carpeta propia con el nombre del lote (`…/scratchpad/<lote>/`): hay otros traductores y revisores trabajando a la vez.

## Variedades

- **ca (catalán):** catalán estándar (IEC), el registro de la administración y la prensa en Cataluña.
- **va (valenciano):** valenciano normativo de la Acadèmia Valenciana de la Llengua, el de la Generalitat Valenciana y À Punt.
  - Demostrativos «este, esta, estos, estes, eixe, eixa».
  - Incoativos en -ix: «garantix, oferix, servixen».
  - Subjuntivo en -e: «que garantisca, que puga, que siga, que tinga».
  - Primera persona del presente en -e: «propose». Pero «proposem, impulsarem», como en catalán.
  - Vocabulario: «hui, eixir, huit, xiquet, servici, vore» solo si encaja en registro formal; «veure» y «servei» también son correctos. Sé coherente en todo el lote.
  - No lo escribas en catalán central: nada de «aquest», «sigui», «puguin», «garanteixin», «nens».
- **gl (gallego):** gallego normativo de la RAG (norma de 2003), el de la Xunta y la CRTVG. No uses la norma reintegracionista.
  - Formas «-ble» («posible», «sustentable»).
  - Contracciones normativas: «co, coa, polo, pola, nun, nunha».
  - Colocación correcta del pronombre átono: «comprometémonos», «que nos comprometemos».
- **eu (euskera):** euskera batua según las normas de Euskaltzaindia, el registro de las instituciones vascas y de EITB.
  - Frases naturales en euskera: reordena dentro de la frase lo que haga falta, pero sin cambiar el contenido.
  - Respeta la regla de las líneas: lo que está en una línea sigue en esa línea.
- **es (castellano):** castellano estándar de España.

## Glosario (términos que tienen que salir siempre igual)

| castellano | ca / va | gl | eu |
|---|---|---|---|
| Congreso de los Diputados | Congrés dels Diputats | Congreso dos Deputados | Diputatuen Kongresua |
| Senado | Senat | Senado | Senatua |
| Cortes Generales | Corts Generals | Cortes Xerais | Gorte Nagusiak |
| Gobierno (de España) | Govern (d'Espanya) | Goberno (de España) | (Espainiako) Gobernua |
| Constitución | Constitució | Constitución | Konstituzioa |
| comunidad autónoma | comunitat autònoma | comunidade autónoma | autonomia-erkidegoa |
| Estado | Estat | Estado | Estatua |
| Unión Europea (UE) | Unió Europea (UE) | Unión Europea (UE) | Europar Batasuna (EB) |
| Seguridad Social | Seguretat Social | Seguridade Social | Gizarte Segurantza |
| IRPF | IRPF | IRPF | PFEZ |
| IVA | IVA | IVE | BEZ |
| impuesto de sociedades | impost de societats | imposto de sociedades | sozietateen gaineko zerga |
| PIB | PIB | PIB | BPG |
| salario mínimo interprofesional (SMI) | salari mínim interprofessional (SMI) | salario mínimo interprofesional (SMI) | lanbide arteko gutxieneko soldata (LGS) |
| OTAN | OTAN | OTAN | NATO |
| ONU | ONU | ONU | NBE |
| vivienda | habitatge | vivenda | etxebizitza |
| alquiler | lloguer | aluguer | alokairua |
| desahucio | desnonament | desafiuzamento | etxegabetzea |
| okupación / okupa | ocupació il·legal / okupa | ocupación ilegal / okupa | okupazioa / okupa |
| sanidad pública | sanitat pública | sanidade pública | osasun publikoa |
| pensiones | pensions | pensións | pentsioak |
| autónomos | autònoms | autónomos | autonomoak |
| fondos buitre | fons voltor | fondos voitre | putre-funtsak |
| Fuerzas y Cuerpos de Seguridad del Estado | Forces i Cossos de Seguretat de l'Estat | Forzas e Corpos de Seguridade do Estado | Estatuko Segurtasun Indar eta Kidegoak |
| Guardia Civil / Policía Nacional | Guàrdia Civil / Policia Nacional | Garda Civil / Policía Nacional | Guardia Zibila / Polizia Nazionala |
| Tribunal Constitucional | Tribunal Constitucional | Tribunal Constitucional | Konstituzio Auzitegia |
| Tribunal Supremo | Tribunal Suprem | Tribunal Supremo | Auzitegi Gorena |
| ley orgánica | llei orgànica | lei orgánica | lege organikoa |
| real decreto(-ley) | reial decret (llei), sin guion (IEC 2016) | real decreto(-lei) | errege-dekretua (errege lege-dekretua) |
| Agencia Tributaria | Agència Tributària | Axencia Tributaria | Zerga Agentzia |
| «suelo» como mínimo (de gasto, de renta) | mínim | mínimo | gutxieneko … |
| «topar» (poner un límite máximo) | posar topall / limitar | poñer teito / limitar | muga jarri / mugatu |
| Ministerio de … | Ministeri de … | Ministerio de … | …ko Ministerioa |
| trata (de seres humanos, de personas) | tràfic (d'éssers humans, de persones) | trata (de seres humanos, de persoas) | (gizakien, pertsonen) salerosketa |
| pymes | pimes | pemes | ETE (enpresa txiki eta ertainak) |
| I+D+i | R+D+I | I+D+i | I+G+B |
| inteligencia artificial (IA) | intel·ligència artificial (IA) | intelixencia artificial (IA) | adimen artifiziala (AA) |
| IPC | IPC | IPC | KPI |
| TIC | TIC | TIC | IKT |
| Banco Central Europeo (BCE) | Banc Central Europeu (BCE) | Banco Central Europeo (BCE) | Europako Banku Zentrala (EBZ) |
| Cercanías (servicio de Renfe) | Rodalies (va: Rodalia); pero si el original distingue Cercanías de Rodalies de Catalunya, se deja «Cercanías» | Cercanías | Aldiriak |
| Correos | Correus | Correos | Correos |

Siglas: se copian como están en el original (VUT sigue siendo VUT aunque en otra comunidad se diga HUT), salvo las del glosario, que tienen una forma fija en cada idioma. Excepción: si la sigla abrevia un término común que en el idioma de destino tiene una sigla propia muy asentada para lo mismo, se usa esa (al castellano: ERTO → ERTE, R+D+i → I+D+i, pimes → pymes, EUA → EE. UU.). Las siglas de nombres propios (organismos, leyes, planes) no se cambian. En la duda, se copia.

Coherencia en todos los lotes al castellano: «Cataluña», «Galicia» (también por «Galiza»), «Islas Baleares», «Valle de Arán» para el territorio (las comarcas, en su forma original: «Empordà», «Vallès»; los servicios con nombre propio también: «Rodalies de Catalunya»), «Parlamento de Cataluña» (como en el BOE), pero se dejan los nombres de instituciones que en castellano se usan sin traducir («Generalitat de Catalunya», «Mossos d'Esquadra», «Xunta de Galicia»); «EE. UU.»; porcentajes con espacio («30 %»).

El glosario vale en las dos direcciones, pero al traducir **al castellano** se respeta la palabra que eligió el original: «ocupació il·legal» → «ocupación ilegal» (no «okupación»); «okupació» u «okupa» → «okupación», «okupa».

Topónimos:
- Usa la forma oficial o la habitual en el idioma de destino: ca «Saragossa, Osca, Terol, Conca»; gl «Xixón», «Illas Baleares», «Comunidade Valenciana», «Cataluña»; eu «Iruñea, Gasteiz, Donostia, Nafarroa, Araba, Bizkaia, Gipuzkoa».
- Si no hay una forma establecida, deja el nombre como está.

## Revisión (para quien revisa una traducción)

Se revisa **cada extracto**, no una muestra. Compara frase a frase el original (`data/trad/lotes/<lote>.txt`) con la traducción (`data/trad/salida/<lote>.txt`) y busca:

- frases, incisos o elementos de una lista que falten o sobren;
- cambios de significado: una negación perdida, «podrá» por «deberá», futuro por condicional, «hasta» por «al menos», sujetos cambiados, un término técnico mal traducido (por ejemplo, confundir «desgravación» con «exención»);
- falsos amigos y calcos que en el idioma de destino dicen otra cosa;
- trozos sin traducir, o en otra variedad (catalán central en un lote de valenciano, castellanismos en gallego…);
- incoherencias con el glosario;
- citas (`@q`) que ya no corresponden al trozo del original.

No reescribas lo que está bien solo por estilo. Corrige únicamente errores de significado, de idioma o de variedad, y frases que no se entiendan.

Para entregar la revisión:
1. Escribe `data/trad/revision/<lote>.txt` con **solo los extractos que corriges**, completos y con todos sus campos, en el mismo formato. Antes de cada `@@@` corregido, pon una línea `# <id>: <qué estaba mal, en pocas palabras>`.
2. Si no hay nada que corregir, el fichero contiene solo la línea `# sin cambios`.
3. Después ejecuta `python -I pipeline/aplicar_revision.py <lote>`. Aplica las correcciones y vuelve a validar el lote, y tiene que acabar en `0 errores`.

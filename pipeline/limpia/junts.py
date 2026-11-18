"""Limpieza propia del programa de Junts per Catalunya (Elecciones generales 29N 2026, «Catalunya al centre»).

Junts solo publicó el programa como página web. El PDF lo genera pipeline/junts_pdf.py a partir de una
copia de esa página, así que su estructura es la de la web: título, lema, siete bloques numerados
(«01. El benestar que mereixes, al centre»…) con una frase de entrada y una lista de medidas, cada una
con su título en negrita, y un último bloque «TU» con ocho lemas cortos.

- El aviso del principio («Documento generado a partir de una página web…») es de Programas 29N, no
  del partido: se quita.
- Dos medidas quedan partidas por el salto de página en dos puntos de lista («…de les competències» |
  «- d’immigració…»; «…en mecanismes» | «- europeus/internacionals…»): se vuelven a unir. Se reconocen
  porque el segundo trozo empieza en minúscula.
- Los tres últimos lemas del bloque «TU» pierden el «- » en la conversión: se les devuelve.
"""
import re

AVISO = ('**Documento generado a partir de una página web.**', 'Este PDF lo ha generado Programas 29N')


def limpiar(lineas):
    b = [l.strip() for l in lineas]
    b = [l for l in b if l and not l.startswith(AVISO)]
    # títulos sin negrita
    b = [re.sub(r'^(#+)\s*\*\*(.+?)\*\*$', r'\1 \2', l) for l in b]
    out = []
    en_tu = False
    for l in b:
        if l.startswith('#'):
            en_tu = l.startswith('## TU.')
        elif l.startswith('- ') and l[2:3].islower() and out and out[-1].startswith('- '):
            out[-1] = out[-1] + ' ' + l[2:]
            continue
        elif en_tu and l.startswith('**'):
            l = '- ' + l
        out.append(l)
    assert out[0] == '# Catalunya al centre', out[0]
    assert sum(l.startswith('## ') for l in out) == 8
    assert sum(l.startswith('- ') for l in out) == 51, sum(l.startswith('- ') for l in out)
    return [x for l in out for x in (l, '')]

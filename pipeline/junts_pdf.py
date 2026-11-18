"""Junts publicó su programa del 29N solo como página web (https://www.tualcentre.cat/catalunya-al-centre/).
Este script lo pasa a PDF para que entre en el mismo flujo que los demás programas:
lee la copia guardada de la página, saca el texto del programa tal cual, en su orden, y lo imprime
a PDF con Chrome headless. Al principio del PDF va un aviso que explica de dónde sale.
Se omiten el menú, el bloque «Actualitat dia a dia» (vídeos y frases de campaña), los donativos y las cookies.

Uso: python -I pipeline/junts_pdf.py <copia.html> <salida.pdf> <fecha_copia AAAA-MM-DD>
"""
import html, pathlib, re, subprocess, sys, tempfile
from bs4 import BeautifulSoup

URL = 'https://www.tualcentre.cat/catalunya-al-centre/'
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
MESES = 'enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre'.split()

src, out, fecha = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]).resolve(), sys.argv[3]
a, m, d = (int(x) for x in fecha.split('-'))
fecha_larga = f'{d} de {MESES[m - 1]} de {a}'
s = BeautifulSoup(src.read_text(encoding='utf-8'), 'html.parser')
t = lambda el: re.sub(r'\s+', ' ', el.get_text(' ')).strip()
e = html.escape

titulo = ' '.join(t(x) for x in s.select('h1 .hp-line-in'))
lema = t(s.select_one('section.text-block p'))
partes = [f'<h1>{e(titulo)}</h1>', f'<p class="lema">{e(lema)}</p>']
for sec in s.select('section.circle-swiper'):
    h3 = sec.find('h3')
    for sr in h3.select('.sr-only'):
        sr.extract()
    num = t(sec.find('p', attrs={'aria-hidden': 'true'}))
    partes.append(f'<h2>{e(num)}. {e(t(h3))}</h2>')
    intro = h3.find_next_sibling('p')
    if intro:
        partes.append(f'<p>{e(t(intro))}</p>')
    items = []
    for li in sec.select('li.cs-item'):
        tit, txt = li.select_one('.cs-full-title'), li.select_one('.cs-full-text')
        items.append(f'<li><strong>{e(t(tit))}</strong>' + (f' {e(t(txt))}' if txt and t(txt) else '') + '</li>')
    partes.append('<ul>' + ''.join(items) + '</ul>')
assert len(partes) > 10, 'no se ha encontrado el programa en la página'

aviso = (f'<div class="aviso"><p><strong>Documento generado a partir de una página web.</strong> '
         f'Junts per Catalunya no ha publicado su programa para las elecciones generales del 29 de noviembre de 2026 '
         f'en PDF, solo como página web: <a href="{URL}">{URL}</a>.</p>'
         f'<p>Este PDF lo ha generado Programas 29N a partir de una copia de esa página descargada el {fecha_larga}. '
         f'El texto del programa se reproduce literalmente y en el mismo orden que en la web. Se han omitido el menú, '
         f'el bloque «Actualitat dia a dia» (vídeos y frases de campaña), el bloque de donativos y el aviso de cookies.</p></div>')

doc = f'''<!doctype html><html lang="ca"><head><meta charset="utf-8"><title>{e(titulo)} · Junts per Catalunya · 29N</title>
<style>
@page {{ size: A4; margin: 22mm 20mm; }}
body {{ font-family: Georgia, 'Times New Roman', serif; font-size: 11.5pt; line-height: 1.45; color: #111; }}
.aviso {{ font-family: Arial, sans-serif; font-size: 9.5pt; border: 1px solid #999; padding: 8px 12px; margin-bottom: 22px; background: #f3f3f3; }}
.aviso p {{ margin: 4px 0; }} .aviso a {{ color: #111; }}
h1 {{ font-family: Arial, sans-serif; font-size: 26pt; margin: 0 0 6px; }}
.lema {{ font-size: 14pt; margin: 0 0 20px; }}
h2 {{ font-family: Arial, sans-serif; font-size: 15pt; margin: 22px 0 6px; break-after: avoid; }}
ul {{ padding-left: 20px; }} li {{ margin: 5px 0; break-inside: avoid; }}
</style></head><body>{aviso}{''.join(partes)}</body></html>'''

with tempfile.TemporaryDirectory() as tmp:
    h = pathlib.Path(tmp) / 'junts.html'
    h.write_text(doc, encoding='utf-8')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                    f'--user-data-dir={tmp}\\perfil', f'--print-to-pdf={out}', h.as_uri()],
                   check=True, capture_output=True, timeout=120)
print(out.name, out.stat().st_size, 'bytes')

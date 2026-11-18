"""Une web/index.html, styles.css, data.js, app.js y las fuentes en un único HTML: dist/programas29N.html.
Uso, desde la raíz del proyecto: python -I pipeline/bundle.py"""
import base64, pathlib, re

raiz = pathlib.Path(__file__).resolve().parent.parent
web = raiz / 'web'
html = (web / 'index.html').read_text(encoding='utf-8')
css = (web / 'styles.css').read_text(encoding='utf-8')
fuente = lambda m: 'url("data:font/woff2;base64,' + base64.b64encode((web / m[1]).read_bytes()).decode() + '")'
css = re.sub(r'url\("(fonts/[^"]+\.woff2)"\)', fuente, css)
html = re.sub(r'<link rel="preload" href="fonts/[^"]+"[^>]*>\n', '', html)
html = html.replace('<link rel="icon" href="favicon.ico" sizes="any">\n', '')
html = re.sub(r'<!-- Cloudflare Web Analytics.*?</script>\n', '', html, flags=re.S)  # se abre en local: sin analítica
for png in ('favicon-32.png', 'icono.png'):
    html = html.replace(f'href="{png}"', 'href="data:image/png;base64,' + base64.b64encode((web / png).read_bytes()).decode() + '"')
js = lambda n: (web / n).read_text(encoding='utf-8').replace('</script', '<\\/script')
# el ZIP de Markdown no va dentro: se enlaza el de la web
datos = js('data.js').replace('"url":"descargas/', '"url":"https://programas29n.jamarlli.workers.dev/descargas/')

piezas = {
    '<link rel="stylesheet" href="styles.css">': f'<style>\n{css}\n</style>',
    '<script src="data.js"></script>': f'<script>\n{datos}\n</script>',
    '<script src="app.js"></script>': f'<script>\n{js("app.js")}\n</script>',
}
for etiqueta, dentro in piezas.items():
    assert html.count(etiqueta) == 1, etiqueta
    html = html.replace(etiqueta, dentro)

out = raiz / 'dist' / 'programas29N.html'
out.parent.mkdir(exist_ok=True)
out.write_text(html, encoding='utf-8')
print(out.relative_to(raiz), round(out.stat().st_size / 1024), 'KB')

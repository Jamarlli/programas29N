"""Une index.html, styles.css, el data.js de cada idioma, app.js y las fuentes en un único HTML por idioma:
dist/programas29N.html (castellano) y dist/programas29N-<idioma>.html.
Uso, desde la raíz del proyecto: python -I pipeline/bundle.py"""
import base64, pathlib, re

raiz = pathlib.Path(__file__).resolve().parent.parent
web = raiz / 'web'
SITIO = 'https://programas29n.jamarlli.workers.dev'
css = (web / 'styles.css').read_text(encoding='utf-8')
fuente = lambda m: 'url("data:font/woff2;base64,' + base64.b64encode((web / m[1]).read_bytes()).decode() + '")'
css = re.sub(r'url\("(fonts/[^"]+\.woff2)"\)', fuente, css)
js = lambda n: (web / n).read_text(encoding='utf-8').replace('</script', '<\\/script')

for L in ['es', 'ca', 'va', 'gl', 'eu']:
    pagina = web / 'index.html' if L == 'es' else web / L / 'index.html'
    datos_f = 'data.js' if L == 'es' else f'data-{L}.js'
    if not pagina.exists() or not (web / datos_f).exists():
        continue
    html = pagina.read_text(encoding='utf-8').replace('="../', '="')
    html = re.sub(r'<link rel="preload" href="fonts/[^"]+"[^>]*>\n', '', html)
    html = html.replace('<link rel="icon" href="favicon.ico" sizes="any">\n', '')
    html = re.sub(r'<!-- Cloudflare Web Analytics.*?</script>\n', '', html, flags=re.S)  # se abre en local: sin analítica
    for png in ('favicon-32.png', 'icono.png'):
        html = html.replace(f'href="{png}"', 'href="data:image/png;base64,' + base64.b64encode((web / png).read_bytes()).decode() + '"')
    # el ZIP de Markdown y los PDF generados de programas que solo son web no van dentro: se enlazan los de la web
    datos = re.sub(r'"(url|pdfCopia)":"/descargas/', rf'"\1":"{SITIO}/descargas/', js(datos_f))
    piezas = {
        '<link rel="stylesheet" href="styles.css">': f'<style>\n{css}\n</style>',
        f'<script src="{datos_f}"></script>': f'<script>\n{datos}\n</script>',
        '<script src="app.js"></script>': f'<script>\n{js("app.js")}\n</script>',
    }
    for etiqueta, dentro in piezas.items():
        assert html.count(etiqueta) == 1, (L, etiqueta)
        html = html.replace(etiqueta, dentro)
    out = raiz / 'dist' / ('programas29N.html' if L == 'es' else f'programas29N-{L}.html')
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print(out.relative_to(raiz), round(out.stat().st_size / 1024), 'KB')

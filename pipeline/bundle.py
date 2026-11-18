"""Une web/index.html, styles.css, data.js y app.js en un único HTML: dist/programas29N.html.
Uso, desde la raíz del proyecto: python -I pipeline/bundle.py"""
import pathlib

raiz = pathlib.Path(__file__).resolve().parent.parent
web = raiz / 'web'
html = (web / 'index.html').read_text(encoding='utf-8')
css = (web / 'styles.css').read_text(encoding='utf-8')
js = lambda n: (web / n).read_text(encoding='utf-8').replace('</script', '<\\/script')

piezas = {
    '<link rel="stylesheet" href="styles.css">': f'<style>\n{css}\n</style>',
    '<script src="data.js"></script>': f'<script>\n{js("data.js")}\n</script>',
    '<script src="app.js"></script>': f'<script>\n{js("app.js")}\n</script>',
}
for etiqueta, dentro in piezas.items():
    assert html.count(etiqueta) == 1, etiqueta
    html = html.replace(etiqueta, dentro)

out = raiz / 'dist' / 'programas29N.html'
out.parent.mkdir(exist_ok=True)
out.write_text(html, encoding='utf-8')
print(out.relative_to(raiz), round(out.stat().st_size / 1024), 'KB')

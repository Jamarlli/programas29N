"""Hace web/favicon.ico (16, 32 y 48 px) y web/favicon-32.png a partir de las capturas de favicon.html y favicon-16.html.
A 16 px «29N» no se lee, así que esa medida sale de favicon-16.html, que solo pone «29».
Uso, desde la raíz del proyecto: python -I pipeline/og/favicon.py <captura.png> <captura-16.png>"""
import io, pathlib, struct, sys
from PIL import Image, ImageDraw

web = pathlib.Path(__file__).resolve().parents[2] / 'web'


def redondeada(ruta, lado):
    im = Image.open(ruta).convert('RGBA')
    mascara = Image.new('L', im.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, *im.size), radius=round(im.width * .22), fill=255)
    im.putalpha(mascara)
    return im.resize((lado, lado), Image.LANCZOS)


tamanos = [redondeada(sys.argv[2], 16), redondeada(sys.argv[1], 32), redondeada(sys.argv[1], 48)]
tamanos[1].save(web / 'favicon-32.png')

# ICO con un PNG por tamaño (Pillow no deja usar una imagen distinta para cada medida)
pngs = []
for im in tamanos:
    b = io.BytesIO(); im.save(b, 'PNG'); pngs.append(b.getvalue())
cab = struct.pack('<HHH', 0, 1, len(pngs))
pos = 6 + 16 * len(pngs)
dirs = b''
for im, png in zip(tamanos, pngs):
    dirs += struct.pack('<BBBBHHII', im.width, im.height, 0, 0, 1, 32, len(png), pos)
    pos += len(png)
(web / 'favicon.ico').write_bytes(cab + dirs + b''.join(pngs))
print('favicon.ico y favicon-32.png en', web)

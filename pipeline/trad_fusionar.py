"""Junta las traducciones validadas de cada idioma en data/trad/<idioma>.json, que es lo que lee build_web.py.

Uso: python -I pipeline/trad_fusionar.py [--sin-revisar]

Solo entra un lote si su traducción pasa validar_trad.py sin errores y, salvo con --sin-revisar, si además
está revisado (data/trad/revision/<lote>.txt). Así la web nunca publica una traducción a medias.
Formato de salida:
  {"extractos": {id: {"h": titular, "t": texto, "q": {cita original: cita traducida}}},
   "rutas": {partido: {título original: título traducido}}, "titulos": {partido: título del programa},
   "lotes": {lote: "revisado" | "sin revisar"}}
"""
import json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from validar_trad import TRAD, comprobar, leer  # noqa: E402


def main():
    sin_revisar = '--sin-revisar' in sys.argv
    indice = json.loads((TRAD / 'indice.json').read_text(encoding='utf-8'))
    por_idioma = {}
    for lote, info in indice.items():
        L = info['idioma']
        d = por_idioma.setdefault(L, {'extractos': {}, 'rutas': {}, 'titulos': {}, 'lotes': {}})
        if not (TRAD / 'salida' / f'{lote}.txt').exists():
            continue
        revisado = (TRAD / 'revision' / f'{lote}.txt').exists()
        if not revisado and not sin_revisar:
            continue
        err, _ = comprobar(lote)
        if err:
            print(f'{lote}: {len(err)} errores, no entra')
            continue
        orig = dict(leer(TRAD / 'lotes' / f'{lote}.txt'))
        for i, campos in leer(TRAD / 'salida' / f'{lote}.txt'):
            o = orig[i]
            if lote.endswith('-rutas'):
                tipo, pid, *_ = i.split(':')
                if tipo == 'titulo':
                    d['titulos'][pid] = campos['s'][0]
                else:
                    d['rutas'].setdefault(pid, {})[o['s'][0]] = campos['s'][0]
                continue
            x = {}
            if 'h' in campos:
                x['h'] = campos['h'][0]
            if 't' in campos:
                x['t'] = campos['t'][0]
                x['q'] = dict(zip(o.get('q', []), campos.get('q', [])))
            d['extractos'][i] = x
        d['lotes'][lote] = 'revisado' if revisado else 'sin revisar'
    for L, d in por_idioma.items():
        total = sum(1 for k, v in indice.items() if v['idioma'] == L)
        (TRAD / f'{L}.json').write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        print(f"{L}: {len(d['lotes'])} de {total} lotes ({sum(v == 'revisado' for v in d['lotes'].values())} revisados), "
              f"{len(d['extractos'])} extractos, {sum(len(v) for v in d['rutas'].values())} títulos de apartado")


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()

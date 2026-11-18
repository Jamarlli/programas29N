"""Estado de la traducción de los programas: qué lotes faltan por traducir, por revisar o están listos.

Uso: python -I pipeline/trad_estado.py [idioma]
"""
import json, pathlib, sys

TRAD = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'trad'


def estado(lote):
    if (TRAD / 'revision' / f'{lote}.txt').exists():
        return 'revisado'
    if (TRAD / 'salida' / f'{lote}.txt').exists():
        return 'traducido'
    if list((TRAD / 'salida').glob(f'{lote}.p*.txt')):
        return 'en curso'
    return 'pendiente'


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    indice = json.loads((TRAD / 'indice.json').read_text(encoding='utf-8'))
    solo = sys.argv[1] if len(sys.argv) > 1 else None
    por = {}
    for lote, info in indice.items():
        if solo and info['idioma'] != solo:
            continue
        por.setdefault(info['idioma'], {}).setdefault(estado(lote), []).append(lote)
    for L, d in por.items():
        print(L + ': ' + ' · '.join(f'{k} {len(v)}' for k, v in sorted(d.items())))
        for k in ('traducido', 'en curso'):
            if d.get(k):
                print(f'  {k}: ' + ' '.join(d[k]))

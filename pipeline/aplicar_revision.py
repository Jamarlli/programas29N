"""Aplica la revisión de un lote y vuelve a validarlo: python -I pipeline/aplicar_revision.py <lote>

La revisión está en data/trad/revision/<lote>.txt. Tiene los extractos corregidos, completos, en el formato de
los lotes; antes de cada uno va una línea «# <id>: <qué estaba mal>». Si no hay nada que corregir, contiene
solo «# sin cambios».
Los extractos corregidos sustituyen a los de data/trad/salida/<lote>.txt. Antes, la primera vez, se guarda una
copia de la traducción sin revisar en data/trad/salida/<lote>.sin-revisar.txt.
"""
import pathlib, re, shutil, sys, tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from validar_trad import TRAD, comprobar, leer  # noqa: E402


def escribir(items):
    out = []
    for i, campos in items:
        out.append(f'@@@ {i}')
        for c, vs in campos.items():
            for v in vs:
                out += [f'@{c}', v]
    return '\n'.join(out) + '\n'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    lote = sys.argv[1].removesuffix('.txt')
    rev = TRAD / 'revision' / f'{lote}.txt'
    lineas = rev.read_text(encoding='utf-8').split('\n')
    notas = [l for l in lineas if re.match(r'^# ', l)]
    limpio = [l for k, l in enumerate(lineas) if not (re.match(r'^# ', l) and (k + 1 == len(lineas) or not lineas[k + 1].strip() or lineas[k + 1].startswith(('@@@ ', '# '))))]
    with tempfile.TemporaryDirectory() as tmp:
        f = pathlib.Path(tmp) / 'rev.txt'
        f.write_text('\n'.join(limpio), encoding='utf-8')
        cambios = leer(f)
    sal = TRAD / 'salida' / f'{lote}.txt'
    copia = sal.with_name(f'{lote}.sin-revisar.txt')
    if cambios and not copia.exists():
        shutil.copyfile(sal, copia)
    items = leer(sal)
    pos = {i: k for k, (i, _) in enumerate(items)}
    for i, campos in cambios:
        if i not in pos:
            sys.exit(f'{lote}: la revisión trae un extracto que no está en el lote: {i}')
        items[pos[i]] = (i, campos)
    if cambios:
        sal.write_text(escribir(items), encoding='utf-8')
    err, avi = comprobar(lote)
    for e in err:
        print('ERROR', e)
    print(f'{lote}: {len(cambios)} extractos corregidos en la revisión; {len(err)} errores, {len(avi)} avisos')
    for n in notas[:200]:
        print(' ', n)
    sys.exit(1 if err else 0)


if __name__ == '__main__':
    main()

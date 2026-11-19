"""Comprueba la traducción de un lote: python -I pipeline/validar_trad.py <lote>   (p. ej. eu-001 o eu-rutas)

Lee data/trad/lotes/<lote>.txt (original) y data/trad/salida/<lote>.txt (traducción). Si la traducción se ha
escrito en partes (<lote>.p1.txt, <lote>.p2.txt…), las une en <lote>.txt (por id: se pueden añadir partes después) y borra las partes.

Errores (hay que corregirlos):
- falta o sobra algún extracto, o no van en el mismo orden; falta o sobra un campo (@h, @t, @q, @s);
- el texto no tiene la misma forma: mismo número de líneas, líneas en blanco en los mismos sitios, mismas marcas
  de lista con la misma sangría y la misma numeración, el mismo número de «**» en cada línea;
- no salen las mismas cifras (cada secuencia de dígitos, las mismas veces), ni los mismos enlaces o correos;
- una cita traducida no aparece tal cual dentro del texto traducido de su extracto;
- el texto se ha quedado sin traducir o tiene una longitud muy distinta de la del original.
Avisos (hay que mirarlos, pero pueden estar bien): longitud algo distinta; palabras típicas del idioma de origen.
"""
import collections, json, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
TRAD = RAIZ / 'data' / 'trad'

# palabras muy frecuentes que solo son de un idioma: sirven para ver si un texto se ha quedado en el original
PROPIAS = {
    'es': set('los las y pero también muy hacia hasta cuando nuestra nuestro nuestras nuestros sus'.split()),
    'ca': set('els amb però també aquesta aquest dels perquè nostra nostre nostres fins quan mitjançant i seus seves'.split()),
    'va': set('els amb però també esta este dels perquè nostra nostre nostres fins quan mitjançant i seus seues'.split()),
    'gl': set('os do da das non polo pola polos nun nunha cun cunha dun dunha ao aos xa unha tamén moi nosa noso nosas nosos ata cando mais coa co e súa seu'.split()),
    'eu': set('eta dira ditu dute izan bat egin behar ere baina gure hori honek dugu ditugu du'.split()),
}


def sin_cursivas(s):
    s = re.sub(r'https?://\S+|www\.\S+', ' ', s)  # las URL tampoco cuentan
    return re.sub(r'(?<![\w_])_[^_\n]+_(?![\w_])', ' ', s)

def leer(ruta):
    """Devuelve [(id, {campo: [valores]})] en orden."""
    out = []
    campo = None
    for linea in ruta.read_text(encoding='utf-8').split('\n'):
        if linea.startswith('@@@ '):
            out.append((linea[4:].strip(), collections.OrderedDict()))
            campo = None
        elif re.fullmatch(r'@[htqs]\s*', linea):
            campo = linea.strip()[1]
            out[-1][1].setdefault(campo, []).append([])
        elif out and campo:
            out[-1][1][campo][-1].append(linea)
        elif linea.strip():
            raise ValueError(f'{ruta.name}: línea fuera de un campo: {linea[:80]!r}')
    return [(i, {k: ['\n'.join(v).strip('\n') for v in vs] for k, vs in d.items()}) for i, d in out]


def juntar_partes(lote):
    sal = TRAD / 'salida'
    partes = sorted(sal.glob(f'{lote}.p*.txt'), key=lambda p: int(re.search(r'\.p(\d+)\.txt$', p.name).group(1)))
    if partes:
        # se combinan por id con lo que ya estuviera unido: una parte nueva añade los extractos que faltaban o
        # sustituye los que trae, sin perder el resto; el orden es el del lote original
        bloques = {}
        for f in ([sal / f'{lote}.txt'] if (sal / f'{lote}.txt').exists() else []) + partes:
            for b in re.split(r'(?m)^(?=@@@ )', f.read_text(encoding='utf-8')):
                if b.startswith('@@@ '):
                    bloques[b.split('\n', 1)[0][4:].strip()] = b.strip('\n')
        orden = [i for i, _ in leer(TRAD / 'lotes' / f'{lote}.txt')]
        ids = [i for i in orden if i in bloques] + [i for i in bloques if i not in set(orden)]
        (sal / f'{lote}.txt').write_text('\n'.join(bloques[i] for i in ids) + '\n', encoding='utf-8')
        for p in partes:
            p.unlink()


cifras = lambda s: collections.Counter(re.findall(r'\d+', s))
enlaces = lambda s: collections.Counter(re.findall(r'https?://[^\s)\]>]+|www\.[^\s)\]>]+|[\w.+-]+@[\w-]+\.[\w.]+', s))
plano = lambda s: re.sub(r'\s+', '', s.replace('**', ''))
palabras = lambda s: re.findall(r"[a-záéíóúàèòïüçñ·'’]+", s.lower())


def forma(linea):
    m = re.match(r'^(\s*)([-*]\s|\d+[.)]\s|\*\*\d+[.)]?)?', linea)
    return (len(m.group(1)), (m.group(2) or '').strip()), linea.count('**')


def comprobar(lote):
    idioma = lote.split('-')[0]
    orig = leer(TRAD / 'lotes' / f'{lote}.txt')
    f_trad = TRAD / 'salida' / f'{lote}.txt'
    if not f_trad.exists():
        return [f'{lote}: no está la traducción ({f_trad.relative_to(RAIZ)})'], []
    trad = leer(f_trad)
    err, avi = [], []
    ids_o, ids_t = [i for i, _ in orig], [i for i, _ in trad]
    if ids_o != ids_t:
        faltan = [i for i in ids_o if i not in ids_t]
        sobran = [i for i in ids_t if i not in ids_o]
        err.append(f'los extractos no coinciden: faltan {faltan[:10]}{"…" if len(faltan) > 10 else ""}, sobran {sobran[:10]}'
                   + ('' if faltan or sobran else ' (están en otro orden)'))
    tdic = dict(trad)
    for i, o in orig:
        t = tdic.get(i)
        if t is None:
            continue
        for campo in o:
            if len(t.get(campo, [])) != len(o[campo]):
                err.append(f'{i}: el campo @{campo} sale {len(t.get(campo, []))} veces y en el original {len(o[campo])}')
        for campo in t:
            if campo not in o:
                err.append(f'{i}: sobra el campo @{campo}')
        for campo in ('h', 't', 's'):
            for a, b in zip(o.get(campo, []), t.get(campo, [])):
                if not b.strip():
                    err.append(f'{i}: @{campo} vacío')
                    continue
                if cifras(a) != cifras(b):
                    d1, d2 = cifras(a) - cifras(b), cifras(b) - cifras(a)
                    err.append(f'{i}: @{campo} cifras distintas: faltan {dict(d1)}, sobran {dict(d2)}')
                if enlaces(a) != enlaces(b):
                    err.append(f'{i}: @{campo} enlaces o correos distintos')
                la, lb = len(plano(a)), len(plano(b))
                if la >= 40:
                    r = lb / la
                    if r < 0.55 or r > 1.9:
                        err.append(f'{i}: @{campo} longitud muy distinta del original ({r:.2f} veces)')
                    elif r < 0.72 or r > 1.5:
                        avi.append(f'{i}: @{campo} longitud {r:.2f} veces la del original')
                # Los títulos de obras en cursiva (_…_) se dejan en el idioma original (regla 4):
                # no cuentan para «sin traducir» ni para el detector de idioma.
                a_sc, b_sc = sin_cursivas(a), sin_cursivas(b)
                wa = palabras(a_sc)
                if len(wa) >= 6 and a.strip() == b.strip():
                    # igual que el original: error si, quitados los títulos en cursiva, queda alguna palabra típica de otro idioma
                    if any(w in PROPIAS[k] for w in wa for k in PROPIAS if k != idioma):
                        err.append(f'{i}: @{campo} sin traducir (igual que el original)')
                    else:
                        avi.append(f'{i}: @{campo} igual que el original (solo títulos, nombres o enlaces): compruébalo')
                wb = palabras(b_sc)
                if len(wb) >= 25:
                    propias = sum(w in PROPIAS[idioma] for w in wb)
                    ajenas = max(sum(w in PROPIAS[k] for w in wb) for k in PROPIAS if k != idioma and not {k, idioma} <= {'ca', 'va'})
                    if ajenas >= 3 and not propias:
                        err.append(f'{i}: @{campo} no parece estar en {idioma}')
                    elif ajenas > propias:
                        avi.append(f'{i}: @{campo} comprueba que está en {idioma} (tiene pocas palabras típicas)')
        for a, b in zip(o.get('t', []), t.get('t', [])):
            la, lb = a.split('\n'), b.split('\n')
            if len(la) != len(lb):
                err.append(f'{i}: @t tiene {len(lb)} líneas y el original {len(la)} (hay que mantener una línea por línea, con las líneas en blanco en el mismo sitio)')
                continue
            for k, (x, y) in enumerate(zip(la, lb), 1):
                if bool(x.strip()) != bool(y.strip()):
                    err.append(f'{i}: @t línea {k}: las líneas en blanco no están en el mismo sitio')
                elif forma(x) != forma(y):
                    err.append(f'{i}: @t línea {k}: cambia la marca de lista, la sangría, la numeración o el número de «**» ({forma(x)} → {forma(y)})')
        if 'q' in o and 't' in t:
            texto = plano(t['t'][0])
            for c in t.get('q', []):
                if plano(c) not in texto:
                    err.append(f'{i}: la cita traducida no está tal cual en el texto traducido: «{c[:90]}»')
    return err, avi


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    lote = sys.argv[1].removesuffix('.txt')
    juntar_partes(lote)
    err, avi = comprobar(lote)
    for e in err:
        print('ERROR', e)
    for a in avi:
        print('aviso', a)
    print(f'{lote}: {len(err)} errores, {len(avi)} avisos')
    sys.exit(1 if err else 0)


if __name__ == '__main__':
    main()

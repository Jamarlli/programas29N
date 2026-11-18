"""Limpia el Markdown bruto de pymupdf4llm para ingesta por LLM.

Uso: python -I pipeline/clean.py <dir_raw> <dir_salida>
"""
import re, sys, pathlib, unicodedata

TERM = tuple('.:;!?)»"”…')


def norm(s):
    s = re.sub(r'[*_#`~>|]', ' ', s)
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def plain(s):
    """Texto de un título sin marcas markdown."""
    s = re.sub(r'^#+\s*', '', s)
    s = s.replace('**', '').replace('<sup>', '').replace('</sup>', '')
    s = re.sub(r'(?<!\w)_|_(?!\w)', '', s)
    return re.sub(r'\s+', ' ', s).strip()


def is_heading(l): return l.startswith('#')
def is_block(l): return l.startswith(('|', '- ', '* ', '#', '<')) or re.match(r'^\s*(\d+\.|[-*■•])\s', l)


def drop_range(lines, start_pred, end_pred):
    """Quita desde la primera línea que cumple start_pred hasta (sin incluir) la primera que cumple end_pred."""
    out, i = [], 0
    while i < len(lines):
        if start_pred(lines[i]):
            j = i + 1
            while j < len(lines) and not end_pred(lines[j]):
                j += 1
            out.extend(lines[j:])
            return out
        out.append(lines[i]); i += 1
    return out


def generic_pre(text):
    text = text.replace('~~', '')
    text = re.sub(r'</?(mark|u)>', '', text)  # resaltados/subrayados del PDF
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    text = text.replace('­', '')  # guion blando
    lines = [l.rstrip() for l in text.split('\n')]
    return lines


def join_broken(lines):
    """Une palabras partidas con guion y párrafos cortados entre líneas/páginas."""
    nb = [l for l in lines]
    out = []
    for l in nb:
        if not l.strip():
            out.append(l); continue
        k = len(out) - 1
        while k >= 0 and not out[k].strip():
            k -= 1
        if k >= 0:
            prev = out[k]
            # título en mayúsculas partido en dos negritas: «**… ELEGIR CÓMO**» + «**VIVIR.** …»
            caps_split = (prev.rstrip().endswith('**') and l.startswith('**')
                          and re.match(r'^\*\*[A-ZÁÉÍÓÚÑ]{2,}', l) is not None
                          and not prev.rstrip()[:-2].rstrip().endswith(TERM)
                          and re.search(r'[A-ZÁÉÍÓÚÑ]{2,}-?$', prev.rstrip()[:-2]) is not None)
            if caps_split:
                p = prev.rstrip()[:-2]
                cur = l[2:]
                out = out[:k] + [p[:-1] + cur if p.endswith('-') else p + ' ' + cur]
                continue
            starts_lower = re.match(r'^(\*\*)?[a-záéíóúñü(«"]', l.lstrip()) is not None and not is_block(l)
            prev_ok = not prev.startswith(('|', '<')) and not re.match(r'^\s*#+\s*$', prev)
            if starts_lower and prev_ok:
                p = prev.rstrip()
                if is_heading(p):  # título que en realidad era el arranque de un párrafo
                    p = re.sub(r'^#+\s*', '', p)
                cur = l.strip()
                # negrita partida: "**94. ... precios,**" + "**reforzando ...**"
                if p.endswith('**') and cur.startswith('**') and not p[:-2].rstrip().endswith(TERM):
                    p, cur = p[:-2].rstrip(), cur[2:]
                if re.search(r'[A-Za-zÁÉÍÓÚáéíóúñÑüÜ]-$', p):
                    joined = p[:-1] + cur
                elif not p.endswith(TERM):
                    joined = p + ' ' + cur
                else:
                    joined = None
                if joined is not None:
                    out = out[:k] + [joined]
                    continue
        out.append(l)
    return out


def generic_post(lines, drop_re=()):
    out = []
    for l in lines:
        if any(re.match(r, l.strip()) for r in drop_re):
            continue
        if is_heading(l):
            m = re.match(r'^(#+)\s*(.*)$', l)
            l = f"{m.group(1)} {plain(m.group(2))}"
        out.append(l)
    text = '\n'.join(out)
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # asegurar línea en blanco alrededor de los títulos
    text = re.sub(r'\n(#+ [^\n]*)\n(?!\n)', r'\n\1\n\n', text)
    return text.strip() + '\n'


def set_level(l, n):
    return '#' * n + ' ' + plain(l)


def demote(l):
    t = plain(l)
    return f'**{t}**' if t else ''


FA_CAPS = [
    "Acabar con la especulación y garantizar el derecho a la vivienda",
    "Derechos sociales para una vida digna",
    "Una reforma fiscal en profundidad",
    "Salarios y pensiones dignos y precios asequibles",
    "Continuar el impulso hacia una transición ecológica justa",
    "Estado emprendedor y política industrial activa",
    "Agricultura, ganadería y pesca: hacia su sostenibilidad medioambiental, social y económica",
    "Autónomos, pymes y economía social",
    "Lucha contra la despoblación y retos de la insularidad",
    "Empleo público de calidad",
    "Financiación autonómica y vertebración territorial",
    "Ayuntamientos con recursos y autonomía",
    "Democratización económica y poder financiero",
    "Poder digital y pluralismo informativo",
    "Igualdad y más derechos para todas, todos y todes",
    "Migraciones y antirracismo",
    "La seguridad humana: paz, solidaridad y Europa",
    "Hacia una democracia avanzada",
]


def promote_titles(lines, titles, level, fmt, maxlen=160):
    """Busca cada título (en orden) en líneas cortas y lo convierte en encabezado.
    Si el título está partido en varias líneas consecutivas, las fusiona."""
    pos = 0
    missing = []
    for idx, t in enumerate(titles):
        nt = norm(t)
        found = False
        for i in range(pos, len(lines)):
            l = lines[i]
            nl = norm(l)
            if not nl or len(plain(l)) > maxlen or l.startswith('|'):
                continue
            if nl == nt or (len(nl) >= 12 and nt.startswith(nl)) or nl.startswith(nt):
                # fusionar continuaciones
                acc, j = nl, i
                while acc != nt and nt.startswith(acc):
                    j += 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j >= len(lines):
                        break
                    nxt = norm(lines[j])
                    if nxt and nt.startswith((acc + ' ' + nxt).strip()):
                        acc = (acc + ' ' + nxt).strip()
                        lines[j] = ''
                    else:
                        break
                lines[i] = '#' * level + ' ' + fmt(idx, t)
                pos = i + 1
                found = True
                break
        if not found:
            missing.append(t)
    return lines, missing


def clean_fa(lines):
    lines = drop_range(lines, lambda l: 'Contenido' in l and l.startswith('#'),
                       lambda l: l.strip() and not l.startswith('|'))
    out = []
    for l in lines:
        s = l.strip()
        if re.match(r'^(#+\s*)?(\*\*)?\d{2}(\*\*)?$', s):  # número de capítulo suelto
            continue
        if re.match(r'^(#+\s*|- )?(\*\*)?\d{1,2}\.\d{1,2}\.\s', s) and len(s) < 220:
            out.append(set_level(re.sub(r'^- ', '', s), 3)); continue
        if is_heading(s):
            out.append(set_level(s, 4)); continue
        out.append(l)
    lines = out
    i = next(i for i, l in enumerate(lines) if l.strip())
    lines.insert(i, '## Introducción')
    lines, miss = promote_titles(lines, FA_CAPS, 2, lambda i, t: f"{i + 1:02d}. {t}")
    return lines, miss


def clean_pp(lines):
    lines, _ = _clean_pp(lines)
    res = []
    for l in lines:
        if l.startswith('@@SPLIT'):
            h, r = l[7:].split('@@', 1)
            res += [h, '', r]
        else:
            res.append(l)
    return res, []


def _clean_pp(lines):
    # índice: desde el primer título "LA ESPAÑA QUE HAREMOS..." hasta su repetición
    first = next(i for i, l in enumerate(lines) if 'LA ESPAÑA QUE HAREMOS ENTRE TODOS' in l)
    second = next(i for i, l in enumerate(lines) if i > first and 'LA ESPAÑA QUE HAREMOS ENTRE TODOS' in l)
    lines = lines[:first] + lines[second:]
    for i, l in enumerate(lines):
        if l.startswith('nuidad y previsibilidad las convocatorias'):
            lines[i] = ('**33 CREAREMOS LAS PLAZAS DE JUECES, FISCALES, LETRADOS Y FUNCIONARIOS DE LA ADMINISTRACIÓN '
                        'DE JUSTICIA NECESARIAS PARA QUE RESPONDA A TIEMPO.** Planificaremos con conti' + l)
    # «#### 113» + «**LA SOLEDAD…» → «**113 LA SOLEDAD…»
    for i, l in enumerate(lines):
        m = re.match(r'^#+\s*(?:\*\*)?(\d{1,3})(?:\*\*)?\s*$', l.strip())
        if m:
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].startswith('**'):
                if not lines[j].startswith(f"**{m.group(1)} "):
                    lines[j] = f"**{m.group(1)} " + lines[j][2:]
                lines[i] = ''
    # subtítulo en cursiva intercalado en un párrafo («_Fortaleceremos_ Una comunidad … _el pacto entre_ …»)
    for i, l in enumerate(lines):
        if l.startswith('_') and len(re.findall(r'(?<!\w)_[^_]+_(?!\w)', l)) >= 2 and len(l) > 120:
            trozos = re.findall(r'(?<!\w)_([^_]+)_(?!\w)', l)
            resto = re.sub(r'\s*(?<!\w)_[^_]+_(?!\w)\s*', ' ', l).strip()
            resto = re.sub(r'(\w)- (\w)', r'\1\2', resto)
            lines[i] = '@@SPLIT' + '#### ' + ' '.join(trozos) + '@@' + resto
    # título de medida repetido justo antes de la medida completa
    for i, l in enumerate(lines):
        if re.match(r'^(?:#+\s*)?\*\*\d+ [^*]+\*\*\s*$', l.strip()):
            l = re.sub(r'^#+\s*', '', l.strip())
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].startswith(l.strip()) and len(lines[j].strip()) > len(l.strip()):
                lines[i] = ''
    out = []
    skip_table = False
    for l in lines:
        s = l.strip()
        m = re.match(r'^\|_Permanezca_\|\*\*(\d+)\*\*\|$', s)
        if m:  # medida en blanco en el PDF
            out.append(f"**{m.group(1)}** _Permanezca atento a la campaña para conocer esta nueva medida._")
            skip_table = True; continue
        if skip_table:
            if s.startswith('|'):
                continue
            skip_table = False
        m = re.match(r'^(?:_Permanezca_\s*)?\*\*(\d+)\*\*\s*_(?:Permanezca )?atento a la campaña para conocer esta nueva medida\.?_$', s)
        if m:
            out.append(f"**{m.group(1)}** _Permanezca atento a la campaña para conocer esta nueva medida._"); continue
        if re.match(r'^#+\s*[‘’"“”\']+\s*$', s):
            continue
        m = re.match(r'^#\s+([A-ZÁÉÍÓÚÑ ]*?)\s*(\d{2})\s+([A-ZÁÉÍÓÚÑ ]+?)\s*$', s) or re.match(r'^#\s+([A-ZÁÉÍÓÚÑ ]+?)\s+(\d{2})()\s*$', s)
        if m:
            out.append(f"## {m.group(2)}. {(m.group(1) + ' ' + m.group(3)).strip()}"); continue
        m = re.match(r'^#+\s*(_[^_]+_)\s*$', s)
        if m:
            out.append(m.group(1)); continue
        m = re.match(r'^#\s+(\d{2})\s+(.+?)\s+_(.+)_\s*$', s)
        if m:
            out.append(f"## {m.group(1)}. {m.group(2)}\n\n_{m.group(3)}_"); continue
        m = re.match(r'^#+\s*\*\*_?(\d+\.\d+)_?\*\*\s*_?(.+?)_?\s*$', s)
        if m:
            out.append(f"### {m.group(1)} {m.group(2)}"); continue
        if 'LA ESPAÑA QUE HAREMOS ENTRE TODOS' in s and is_heading(s):
            out.append('## La España que haremos entre todos'); continue
        if re.match(r'^#+\s*RECONSTRUCCI', s):
            out.append('# Reconstrucción Nacional'); continue
        if re.match(r'^#+\s*EL PROGRAMA DEL CAMBIO', s):
            out.append('_El programa del cambio necesario para España_'); continue
        if is_heading(s):
            out.append(re.sub(r'^#+\s*', '', s) if re.match(r'^#+\s*\*\*\d+\s', s) else set_level(s, 4)); continue
        out.append(l)
    return out, []


PSOE_NUM_PREFIX = re.compile(r'^(?:- )?((?:\*{0,2}[\d.]+\*{0,2}\s+)+)(?=\S)')


def fix_psoe_numbers(lines):
    """Números de compromiso rotos por resaltados: «1 **1** 30 **30. Texto» → «**130. Texto».
    Los compromisos van del 1 al 500 seguidos, así que el número correcto es el anterior + 1."""
    prev, out = 0, []
    for l in lines:
        m = re.match(r'^\*\*(\d+)\.', l)
        if m:
            prev = int(m.group(1))
            l = re.sub(r'^\*\*(\d+)\.\*\*\s+\1\s+\*\*', r'**\1. ', l)
            out.append(l); continue
        m = PSOE_NUM_PREFIX.match(l)
        if m and re.search(r'\d', m.group(1)) and '**' in m.group(1) and str(prev + 1)[-2:] in re.sub(r'\D', '', m.group(1)):
            pre, rest = m.group(1), l[m.end():]
            n = prev + 1
            if pre.count('**') % 2:   # negrita abierta en el prefijo
                l = f'**{n}. {rest}'
            else:
                l = f'**{n}.** {rest}'
            l = l.replace('** **', ' ')
            prev = n
        out.append(l)
    return out


def clean_psoe(lines):
    lines = [l.lstrip() if re.match(r'^\s+\*\*\d+\.', l) else l for l in lines]
    lines = fix_psoe_numbers(lines)
    lines = drop_range(lines, lambda l: l.startswith('|ÍNDICE') or l.startswith('|**ÍNDICE'),
                       lambda l: l.startswith('## ') or l.startswith('# '))
    out = []
    for l in lines:
        s = l.strip()
        if s.startswith('# Un Estado de bienestar fuerte.'):
            continue
        if s.startswith('LA FUERZA DE SEGUIR AVANZANDO. PROGRAMA'):
            out.append('# La fuerza de la gente. La fuerza de seguir avanzando\n\n_Programa elecciones generales 29 noviembre 2026_'); continue
        # "#### 8 **8.**" / "##### **29.**" → número de compromiso que se une a la línea siguiente
        m = re.match(r'^(?:#+\s*)?(?:\d+\s*)?\*\*(\d+)\.\*\*\s*$', s)
        if m:
            out.append(f'@@NUM{m.group(1)}'); continue
        if re.match(r'^#+\s*\*\*\d+\.', s):  # compromiso numerado tomado por título
            out.append(re.sub(r'^#+\s*', '', s)); continue
        if re.match(r'^#+\s*_.*_\s*$', s):
            out.append(set_level(s, 4)); continue
        if re.match(r'^#+\s*Compromisos\s*$', s):
            out.append('##### Compromisos'); continue
        out.append(l)
    # fusionar marcadores de número con la línea siguiente no vacía
    res, pend = [], None
    for l in out:
        if l.startswith('@@NUM'):
            pend = l[5:]; continue
        if pend and l.strip():
            l = re.sub(r'^\*\*', f'**{pend}. ', l.strip(), count=1) if l.strip().startswith('**') else f'**{pend}.** {l.strip()}'
            pend = None
        res.append(l)
    return res, []


VOX_CAPS = ["Ceuta y Melilla", "Economía, industria y energía", "Inmigración", "Prioridad nacional",
            "Vivienda", "Desregulación", "Sector primario y Mundo rural", "Sanidad",
            "Educación, Cultura y Deporte", "Seguridad y Defensa", "Familia y Vida",
            "Independencia de la Justicia y lucha contra la corrupción", "Infraestructuras y Transportes"]


def clean_vox(lines):
    lines = drop_range(lines, lambda l: 'ÍNDICE' in l and l.startswith('#'),
                       lambda l: l.startswith('### ') and 'CEUTA' in l)
    out = []
    started = False
    for l in lines:
        s = l.strip()
        if not started:
            if s.startswith('### ') and 'CEUTA' in s:
                started = True
                out.append('# Es sentido común\n')
            else:
                continue
        if re.match(r'^###\s', s):
            t = norm(s)
            out.append('## ' + next((c for c in VOX_CAPS if norm(c) == t), plain(s))); continue
        m = re.match(r'^#+\s*(\d{1,3}\.\s.+)$', s)
        if m:
            out.append(plain(m.group(1))); continue
        if is_heading(s):
            out.append(set_level(s, 3)); continue
        out.append(l)
    return out, []


DOCS = {
    'FRENTEAMPLIO': (clean_fa, ()),
    'PP': (clean_pp, (r'^\d{1,3}$',)),
    'PSOE': (clean_psoe, (r'^SOL$', r'.*LA ?FUERZA D[AE] ?(LA )?GENTE\.?$', r'^ELECCIONES GENERALES')),
    'VOX': (clean_vox, (r'^ES SENTIDO COMÚN$',)),
}


def main(src, dst):
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob('*.raw.md')):
        key = f.name.split('_')[0]
        fn, drops = DOCS[key]
        lines = generic_pre(f.read_text(encoding='utf-8'))
        lines, missing = fn(lines)
        lines = '\n'.join(lines).split('\n')
        lines = join_broken(lines)
        text = generic_post(lines, drops)
        name = f.name.replace('.raw.md', '.md')
        (dst / name).write_text(text, encoding='utf-8')
        print(f"{name}: {len(text)} chars; títulos no encontrados: {missing}")


if __name__ == '__main__':
    main(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]))

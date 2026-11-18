"""Limpieza propia del programa de Por un Mundo Más Justo (M+J), versión en castellano.

Estructura del PDF: portada (imagen), índice y «Guía por colectivos» (se quitan), 32 ejes
numerados y un anexo de fuentes. Cada eje: número grande, rótulo «EJE NN · PROGRAMA ELECTORAL
29N 2026» (se quita), título, línea «Te interesa si te importa: …», entradilla en cursiva,
medidas numeradas (01, 02… o 1., 2.…) y un cuadro «Compromisos medibles 2026–2030» (tabla
Qué/Hoy/Meta/Plazo) seguido a veces de «Fuentes consultadas».
"""
import re
from clean import plain, norm

TERM = tuple('.:;!?)»"”…')

CAPS = [
    "Vivienda", "Convivencia", "Mayores", "Infancia y adolescencia", "Jóvenes", "Pensiones",
    "Fiscalidad justa y sostenibilidad de las finanzas públicas", "Trabajo digno", "Autónomos",
    "Industria", "Sanidad pública, universal y de calidad", "Salud mental",
    "Cuidar al principio y al final de la vida", "Educación equitativa, inclusiva y de calidad",
    "Ciencia e investigación", "Política migratoria", "Lucha contra la emergencia climática",
    "Cuidado del planeta y la biodiversidad", "Políticas de transición energética",
    "Protección animal", "Cultura", "Política exterior al servicio de la paz y el desarrollo sostenible",
    "Calidad democrática", "Buen gobierno", "Participación ciudadana", "Erradicación de la pobreza",
    "Igualdad de género y protección de los derechos de las mujeres",
    "Derechos e igualdad efectiva de las personas LGTBI", "Sinhogarismo",
    "Prisiones y reinserción social", "Cooperación internacional", "Repoblación rural",
]
ANEXO = "Fuentes documentales y aportaciones de la sociedad civil"

TAGS = sorted(["Derechos y democracia", "Mundo y paz", "Inclusión social", "Igualdad",
               "Economía y empleo", "Conocimiento y cultura", "Servicios públicos", "Mayores",
               "Planeta", "Mundo rural", "Familias e infancia", "Jóvenes"], key=len, reverse=True)

# URL del anexo tal como se ven en el PDF (la conversión las partió con espacios y perdió guiones)
URLS = [
    "https://www.es.amnesty.org/fileadmin/user_upload/Prioridades_Amnistia_Internacional_ELECCIONES_GENERALES_2023.pdf",
    "https://coordinadoraongd.org/wp-content/uploads/2026/10/Documento_Politico_Elecciones26.pdf",
    "https://www.enlazateporlajusticia.org/l/enlazate-por-la-justicia-promueve-un-dialogo-plural-sobre-cooperacion-justicia-socioambiental-y-paz/",
    "https://puedeserlahostia.es/?utm_source=chatgpt.com",
    "https://ciudadaniaglobal.es/crisis-ceuta/?utm_source=chatgpt.com",
    "https://www.oxfamintermon.org/es/publicacion/agenda-pais-elecciones-generales-2026?utm_source=chatgpt.com",
    "https://www.plataformadeinfancia.org/documento/12-propuestas-de-infancia-para-las-elecciones-generales-2026/",
    "https://coceder.org/documentacion/propuestas-de-la-plataforma-del-tercer-sector-para-una-legislatura-social?utm_source=chatgpt.com",
    "https://faciam.org/2026/10/29/cinco-propuestas-para-avanzar-hacia-la-erradicacion-del-sinhogarismo-en-espana/?utm_source=chatgpt.com.",
]

SIMBOLOS = ('≥', '≤', '≈', '₂')

# reparaciones puntuales de la conversión (negritas cortadas, guiones perdidos)
ARREGLOS = [
    ('exterio** r a nivel', 'exterior** a nivel'),
    ('ciudadaní** a.', 'ciudadanía**.'),
    ('**aprendizajeservicio**', '**aprendizaje-servicio**'),
    ('Parque a ≥ 15 min', 'Parque a ≤ 15 min'),  # el PDF dice ≤
]


def compacto(s):
    return re.sub(r'\s+', '', plain(s))


def sin_marcas(s):
    return re.sub(r'\s+', ' ', s.replace('**', '').replace('_', ' ')).strip()


def unir(prev, cur):
    """Une una línea cortada con la anterior (sin punto final) arreglando la negrita partida."""
    if prev.endswith('**') and cur.startswith('**'):
        return prev[:-2].rstrip() + ' ' + cur[2:]
    if re.search(r'[A-Za-zÁÉÍÓÚáéíóúñÑ]-$', prev) and re.match(r'^[a-záéíóúñ]', cur):
        return prev[:-1] + cur
    return prev + ' ' + cur


def termina(s):
    t = re.sub(r'[*_\s]+$', '', s)
    return t.endswith(TERM)


# Cuadro «Compromisos medibles»
def celdas(fila):
    cs = fila.strip()[1:-1].split('|')
    return [[p.strip() for p in c.split('<br>') if p.strip()] for c in cs]


def es_valor(p):
    return '**' in p or p.startswith('_')


def con_simbolos(partes):
    """Coloca ≥ ≤ ≈ ₂ donde estaban (la conversión los saca a una línea aparte)."""
    out = []
    for p in partes:
        if p in SIMBOLOS:
            if p == '₂':
                for i in range(len(out) - 1, -1, -1):
                    if 'CO -' in out[i]:
                        out[i] = out[i].replace('CO -', 'CO₂-'); break
                continue
            hecho = False
            for i in range(len(out) - 1, -1, -1):
                if '  ' in out[i]:
                    out[i] = out[i].replace('  ', f' {p} ', 1); hecho = True; break
            if not hecho:
                k = next((i for i, x in enumerate(out) if es_valor(x)), 0)
                if out:
                    out[k] = re.sub(r'^(\*\*)?', lambda m: (m.group(1) or '') + p + ' ', out[k], count=1)
            continue
        out.append(p)
    return out


def juntar(partes):
    s = ''
    for p in partes:
        p = sin_marcas(p)
        s = s + p if s.endswith(('–', '-')) or not s else s + ' ' + p
    return s


def tabla_compromisos(filas):
    filas = [f for f in filas if not re.match(r'^\|[-|]+\|$', f.strip()) and 'Q U É' not in f]
    grupos, pendiente = [], None
    for n, f in enumerate(filas):
        c = celdas(f)
        llenas = sum(1 for x in c if x)
        ultima = n == len(filas) - 1
        if llenas <= 2:  # trozo de una fila partida
            if c[0]:
                t = sin_marcas(c[0][0])
                previa = (re.match(r'^[a-záéíóúñ(]', t) or ultima or
                          (grupos and sin_marcas(' '.join(grupos[-1][0])).count('(') > sin_marcas(' '.join(grupos[-1][0])).count(')')))
            else:
                texto = [p for x in c for p in x if p not in SIMBOLOS]
                previa = ultima or not any(es_valor(p) for p in texto)
            if previa and grupos and not pendiente:
                for i in range(4):
                    grupos[-1][i] += c[i]
            elif pendiente:
                for i in range(4):
                    pendiente[i] += c[i]
            else:
                pendiente = c
            continue
        if pendiente:
            for i in range(4):
                pendiente[i] += c[i]
            grupos.append(pendiente); pendiente = None
        elif grupos and (re.match(r'^[a-záéíóúñ(]', sin_marcas(c[0][0]) if c[0] else 'x')
                         or not grupos[-1][3] or juntar(grupos[-1][3]).endswith('–')):
            for i in range(4):
                grupos[-1][i] += c[i]
        else:
            grupos.append(c)
    if pendiente:
        grupos.append(pendiente)
    out = []
    for g in grupos:
        que = juntar(g[0])
        hoy = con_simbolos(g[1])
        val = juntar([p for p in hoy if es_valor(p)])
        fuente = juntar([p for p in hoy if not es_valor(p)])
        hoy_s = f"{val} ({fuente})" if fuente else val
        meta = juntar(con_simbolos(g[2]))
        plazo = juntar(g[3])
        out += [f"- **{que}** — {hoy_s} — Meta: {meta} — Plazo: {plazo}", '']
    return out


def limpiar(lineas):
    ini = next(i for i, l in enumerate(lineas) if re.match(r'^#\s+\*\*01\*\*', l.strip()))
    ls = [l.rstrip() for l in lineas[ini:]]
    for a, b in ARREGLOS[:3]:
        ls = [l.replace(a, b) for l in ls]

    # infografía «El esfuerzo en cifras» de Vivienda: columnas mezcladas, se reordenan según el PDF
    i1 = next(i for i, l in enumerate(ls) if l.strip() == '##### **1,35 M**')
    i2 = next(i for i, l in enumerate(ls) if l.strip() == 'la aportación estatal anual actual')
    ls[i1:i2 + 1] = ['**1,1 %** → **5 %** del parque de vivienda en 2030', '',
                     '**1,35 M** viviendas sociales y asequibles permanentes', '',
                     '≤ **30 %** de la renta familiar como alquiler máximo', '',
                     '**× 12–18** la aportación estatal anual actual']

    out = ['# Programa elecciones generales 2026', '']
    modo, titulo, esperado = 'intro', None, 1
    medida = None   # lista de trozos de la medida en curso
    tabla, anexo_ref = [], None

    def cerrar_medida():
        nonlocal medida
        if medida:
            txt = medida[0]
            for t in medida[1:]:
                if t.startswith('  - '):
                    txt += '\n' + t
                elif t.startswith('\n'):
                    txt += t
                else:
                    ultimo = txt.split('\n')[-1]
                    txt = txt[:len(txt) - len(ultimo)] + unir(ultimo, t)
            out.extend([txt, ''])
            medida = None

    def cerrar_tabla():
        nonlocal tabla
        if tabla:
            if modo == 'compromisos':
                out.extend(tabla_compromisos(tabla))
            else:
                out.extend([t.replace('<br>', ' ') for t in tabla] + [''])
            tabla = []

    for raw in ls:
        s = raw.strip()
        if not s:
            continue
        if s.startswith('|'):
            cerrar_medida()
            tabla.append(s); continue
        cerrar_tabla()
        c = compacto(s)

        # comienzo de eje o del anexo
        m = re.match(r'^#\s+\*\*(\d{2}|\+)', s)
        if m:
            cerrar_medida()
            if m.group(1) == '+':
                titulo = ANEXO
                out += [f'## Anexo. {ANEXO}', '']
                modo = 'anexo'
            else:
                titulo = CAPS[int(m.group(1)) - 1]
                out += [f'## {m.group(1)}. {titulo}', '']
                modo = 'intro'
            esperado = 1
            continue
        if re.match(r'^(EJE\d+|ANEXO)·PROGRAMAELECTORAL29N2026$', c):
            continue
        if s.startswith('#') and titulo and norm(s) == norm(titulo):
            continue
        if c.startswith('Teinteresasiteimporta:'):
            resto = plain(s).split(':', 1)[1].strip()
            tags = []
            while resto:
                t = next((t for t in TAGS if resto.startswith(t)), None)
                if not t:
                    tags = None; break
                tags.append(t); resto = resto[len(t):].strip()
            out += ['Te interesa si te importa: ' + (' · '.join(tags) if tags else plain(s).split(':', 1)[1].strip()), '']
            continue
        # rótulos de sección (letras espaciadas)
        if c == 'OBJETIVOS':
            cerrar_medida(); out += ['### Objetivos', '']; modo = 'objetivos'; continue
        if c == 'MEDIDAS':
            cerrar_medida(); out += ['### Medidas', '']; modo = 'texto'; continue
        if c == 'ELESFUERZOENCIFRAS':
            cerrar_medida(); out += ['**El esfuerzo en cifras**', '']; modo = 'texto'; continue
        if c.startswith('COMPROMISOSMEDIBLES'):
            cerrar_medida()
            out += ['### Compromisos medibles 2026–2030. Así podrás comprobar si cumplimos', '']
            modo = 'compromisos'; continue
        if c == 'Asípodráscomprobarsicumplimos':
            continue
        if c.startswith('FUENTESCONSULTADAS'):
            cerrar_medida()
            refs = plain(s)[plain(s).index('['):]
            out += ['Fuentes consultadas: ' + refs, '']
            continue

        if modo == 'anexo':
            if s.startswith('- '):
                if anexo_ref is not None:
                    out += [anexo_ref, '']
                k = int(re.search(r'\[(\d)\]', s).group(1))
                txt = s[2:].split('http')[0].rstrip()
                txt = re.sub(r'_ \.', '_.', txt)
                anexo_ref = txt + ' ' + URLS[k - 1]
            elif anexo_ref is None:
                out += [s, '']
            # las demás líneas son trozos de URL ya repuestos
            continue

        # medida numerada
        mm = re.match(r'^(#+\s*)?(-\s+)?(\*\*)?(\d{1,2})(\.)?(\*\*)?\s+(.*)$', s)
        if mm and int(mm.group(4)) == esperado and (mm.group(1) or mm.group(2) or mm.group(3) or mm.group(5)):
            cerrar_medida()
            resto = mm.group(7)
            txt = ('**' if mm.group(3) and not mm.group(6) else '') + resto
            medida = [f'{esperado}. {txt}']
            esperado += 1
            modo = 'medida'
            continue

        if modo == 'medida':
            if re.match(r'^-\s', s):
                medida.append('  - ' + re.sub(r'^-\s+', '', s)); continue
            t = re.sub(r'^#+\s*', '', s)
            ultimo = medida[-1].split('\n')[-1] if not medida[-1].startswith('\n') else medida[-1]
            if termina(ultimo) and not medida[-1].startswith('  - '):
                medida.append('\n' + t)
            elif termina(ultimo):
                medida.append('\n' + t)
            else:
                medida.append(t)
            continue

        if modo == 'objetivos' and re.match(r'^-\s', s):
            out += ['  - ' + s[2:].strip(), '']
            continue
        if s.startswith('#'):
            out += [f'**{plain(s)}**', '']
            continue
        out += [s, '']
    cerrar_medida()
    cerrar_tabla()
    if anexo_ref is not None:
        out += [anexo_ref, '']

    # entradillas en cursiva partidas en dos líneas
    res = []
    for l in out:
        k = len(res) - 1
        while k >= 0 and not res[k].strip():
            k -= 1
        if (k >= 0 and l.startswith('_') and re.match(r'^_[a-záéíóúñ]', l) and res[k].endswith('_')
                and not res[k][:-1].rstrip().endswith(TERM + (',',))):
            res = res[:k] + [res[k][:-1].rstrip() + ' ' + l[1:]]
            continue
        res.append(l)
    out = res

    texto = '\n'.join(out)
    texto = re.sub(r'\*\* ([,.;:)])', r'**\1', texto)
    texto = re.sub(r'\*\* _,', '**_,', texto)
    texto = re.sub(r' \._$', '._', texto, flags=re.M)
    texto = texto.replace('** **', ' ')
    for a, b in ARREGLOS[3:]:
        texto = texto.replace(a, b)
    # los subpuntos de los objetivos van pegados al párrafo que los presenta
    texto = re.sub(r'\n\n(  - )', r'\n\1', texto)
    return texto.split('\n')


DROP = ()

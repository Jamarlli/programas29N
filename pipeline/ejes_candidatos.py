"""Prepara la revisión de ejes de contraste: para cada eje, los extractos candidatos.

Un extracto es candidato si:
- su subtema principal o uno secundario está entre los subtemas del eje;
- su texto contiene alguna palabra clave del eje;
- o ya marcaba posición en ese eje.

Uso: python -I pipeline/ejes_candidatos.py <raiz_proyecto> <n_grupos> [--partidos a,b,c] [--ejes x,y] [--desde N]
Escribe data/ejes/candidatos-NN.json (reparto equilibrado de ejes por grupos).
Con --partidos solo entran extractos de esos partidos y los grupos se numeran desde N
(para revisar partidos nuevos sin tocar los grupos ya revisados).
Con --ejes solo entran esos ejes (para revisar ejes nuevos en todos los partidos).
"""
import json, re, sys, pathlib

raiz = pathlib.Path(sys.argv[1])
n = int(sys.argv[2])
args = sys.argv[3:]
solo = set(args[args.index('--partidos') + 1].split(',')) if '--partidos' in args else None
sel = set(args[args.index('--ejes') + 1].split(',')) if '--ejes' in args else None
desde = int(args[args.index('--desde') + 1]) if '--desde' in args else 1
assert (solo is None and sel is None) == (desde == 1), 'usa --partidos o --ejes junto con --desde'
data = raiz / 'data'

CFG = {
    'eje-irpf': (['imp-irpf', 'imp-modelo'], r'IRPF|[Rr]enta de las [Pp]ersonas'),
    'eje-patrimonio': (['imp-capital-patrimonio', 'imp-modelo'], r'[Ii]mpuesto (sobre el|de) [Pp]atrimonio|[Gg]randes (fortunas|patrimonios)|riqueza'),
    'eje-herencias': (['imp-capital-patrimonio'], r'[Ss]ucesiones|[Hh]erencia|[Dd]onaciones'),
    'eje-sociedades': (['imp-sociedades'], r'[Ii]mpuesto (sobre|de) [Ss]ociedades|tipo m[ií]nimo'),
    'eje-iva': (['imp-iva-indirectos'], r'\bIVA\b'),
    'eje-capital': (['imp-capital-patrimonio'], r'rentas del capital|dividendos|plusval[ií]as|ahorro'),
    'eje-ley-vivienda': (['vivienda-derecho'], r'Ley (por el Derecho a la|de) Vivienda|Ley 12/2023|ley de vivienda'),
    'eje-alquiler': (['vivienda-alquiler'], r'precios? del alquiler|zonas? tensionad|[ií]ndice de referencia|control de (precios|rentas)|limitar? (el precio|las rentas)'),
    'eje-okupacion': (['vivienda-okupacion-desahucios'], r'[Oo]kupa|[Oo]cupaci[oó]n ilegal|desahucio|desalojo|inquiokup'),
    'eje-smi': (['trab-salarios'], r'[Ss]alario [Mm][ií]nimo|\bSMI\b'),
    'eje-jornada': (['trab-jornada'], r'jornada laboral|reducci[oó]n de (la )?jornada|horas semanales|37[,.]5'),
    'eje-reforma-laboral': (['trab-contratos-despido'], r'[Rr]eforma [Ll]aboral|despido'),
    'eje-nuclear': ([], r'[Nn]uclear'),
    'eje-agua': (['agua'], r'[Tt]rasvase|interconexi[oó]n de cuencas|[Pp]lan [Hh]idrol[oó]gico'),
    'eje-gestion-sanitaria': (['san-modelo'], r'gesti[oó]n (p[uú]blica|directa|privada)|privatiz|concierto|colaboraci[oó]n p[uú]blico'),
    'eje-regularizacion': (['inm-regularizacion'], r'[Rr]egulariza|arraigo'),
    'eje-violencia-genero': (['igu-violencia'], r'[Vv]iolencia de g[eé]nero|[Vv]iolencia intrafamiliar|[Ll]ey [Ii]ntegral|1/2004'),
    'eje-aborto': (['igu-vida', 'san-sexual-reproductiva'], r'[Aa]borto|[Ii]nterrupci[oó]n voluntaria|desde (su|la) concepci[oó]n'),
    'eje-trans': (['igu-lgtbi'], r'[Ll]ey [Tt]rans|autodeterminaci[oó]n|personas trans'),
    'eje-memoria': (['igu-memoria'], r'[Mm]emoria [Dd]emocr[aá]tica|[Mm]emoria [Hh]ist[oó]rica|[Cc]oncordia'),
    'eje-territorial': (['inst-territorial'], r'[Ff]ederal|[Pp]lurinacional|recentraliz|devolver al Estado|[Ee]stado de las [Aa]utonom[ií]as'),
    'eje-jefatura': ([], r'[Mm]onarqu[ií]a|[Rr]ep[uú]blica|\bCorona\b|[Jj]efatura del Estado'),
    'eje-defensa': (['seg-defensa'], r'[Gg]asto (militar|en defensa)|\bOTAN\b|PIB en defensa|[Rr]earme|belicis'),
    'eje-cgpj': ([], r'\bCGPJ\b|Consejo General del Poder Judicial|vocales'),
    'eje-lengua': (['edu-lenguas'], r'lengua vehicular|inmersi[oó]n|lenguas cooficiales|en espa[nñ]ol'),
    'eje-financiacion-autonomica': (['inst-financiacion-autonomica'], r'[Cc]ondona|deuda auton[oó]mica|deuda de las [Cc]omunidades'),
    'eje-amnistia': ([], r'[Aa]mnist[ií]a'),
    'eje-sedicion': ([], r'[Ss]edici[oó]n|[Uu]ltrajes?|[Ii]njurias a la Corona|[Oo]fensas'),
    'eje-mordaza': ([], r'[Ss]eguridad [Cc]iudadana|[Mm]ordaza'),
    'eje-prioridad-nacional': (['inm-integracion'], r'[Pp]rioridad nacional|[Pp]rioridad .{0,40}espa[nñ]oles|arraigo|a[nñ]os de residencia'),
    'eje-burka': ([], r'[Bb]urka|[Nn]iqab'),
    'eje-clima-ritmo': (['clima'], r'[Pp]acto [Vv]erde|[Aa]genda 2030|[Nn]eutralidad clim[aá]tica|PNIEC|[Dd]escarboniza'),
    'eje-tauromaquia': (['rural-tradiciones'], r'[Tt]aurom|[Tt]oros|[Cc]orridas'),
    'eje-prostitucion': ([], r'[Pp]rostituci|[Pp]roxenet|[Tt]rabajo sexual|[Tt]rabajadoras sexuales'),
    'eje-eutanasia': (['igu-vida'], r'[Ee]utanasia|[Cc]uidados paliativos|[Ss]uicidio asistido|[Mm]uerte digna'),
    'eje-concertada': ([], r'[Cc]oncertad|[Ll]ibertad de (elecci[oó]n|ense[nñ]anza)|elecci[oó]n de centro'),
    'eje-lomloe': ([], r'LOMLOE|[Ll]ey educativa|[Ll]ey Cela[aá]'),
    'eje-jubilacion': ([], r'[Ee]dad (legal )?de jubilaci[oó]n|jubilaci[oó]n anticipada|jubilaci[oó]n flexible|jubilaci[oó]n activa|65 a[nñ]os|67 a[nñ]os'),
    'eje-voto16': ([], r'16 a[nñ]os'),
    'eje-mercosur': ([], r'[Mm]ercosur|[Cc]l[aá]usulas? espejo'),
    'eje-otan': ([], r'\bOTAN\b|\bNATO\b|[Aa]lianza [Aa]tl[aá]ntica|[Aa]li[aà]n[cç]a [Aa]tl[aà]ntica|[Bb]ases (militares|estadounidenses|norteamericanas|de Rota)|[Bb]ases militars|\bRota\b|Mor[oó]n'),
    'eje-ppr': ([], r'[Pp]risi[oó]n [Pp]ermanente|[Cc]adena [Pp]erpetua|[Pp]res[oó] [Pp]ermanent|[Cc]adena [Pp]erp[eè]tua|[Pp]risi[oó]n perpetua'),
    'eje-gestacion': ([], r'[Gg]estaci[oó]n? subrogada|[Vv]ientres? de alquiler|[Vv]entres? de lloguer|[Mm]aternidad subrogada|[Ee]xplotaci[oó]n reproductiva|[Ee]xplotaci[oó] reproductiva'),
    'eje-cie': ([], r'\bCIE\b|\bCIEs\b|[Cc]entros? de [Ii]nternamiento|[Cc]entres? d.[Ii]nternament|[Ii]nternamento|\bCATE\b'),
    'eje-cannabis': ([], r'[Cc][aà]nn?abis|[Mm]arihuana|[Cc]a[nñ]amo|[Dd]espenaliz|[Aa]utocultivo|[Dd]rogas|[Dd]rogues'),
    'eje-renta-basica': (['fam-pobreza'], r'[Rr]enta [Bb][aá]sica|[Rr]enda [Bb][aá]sica|[Rr]enda [Bb]àsica|[Ii]ngreso [Mm][ií]nimo|\bIMV\b|[Pp]aguitas|incondicional'),
    'eje-ley-electoral': ([], r'[Ll]ey [Ee]lectoral|[Rr]eforma electoral|[Ll]lei [Ee]lectoral|LOREG|[Rr][eé]gimen [Ee]lectoral|[Ss]istema [Ee]lectoral|[Cc]ircunscripci[oó]n|[Cc]ircumscripci|proporcional|D.Hondt|lista m[aá]s votada'),
    'eje-listas': ([], r'[Ll]istas? (electorales )?(abiertas|desbloqueadas|cerradas|abertas)|[Ll]listes (electorals )?(obertes|desbloquejades|tancades)|[Dd]esbloque|[Dd]esbloqueig|[Vv]oto preferencial'),
    'eje-mandatos': ([], r'[Ll]imitaci[oó]n de mandatos|[Ll]imitar (los )?mandatos|[Ll]imitaci[oó] de mandats|dos mandatos|ocho a[nñ]os|m[aá]ximo de (dos|tres) (mandatos|legislaturas)|mandatos'),
    'eje-santa-sede': ([], r'[Ss]anta [Ss]ede|[Ss]anta [Ss]eu|[Ss]anta S[eé]\b|[Vv]aticano|[Cc]oncordato|[Ii]nmatricula|[Ii]mmatricula|[Cc]asilla de la [Ii]glesia|[Ff]inanciaci[oó]n de la [Ii]glesia'),
}


def main():
    tax = json.loads((data / 'taxonomia.json').read_text(encoding='utf-8'))
    ejes = {e['id']: e for e in tax['ejes']}
    assert set(ejes) == set(CFG), set(ejes) ^ set(CFG)
    ext = {f['id']: f for f in json.loads((data / 'extractos.json').read_text(encoding='utf-8'))}
    cl = {c['id']: c for c in json.loads((data / 'clasificacion.json').read_text(encoding='utf-8'))}
    paquetes = []
    for eid, (subs, rx) in CFG.items():
        if sel is not None and eid not in sel:
            continue
        r = re.compile(rx)
        cands = []
        for i, f in ext.items():
            if solo is not None and f['partido'] not in solo:
                continue
            c = cl[i]
            marcado = any(x['eje'] == eid for x in c['ejes'])
            if marcado or c['subtema'] in subs or set(c['otros']) & set(subs) or r.search(f['texto']):
                cands.append({'id': i, 'partido': f['partido'], 'titular': c['titular'],
                              'marca_actual': [x['posicion'] for x in c['ejes'] if x['eje'] == eid],
                              'texto': f['texto']})
        e = ejes[eid]
        paquetes.append({'eje': eid, 'pregunta': e['pregunta'], 'posiciones': e['posiciones'],
                         'n': len(cands), 'palabras': sum(len(x['texto'].split()) for x in cands), 'candidatos': cands})
    # reparto por palabras (codicioso)
    grupos = [[] for _ in range(n)]
    for p in sorted(paquetes, key=lambda p: -p['palabras']):
        min(grupos, key=lambda g: sum(x['palabras'] for x in g)).append(p)
    out = data / 'ejes'
    out.mkdir(exist_ok=True)
    for k, g in enumerate(grupos, desde):
        assert desde == 1 or not (out / f'candidatos-{k:02d}.json').exists(), f'ya existe candidatos-{k:02d}.json'
        (out / f'candidatos-{k:02d}.json').write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'grupo {k:02d}: {len(g)} ejes, {sum(p["n"] for p in g)} candidatos, {sum(p["palabras"] for p in g)} palabras:',
              ', '.join(f'{p["eje"]}({p["n"]})' for p in g))


main()

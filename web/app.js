/* Programas 29N. Vistas: inicio, tema, dónde chocan, programas, programa, búsqueda. */
(function () {
  'use strict';

  const D = window.PROGRAMAS;
  const main = document.getElementById('main');
  if (!D || !Array.isArray(D.extractos)) {
    main.innerHTML = `<div class="fallo"><h1>No se han podido cargar los programas</h1>
      <p>Falta el archivo de datos (data.js) o está dañado. Si has descargado la web, comprueba que data.js está en la misma carpeta que index.html y recarga la página.</p></div>`;
    return;
  }
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const norm = (s) => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const fmt = (n) => n.toLocaleString('es-ES');
  const pct = (x) => `${x.toLocaleString('es-ES', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} %`;
  const plural = (n, uno, varios) => `${fmt(n)} ${n === 1 ? uno : varios}`;
  const leer = (k, def) => { try { const v = JSON.parse(localStorage.getItem(k)); return v == null ? def : v; } catch (_) { return def; } };
  const guardar = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) { /* sin almacenamiento */ } };

  /* ---------- Índices ---------- */
  // todos: los programas que hay en la web. partidos: los que el lector compara (por defecto, los cuatro «base»),
  // en el orden de los datos. Se cambian con «Añadir partidos» y se recuerdan en este navegador.
  const todos = D.partidos;
  const P = Object.fromEntries(todos.map((p) => [p.id, p]));
  const BASE = todos.filter((p) => p.base !== false).map((p) => p.id);
  let partidos = [];
  function fijarPartidos(ids) {
    partidos = todos.filter((p) => ids.includes(p.id));
    if (!partidos.length) partidos = todos.filter((p) => BASE.includes(p.id));
  }
  fijarPartidos((leer('p29n-partidos', null) || BASE).filter((id) => P[id]));
  // color de cada partido: los cuatro primeros están en styles.css; los demás vienen en los datos
  const estiloPartidos = document.createElement('style');
  estiloPartidos.textContent = todos.filter((p) => /^#[0-9a-f]{6}$/i.test(p.color || '')).map((p) => `[data-p="${p.id}"]{--pc:${p.color}}`).join('');
  document.head.appendChild(estiloPartidos);
  const sub = {};
  const bloqueDe = {};
  D.bloques.forEach((b) => b.subtemas.forEach((s) => { sub[s.id] = s; bloqueDe[s.id] = b; }));
  const ejesDe = {};
  D.ejes.forEach((e) => (ejesDe[e.subtema] = ejesDe[e.subtema] || []).push(e));
  const E = D.extractos;
  const porId = Object.fromEntries(E.map((e) => [e.i, e]));
  const porSub = {}; // subtema → partido → [extractos]
  const tambien = {}; // subtema → partido → [extractos con ese subtema como secundario]
  const nExt = {};
  const palabras = {};
  const enComparacion = (e) => partidos.some((p) => p.id === e.p);
  E.forEach((e) => {
    nExt[e.p] = (nExt[e.p] || 0) + 1;
    palabras[e.p] = (palabras[e.p] || 0) + e.w;
    if (e.s) ((porSub[e.s] = porSub[e.s] || {})[e.p] = porSub[e.s][e.p] || []).push(e);
    e.x.forEach((x) => ((tambien[x] = tambien[x] || {})[e.p] = tambien[x][e.p] || []).push(e));
  });
  Object.values(porSub).forEach((f) => Object.values(f).forEach((l) => l.sort((a, b) => a.o - b.o)));
  const marcasDe = {}; // eje → posición → partido → [{e, cita}]
  D.marcas.forEach(([eje, id, pos, cita]) => {
    const e = porId[id];
    if (!e) return;
    const m = (marcasDe[eje] = marcasDe[eje] || {});
    const q = (m[pos] = m[pos] || {});
    (q[e.p] = q[e.p] || []).push({ e, cita });
  });
  const pendientesTodos = E.filter((e) => !e.s);
  const pendientes = () => pendientesTodos.filter(enComparacion);
  const nSubtemas = D.bloques.reduce((a, b) => a + b.subtemas.length, 0);
  let textoBusqueda = null;

  /* ---------- Preferencias locales ---------- */
  let visibles = partidos.map((p) => p.id); // no se guarda: cada visita empieza con todos los partidos elegidos
  let vistaTexto = leer('p29n-vista', 'titulares') === 'texto' ? 'texto' : 'titulares';
  let pestana = null; // partido elegido en las pestañas de móvil; se mantiene entre subtemas
  let ordenIndice = null;
  const pvis = () => partidos.filter((p) => visibles.includes(p.id));

  /* ---------- Piezas ---------- */
  const ICO = {
    chev: '<svg class="i i-chev" viewBox="0 0 16 16" aria-hidden="true"><path d="m4 6 4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    ext: '<svg class="i" viewBox="0 0 16 16" aria-hidden="true"><path d="M6.5 3.5h-3v9h9v-3M9.5 3h3.5v3.5M13 3 7.5 8.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    der: '<svg class="i" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    izq: '<svg class="i" viewBox="0 0 16 16" aria-hidden="true"><path d="M13 8H3M7 4 3 8l4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    mas: '<svg class="i" viewBox="0 0 16 16" aria-hidden="true"><path d="M8 3v10M3 8h10" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
    ok: '<svg class="i" viewBox="0 0 16 16" aria-hidden="true"><path d="m3.5 8.5 3 3 6-7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    x: '<svg class="i" viewBox="0 0 16 16" aria-hidden="true"><path d="m4 4 8 8M12 4l-8 8" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
    abajo: '<svg class="i" viewBox="0 0 16 16" aria-hidden="true"><path d="M8 3v10M4 9l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  };
  const enlacePDF = (e) => `${P[e.p].fuente}#page=${e.g}`;
  const hrefSub = (s) => `#/tema/${bloqueDe[s].id}/${s}`;
  // «Frente Amplio» → «FA»; los nombres cortos se quedan igual
  const abrev = (p) => (p.corto.includes(' ') ? p.corto.split(/\s+/).map((w) => w[0]).join('').toUpperCase() : p.corto);
  const sigla = (p, extra = '') => `<span class="pt" data-p="${p.id}" title="${esc(p.corto)}">${esc(abrev(p))}${extra}</span>`;
  const punto = (p) => `<span class="pc" data-p="${p.id}" aria-hidden="true"></span>`;
  const nombreP = (p) => (abrev(p) === p.corto ? esc(p.corto) : `<span class="largo">${esc(p.corto)}</span><abbr class="corto" title="${esc(p.corto)}">${esc(abrev(p))}</abbr>`);

  // punto lleno = partido visible; punto hueco = oculto (la forma lo dice, no solo el color)
  function filtroHTML(cuentas) {
    return `<div class="filtro" role="group" aria-labelledby="filtro-t">
      <span class="filtro-t" id="filtro-t">Comparar</span>
      ${partidos.map((p) => `<button type="button" class="chip" data-p="${p.id}" data-partido="${p.id}" aria-pressed="${visibles.includes(p.id)}">${punto(p)}${nombreP(p)}${cuentas ? `<span class="c">${fmt(cuentas[p.id] || 0)}</span>` : ''}</button>`).join('')}
    </div>`;
  }
  // Una fila por postura y, pegadas al nombre, las siglas de quien la defiende. Las siglas no son enlaces:
  // las citas se despliegan debajo, en la misma ficha.
  function posturasHTML(eje) {
    const m = marcasDe[eje.id] || {};
    return `<ul class="pf">${eje.posiciones.map((pos) => {
      const q = m[pos.id] || {};
      const ps = pvis().filter((p) => q[p.id]);
      return `<li${ps.length ? '' : ' class="pf--nadie"'}><span class="pf-n">${esc(pos.nombre)}</span><span class="pf-p">${ps.map((p) => sigla(p)).join('') || '<span class="nadie">Ningún partido</span>'}</span></li>`;
    }).join('')}</ul>`;
  }
  const segmentado = (clave, opciones, actual, etiqueta) =>
    `<div class="seg" role="group" aria-label="${esc(etiqueta)}">${opciones.map(([v, t]) =>
      `<button type="button" data-${clave}="${v}" aria-pressed="${v === actual}">${t}</button>`).join('')}</div>`;

  function extracto(e, o = {}) {
    const p = P[e.p];
    const abierto = o.fijo || (o.abierto != null ? o.abierto : vistaTexto === 'texto');
    const src = [];
    if (o.partido) src.push(`<strong>${esc(p.corto)}</strong>`);
    if (e.k === 'm' && e.n) src.push(`Medida ${esc(e.n)}`);
    if (!o.fijo) src.push(`<a href="#/e/${e.i}">Ver en su programa${ICO.der}</a>`);
    src.push(e.g ? `<a href="${esc(enlacePDF(e))}" target="_blank" rel="noopener">PDF, p. ${e.g}${ICO.ext}</a>` : 'Página sin localizar');
    if (o.tema && e.s) src.push(`<span>Tema: <a href="${hrefSub(e.s)}">${esc(sub[e.s].nombre)}</a></span>`);
    const ruta = D.rutas[e.r];
    const cab = o.fijo
      ? `<h3 class="ex-tit">${esc(e.h || 'Sin titular')}</h3>`
      : `<h3 class="ex-hh"><button type="button" class="ex-h" aria-expanded="${abierto}">
          ${o.partido ? sigla(p) : ''}<span class="ex-tit">${esc(e.h || 'Sin titular')}</span>
          ${ICO.chev}</button></h3>`;
    return `<article class="ex${abierto ? ' abierto' : ''}${o.fijo ? ' ex--fijo' : ''}" id="${e.i}">
      ${cab}
      <div class="ex-body">
        <div class="ex-txt" lang="es">${e.c}</div>
        <p class="ex-src">${src.join('<span class="sep" aria-hidden="true">·</span>')}</p>
        ${ruta && !o.sinRuta ? `<p class="ex-ruta">${esc(ruta)}</p>` : ''}
      </div>
    </article>`;
  }

  // reparte el 100 % entre los partidos según sus cuentas, en décimas y por el mayor resto,
  // para que la fila sume exactamente 100,0 % aunque se redondee a un decimal
  function reparto(c) {
    const suma = partidos.reduce((s, p) => s + (c[p.id] || 0), 0);
    const r = Object.fromEntries(partidos.map((p) => [p.id, 0]));
    if (!suma) return r;
    const exactos = partidos.map((p) => ({ id: p.id, x: ((c[p.id] || 0) / suma) * 1000 }));
    exactos.forEach((e) => { r[e.id] = Math.floor(e.x); });
    let falta = 1000 - exactos.reduce((s, e) => s + Math.floor(e.x), 0);
    // por grupos de la misma cuenta, para que dos partidos con los mismos extractos lleven el mismo porcentaje:
    // si un grupo no cabe entero en lo que falta, la décima pasa al siguiente
    const grupos = {};
    exactos.forEach((e) => { const k = (c[e.id] || 0).toFixed(6); (grupos[k] = grupos[k] || []).push(e); });
    Object.values(grupos).sort((a, b) => (b[0].x - Math.floor(b[0].x)) - (a[0].x - Math.floor(a[0].x))).forEach((g) => {
      if (g[0].x > Math.floor(g[0].x) && g.length <= falta) { g.forEach((e) => { r[e.id] += 1; }); falta -= g.length; }
    });
    partidos.forEach((p) => { r[p.id] /= 10; });
    return r;
  }

  function contarBloque(b) {
    const c = Object.fromEntries(partidos.map((p) => [p.id, 0]));
    b.subtemas.forEach((s) => partidos.forEach((p) => {
      ((porSub[s.id] || {})[p.id] || []).forEach((e) => { c[p.id] += 1; });
    }));
    return c;
  }

  /* Ficha de pregunta: la misma pieza en el tema y en «Dónde chocan».
     1) la pregunta; 2) las posturas con sus siglas; 3) un botón que despliega aquí mismo la cita de cada
     partido, con enlace a su programa; 4) un enlace que dice adónde lleva: todo lo que dicen sobre el subtema. */
  const citasAbiertas = {}; // eje → abierto o cerrado por el lector; si no ha tocado nada, manda la vista
  function preguntaHTML(eje, o = {}) {
    const m = marcasDe[eje.id] || {};
    const vs = pvis();
    const abierta = eje.id in citasAbiertas ? citasAbiertas[eje.id] : !!o.abierta;
    const sin = vs.filter((p) => !eje.posiciones.some((pos) => (m[pos.id] || {})[p.id]));
    const cols = vs.map((p) => {
      const suyas = eje.posiciones.filter((pos) => (m[pos.id] || {})[p.id]);
      const cuerpo = suyas.length ? suyas.map((pos) => `<div class="cp-pos">
          <p class="postura">${esc(pos.nombre)}</p>
          <ul>${m[pos.id][p.id].map(({ e, cita }) => `<li>${cita ? `<blockquote class="cita" lang="es">${esc(cita)}</blockquote>` : `<p class="cita-tit">${esc(e.h)}</p>`}
            <a class="ir" href="#/e/${e.i}/${eje.id}">Ver en su programa${e.g ? ` · p. ${e.g}` : ''}${ICO.der}</a></li>`).join('')}</ul>
        </div>`).join('') : '<p class="nadie">Su programa no toma una postura explícita.</p>';
      return `<div class="cp${suyas.length ? '' : ' cp--sin'}" data-p="${p.id}"><h4 class="cp-n">${punto(p)}${esc(p.corto)}</h4><div class="cp-cuerpo">${cuerpo}</div></div>`;
    });
    const s = sub[eje.subtema];
    const pie = o.enTema
      ? `<a class="eje-a" href="${hrefSub(s.id)}" data-salto="${s.id}">Todo lo que dicen sobre «${esc(s.nombre)}»${ICO.abajo}</a>`
      : `<a class="eje-a" href="${hrefSub(s.id)}">Todo lo que dicen sobre «${esc(s.nombre)}»${ICO.der}</a>`;
    return `<article class="eje" id="${eje.id}" aria-labelledby="q-${eje.id}">
      <h3 class="eje-q" id="q-${eje.id}">${esc(eje.pregunta)}</h3>
      ${posturasHTML(eje)}
      ${sin.length ? `<p class="eje-sin">Sin postura explícita: ${sin.map((p) => esc(p.corto)).join(', ')}</p>` : ''}
      <div class="eje-acc">
        <button type="button" class="eje-ver" data-citas="${eje.id}" aria-expanded="${abierta}" aria-controls="par-${eje.id}">${ICO.chev}<span class="si-cerrada">Ver la cita de cada partido</span><span class="si-abierta">Ocultar las citas</span></button>
        ${pie}
      </div>
      <div class="eje-par" id="par-${eje.id}" style="--k:${Math.min(vs.length, 4)}"${abierta ? '' : ' hidden'}>${cols.join('')}</div>
    </article>`;
  }

  /* ---------- Inicio ---------- */
  function indiceHTML() {
    const filas = D.bloques.map((b) => ({ b, c: contarBloque(b) }));
    // cifra: qué parte de su programa dedica cada partido al tema (comparable entre programas de distinta extensión);
    // barra: esas cifras repartidas entre los partidos de la fila, que suma el 100 %
    filas.forEach((f) => {
      f.cuota = Object.fromEntries(partidos.map((p) => [p.id, nExt[p.id] ? (f.c[p.id] / nExt[p.id]) * 100 : 0]));
      f.barra = reparto(f.cuota);
    });
    const orden = filas.slice();
    if (ordenIndice) orden.sort((a, b) => b.cuota[ordenIndice] - a.cuota[ordenIndice]);
    return `<div class="indice-w${partidos.length > 4 ? ' indice-w--ancha' : ''}" id="indice" style="--np:${partidos.length}">
      <p class="nota indice-nota">La cifra grande es el número de extractos. El porcentaje pequeño dice qué parte de su programa dedica cada partido al tema, para comparar programas de extensiones muy distintas. La barra reparte esos porcentajes entre los partidos de la fila, que entre todas suman el 100 %: la más larga es la del partido que más peso le da al tema dentro de su programa. Pulsa el nombre de un partido para ordenar por su porcentaje.</p>
      <div class="indice-scroll"><table class="indice">
        <caption class="sr">Extractos de cada programa por tema, porcentaje que suponen sobre todos los extractos del partido y reparto de esos porcentajes entre los partidos</caption>
        <thead><tr><th scope="col">Tema</th>${partidos.map((p) => `<th scope="col" class="num"${ordenIndice === p.id ? ' aria-sort="descending"' : ''}>
          <button type="button" class="ord" data-orden="${p.id}" aria-pressed="${ordenIndice === p.id}">${punto(p)}${nombreP(p)}${ICO.abajo}</button></th>`).join('')}</tr></thead>
        <tbody>${orden.map((f) => `<tr data-href="#/tema/${f.b.id}">
          <th scope="row"><a href="#/tema/${f.b.id}">${esc(f.b.nombre)}</a><span class="n-sub">${plural(f.b.subtemas.length, 'subtema', 'subtemas')}</span></th>
          ${partidos.map((p) => {
            const n = f.c[p.id];
            const q = f.cuota[p.id];
            const t = `${p.corto}: ${plural(n, 'extracto', 'extractos')}, el ${pct(q)} de su programa; en la barra, el ${pct(f.barra[p.id])} del peso que le dan al tema los partidos`;
            return `<td class="num${n ? '' : ' cero'}" data-p="${p.id}" title="${esc(t)}"><span class="v">${fmt(n)}<span class="sr"> extractos</span></span>
              <span class="cuota"><span class="bar" aria-hidden="true"><i style="width:${f.barra[p.id].toFixed(1)}%"></i></span><span class="q">${n ? pct(q) : ''}<span class="sr"> de su programa</span></span></span></td>`;
          }).join('')}
        </tr>`).join('')}
        ${pendientes().length ? `<tr data-href="#/tema/_pendientes"><th scope="row"><a href="#/tema/_pendientes">Pendientes de clasificar</a></th>${partidos.map((p) => `<td class="num">${pendientes().filter((e) => e.p === p.id).length}</td>`).join('')}</tr>` : ''}
        </tbody>
        <tfoot><tr><th scope="row">Programa completo</th>${partidos.map((p) => `<td class="num"><a href="#/programa/${p.id}">${fmt(nExt[p.id])}</a> <span class="q">100 %</span></td>`).join('')}</tr></tfoot>
      </table></div>
    </div>`;
  }

  function vInicio() {
    const destacados = D.ejes.filter((e) => marcasDe[e.id]).map((e) => {
      const ps = new Set(Object.values(marcasDe[e.id]).flatMap((q) => Object.keys(q)).filter((id) => partidos.some((p) => p.id === id)));
      return { e, pos: e.posiciones.filter((p) => marcasDe[e.id][p.id]).length, n: ps.size };
    }).filter((x) => x.pos > 1).sort((a, b) => b.n - a.n || b.pos - a.pos).slice(0, 6);
    const nEjes = D.ejes.filter((e) => marcasDe[e.id]).length;
    return `
      <section class="hero">
        <h1>Qué proponen los partidos para el 29N</h1>
        <p class="lead">${partidos.length > 4 ? `Los programas de los ${partidos.length} partidos que comparas` : `Los programas de ${partidos.map((p) => esc(p.corto)).join(', ').replace(/, ([^,]*)$/, ' y $1')}`}, enteros y ordenados por temas. <a href="#/" data-salto="h-temas">Elige un tema</a> para leer qué dice cada partido, mira <a href="#/choques">dónde chocan</a> en ${nEjes} preguntas concretas o <a href="#/buscar">busca una palabra</a>. Lo que dice un partido está copiado tal cual de su programa, y siempre puedes verlo en el original.</p>
        <ul class="hero-p">${partidos.map((p) => `<li><a href="#/programa/${p.id}" data-p="${p.id}">${punto(p)}${esc(p.corto)}</a><span class="c">${p.paginas} págs.</span></li>`).join('')}</ul>
      </section>
      <section class="bloque" aria-labelledby="h-temas">
        <div class="bloque-h"><h2 id="h-temas">Elige un tema</h2><p class="bloque-d">${D.bloques.length} temas y ${nSubtemas} subtemas. Dentro de cada tema verás primero dónde chocan los partidos y después todo lo que dice cada uno.</p></div>
        ${indiceHTML()}
      </section>
      ${destacados.length ? `<section class="bloque bloque--choques" aria-labelledby="h-choques">
        <div class="bloque-h"><h2 id="h-choques">Dónde chocan</h2><p class="bloque-d">Preguntas en las que los programas dicen cosas opuestas. Cada sigla está junto a la postura que defiende su partido; pulsa una pregunta para leer las citas.</p></div>
        <ul class="qcs">${destacados.map(({ e }) => `<li class="qc">
          <p class="qc-t">${esc(bloqueDe[e.subtema].nombre)} › ${esc(sub[e.subtema].nombre)}</p>
          <h3 class="qc-q"><a href="#/choques#${e.id}">${esc(e.pregunta)}</a></h3>
          ${posturasHTML({ ...e, posiciones: e.posiciones.filter((pos) => marcasDe[e.id][pos.id]) })}
        </li>`).join('')}</ul>
        <p class="mas-p"><a class="btn" href="#/choques">Ver las ${nEjes} preguntas</a></p>
      </section>` : ''}`;
  }

  /* ---------- Tema ---------- */
  function vBloque(bid) {
    if (bid === '_pendientes') return vPendientes();
    const b = D.bloques.find((x) => x.id === bid);
    if (!b) return vNoEncontrado();
    const vs = pvis();
    const i = D.bloques.indexOf(b);
    const ant = D.bloques[i - 1];
    const sig = D.bloques[i + 1];
    const nDe = (s) => vs.reduce((a, p) => a + ((porSub[s.id] || {})[p.id] || []).length, 0);
    const total = b.subtemas.reduce((a, s) => a + nDe(s), 0);
    const subs = b.subtemas.map((s) => {
      const fila = porSub[s.id] || {};
      const tam = tambien[s.id] || {};
      const n = nDe(s);
      // extractos con postura en los ejes de este subtema aunque su tema principal sea otro
      const conEje = {};
      (ejesDe[s.id] || []).forEach((ej) => Object.values(marcasDe[ej.id] || {}).forEach((q) =>
        Object.entries(q).forEach(([pid, l]) => l.forEach(({ e }) => { if (e.s !== s.id) (conEje[pid] = conEje[pid] || new Set()).add(e); }))));
      const act = pestana && visibles.includes(pestana) ? pestana : (vs.find((p) => (fila[p.id] || []).length) || vs[0]).id;
      const cols = vs.map((p) => {
        const l = fila[p.id] || [];
        const t = [...new Set([...(tam[p.id] || []), ...(conEje[p.id] || [])])].sort((a, b2) => a.o - b2.o);
        return `<div class="col${p.id === act ? ' on' : ''}" data-p="${p.id}" id="${s.id}--${p.id}" role="tabpanel" aria-label="${esc(p.corto)}">
          <h3 class="col-h">${punto(p)}${esc(p.corto)}<span class="c">${l.length || ''}</span></h3>
          ${l.length ? `<div class="col-l">${l.map((e) => extracto(e)).join('')}</div>` : '<p class="vacio">Ningún extracto clasificado en este subtema.</p>'}
          ${t.length ? `<details class="tambien"${l.length ? '' : ' open'}><summary>${ICO.chev}Lo trata también en otros subtemas<span class="c">${t.length}</span></summary>
            <div class="col-l">${t.map((e) => extracto(e, { tema: true })).join('')}</div></details>` : ''}
        </div>`;
      }).join('');
      return `<section class="sub" id="${s.id}" aria-labelledby="h-${s.id}">
        <header class="sub-h"><h2 id="h-${s.id}">${esc(s.nombre)}</h2><span class="c">${plural(n, 'extracto', 'extractos')}</span></header>
        ${vs.length > 1 ? `<div class="pestanas" role="tablist" aria-label="Partido">${vs.map((p) => {
          const k = (fila[p.id] || []).length;
          return `<button type="button" role="tab" data-tab="${p.id}" aria-selected="${p.id === act}">${punto(p)}${nombreP(p)}<span class="c">${k}</span></button>`;
        }).join('')}</div>` : ''}
        <div class="fila" style="--n:${Math.min(vs.length, 4)}">${cols}</div>
      </section>`;
    }).join('');
    // primero lo que separa a los partidos en este tema; después, todo lo que dice cada uno
    const ejes = b.subtemas.flatMap((s) => (ejesDe[s.id] || []).filter((e) => marcasDe[e.id]));
    const idCh = `choques-${b.id}`;
    const choques = ejes.length ? `<section class="sub sub--choques" id="${idCh}" aria-labelledby="h-${idCh}">
        <header class="sub-h"><h2 id="h-${idCh}">Dónde chocan</h2><span class="c">${plural(ejes.length, 'pregunta', 'preguntas')}</span></header>
        <p class="sub-d">Lo que separa a los partidos en ${esc(b.nombre.toLowerCase())}. Cada sigla está junto a la postura que defiende su programa; despliega las citas para leer lo que dice cada uno.</p>
        ${ejes.map((e) => preguntaHTML(e, { enTema: true })).join('')}
      </section>` : '';
    const entradas = [
      ...(ejes.length ? [{ id: idCh, nombre: 'Dónde chocan', n: ejes.length, cls: ' class="ir-choques"' }] : []),
      ...b.subtemas.map((s) => ({ id: s.id, href: hrefSub(s.id), nombre: s.nombre, n: nDe(s), cls: '' })),
    ];
    const hrefE = (x) => x.href || `#/tema/${b.id}/${x.id}`;
    return `
      <div class="con-lado">
        <aside class="lado">
          <nav aria-label="Secciones de ${esc(b.nombre)}">
            <p class="lado-t">En este tema</p>
            <ol class="lado-l">${entradas.map((x) => `<li${x.cls}><a href="${hrefE(x)}" data-salto="${x.id}"><span>${esc(x.nombre)}</span><span class="c">${x.n}</span></a></li>`).join('')}</ol>
            <details class="lado-o"><summary>${ICO.chev}Otros temas</summary><ol>${D.bloques.map((x) => `<li><a href="#/tema/${x.id}"${x === b ? ' aria-current="page"' : ''}>${esc(x.nombre)}</a></li>`).join('')}</ol></details>
          </nav>
        </aside>
        <div class="cuerpo">
          <div class="cab">
            <nav class="migas" aria-label="Estás en"><a href="#/">Temas</a><span aria-hidden="true">›</span><span aria-current="page">${esc(b.nombre)}</span></nav>
            <h1>${esc(b.nombre)}</h1>
            <p class="cab-d">${plural(b.subtemas.length, 'subtema', 'subtemas')} · ${plural(total, 'extracto', 'extractos')}${ejes.length ? ` · ${plural(ejes.length, 'pregunta', 'preguntas')} en las que chocan` : ''}</p>
            <nav class="subindice" aria-label="Secciones">${entradas.map((x) => `<a href="${hrefE(x)}" data-salto="${x.id}">${esc(x.nombre)}<span class="c">${x.n}</span></a>`).join('')}</nav>
            <div class="barra">${filtroHTML()}<div class="vista">${segmentado('vista', [['titulares', 'Resumen'], ['texto', 'Texto completo']], vistaTexto, 'Cómo se muestran los extractos')}<p class="nota">Los titulares son nuestros; el texto es literal del partido.</p></div></div>
          </div>
          ${choques}
          ${subs}
          <nav class="paso" aria-label="Otros temas">
            ${ant ? `<a class="paso-a" href="#/tema/${ant.id}"><span class="paso-k">${ICO.izq}Anterior</span><span class="paso-n">${esc(ant.nombre)}</span></a>` : '<span></span>'}
            ${sig ? `<a class="paso-a der" href="#/tema/${sig.id}"><span class="paso-k">Siguiente${ICO.der}</span><span class="paso-n">${esc(sig.nombre)}</span></a>` : ''}
          </nav>
        </div>
      </div>`;
  }

  function vPendientes() {
    return `<div class="cab"><h1>Pendientes de clasificar</h1>
      <p class="lead">Extractos que aún no tienen tema asignado. Siguen estando en el programa completo de cada partido.</p></div>
      <div class="lista">${pendientes().map((e) => extracto(e, { partido: true, abierto: true })).join('')}</div>`;
  }

  /* ---------- Dónde chocan ---------- */
  function vChoques() {
    const bloques = D.bloques.map((b) => ({ b, ejes: D.ejes.filter((e) => bloqueDe[e.subtema] === b && marcasDe[e.id]) })).filter((x) => x.ejes.length);
    const vacios = D.ejes.filter((e) => !marcasDe[e.id]);
    return `
      <div class="con-lado">
        <aside class="lado">
          <nav aria-label="Temas con preguntas">
            <p class="lado-t">Temas</p>
            <ol class="lado-l">${bloques.map(({ b, ejes }) => `<li><a href="#/choques#hb-${b.id}" data-salto="hb-${b.id}"><span>${esc(b.nombre)}</span><span class="c">${ejes.length}</span></a></li>`).join('')}</ol>
          </nav>
        </aside>
        <div class="cuerpo">
          <div class="cab">
            <h1>Dónde chocan</h1>
            <p class="lead">${plural(bloques.reduce((a, x) => a + x.ejes.length, 0), 'pregunta', 'preguntas')} en las que los programas toman posturas distintas. Un partido aparece en una postura solo si su programa lo dice de forma explícita; debajo de cada pregunta está su cita literal, con enlace a la página de su programa.</p>
            <nav class="subindice" aria-label="Temas">${bloques.map(({ b, ejes }) => `<a href="#/choques#hb-${b.id}" data-salto="hb-${b.id}">${esc(b.nombre)}<span class="c">${ejes.length}</span></a>`).join('')}</nav>
            <div class="barra">${filtroHTML()}</div>
          </div>
          ${bloques.map(({ b, ejes }) => `<section class="grupo-ejes" id="hb-${b.id}" aria-labelledby="hbh-${b.id}">
            <div class="grupo-h"><h2 id="hbh-${b.id}">${esc(b.nombre)}</h2><a class="eje-a" href="#/tema/${b.id}">Todo el tema${ICO.der}</a></div>
            ${ejes.map((e) => preguntaHTML(e, { abierta: true })).join('')}
          </section>`).join('')}
          ${vacios.length ? `<p class="nota nota--pie">Sin postura explícita de ningún partido: ${vacios.map((e) => esc(e.pregunta)).join(' · ')}</p>` : ''}
        </div>
      </div>`;
  }

  /* ---------- Programas ---------- */
  function vProgramas() {
    return `
      <div class="cab"><h1>Programas completos</h1>
        <p class="lead">Cada programa entero, en su orden original y con sus títulos. Aquí se puede comprobar que no falta nada. Los que no estás comparando se añaden desde «Añadir partidos», arriba.</p></div>
      <ul class="programas">${todos.map((p) => `<li>
          <a class="pg" href="#/programa/${p.id}" data-p="${p.id}">
            <span class="pg-n">${punto(p)}${esc(p.corto)}</span>
            <span class="pg-t">${esc(p.titulo)}</span>
            <span class="pg-d">${esc(p.nombre)}</span>
            <span class="pg-s"><span><b>${p.paginas}</b> páginas</span><span><b>${fmt(nExt[p.id])}</b> extractos</span><span><b>${fmt(palabras[p.id])}</b> palabras</span></span>
            <span class="pg-a">Leer el programa${ICO.der}</span>
          </a>
          <a class="pg-pdf" href="${esc(p.fuente)}" target="_blank" rel="noopener">PDF original${ICO.ext}</a>
        </li>`).join('')}</ul>`;
  }

  function vPrograma(pid) {
    const p = P[pid];
    if (!p) return vNoEncontrado();
    const l = E.filter((e) => e.p === pid).sort((a, b) => a.o - b.o);
    let prev = [];
    const toc = [];
    const cuerpo = l.map((e) => {
      const r = D.rutas[e.r] ? D.rutas[e.r].split(' › ') : [];
      let h = '';
      r.forEach((t, k) => {
        if (prev[k] === t && h === '') return;
        const nivel = Math.min(k + 2, 4);
        const id = `c-${pid}-${toc.length}`;
        if (k === 0) toc.push({ id, t });
        h += `<h${nivel} class="cap"${k === 0 ? ` id="${id}"` : ''}>${esc(t)}</h${nivel}>`;
      });
      prev = r;
      return h + extracto(e, { tema: true, sinRuta: true, fijo: true });
    }).join('');
    return `
      <div class="con-lado con-lado--prog">
        <aside class="lado">
          ${toc.length > 1 ? `<nav aria-label="Índice del programa"><details class="toc" open><summary>${ICO.chev}Índice</summary><ol class="lado-l">${toc.map((c) => `<li><a href="#/programa/${pid}#${c.id}" data-salto="${c.id}"><span>${esc(c.t)}</span></a></li>`).join('')}</ol></details></nav>` : ''}
        </aside>
        <div class="cuerpo">
          <div class="cab">
            <nav class="migas" aria-label="Estás en"><a href="#/programas">Programas</a><span aria-hidden="true">›</span><span aria-current="page">${esc(p.corto)}</span></nav>
            <h1>${esc(p.corto)}: <span class="prog-titulo">${esc(p.titulo)}</span></h1>
            <dl class="ficha">
              <div><dt>Candidatura</dt><dd>${esc(p.nombre)}</dd></div>
              <div><dt>Fuente</dt><dd><a href="${esc(p.fuente)}" target="_blank" rel="noopener">PDF de ${p.paginas} páginas${ICO.ext}</a> · ${esc(p.tipoFuente)} · descargado el ${esc(p.descarga)}</dd></div>
              <div><dt>Contenido</dt><dd>${plural(l.length, 'extracto', 'extractos')}, ${fmt(palabras[pid])} palabras. Es todo el texto del PDF; solo se han quitado el índice y las cabeceras de página.</dd></div>
            </dl>
            ${toc.length > 1 ? `<details class="toc-m"><summary>${ICO.chev}Índice del programa</summary><ol>${toc.map((c) => `<li><a href="#/programa/${pid}#${c.id}" data-salto="${c.id}">${esc(c.t)}</a></li>`).join('')}</ol></details>` : ''}
          </div>
          <div class="prog-txt">${cuerpo}</div>
        </div>
      </div>`;
  }

  /* ---------- Búsqueda ---------- */
  let terminos = [];
  let resultados = {};
  const POR_PAGINA = 40;
  function resultadosPartido(pid, desde) {
    const l = resultados[pid] || [];
    const hasta = Math.min(l.length, desde + POR_PAGINA);
    return l.slice(desde, hasta).map((e) => extracto(e, { tema: true, abierto: true })).join('') +
      (hasta < l.length ? `<p class="mas"><button type="button" class="btn" data-mas="${pid}:${hasta}">Mostrar ${Math.min(POR_PAGINA, l.length - hasta)} más de ${fmt(l.length - hasta)}</button></p>` : '');
  }
  // palabras de ejemplo para quien llega sin saber qué buscar; solo se muestran las que aparecen en los programas
  const EJEMPLOS = ['alquiler', 'pensiones', 'sanidad', 'inmigración', 'impuestos', 'educación', 'energía', 'agua', 'igualdad', 'autónomos', 'okupación', 'despoblación'];
  const prepararBusqueda = () => {
    if (textoBusqueda) return;
    const tmp = document.createElement('div');
    textoBusqueda = new Map(E.map((e) => { tmp.innerHTML = e.c; return [e.i, norm(`${e.h} ${tmp.textContent}`)]; }));
  };
  const cajaBusqueda = (q) => `<form class="busca-v" data-buscar role="search">
      <label class="sr" for="qv">Buscar en los programas</label>
      <svg class="busca-i" viewBox="0 0 20 20" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.75" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="m13 13 4.25 4.25" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
      <input id="qv" type="search" value="${esc(q)}" placeholder="Una o varias palabras" autocomplete="off" spellcheck="false" enterkeyhint="search">
      <button type="submit" class="btn btn--fuerte">Buscar</button>
    </form>`;
  function vBuscar(q) {
    $('#q').value = q;
    terminos = norm(q).split(/\s+/).filter((t) => t.length > 1);
    prepararBusqueda();
    if (!terminos.length) {
      const ejemplos = EJEMPLOS.map((w) => [w, E.filter((e) => enComparacion(e) && textoBusqueda.get(e.i).includes(norm(w))).length]).filter(([, n]) => n);
      return `<div class="cab cab--buscar"><h1>Buscar en los programas</h1>
        ${cajaBusqueda('')}
        <p class="nota">${q.trim() ? 'Escribe al menos una palabra de dos letras. ' : ''}Busca en el texto literal de ${partidos.length === 4 ? 'los cuatro programas' : `los ${partidos.length} programas`} que comparas.</p>
        ${ejemplos.length ? `<div class="ejemplos"><p class="ejemplos-t">Por ejemplo</p><ul>${ejemplos.map(([w, n]) => `<li><a href="#/buscar/${encodeURIComponent(w)}">${esc(w)}<span class="c">${fmt(n)}</span></a></li>`).join('')}</ul></div>` : ''}
      </div>`;
    }
    resultados = {};
    E.forEach((e) => {
      const t = textoBusqueda.get(e.i);
      if (terminos.every((w) => t.includes(w))) (resultados[e.p] = resultados[e.p] || []).push(e);
    });
    const vs = pvis();
    const total = vs.reduce((a, p) => a + (resultados[p.id] || []).length, 0);
    return `
      <div class="cab cab--buscar"><h1 class="sr">Resultados de la búsqueda</h1>
        ${cajaBusqueda(q)}
        <p class="res-n">${total ? `${plural(total, 'extracto contiene', 'extractos contienen')} ${terminos.length > 1 ? 'todas estas palabras' : '«' + esc(q.trim()) + '»'}.` : `Ningún extracto contiene ${terminos.length > 1 ? 'todas estas palabras' : '«' + esc(q.trim()) + '»'}. Prueba con menos palabras o con otra forma, por ejemplo «alquiler» en vez de «alquileres».`}</p>
        ${total ? `<div class="barra">${filtroHTML(Object.fromEntries(partidos.map((p) => [p.id, (resultados[p.id] || []).length])))}</div>` : ''}
      </div>
      ${total ? vs.map((p) => {
        const n = (resultados[p.id] || []).length;
        return `<section class="res-p" data-p="${p.id}" id="hr-${p.id}" aria-labelledby="hrh-${p.id}"><h2 id="hrh-${p.id}">${punto(p)}${esc(p.corto)}<span class="c">${plural(n, 'extracto', 'extractos')}</span></h2>
          ${n ? `<div class="lista">${resultadosPartido(p.id, 0)}</div>` : '<p class="vacio">Su programa no contiene esta búsqueda.</p>'}</section>`;
      }).join('') : ''}`;
  }
  const ACENTOS = { a: '[aáàäâ]', e: '[eéèëê]', i: '[iíìïî]', o: '[oóòöô]', u: '[uúùüû]', n: '[nñ]', c: '[cç]' };
  function resaltarBusqueda() {
    if (!terminos.length) return;
    const rx = new RegExp(terminos.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/[aeiounc]/g, (ch) => ACENTOS[ch] || ch)).join('|'), 'gi');
    $$('.res-p .ex-tit, .res-p .ex-txt').forEach((el) => {
      if (el.dataset.marcado) return;
      el.dataset.marcado = '1';
      const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      const nodos = [];
      while (w.nextNode()) nodos.push(w.currentNode);
      nodos.forEach((n) => {
        const s = n.nodeValue;
        rx.lastIndex = 0;
        if (!rx.test(s)) return;
        rx.lastIndex = 0;
        const frag = document.createDocumentFragment();
        let ult = 0;
        s.replace(rx, (m, pos) => {
          frag.appendChild(document.createTextNode(s.slice(ult, pos)));
          const mk = document.createElement('mark');
          mk.textContent = m;
          frag.appendChild(mk);
          ult = pos + m.length;
          return m;
        });
        frag.appendChild(document.createTextNode(s.slice(ult)));
        n.parentNode.replaceChild(frag, n);
      });
    });
  }

  function vNoEncontrado() {
    return '<div class="cab"><h1>Esta página no existe</h1><p class="lead"><a href="#/">Volver a los temas</a></p></div>';
  }

  /* ---------- Llegar a un extracto en su programa ---------- */
  // Subraya en amarillo un trozo del texto. Compara sin espacios, porque la cita y el texto
  // pueden diferir en un espacio antes de una coma. Sin cita, subraya el extracto entero.
  function subrayar(el, cita) {
    const nodos = [];
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    while (w.nextNode()) if (w.currentNode.nodeValue.trim()) nodos.push(w.currentNode);
    let plano = '';
    const mapa = [];
    nodos.forEach((n, k) => { const s = n.nodeValue; for (let j = 0; j < s.length; j++) if (!/\s/.test(s[j])) { plano += s[j]; mapa.push([k, j]); } });
    const buscado = cita ? cita.replace(/\s+/g, '') : plano;
    const i = buscado ? plano.indexOf(buscado) : -1;
    if (i < 0) return false;
    const [n0, o0] = mapa[i];
    const [n1, o1] = mapa[i + buscado.length - 1];
    for (let k = n1; k >= n0; k--) { // de atrás adelante, para que los cortes no muevan lo que falta
      const n = nodos[k];
      const r = document.createRange();
      r.setStart(n, k === n0 ? o0 : 0);
      r.setEnd(n, k === n1 ? o1 + 1 : n.nodeValue.length);
      const m = document.createElement('mark');
      m.className = 'subr';
      r.surroundContents(m);
    }
    return true;
  }
  function marcarLlegada(e, ejeId) {
    const art = document.getElementById(e.i);
    if (!art) return;
    const txt = $('.ex-txt', art);
    const citas = [];
    if (ejeId && marcasDe[ejeId]) Object.values(marcasDe[ejeId]).forEach((q) => (q[e.p] || []).forEach((x) => { if (x.e === e && x.cita) citas.push(x.cita); }));
    const exacta = citas.map((c) => subrayar(txt, c)).some(Boolean);
    if (!exacta) subrayar(txt, '');
    const eje = ejeId && D.ejes.find((x) => x.id === ejeId);
    art.classList.add('ex--aqui');
    art.insertAdjacentHTML('afterbegin', `<p class="aqui">
      <span class="aqui-t">${exacta && eje ? `Subrayada, la cita de «${esc(eje.pregunta)}»` : 'Subrayado, el texto que buscabas'}</span>
      ${history.length > 1 ? `<button type="button" class="btn aqui-v" data-volver>${ICO.izq}Volver</button>` : ''}</p>`);
    const foco = $('mark.subr', art) || art;
    const centrar = () => foco.scrollIntoView({ block: 'center' });
    requestAnimationFrame(centrar);
    // las fuentes llegan tarde y cambian la altura del texto: durante unos segundos, cada vez que la página
    // cambia de alto se vuelve a centrar la cita, hasta que el lector se mueva por su cuenta
    if ('ResizeObserver' in window) {
      const ro = new ResizeObserver(() => { if (document.contains(foco)) centrar(); else parar(); });
      const eventos = ['wheel', 'touchstart', 'keydown', 'mousedown', 'hashchange'];
      function parar() { ro.disconnect(); eventos.forEach((t) => removeEventListener(t, parar)); }
      eventos.forEach((t) => addEventListener(t, parar, { passive: true }));
      ro.observe(main);
      setTimeout(parar, 5000);
    }
  }

  /* ---------- Interacción ---------- */
  function abrirExtracto(art, abierto) {
    art.classList.toggle('abierto', abierto);
    const bt = $('.ex-h', art);
    if (bt) bt.setAttribute('aria-expanded', String(abierto));
  }
  function activarPestana(seccion, pid) {
    $$('.pestanas [data-tab]', seccion).forEach((b) => b.setAttribute('aria-selected', String(b.dataset.tab === pid)));
    $$('.fila > .col', seccion).forEach((c) => c.classList.toggle('on', c.dataset.p === pid));
  }

  main.addEventListener('click', (ev) => {
    const t = ev.target;
    const chip = t.closest('.chip[data-partido]');
    if (chip) {
      const id = chip.dataset.partido;
      if (visibles.includes(id)) {
        if (visibles.length === 1) return;
        visibles = visibles.filter((x) => x !== id);
      } else {
        visibles = partidos.map((p) => p.id).filter((x) => x === id || visibles.includes(x));
      }
      const y = window.scrollY;
      render(false);
      window.scrollTo(0, y);
      const vuelta = $(`.chip[data-partido="${id}"]`);
      if (vuelta) vuelta.focus({ preventScroll: true });
      return;
    }
    const ver = t.closest('[data-citas]');
    if (ver) {
      const abierta = ver.getAttribute('aria-expanded') !== 'true';
      citasAbiertas[ver.dataset.citas] = abierta;
      ver.setAttribute('aria-expanded', String(abierta));
      document.getElementById(`par-${ver.dataset.citas}`).hidden = !abierta;
      return;
    }
    if (t.closest('[data-volver]')) { history.back(); return; }
    const avance = t.closest('.ex:not(.abierto):not(.ex--fijo) .ex-txt');
    if (avance) { abrirExtracto(avance.closest('.ex'), true); return; }
    const exh = t.closest('.ex-h');
    if (exh) { const art = exh.closest('.ex'); abrirExtracto(art, !art.classList.contains('abierto')); return; }
    const vista = t.closest('button[data-vista]');
    if (vista) {
      vistaTexto = vista.dataset.vista;
      guardar('p29n-vista', vistaTexto);
      $$('[data-vista]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.vista === vistaTexto)));
      main.dataset.lectura = vistaTexto;
      $$('.ex:not(.ex--fijo)').forEach((a) => abrirExtracto(a, vistaTexto === 'texto'));
      return;
    }
    const ord = t.closest('[data-orden]');
    if (ord) {
      ordenIndice = ordenIndice === ord.dataset.orden ? null : ord.dataset.orden;
      const id = ord.dataset.orden;
      $('#indice').outerHTML = indiceHTML();
      $(`[data-orden="${id}"]`).focus();
      return;
    }
    const tab = t.closest('[data-tab]');
    if (tab) {
      pestana = tab.dataset.tab;
      const y = tab.getBoundingClientRect().top;
      $$('.sub').forEach((s) => activarPestana(s, pestana));
      window.scrollBy(0, tab.getBoundingClientRect().top - y); // que la pestaña no salte al cambiar las de arriba
      return;
    }
    const salto = t.closest('a[data-salto]');
    if (salto) {
      const dest = document.getElementById(salto.dataset.salto);
      if (dest) {
        ev.preventDefault();
        dest.scrollIntoView({ block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
        history.replaceState(null, '', salto.getAttribute('href'));
      }
      return;
    }
    const masRes = t.closest('[data-mas]');
    if (masRes) {
      const [pid, desde] = masRes.dataset.mas.split(':');
      masRes.parentElement.outerHTML = resultadosPartido(pid, +desde);
      resaltarBusqueda();
      return;
    }
    const fila = t.closest('tr[data-href]');
    if (fila && !t.closest('a, button')) location.hash = fila.dataset.href;
  });
  main.addEventListener('keydown', (ev) => {
    const tab = ev.target.closest('[role="tab"]');
    if (!tab || (ev.key !== 'ArrowRight' && ev.key !== 'ArrowLeft')) return;
    const tabs = $$('[role="tab"]', tab.parentElement);
    const k = (tabs.indexOf(tab) + (ev.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
    tabs[k].focus();
    tabs[k].click();
  });
  main.addEventListener('submit', (ev) => {
    const f = ev.target.closest('form[data-buscar]');
    if (!f) return;
    ev.preventDefault();
    const q = $('input', f).value.trim();
    if (q) location.hash = `#/buscar/${encodeURIComponent(q)}`;
  });
  document.addEventListener('keydown', (ev) => {
    if (ev.key !== '/' || /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) return;
    ev.preventDefault();
    const campo = $('#qv') || $('#q');
    if (campo.offsetParent) campo.focus(); else location.hash = '#/buscar';
  });

  // resalta en el lateral la sección que se está leyendo
  let espia = null;
  function espiar() {
    if (espia) espia.disconnect();
    const enlaces = $$('.lado a[data-salto]');
    if (!enlaces.length || !('IntersectionObserver' in window)) return;
    const porDest = new Map(enlaces.map((a) => [a.dataset.salto, a]));
    const secciones = [...porDest.keys()].map((id) => document.getElementById(id)).filter(Boolean);
    espia = new IntersectionObserver(() => {
      // la sección activa es la última cuyo comienzo ya ha pasado la línea de lectura
      const linea = innerHeight * 0.45;
      let mejor = secciones[0] && secciones[0].id;
      secciones.forEach((el) => { if (el.getBoundingClientRect().top <= linea) mejor = el.id; });
      if (!mejor) return;
      enlaces.forEach((a) => a.removeAttribute('aria-current'));
      const a = porDest.get(mejor);
      a.setAttribute('aria-current', 'true');
    }, { rootMargin: '-80px 0px -55% 0px' });
    porDest.forEach((_, id) => { const el = document.getElementById(id); if (el) espia.observe(el); });
  }

  /* ---------- Pie ---------- */
  // Los mensajes se envían con EmailJS: la plantilla decide a quién llegan; la clave es pública.
  const EMAILJS = { servicio: 'service_vg6oefs', plantilla: '', clave: 'djSnpxKmk53yDPEEq' };
  const fecha = (iso) => new Date(`${iso}T12:00:00`).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' });
  const pintarPie = () => { document.getElementById('pie').innerHTML = `<div class="pie-in">
    <details class="pie-fuentes">
      <summary>${ICO.chev}Fuentes: los ${todos.length} programas oficiales</summary>
      <ul>${todos.map((p) => `<li><a href="${esc(p.fuente)}" target="_blank" rel="noopener">${esc(p.corto)}: ${esc(p.titulo)}</a> · ${p.paginas} págs.</li>`).join('')}</ul>
      <p>Datos del ${esc(fecha(D.generado))}.</p>
    </details>
    ${EMAILJS.plantilla ? `<form class="opina" novalidate>
      <h2>¿Has visto un error o quieres comentar algo?</h2>
      <div class="opina-campos">
        <label class="campo"><span class="campo-t">Asunto</span><input name="asunto" required maxlength="120" autocomplete="off"></label>
        <label class="campo"><span class="campo-t">Tu correo <span class="opc">(opcional, para poder responderte)</span></span><input name="correo" type="email" maxlength="200" autocomplete="email"></label>
        <label class="campo opina-msg"><span class="campo-t">Mensaje</span><textarea name="mensaje" required rows="4" maxlength="5000"></textarea></label>
        <input name="botcheck" type="checkbox" hidden tabindex="-1" autocomplete="off">
      </div>
      <div class="opina-pie"><button type="submit" class="btn btn--fuerte btn--peq">Enviar</button><p class="opina-estado" role="status" aria-live="polite"></p></div>
    </form>` : ''}
  </div>`; };
  pintarPie();
  document.getElementById('pie').addEventListener('submit', async (ev) => {
    const form = ev.target.closest('.opina');
    if (!form) return;
    ev.preventDefault();
    const estado = $('.opina-estado', form);
    const boton = $('button', form);
    const v = (n) => form.elements[n].value.trim();
    if (!v('asunto') || !v('mensaje')) { estado.textContent = 'Escribe un asunto y un mensaje.'; return; }
    if (v('correo') && !form.elements.correo.checkValidity()) { estado.textContent = 'Revisa el correo: no parece válido.'; return; }
    boton.disabled = true;
    estado.textContent = 'Enviando…';
    try {
      if (form.elements.botcheck.checked) throw new Error();
      const r = await fetch('https://api.emailjs.com/api/v1.0/email/send', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_id: EMAILJS.servicio, template_id: EMAILJS.plantilla, user_id: EMAILJS.clave,
          template_params: { asunto: v('asunto'), correo: v('correo') || '(sin correo)', mensaje: v('mensaje'), pagina: location.href },
        }),
      });
      if (!r.ok) throw new Error();
      form.reset();
      estado.textContent = 'Enviado. Gracias.';
    } catch (_) {
      estado.textContent = 'No se ha podido enviar. Inténtalo de nuevo en un rato.';
    } finally {
      boton.disabled = false;
    }
  });

  /* ---------- Elegir partidos ---------- */
  // Una fila por programa: las candidaturas que comparten programa vienen fundidas desde build_web.py.
  const CAND = D.candidaturas || [];
  const filtroC = { q: '', prov: '' };
  const SIN_PROG = { pdf: 'Aún no está disponible.', 'no-publicado': 'Aún no está disponible.' };
  const listaY = (l) => (l.length > 1 ? `${l.slice(0, -1).join(', ')} y ${l[l.length - 1]}` : l[0] || '');
  const lugares = (c) => [...new Set([...c.c, ...c.se])];
  const N_CIRC = (D.mapa && D.mapa.zonas.length) || 52;
  function coincide(c, prov = filtroC.prov) {
    if (prov && !lugares(c).includes(prov)) return false;
    const ts = norm(filtroC.q).split(/\s+/).filter(Boolean);
    if (ts.length) {
      const t = norm(`${c.n} ${c.s} ${c.prog ? `${P[c.prog].corto} ${P[c.prog].nombre}` : ''}`);
      if (!ts.every((w) => t.includes(w))) return false;
    }
    return true;
  }
  function dondeTexto(c) {
    const l = lugares(c);
    if (l.length >= N_CIRC) return 'Toda España';
    if (filtroC.prov && l.length > 1) return `${esc(filtroC.prov)} <span class="cand-mas">y ${plural(l.length - 1, 'circunscripción más', 'circunscripciones más')}</span>`;
    return l.length > 4 ? plural(l.length, 'circunscripción', 'circunscripciones') : esc(listaY(l));
  }
  const elegido = (id) => partidos.some((p) => p.id === id);
  function candHTML(c) {
    const pr = c.prog && P[c.prog];
    const accion = pr
      ? `<button type="button" class="btn btn--peq cand-b" data-alternar="${pr.id}" aria-pressed="${elegido(pr.id)}"${elegido(pr.id) && partidos.length === 1 ? ' disabled' : ''}><span class="si-no">${ICO.mas}Añadir</span><span class="si-si">${ICO.ok}Añadido</span><span class="sr"> ${esc(c.n)}</span></button>`
      : '';
    return `<li class="cand${pr ? '' : ' cand--sin'}">
      <p class="cand-n">${pr ? punto(pr) : '<span class="pc pc--vacio" aria-hidden="true"></span>'}<span>${esc(c.n)}</span><span class="cand-s">${esc(c.s)}</span></p>
      <p class="cand-d">${dondeTexto(c)}</p>
      ${pr ? '' : `<p class="cand-e">${SIN_PROG[c.e] || 'No se ha encontrado su programa.'}</p>`}
      ${accion}
    </li>`;
  }
  const alfa = (a, b) => a.n.localeCompare(b.n, 'es', { sensitivity: 'base' });
  function elegirResultados() {
    // primero los que ya comparas, luego los que se pueden añadir y al final los que no tienen programa en la web
    const grupo = (c) => (!c.prog ? 2 : elegido(c.prog) ? 0 : 1);
    const l = CAND.filter((c) => coincide(c)).sort((a, b) => grupo(a) - grupo(b) || alfa(a, b));
    const progs = [...new Set(l.map((c) => c.prog).filter(Boolean))];
    const faltan = progs.filter((id) => !elegido(id));
    const deCirc = filtroC.prov ? [...new Set(CAND.filter((c) => c.prog && lugares(c).includes(filtroC.prov)).map((c) => c.prog))] : [];
    const soloCirc = deCirc.length && (deCirc.length !== partidos.length || deCirc.some((id) => !elegido(id)));
    return `<div class="dlg-acc">
        <p class="dlg-n" role="status">${plural(l.length, 'partido', 'partidos')}${filtroC.prov ? ` en ${esc(filtroC.prov)}` : ''}</p>
        <div class="dlg-bs">
          ${faltan.length ? `<button type="button" class="btn btn--peq btn--fuerte" data-anadir-todos="${faltan.join(' ')}">${ICO.mas}${faltan.length === 1 ? `Añadir ${esc(P[faltan[0]].corto)}` : `Añadir los ${faltan.length} que faltan`}</button>` : (progs.length ? '<span class="dlg-ok" tabindex="-1">Ya comparas todos</span>' : '')}
          ${soloCirc ? `<button type="button" class="btn btn--peq" data-solo-estos="${deCirc.join(' ')}">Comparar toda la circunscripción</button>` : ''}
        </div>
      </div>
      ${l.length ? `<ul class="cands">${l.map(candHTML).join('')}</ul>` : '<p class="vacio dlg-vacio">Ningún partido coincide.</p>'}`;
  }
  function elegidosHTML() {
    const uno = partidos.length === 1;
    return `<p class="dlg-st">Comparas <span class="c">${partidos.length}</span></p>
      <ul class="dlg-chips">${partidos.map((p) => `<li><button type="button" class="chip chip--quitar" data-p="${p.id}" data-alternar="${p.id}"${uno ? ' disabled' : ''}>${punto(p)}${esc(p.corto)}${uno ? '' : `<span class="sr">: quitar de la comparación</span>${ICO.x}`}</button></li>`).join('')}</ul>
      ${partidos.map((p) => p.id).join() !== BASE.join() ? '<button type="button" class="enlace dlg-base" data-base>Restablecer</button>' : ''}`;
  }
  // Mapa de circunscripciones: cada una es un botón; Ceuta y Melilla llevan además un círculo para poder pulsarlas.
  const MAPA = D.mapa;
  const PEQUENAS = ['Ceuta', 'Melilla'];
  function mapaHTML() {
    if (!MAPA) return '';
    const zonas = MAPA.zonas.slice().sort((a, b) => PEQUENAS.includes(a.n) - PEQUENAS.includes(b.n));
    return `<svg class="mapa-svg" viewBox="${MAPA.caja.join(' ')}" role="group" aria-label="Mapa de circunscripciones">
      <path class="mapa-marco" d="${MAPA.marco}" aria-hidden="true"/>
      ${zonas.map((z) => `<g class="mapa-z" data-prov="${esc(z.n)}" role="button" tabindex="0" aria-pressed="false">
        <title>${esc(z.n)}</title><path d="${z.d}"/>${PEQUENAS.includes(z.n) ? `<circle cx="${z.x}" cy="${z.y}" r="7"/>` : ''}</g>`).join('')}
      ${MAPA.lineas ? `<path class="mapa-lineas" d="${MAPA.lineas}" aria-hidden="true"/>` : ''}
    </svg>`;
  }
  function pintarMapa() {
    if (!dlg) return;
    dlg.querySelectorAll('.mapa-z').forEach((g) => {
      const n = g.dataset.prov;
      const k = CAND.filter((c) => coincide(c, n)).length;
      g.setAttribute('aria-pressed', String(filtroC.prov === n));
      g.setAttribute('aria-label', `${n}: ${plural(k, 'partido', 'partidos')}`);
      g.classList.toggle('mapa-z--vacia', !k);
      $('title', g).textContent = `${n} · ${plural(k, 'partido', 'partidos')}`;
    });
    $('#mapa-t', dlg).innerHTML = filtroC.prov
      ? `<span>${esc(filtroC.prov)}</span><button type="button" class="enlace" data-espana>Ver toda España</button>`
      : '<span>Toda España</span>';
    const n = CAND.filter((c) => coincide(c)).length;
    $('.mapa-ir', dlg).textContent = `Ver ${n === 1 ? 'el partido' : `los ${n} partidos`}`;
  }
  let dlg = null;
  function abrirElegir() {
    if (!dlg) {
      dlg = document.createElement('dialog');
      dlg.className = 'dlg';
      dlg.setAttribute('aria-labelledby', 'dlg-t');
      dlg.innerHTML = `<div class="dlg-in">
        <header class="dlg-h">
          <h2 id="dlg-t">Añadir partidos</h2>
          <button type="button" class="dlg-x" data-cerrar aria-label="Cerrar">${ICO.x}</button>
        </header>
        <div class="dlg-cuerpo">
          <section class="dlg-izq" aria-label="Partidos">
            <form class="dlg-f" role="search">
              <label class="campo campo--q"><span class="sr">Buscar por nombre o sigla</span><input type="search" id="dlg-q" autocomplete="off" spellcheck="false" placeholder="Buscar por nombre o sigla"></label>
            </form>
            <div class="dlg-res" id="dlg-res"></div>
          </section>
          <aside class="dlg-der" aria-label="Filtrar por circunscripción">
            <div class="mapa">
              <p class="mapa-t" id="mapa-t" tabindex="-1"></p>
              ${mapaHTML()}
              <p class="mapa-h" id="mapa-h" aria-hidden="true"></p>
              <button type="button" class="btn btn--peq mapa-ir" data-ir-lista></button>
            </div>
            <div class="dlg-sel" id="dlg-sel"></div>
          </aside>
        </div>
        <footer class="dlg-pie"><button type="button" class="btn btn--fuerte" data-cerrar>Hecho</button></footer>
      </div>`;
      document.body.appendChild(dlg);
      const pintar = () => { $('#dlg-res', dlg).innerHTML = elegirResultados(); pintarMapa(); };
      const ponerProv = (n) => {
        filtroC.prov = n;
        pintar();
        $('.dlg-izq', dlg).scrollTop = 0;
      };
      $('.dlg-f', dlg).addEventListener('submit', (ev) => ev.preventDefault());
      $('#dlg-q', dlg).addEventListener('input', (ev) => { filtroC.q = ev.target.value; pintar(); });
      const sobreMapa = (ev) => {
        const z = ev.target.closest && ev.target.closest('.mapa-z');
        $('#mapa-h', dlg).textContent = z ? $('title', z).textContent : '';
      };
      ['pointerover', 'focusin'].forEach((e) => dlg.addEventListener(e, sobreMapa));
      $('.mapa-svg', dlg)?.addEventListener('pointerleave', () => { $('#mapa-h', dlg).textContent = ''; });
      dlg.addEventListener('keydown', (ev) => {
        const z = ev.target.closest && ev.target.closest('.mapa-z');
        if (z && (ev.key === 'Enter' || ev.key === ' ')) { ev.preventDefault(); z.dispatchEvent(new MouseEvent('click', { bubbles: true })); }
      });
      dlg.addEventListener('click', (ev) => {
        const t = ev.target;
        if (t === dlg || t.closest('[data-cerrar]')) { dlg.close(); return; }
        const z = t.closest('.mapa-z');
        if (z) { ponerProv(filtroC.prov === z.dataset.prov ? '' : z.dataset.prov); return; }
        if (t.closest('[data-ir-lista]')) { $('.dlg-izq', dlg).scrollIntoView({ block: 'start', behavior: 'smooth' }); return; }
        if (t.closest('[data-espana]')) { ponerProv(''); $('#mapa-t', dlg).focus(); return; }
        const alt = t.closest('[data-alternar]');
        if (alt && !alt.disabled) {
          const id = alt.dataset.alternar;
          const enChips = !!alt.closest('.dlg-chips');
          cambiarPartidos(elegido(id) ? partidos.map((p) => p.id).filter((x) => x !== id) : [...partidos.map((p) => p.id), id],
            enChips ? '.dlg-chips button, #dlg-q' : `.cands [data-alternar="${id}"]`);
          return;
        }
        const varios = t.closest('[data-anadir-todos]');
        if (varios) { cambiarPartidos([...partidos.map((p) => p.id), ...varios.dataset.anadirTodos.split(' ')], '[data-solo-estos], .dlg-ok, #dlg-q'); return; }
        const solo = t.closest('[data-solo-estos]');
        if (solo) { cambiarPartidos(solo.dataset.soloEstos.split(' '), '.dlg-ok, #dlg-q'); return; }
        if (t.closest('[data-base]')) cambiarPartidos(BASE, '#dlg-q');
      });
      dlg.addEventListener('close', () => { const b = $('.top-partidos'); if (b) b.focus({ preventScroll: true }); });
      dlg.pintar = () => { $('#dlg-sel', dlg).innerHTML = elegidosHTML(); pintar(); };
    }
    dlg.pintar();
    if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
    $('.dlg-cuerpo', dlg).scrollTop = 0;
    $('#dlg-q', dlg).focus({ preventScroll: true });
  }
  function cambiarPartidos(ids, foco) {
    fijarPartidos(ids);
    guardar('p29n-partidos', partidos.map((p) => p.id));
    visibles = partidos.map((p) => p.id);
    if (pestana && !elegido(pestana)) pestana = null;
    if (ordenIndice && !elegido(ordenIndice)) ordenIndice = null;
    contarPartidos();
    const y = window.scrollY;
    render(false);
    window.scrollTo(0, y);
    if (dlg && dlg.open) {
      dlg.pintar();
      const f = foco && foco.split(', ').map((x) => $(x, dlg)).find(Boolean);
      (f || $('#dlg-q', dlg)).focus({ preventScroll: true });
    }
  }
  function contarPartidos() {
    const n = $('.top-partidos .c');
    if (n) n.textContent = partidos.length;
    const b = $('.top-partidos');
    if (b) b.setAttribute('aria-label', `Añadir partidos (comparas ${plural(partidos.length, 'partido', 'partidos')})`);
  }
  document.addEventListener('click', (ev) => {
    if (ev.target.closest('[data-elegir]')) { ev.preventDefault(); abrirElegir(); }
  });
  contarPartidos();

  /* ---------- Rutas ---------- */
  function ruta() {
    const h = decodeURIComponent(location.hash.replace(/^#/, ''));
    const [camino, ancla] = h.split('#');
    return { partes: camino.split('/').filter(Boolean), ancla };
  }
  let ultimaVista = '';
  function render(irArriba = true) {
    const { partes, ancla } = ruta();
    const [v, a, b] = partes;
    let html;
    let nav = 'temas';
    let titulo = 'Programas 29N';
    let objetivo = ancla;
    // «Ver en su programa»: el programa entero, con el extracto subrayado en su sitio
    const llegada = v === 'e' && porId[a];
    if (llegada) { html = vPrograma(llegada.p); nav = 'programas'; titulo = `Programa de ${P[llegada.p].corto} · Programas 29N`; }
    else if (!v) html = vInicio();
    else if (v === 'tema') { html = vBloque(a); objetivo = ancla || b; const bl = D.bloques.find((x) => x.id === a); if (bl) titulo = `${bl.nombre} · Programas 29N`; }
    else if (v === 'choques') { html = vChoques(); nav = 'choques'; titulo = 'Dónde chocan · Programas 29N'; }
    else if (v === 'programas') { html = vProgramas(); nav = 'programas'; titulo = 'Programas completos · Programas 29N'; }
    else if (v === 'programa') { html = vPrograma(a); nav = 'programas'; if (P[a]) titulo = `Programa de ${P[a].corto} · Programas 29N`; }
    else if (v === 'buscar') { html = vBuscar(a || ''); nav = 'buscar'; titulo = a ? `«${a}» · Buscar · Programas 29N` : 'Buscar · Programas 29N'; }
    else html = vNoEncontrado();
    main.innerHTML = html;
    main.dataset.lectura = vistaTexto;
    document.body.dataset.ruta = v || 'inicio';
    document.title = titulo;
    $$('.nav a').forEach((x) => (x.dataset.nav === nav ? x.setAttribute('aria-current', 'page') : x.removeAttribute('aria-current')));
    if (v === 'buscar') resaltarBusqueda();
    espiar();
    const vista = partes.join('/');
    if (llegada) {
      marcarLlegada(llegada, b);
      main.focus({ preventScroll: true });
      ultimaVista = vista;
      return;
    }
    if (!irArriba) return;
    const t = objetivo && document.getElementById(objetivo);
    if (t) {
      if (t.classList.contains('ex')) {
        const sec = t.closest('.sub');
        const col = t.closest('.col');
        if (sec && col) activarPestana(sec, col.dataset.p);
        abrirExtracto(t, true);
        t.classList.add('destello');
      } else if (t.classList.contains('col')) {
        activarPestana(t.closest('.sub'), t.dataset.p);
      }
      t.scrollIntoView({ block: 'start' });
    } else if (vista !== ultimaVista) {
      window.scrollTo(0, 0);
      // al abrir «Buscar» sin palabras, el cursor va directo a la caja
      if (v === 'buscar' && !a) $('#qv').focus({ preventScroll: true });
      else main.focus({ preventScroll: true });
    }
    ultimaVista = vista;
  }
  window.addEventListener('hashchange', () => render(true));
  $('.busca').addEventListener('submit', (ev) => {
    ev.preventDefault();
    const q = $('#q').value.trim();
    if (q) location.hash = `#/buscar/${encodeURIComponent(q)}`;
  });
  render(true);
})();

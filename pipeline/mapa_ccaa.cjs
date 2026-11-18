// Necesita (npm, en una carpeta aparte): es-atlas@0.6.0 d3-geo@3.1.1 d3-composite-projections@1.4.0 topojson-client@3.1.0
// Cópialo a esa carpeta y ejecútalo allí: node mapa_ccaa.cjs <proyecto>/data/mapa-ccaa.json
// Genera el mapa de circunscripciones (las 50 provincias, Ceuta y Melilla) para el panel «Añadir partidos»:
// trazados SVG ya proyectados (cónica conforme de España, con Canarias recolocada) y, aparte, las líneas
// entre comunidades autónomas para orientarse. Los nombres son los del BOE (los mismos que TERRITORIOS en build_web.py).
const fs = require('fs');
const topo = require('topojson-client');
const d3 = require('d3-geo');
const comp = require('d3-composite-projections');
const t = require('./node_modules/es-atlas/es/provinces.json');

const TERRITORIOS = {
  'Andalucía': ['Almería', 'Cádiz', 'Córdoba', 'Granada', 'Huelva', 'Jaén', 'Málaga', 'Sevilla'],
  'Aragón': ['Huesca', 'Teruel', 'Zaragoza'], 'Asturias': ['Asturias'], 'Canarias': ['Las Palmas', 'Santa Cruz de Tenerife'],
  'Cantabria': ['Cantabria'], 'Castilla-La Mancha': ['Albacete', 'Ciudad Real', 'Cuenca', 'Guadalajara', 'Toledo'],
  'Castilla y León': ['Ávila', 'Burgos', 'León', 'Palencia', 'Salamanca', 'Segovia', 'Soria', 'Valladolid', 'Zamora'],
  'Cataluña': ['Barcelona', 'Girona', 'Lleida', 'Tarragona'], 'Ceuta': ['Ceuta'],
  'Comunitat Valenciana': ['Alicante', 'Castellón', 'Valencia'], 'Extremadura': ['Badajoz', 'Cáceres'],
  'Galicia': ['A Coruña', 'Lugo', 'Ourense', 'Pontevedra'], 'Illes Balears': ['Illes Balears'], 'La Rioja': ['La Rioja'],
  'Madrid': ['Madrid'], 'Melilla': ['Melilla'], 'Murcia': ['Murcia'], 'Navarra': ['Navarra'], 'País Vasco': ['Álava', 'Bizkaia', 'Gipuzkoa'],
};
const ccaaDe = {};
Object.entries(TERRITORIOS).forEach(([c, ps]) => ps.forEach((p) => { ccaaDe[p] = c; }));
const nombre = (g) => g.properties.name.split('/').pop();

const geoms = t.objects.provinces.geometries.filter((g) => ccaaDe[nombre(g)]);
const obj = { type: 'GeometryCollection', geometries: geoms };
const fc = topo.feature(t, obj);
const W = 600, H = 480;
const proj = comp.geoConicConformalSpain().fitExtent([[4, 4], [W - 4, H - 4]], fc);
const r1 = (s) => s.replace(/(\d+\.\d)\d+/g, '$1').replace(/\.0(?=\D)/g, '');
const ruta = d3.geoPath(proj);
const zonas = fc.features.map((f) => {
  const c = ruta.centroid(f);
  return { n: nombre(f), d: r1(ruta(f)), x: Math.round(c[0] * 10) / 10, y: Math.round(c[1] * 10) / 10 };
});
if (zonas.length !== 52) throw new Error(`esperaba 52 circunscripciones y salen ${zonas.length}`);
const lineas = r1(ruta(topo.mesh(t, obj, (a, b) => a !== b && ccaaDe[nombre(a)] !== ccaaDe[nombre(b)])));
const marco = r1(proj.getCompositionBorders());
// caja real del dibujo, para que el SVG no deje márgenes vacíos
const nums = (s) => [...s.matchAll(/-?\d+(?:\.\d+)?/g)].map(Number);
const xs = [], ys = [];
[marco, ...zonas.map((z) => z.d)].forEach((d) => nums(d).forEach((v, i) => (i % 2 ? ys : xs).push(v)));
const caja = [Math.floor(Math.min(...xs)) - 2, Math.floor(Math.min(...ys)) - 2];
caja.push(Math.ceil(Math.max(...xs)) + 2 - caja[0], Math.ceil(Math.max(...ys)) + 2 - caja[1]);
fs.writeFileSync(process.argv[2], JSON.stringify({ caja, zonas, lineas, marco }));
console.log(zonas.length, 'circunscripciones', fs.statSync(process.argv[2]).size, 'bytes', 'caja', caja);

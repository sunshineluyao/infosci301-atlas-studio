import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {buildGraph,centralities,neighborsWithin,filterPlaces,validateConfig,validateLocalPlaces,safeUrl} from '../src/engine.js';
const papers=JSON.parse(fs.readFileSync(new URL('../public/data/emerging-tech.json',import.meta.url)));
const heritage=JSON.parse(fs.readFileSync(new URL('../public/data/heritage.json',import.meta.url)));
const earth=JSON.parse(fs.readFileSync(new URL('../public/data/earth-events.json',import.meta.url)));
test('Graph IDs are unique; each link has endpoints and one paper/topic pair',()=>{
 const g=buildGraph(papers);assert.equal(g.paperCount,30);const ids=new Set(g.nodes.map(n=>n.id));assert.equal(ids.size,g.nodes.length);
 for(const e of g.links){assert.ok(ids.has(e.source)&&ids.has(e.target));assert.equal(g.nodes.find(n=>n.id===e.source).type,'paper');assert.equal(g.nodes.find(n=>n.id===e.target).type,'topic');}
 assert.equal(g.nodes.reduce((s,n)=>s+n.degree,0),g.links.length*2);
});
test('PageRank is nonnegative and normalized, including a dangling node',()=>{
 const r=centralities([{id:'a'},{id:'b'},{id:'c'}],[{source:'a',target:'b'}]).pagerank;
 assert.ok(Object.values(r).every(v=>v>=0));assert.ok(Math.abs(Object.values(r).reduce((a,b)=>a+b,0)-1)<1e-10);assert.equal(r.a,r.b);assert.ok(r.c<r.a);
});
test('Breadth-first depth changes only the intended frontier',()=>{
 const g={links:[{source:'a',target:'b'},{source:'b',target:'c'},{source:'c',target:'d'}]};assert.deepEqual([...neighborsWithin(g,'a',1)],['a','b']);assert.deepEqual([...neighborsWithin(g,'a',2)],['a','b','c']);
});
test('Graph search and publication-year filters work; empty graphs remain valid',()=>{
 assert.equal(buildGraph(papers,5).paperCount,5);assert.ok(buildGraph(papers,60,2024).nodes.filter(n=>n.type==='paper').every(p=>p.year>=2024));assert.equal(buildGraph(papers,60,2019,'zzznomatchzz').nodes.length,0);
});
test('Real heritage and Earth snapshots have valid unique IDs, coordinates and dates',()=>{
 assert.equal(heritage.length,1457);assert.equal(earth.length,272);
 for(const rows of [heritage,earth]){assert.equal(new Set(rows.map(r=>r.id)).size,rows.length);for(const r of rows){assert.ok(r.lon>=-180&&r.lon<=180&&r.lat>=-90&&r.lat<=90);assert.ok(!Number.isNaN(Date.parse(r.date)));assert.equal(r.year,Number(r.date.slice(0,4)));}}
});
test('Spatial filter counts reconcile and year endpoints are inclusive',()=>{
 assert.equal(filterPlaces(heritage).length,heritage.length);const rows=filterPlaces(heritage,{from:1965,to:1965,group:'Brooklyn'});assert.ok(rows.length>0);assert.ok(rows.every(r=>r.year===1965&&r.group==='Brooklyn'));assert.equal(filterPlaces(heritage,{search:'zznomatch'}).length,0);
});
test('Public configuration rejects invalid values and drops unknown fields',()=>{
 assert.throws(()=>validateConfig({githubRepo:'https://github.com/foo/bar'}));assert.throws(()=>validateConfig({enable3D:'false'}));assert.throws(()=>validateConfig({maxVisiblePapers:200}));assert.throws(()=>validateConfig({spaceUrl:'javascript:alert(1)'}));
 assert.deepEqual(validateConfig({githubRepo:'teacher/course',secret:'no'}),{githubRepo:'teacher/course'});
});
test('Local import validates coordinates, unique IDs, dates and excludes unsafe links',()=>{
 assert.throws(()=>validateLocalPlaces([{id:'x',lon:999,lat:40,date:'2026-01-01'}]));assert.throws(()=>validateLocalPlaces([{id:'x',lon:0,lat:0,date:'wrong'}]));
 const rows=validateLocalPlaces([{id:'x',lon:-74,lat:40,date:'2026-01-01',url:'javascript:evil()'}]);assert.equal(rows[0].url,'');assert.equal(rows[0].year,2026);
 assert.throws(()=>validateLocalPlaces([rows[0],rows[0]]));assert.equal(safeUrl('https://example.org/data'),'https://example.org/data');
});
test('Source files and resource destinations are bundled',()=>{
 for(const file of ['config.json','data/world.json','notebooks/legacy-idiom-atlas.html','notebooks/INFOSCI301_Week4_Network_Studio_Colab.ipynb','notebooks/INFOSCI301_Week4_Spatiotemporal_Studio_Colab.ipynb'])assert.ok(fs.statSync(new URL('../public/'+file,import.meta.url)).size>0);
});

// Static SVG exports from the same React/D3 components; not browser screenshots.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {build} from 'esbuild';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {buildGraph} from '../src/engine.js';
fs.mkdirSync('.test-cache',{recursive:true});fs.mkdirSync('public/reference-figures',{recursive:true});
const out=await build({entryPoints:['src/Visuals.jsx'],bundle:true,format:'esm',platform:'node',packages:'external',write:false});
fs.writeFileSync('.test-cache/visuals.mjs',out.outputFiles[0].text);
const {NetworkView,SpatialView}=await import(pathToFileURL(path.resolve('.test-cache/visuals.mjs')));
const read=n=>JSON.parse(fs.readFileSync('public/data/'+n+'.json'));
const save=(name,element)=>{
 const html=renderToStaticMarkup(element),match=html.match(/<svg[\s\S]*?<\/svg>/);
 let svg=match[0].replace('<svg ','<svg xmlns="http://www.w3.org/2000/svg" width="900" height="480" ')
 .replaceAll('var(--panel)','#ffffff').replaceAll('var(--ink)','#172936').replaceAll('var(--line)','#dbe3df').replaceAll('var(--land)','#d9e3df');
 svg=svg.replace(/(<svg[^>]+>)/,'$1<style>.svg-label{fill:#526571;font-family:DejaVu Sans,sans-serif}</style><rect width="900" height="480" fill="#ffffff"/>');
 const caption=name==='network-paper-topic'?'Cyan circles: papers | Amber squares: topics | Size: degree | Edge: provider classification':'NYC individual-landmark designations | Color: borough | WGS84 longitude/latitude';
 const source=name==='network-paper-topic'?'OpenAlex: first 30 papers of a 60-result sample, 2026-09-14. Position is not scientific authority.':'1,457 unique designation IDs after filtering/deduplication. Designation date is not construction date.';
 svg=svg.replaceAll('height="480"','height="540"').replace('viewBox="0 0 900 480"','viewBox="0 0 900 540"').replace('</svg>',`<text x="20" y="501" fill="#203540" font-family="DejaVu Sans,sans-serif" font-size="12">${caption}</text><text x="20" y="523" fill="#526571" font-family="DejaVu Sans,sans-serif" font-size="11">${source}</text></svg>`);
 fs.writeFileSync('public/reference-figures/'+name+'.svg',svg);
};
save('network-paper-topic',React.createElement(NetworkView,{graph:buildGraph(read('emerging-tech')),layout:'force',metric:'degree',selected:null,onSelect:()=>{},depth:1,labels:true}));
const heritage=read('heritage');save('heritage-place-time',React.createElement(SpatialView,{allData:heritage,rows:heritage,world:read('world'),dataset:'heritage',projection:'mercator',encoding:'points',selected:null,onSelect:()=>{}}));
console.log('Exported reproducible reference SVGs (not UI screenshots).');

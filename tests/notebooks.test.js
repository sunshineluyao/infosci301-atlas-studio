import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {JSDOM} from 'jsdom';
const manifest=JSON.parse(fs.readFileSync('public/notebooks/manifest.json','utf8'));
const canonical=fs.existsSync('notebooks')?'notebooks':'public/notebooks';
for(const lesson of manifest.lessons){
 test(`Saved result matches canonical source: ${lesson.notebook}`,()=>{
  const raw=fs.readFileSync(path.join(canonical,lesson.notebook));
  assert.equal(createHash('sha256').update(raw).digest('hex'),lesson.sha256);
  const nb=JSON.parse(raw),code=nb.cells.filter(c=>c.cell_type==='code');
  assert.equal(code.length,lesson.code_cells);assert.equal(nb.metadata.infosci301_execution.status,'completed');
  assert.ok(code.every(c=>c.execution_count===null && (c.outputs??[]).length===0));
  const html=fs.readFileSync(path.join('public/notebooks',lesson.preview),'utf8'),doc=new JSDOM(html).window.document;
  assert.ok(html.includes(lesson.sha256));
  assert.equal(createHash('sha256').update(html).digest('hex'),lesson.preview_sha256);
  for(const c of code){
   const section=doc.getElementById(c.id);assert.ok(section,`Missing source cell ${c.id}`);
   assert.equal(section.querySelector('details pre code').textContent,c.source.join(''));
   if(c.source.join('').startsWith('# Optional package extension:'))assert.match(c.metadata.infosci_execution,/not run/);
  }
  assert.equal(doc.querySelectorAll('figure[aria-label="Computed notebook figure"]').length+doc.querySelectorAll('script[data-plot]').length,lesson.figures);
  for(const a of doc.querySelectorAll('a[href]')){
   const href=a.getAttribute('href');if(/^(https?:|mailto:|#|data:)/.test(href))continue;
   assert.ok(fs.existsSync(path.join('public/notebooks',href.split('#')[0]))||(href===lesson.notebook && fs.existsSync(path.join(canonical,href))),`Broken saved-result link: ${href}`);
  }
  assert.ok(fs.statSync(path.join('public/notebooks',lesson.bundle)).size>1000);
 });
}

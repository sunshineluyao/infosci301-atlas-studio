import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {JSDOM} from 'jsdom';
import {tmpdir} from 'node:os';
import {execFileSync} from 'node:child_process';
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

test('render-only refuses missing execution without replacing good previews',()=>{
 const root=fs.mkdtempSync(path.join(tmpdir(),'infosci-publisher-'));
 try{
  for(const dir of ['scripts','notebooks','public/notebooks'])fs.mkdirSync(path.join(root,dir),{recursive:true});
  fs.copyFileSync('scripts/publish_notebooks.py',path.join(root,'scripts/publish_notebooks.py'));
  fs.writeFileSync(path.join(root,'notebooks/Lesson.ipynb'),JSON.stringify({cells:[]}));
  const preview=path.join(root,'public/notebooks/Lesson_Executed.html');fs.writeFileSync(preview,'verified saved output');
  assert.throws(()=>execFileSync('python3',[path.join(root,'scripts/publish_notebooks.py'),'--render-only'],{cwd:root,encoding:'utf8',stdio:'pipe'}),error=>error.status!==0 && /Saved execution missing/.test(String(error.stderr)));
  assert.equal(fs.readFileSync(preview,'utf8'),'verified saved output');
 }finally{fs.rmSync(root,{recursive:true,force:true});}
});

test('missing Graphviz renderer exports a fallback rather than completed status',()=>{
 const script=`import json,sys,types,tempfile
from pathlib import Path
n=json.load(open('public/notebooks/INFOSCI301_Week4_Network_Studio_Colab.ipynb'));source=''.join(next(c for c in n['cells'] if c['id']=='network-original-15')['source'])
class FakeDigraph:
 source='digraph { task -> claim }'
 def __init__(self,*a,**k):pass
 def attr(self,*a,**k):pass
 def node(self,*a,**k):pass
 def edges(self,*a,**k):pass
 def render(self,*a,**k):raise FileNotFoundError('renderer unavailable')
sys.modules['graphviz']=types.SimpleNamespace(Digraph=FakeDigraph)
with tempfile.TemporaryDirectory() as folder:
 ns={'RUN_PACKAGE_EXTENSIONS':True,'_extension_status':{},'OUTPUT':Path(folder),'TEAL':'#14877D','PURPLE':'#6A5983','GOLD':'#D97706','CORAL':'#C2413A','NAVY':'#18343E','HTML':lambda x:x,'display':lambda *x:None}
 exec(source,ns)
 assert 'fallback' in ns['_extension_status']['Directed process diagram']
 assert (Path(folder)/'network_reasoning_graphviz.gv').exists()
 print('fallback recorded')`
 assert.match(execFileSync('python3',['-c',script],{encoding:'utf8'}),/fallback recorded/);
});

test('implicit metric tables and legacy Markdown retain rich output',()=>{
 const doc=new JSDOM(fs.readFileSync('public/notebooks/INFOSCI301_Week4_Network_Studio_Executed.html','utf8')).window.document;
 assert.ok(doc.querySelector('#network-original-10 table'));
 const legacy=new JSDOM(fs.readFileSync('public/notebooks/legacy-idiom-atlas.html','utf8')).window.document;
 assert.ok(legacy.querySelector('#legacy-code-16 pre code'));
 assert.ok(legacy.querySelector('#legacy-code-19 table'));
});

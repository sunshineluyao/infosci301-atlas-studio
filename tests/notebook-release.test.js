import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import {createHash} from 'node:crypto';
const hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');const release=JSON.parse(fs.readFileSync('NOTEBOOK_RELEASE.json'));
test('all three source notebooks and saved previews match the execution record',()=>{
 assert.equal(release.notebooks.length,3);
 for(const r of release.notebooks){assert.equal(hash(r.notebook),r.notebook_sha256);assert.equal(hash('public/notebooks/'+r.html),r.html_sha256);const n=JSON.parse(fs.readFileSync(r.notebook));assert.equal(n.cells.filter(c=>c.cell_type==='code').length,r.executed_cells);assert.ok(n.cells.filter(c=>c.cell_type==='code').every(c=>c.execution_count>0&&!c.outputs.some(o=>o.output_type==='error')));}
});
test('every notebook has a matching source and figure evidence bundle',()=>{
 for(const name of ['network','spatial','idiom']){const b=fs.readFileSync('public/notebooks/'+name+'-evidence.zip');assert.equal(b.subarray(0,2).toString(),'PK');assert.ok(b.length>1000);}
 for(const name of ['paper_topic_dictionary.csv','paper_topic_matched.svg','heritage_source_dictionary.csv','heritage_space_time_comparison.svg'])assert.ok(fs.existsSync('public/notebooks/outputs/'+name));
});
test('Vercel source ref and optional execution boundaries are explicit',()=>{
 assert.match(fs.readFileSync('vite.config.js','utf8'),/VERCEL_GIT_COMMIT_SHA/);
 for(const r of release.notebooks.filter(r=>r.notebook.includes('Week4'))){const n=JSON.parse(fs.readFileSync(r.notebook));assert.ok(n.cells.some(c=>c.source.join('').includes('RUN_EXTENSIONS = False')));assert.ok(n.cells.filter(c=>c.metadata.tags?.includes('optional-extension')).every(c=>c.source.join('').includes('if RUN_EXTENSIONS:')));}
});

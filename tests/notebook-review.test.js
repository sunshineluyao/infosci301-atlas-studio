import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
test('review regressions: dependency versions and multi-notebook path isolation',()=>{
 const script="import importlib.util,importlib.metadata,tempfile,os,sys\nfrom pathlib import Path\nfrom unittest.mock import patch\nspec=importlib.util.spec_from_file_location('lesson_generator','scripts/revise_notebooks.py')\ngenerator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)\nfor installed in ('0.0','999.0',None):\n for kind in ('interaction','color','network','spatial'):\n  version=lambda name:installed\n  if installed is None:\n   def version(name):raise importlib.metadata.PackageNotFoundError(name)\n  with patch('importlib.metadata.version',side_effect=version),patch('importlib.util.find_spec',return_value=object()),patch('subprocess.check_call') as pip:\n   ns={};exec(generator.setup(kind,'import json'),ns)\n   assert pip.call_count==(0 if installed=='999.0' else 1),(kind,installed)\n   if pip.call_count:\n    assert pip.call_args.args[0][5:]==list(ns['requirements'].values())\nprint('Missing and outdated dependencies upgraded; compatible dependencies left installed.')\nspec=importlib.util.spec_from_file_location('publisher','scripts/publish_notebooks.py')\npublisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)\noriginal=Path.cwd()\nwith tempfile.TemporaryDirectory() as tmp:\n folder=Path(tmp);source=folder/'sources';public=folder/'public';other=folder/'unrelated';source.mkdir();public.mkdir();other.mkdir()\n for name in ['A.ipynb','B.ipynb']:(source/name).write_text('{}')\n try:\n  os.chdir(other)\n  with patch.object(publisher,'SOURCE',source),patch.object(publisher,'PUBLIC',public),patch.object(publisher,'WATER',True),patch.object(publisher,'pack_outputs'),patch.object(publisher,'render',return_value={}),patch('subprocess.run') as run,patch.object(sys,'argv',['publisher']):\n   publisher.main()\n   assert run.call_count==2\n   args=[call.args[0] for call in run.call_args_list]\n   assert all(Path(cmd[1]).is_absolute() and Path(cmd[3]).is_absolute() for cmd in args)\n   assert [Path(cmd[3]).name for cmd in args]==['A.ipynb','B.ipynb']\n   assert all(cmd[0]==sys.executable and cmd[2]=='--execute' for cmd in args)\n finally:os.chdir(original)\nprint('All notebooks use absolute paths and separate execution processes from an unrelated working directory.')\n";
 const output=execFileSync('python3',['-c',script],{encoding:'utf8'});
 assert.match(output,/Missing and outdated dependencies upgraded/);
 assert.match(output,/absolute paths and separate execution processes/);
});

test('download bundles contain nonempty valid figure exports',()=>{
 const script="import json,zipfile\nfrom pathlib import Path\nroot=Path('public/notebooks')\nfor lesson in json.loads((root/'manifest.json').read_text())['lessons']:\n with zipfile.ZipFile(root/lesson['bundle']) as bundle:\n  for entry in bundle.infolist():\n   if entry.filename.endswith(('.png','.pdf','.svg')):\n    data=bundle.read(entry)\n    assert data,entry.filename\n    if entry.filename.endswith('.png'):assert data.startswith(bytes.fromhex('89504e470d0a1a0a')),entry.filename\n    if entry.filename.endswith('.pdf'):assert data.startswith(b'%PDF-'),entry.filename\nprint('All figure exports contain data and valid PNG/PDF headers.')\n";
 assert.match(execFileSync('python3',['-c',script],{encoding:'utf8'}),/All figure exports contain data/);
});

import fs from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
test('changed output patches fail without replacing the verified result',()=>{
 const root=fs.mkdtempSync(path.join(tmpdir(),'atlas-output-patch-'));
 const hash=raw=>createHash('sha256').update(raw).digest('hex');
 try{
  for(const dir of ['scripts','public/notebooks/packed','public/notebooks/patches'])fs.mkdirSync(path.join(root,dir),{recursive:true});
  fs.copyFileSync('scripts/materialize-notebook-outputs.mjs',path.join(root,'scripts/materialize-notebook-outputs.mjs'));
  const base=Buffer.from('already public geometry\nprevious execution date'),prefix=Buffer.from('already public geometry\n').length,wanted='already public geometry\ncurrent execution date';
  fs.writeFileSync(path.join(root,'public/notebooks/packed/base.txt'),gzipSync(base).toString('base64'));
  const recipe={kind:'text',base_sha256:hash(base),operations:[{copy:[0,prefix]},{text:'current execution date'}]},patch=path.join(root,'public/notebooks/patches/change.json');
  fs.writeFileSync(patch,JSON.stringify(recipe));
  fs.writeFileSync(path.join(root,'public/notebooks/packed.json'),JSON.stringify([{target:'public/notebooks/Test.html',sha256:hash(wanted),parts:['public/notebooks/packed/base.txt'],patch:'public/notebooks/patches/change.json'}]));
  const run=()=>execFileSync(process.execPath,['scripts/materialize-notebook-outputs.mjs'],{cwd:root,stdio:'pipe'});
  run();const target=path.join(root,'public/notebooks/Test.html');assert.equal(fs.readFileSync(target,'utf8'),wanted);
  recipe.operations[1].text='unverified change';fs.writeFileSync(patch,JSON.stringify(recipe));
  assert.throws(run,error=>/checksum mismatch/.test(String(error.stderr)));
  assert.equal(fs.readFileSync(target,'utf8'),wanted);
 }finally{fs.rmSync(root,{recursive:true,force:true});}
});

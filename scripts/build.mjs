import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
const edition=process.argv[2]||'hf';
if(!['hf','vercel'].includes(edition))throw Error('Choose hf or vercel');
const result=spawnSync(process.execPath,['node_modules/vite/bin/vite.js','build','--mode',edition],{stdio:'inherit'});
if(result.status!==0)process.exit(result.status||1);
if(edition==='hf')fs.writeFileSync('dist-hf/README.md',`---
title: INFOSCI 301 Atlas Studio
emoji: 🌐
colorFrom: blue
colorTo: green
sdk: static
app_file: index.html
fullWidth: true
header: mini
pinned: false
---

# Atlas Studio · guided edition

Network intelligence and human-centered place/time intelligence. Four levels: Domain → Data/Task → Idiom → Algorithm, with validation at every level.

Static teaching app. No API keys or server inference. Real datasets and their limitations are documented in data/provenance.json. Configure config.json; read DEPLOYMENT_GUIDE.html. Notebook and original atlas files are under notebooks/.

Review source-data terms and course-material sharing rights before public release. Evidence notes stay in each learner's browser and are not automatically submitted.
`);
console.log(`Prepared dist-${edition}/ for ${edition==='hf'?'Static HTML Space upload':'Vercel static hosting'}.`);

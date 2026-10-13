"""Package served previews from saved notebook outputs, never from hand-drawn substitutes."""
from pathlib import Path
import hashlib,json,shutil,zipfile
import nbformat
from nbconvert import HTMLExporter
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'notebooks' if (ROOT/'notebooks').exists() else ROOT/'public/notebooks'
PUBLIC=ROOT/'public/notebooks';PUBLIC.mkdir(exist_ok=True)

def subset(n,indices,path):
 part=nbformat.v4.new_notebook(cells=[n.cells[i] for i in indices],metadata=n.metadata)
 exporter=HTMLExporter(template_name='lab');exporter.exclude_input=True;exporter.exclude_input_prompt=True;exporter.exclude_output_prompt=True
 body,_=exporter.from_notebook_node(part)
 style='<meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0!important;background:white}main{padding:10px!important}.jp-Notebook{padding:4px!important}.jp-OutputArea-output{overflow:auto}img{max-width:100%;height:auto}table{font-size:13px}h2{font-size:20px}.jp-Cell{padding:4px!important}</style>'
 banner='<p style="margin:0;padding:12px;background:#edf5f6;font:14px sans-serif">Recorded notebook output · '+n.metadata['execution_record']['executed_utc']+' · Python controls rerun in Colab.</p>'
 path.write_text(body.replace('<head>','<head>'+style).replace('<body>','<body>'+banner))

def zip_files(path,files,description):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('README.txt',description+'\nPython widgets require Colab/Jupyter. No peer feedback is fabricated. Source units and boundaries are documented in the notebook.\n')
  for p,arc in files:
   if p.is_file():z.write(p,arc)

manifest=[]
for p in sorted(BASE.glob('*.ipynb')):
 record_path=p.with_suffix('.execution.json')
 if not record_path.exists():continue
 rec=json.loads(record_path.read_text());assert rec['notebook_sha256']==hashlib.sha256(p.read_bytes()).hexdigest()
 manifest.append({**rec,'notebook':str(p.relative_to(ROOT))})
 n=nbformat.read(p,4);kind=''
 if 'Interaction_Design' in p.name:
  kind='interaction'
  for num,ids in enumerate([[5,7],[8,9],[10,11,12],[13,14],[15,16],[17,18],[19,20],[23]],1):subset(n,ids,PUBLIC/f'interaction-step-{num:02d}.html')
  extra=[(q,'outputs/'+q.name) for q in (BASE/'outputs').iterdir()]+[(BASE/'cp_signature_dictionary.csv','cp_signature_dictionary.csv'),(BASE/'student_exports/design_record.json','design_record.json')]
 elif 'Color_Palette' in p.name:
  kind='color';subset(n,[26,27,28],PUBLIC/'color-current-palette.html')
  extra=[(q,'student_exports/'+q.name) for q in (BASE/'student_exports').iterdir()]
 elif 'Network_Studio' in p.name:
  kind='network';names=['network_layout_comparison.png','network_community_centrality.png','openalex_knowledge_graph.png','openalex_knowledge_graph.svg','openalex_knowledge_graph.pdf','knowledge_graph_dictionary.csv','paper_topic_matched.png','paper_topic_matched.svg','paper_topic_matched.pdf','paper_topic_dictionary.csv','paper_topic_edges.csv']
  extra=[(BASE/'outputs'/name,'outputs/'+name) for name in names]+[(BASE/'student_exports/design_record.json','design_record.json')]
 elif 'Spatiotemporal_Studio' in p.name:
  kind='spatial';names=['eonet_monthly_timeline.png','heritage_space_time_comparison.png','heritage_space_time_comparison.svg','heritage_space_time_comparison.pdf','heritage_source_dictionary.csv']
  extra=[(BASE/'outputs'/name,'outputs/'+name) for name in names]+[(BASE/'student_exports/design_record.json','design_record.json')]
 elif 'Idiom_Algorithm' in p.name:
  kind='idiom';extra=[(q,'outputs/'+q.name) for q in (BASE/'idiom_algorithm_outputs').iterdir()]+[(BASE/'student_exports/design_record.json','design_record.json')]
 if kind:
  files=[(p,p.name),(record_path,'execution.json')]+extra
  zip_files(PUBLIC/(kind+'-evidence.zip'),files,kind.title()+' executed Python core results. R and specialist extensions were not rerun. Gallery examples labeled synthetic are not empirical evidence.')
 if BASE!=PUBLIC:
  for suffix in ['.html','.execution.json']:shutil.copy2(p.with_suffix(suffix),PUBLIC/p.with_suffix(suffix).name)
 elif '_Colab' in p.stem:
  shutil.copy2(p.with_suffix('.html'),p.with_name(p.stem.replace('_Colab','_Executed')+'.html'))
(ROOT/'NOTEBOOK_RELEASE.json').write_text(json.dumps({'release':'2026-10-14','notebooks':manifest,'source_ref':'Vercel builds use VERCEL_GIT_COMMIT_SHA for Colab; local builds use the review branch','boundaries':['Python widgets require a kernel','R and optional extensions were not rerun','Student feedback fields remain blank']},indent=2)+'\n')
print('Packaged',len(manifest),'notebooks;',sum(m['executed_cells'] for m in manifest),'recorded code-cell executions')

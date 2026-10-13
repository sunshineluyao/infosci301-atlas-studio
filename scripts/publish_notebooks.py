"""Execute each lesson in a fresh process; publish its authentic saved output."""
from pathlib import Path
import base64,hashlib,html,io,json,os,platform,re,shutil,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
WATER=(ROOT/'notebooks').is_dir()
SOURCE=ROOT/('notebooks' if WATER else 'public/notebooks');PUBLIC=ROOT/'public/notebooks'
CSS='''body{margin:0;background:#f5f7f6;color:#18343e;font:17px/1.6 system-ui,sans-serif}main{max-width:1080px;margin:auto;padding:28px 24px}h1{font-size:32px;line-height:1.2}h2{font-size:25px}a{color:#17646e;overflow-wrap:anywhere}.badge{display:inline-block;padding:5px 12px;background:#dcebea;border-radius:6px;font-size:14px}.intro{border-left:5px solid #d97706;padding:12px 18px;background:#fff7e7}.cell{background:white;border:1px solid #d2dedf;border-radius:10px;padding:20px 24px;margin:18px 0;scroll-margin-top:20px}.cell img,.cell svg{max-width:100%;height:auto}.output,table{overflow:auto}table{border-collapse:collapse;max-width:100%;font-size:14px}th,td{padding:7px 10px;border:1px solid #d9e1e2;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.5 ui-monospace,monospace;background:#f0f4f5;padding:15px}summary{cursor:pointer;font-weight:600;padding:8px 0}nav{display:flex;gap:15px;flex-wrap:wrap}.widget-note{padding:10px 14px;background:#edf3f4;border-left:3px solid #6873c7}.plotly-graph-div{min-height:420px}figure{margin:0}.optional{border-left:4px solid #d97706}code{overflow-wrap:anywhere}@media(max-width:640px){main{padding:18px 12px}.cell{padding:15px 12px}h1{font-size:26px}body{font-size:16px}}@media print{body{background:white}main{max-width:none}.cell{break-inside:avoid}details,nav{display:none}}'''
def execute(path):
    import nbformat,matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt,plotly.basedatatypes,plotly.io as pio
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.utils.capture import capture_output
    from IPython.display import display
    nb=nbformat.read(path,as_version=4);shell=InteractiveShell.instance()
    folder=ROOT/'.notebook-run'/path.stem
    if folder.exists():shutil.rmtree(folder)
    folder.mkdir(parents=True);os.chdir(folder);figfolder=Path('executed_figures');figfolder.mkdir()
    state=os.environ.get('INFOSCI301_PALETTE_INPUT')
    if state and 'Color' in path.name:shutil.copy2(state,'INFOSCI301_palette_state.json')
    current=[''];serial=[0]
    # Emit implicit results with the rich display formatter, rather than terminal repr.
    shell.displayhook.write_output_prompt=lambda:None
    shell.displayhook.write_format_data=lambda *args,**kwargs:None
    def emit_result(value):
        if value is None:return
        if type(value).__module__.startswith('altair') and hasattr(value,'to_html'):
            serial[0]+=1;stem=current[0]+f'-{serial[0]}'
            chart=value.to_html();(figfolder/(stem+'.vegalite.json')).write_text(value.to_json())
            display({'text/html':'<iframe title="Saved Altair chart" style="width:100%;height:650px;border:0" sandbox="allow-scripts allow-downloads" srcdoc="'+html.escape(chart,quote=True)+'"></iframe>'},raw=True)
        else:display(value)
    def show(*args,**kwargs):
        for i in list(plt.get_fignums()):
            fig=plt.figure(i);serial[0]+=1;stem=f'{current[0]}-{serial[0]}'
            buffer=io.StringIO();fig.savefig(buffer,format='svg',bbox_inches='tight')
            (figfolder/(stem+'.svg')).write_text(buffer.getvalue());fig.savefig(figfolder/(stem+'.pdf'),bbox_inches='tight')
            # SVG is sufficient in the notebook. PNG exports still come from lesson cells.
            display({'image/svg+xml':buffer.getvalue()},raw=True)
        plt.close('all')
    def plotly_show(fig,*args,**kwargs):
        serial[0]+=1;raw=pio.to_json(fig);(figfolder/(current[0]+f'-{serial[0]}.plotly.json')).write_text(raw)
        display({'application/vnd.plotly.v1+json':json.loads(raw),'text/plain':'Saved Plotly result; browser inspection requires its renderer.'},raw=True)
    plt.show=show;plotly.basedatatypes.BaseFigure.show=plotly_show
    count=0
    for idx,c in enumerate(nb.cells):
        if c.cell_type!='code':continue
        count+=1;current[0]=c.id;serial[0]=0
        with capture_output() as captured:
            result=shell.run_cell(c.source,store_history=False)
            if not (result.error_before_exec or result.error_in_exec):emit_result(result.result)
        exc=result.error_before_exec or result.error_in_exec
        if exc:
            (folder/'error.txt').write_text(captured.stdout+'\n'+captured.stderr);raise RuntimeError(f'{path.name} cell {idx+1} ({c.id}): {exc}')
        out=[]
        if captured.stdout:out.append(nbformat.v4.new_output('stream',name='stdout',text=captured.stdout))
        if captured.stderr:out.append(nbformat.v4.new_output('stream',name='stderr',text=captured.stderr))
        for item in captured.outputs:out.append(nbformat.v4.new_output('display_data',data=item.data,metadata=item.metadata))
        c.outputs=out;c.execution_count=count;c.metadata['infosci_execution']='completed'
        if c.source.startswith('# Optional package extension:'):
            label=c.source.splitlines()[0].split(': ',1)[1];c.metadata['infosci_execution']=shell.user_ns.get('_extension_status',{}).get(label,'not run')
    nb.metadata['infosci301_execution']={'method':'fresh IPython process; Colab frontend not tested','date':'2026-10-13','python':platform.python_version(),'code_cells':count,'status':'completed','optional_extensions':shell.user_ns.get('_extension_status',{})}
    nbformat.validate(nb);nbformat.write(nb,path);nbformat.write(nb,folder/'executed.ipynb');(folder/'execution.json').write_text(json.dumps(dict(nb.metadata['infosci301_execution']),indent=2));print(path.name,count,'Python cells completed',flush=True)
def render(path):
    import nbformat,markdown
    from plotly.offline.offline import get_plotlyjs_version
    executed=ROOT/'.notebook-run'/path.stem/'executed.ipynb'
    if not executed.exists():raise FileNotFoundError('Saved execution missing. Run notebook:publish; use the Node materializer to restore committed previews.')
    nb=nbformat.read(executed,as_version=4);blocks=[];figures=0;needs_plotly=False
    run=ROOT/'.notebook-run'/path.stem;assets=PUBLIC/'assets'/path.stem;assets.mkdir(parents=True,exist_ok=True)
    for asset in run.glob('INFOSCI301_*'):
        if asset.is_file() and asset.suffix!='.zip':shutil.copy2(asset,assets/asset.name)
    for c in nb.cells:
        cid=html.escape(c.id)
        if c.cell_type=='markdown':blocks.append(f'<section class="cell" id="{cid}">'+markdown.markdown(c.source,extensions=['tables','fenced_code'])+'</section>');continue
        parts=[]
        for j,out in enumerate(c.outputs):
            if out.output_type=='stream':parts.append('<pre>'+html.escape(out.text)+'</pre>');continue
            data=out.get('data',{})
            if 'image/svg+xml' in data:figures+=1;parts.append('<figure aria-label="Computed notebook figure">'+data['image/svg+xml']+'</figure>')
            elif 'image/png' in data:figures+=1;parts.append('<img alt="Computed notebook figure" src="data:image/png;base64,'+data['image/png']+'">')
            elif 'application/vnd.plotly.v1+json' in data:
                figures+=1;needs_plotly=True;pid=f'plot-{c.id}-{j}';spec=json.dumps(data['application/vnd.plotly.v1+json']).replace('</','<\\/')
                parts.append(f'<div id="{pid}" class="plotly-graph-div" aria-label="Saved Plotly result"></div><script type="application/json" data-plot="{pid}">{spec}</script>')
            elif 'text/html' in data:parts.append(data['text/html'])
            elif 'text/markdown' in data:parts.append(markdown.markdown(data['text/markdown'],extensions=['tables','fenced_code']))
            elif 'application/vnd.jupyter.widget-view+json' in data:parts.append('<p class="widget-note">Run this cell in Colab to use its controls. Static counterparts appear later in this lesson.</p>')
            elif 'text/plain' in data:parts.append('<pre>'+html.escape(data['text/plain'])+'</pre>')
        text=''.join('<div class="output">'+p+'</div>' for p in parts)
        for asset in run.glob('INFOSCI301_*'):
            for quote in ['"',"'"]:text=text.replace('href='+quote+asset.name+quote,'href='+quote+'assets/'+path.stem+'/'+asset.name+quote)
        status=c.metadata.get('infosci_execution','not executed')
        blocks.append(f'<section class="cell {"optional" if "not run" in status else ""}" id="{cid}"><span class="badge">{html.escape(status)}</span>{text}<details><summary>Inspect the exact Python source</summary><pre><code>{html.escape(c.source)}</code></pre></details></section>')
    bundle='assets/'+path.stem+'/saved_assets.zip'
    with zipfile.ZipFile(PUBLIC/bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(run.rglob('*')):
            if p.is_file() and p.suffix in ('.svg','.pdf','.png','.csv','.json','.css','.ase','.md','.py','.R'):z.write(p,p.relative_to(run))
    name=path.stem.replace('_Colab','_Executed')+'.html' if '_Colab' in path.stem else path.stem+'_Executed.html'
    clean=json.loads(nbformat.writes(nb))
    for c in clean['cells']:
        if c['cell_type']=='code':c['outputs']=[];c['execution_count']=None
    clean['metadata']['infosci301_execution']['saved_output']='Matching saved HTML and execution receipt; this download contains editable source.'
    path.write_text(json.dumps(clean,ensure_ascii=False,indent=1)+'\n')
    digest=hashlib.sha256(path.read_bytes()).hexdigest();title=nb.metadata.get('colab',{}).get('name',path.stem).replace('.ipynb','').replace('_',' ')
    body=f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} saved output</title><style>{CSS}</style></head><body><main><span class="badge">Saved execution · 13 October 2026</span><h1>{html.escape(title)}</h1><div class="intro">Results below were generated from the downloadable notebook. Python widgets require Colab. Plotly/Altair/deck.gl inspection may require external renderers and browser support; static counterparts remain readable.</div><nav><a href="{path.name}" download>Download the exact notebook</a><a href="{bundle}" download>Download SVG/PDF/PNG figures and source records</a><a href="#execution-record">Execution record</a></nav>'+''.join(blocks)+f'<section class="cell" id="execution-record"><h2>Execution record</h2><pre>{html.escape(json.dumps(dict(nb.metadata["infosci301_execution"]),indent=2))}</pre><p>Notebook SHA-256: <code>{digest}</code></p><p>Optional cells marked not run are retained source, not newly verified outputs. R and end-to-end Colab interaction are not certified by this record.</p></section></main>'
    if needs_plotly:
        body+=f'<script src="https://cdn.plot.ly/plotly-{get_plotlyjs_version()}.min.js"></script>'+'''<script>
const specs=[...document.querySelectorAll('script[data-plot]')];
function render(el){const spec=specs.find(s=>s.dataset.plot===el.id);if(!spec||el.dataset.rendered)return;el.dataset.rendered='true';if(!window.Plotly){el.textContent='Interactive renderer unavailable; read the static counterparts or run Colab.';return}const p=JSON.parse(spec.textContent);Plotly.newPlot(el,p.data,p.layout,{responsive:true,displaylogo:false});if(p.frames?.length)Plotly.addFrames(el,p.frames)}
if('IntersectionObserver' in window){const observer=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){render(e.target);observer.unobserve(e.target)}}),{rootMargin:'250px'});specs.forEach(s=>observer.observe(document.getElementById(s.dataset.plot)))}else{specs.forEach(s=>render(document.getElementById(s.dataset.plot)))}
</script>'''
    (PUBLIC/name).write_text(body+'</body></html>')
    return {'notebook':path.name,'preview':name,'bundle':bundle,'sha256':digest,'code_cells':sum(c.cell_type=='code' for c in nb.cells),'figures':figures,'preview_sha256':hashlib.sha256((PUBLIC/name).read_bytes()).hexdigest(),'execution':dict(nb.metadata['infosci301_execution'])}
def pack_outputs():
    import gzip
    packed=PUBLIC/'packed'
    if packed.exists():shutil.rmtree(packed)
    packed.mkdir()
    files=sorted(PUBLIC.glob('*Executed.html'))
    if (PUBLIC/'legacy-idiom-atlas.html').exists():files.append(PUBLIC/'legacy-idiom-atlas.html')
    files+=sorted((PUBLIC/'assets').rglob('*.zip'))
    rows=[]
    for p in files:
        raw=p.read_bytes();encoded=base64.b64encode(gzip.compress(raw,mtime=0)).decode();prefix=p.stem+'-'+hashlib.sha256(raw).hexdigest()[:12]
        parts=[]
        for i,start in enumerate(range(0,len(encoded),300000)):
            part=packed/(prefix+f'-{i:02d}.txt');part.write_text(encoded[start:start+300000]);parts.append(str(part.relative_to(ROOT)))
        rows.append({'target':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'parts':parts})
    (PUBLIC/'packed.json').write_text(json.dumps(rows,indent=2))
def main():
    paths=sorted(SOURCE.glob('*.ipynb'))
    if '--render-only' in sys.argv:
        for p in paths:
            run=ROOT/'.notebook-run'/p.stem;executed=run/'executed.ipynb'
            if not executed.exists() or not (run/'execution.json').exists() or not (run/'executed_figures').is_dir():
                raise SystemExit('Saved execution missing. Run notebook:publish; use the Node materializer to restore committed previews.')
            current=json.loads(p.read_text());saved=json.loads(executed.read_text())
            signature=lambda n:[(c['cell_type'],c['id'],''.join(c['source'])) for c in n['cells']]
            if signature(current)!=signature(saved):raise SystemExit('Notebook source changed since execution. Run notebook:publish before rendering.')
    else:
        for p in paths:subprocess.run([sys.executable,str(Path(__file__).resolve()),'--execute',str(p.resolve())],check=True,timeout=240)
    rows=[render(p) for p in paths]
    if not WATER:
        legacy=next((r for r in rows if 'Week2' in r['notebook']),None)
        if legacy:(PUBLIC/'legacy-idiom-atlas.html').write_text((PUBLIC/legacy['preview']).read_text())
    (PUBLIC/'manifest.json').write_text(json.dumps({'revision':'2026-10-13','lessons':rows},ensure_ascii=False,indent=2));pack_outputs();print('Published',len(rows),'matching saved views',flush=True)
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--execute':execute(Path(sys.argv[2]).resolve())
    else:main()

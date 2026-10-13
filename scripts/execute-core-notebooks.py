"""Execute core notebook cells and produce HTML from the exact saved outputs.
Optional extensions are gated in notebook source, not silently skipped by this runner.
"""
import ast,base64,contextlib,datetime,hashlib,io,json,os,sys,traceback
from pathlib import Path
os.environ['MPLBACKEND']='Agg'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import nbformat
from nbconvert import HTMLExporter
from nbformat.v4 import new_output
import IPython.display as ipdisplay
import plotly.basedatatypes
import altair
import pydeck

def execute(path):
 path=Path(path).resolve();os.chdir(path.parent)
 n=nbformat.read(path,4);outputs=[];namespace={'__name__':'__main__'};started=datetime.datetime.now(datetime.timezone.utc).isoformat();count=0
 def display(*objects,**kw):
  for obj in objects:
   if obj is None:continue
   if isinstance(obj,altair.TopLevelMixin):data={'text/html':obj.to_html(output_div='vega-cell-'+str(count)+'-'+str(len(outputs)),fullhtml=False),'text/plain':'Altair chart: saved interactive JS output'}
   elif isinstance(obj,pydeck.Deck):data={'text/html':obj.to_html(as_string=True),'text/plain':'pydeck saved JS output'}
   elif obj.__class__.__module__.startswith('ipywidgets'):data={'text/html':'<p style="padding:12px;background:#eef5f7">Python widget controls: rerun this cell in Colab/Jupyter. The initial chart or table above is the executed saved result.</p>','text/plain':'Python widget controls require a Python kernel'}
   elif hasattr(obj,'_repr_html_') and obj._repr_html_():data={'text/html':obj._repr_html_(),'text/plain':repr(obj)}
   elif hasattr(obj,'_repr_markdown_') and obj._repr_markdown_():data={'text/markdown':obj._repr_markdown_(),'text/plain':repr(obj)}
   else:data={'text/plain':repr(obj)}
   outputs.append(new_output('display_data',data=data,metadata={}))
 def show(*args,**kw):
  for num in plt.get_fignums():
   fig=plt.figure(num);buf=io.BytesIO();fig.savefig(buf,format='png',dpi=130,bbox_inches='tight')
   outputs.append(new_output('display_data',data={'image/png':base64.b64encode(buf.getvalue()).decode()},metadata={}))
  plt.close('all')
 def pshow(fig,*args,**kw):outputs.append(new_output('display_data',data={'text/html':fig.to_html(include_plotlyjs='cdn',full_html=False,config={'responsive':True}),'text/plain':'Plotly interactive saved result'},metadata={}))
 orig=ipdisplay.display,ipdisplay.clear_output,plt.show,plotly.basedatatypes.BaseFigure.show
 ipdisplay.display=display;ipdisplay.clear_output=lambda **kw:None;plt.show=show;plotly.basedatatypes.BaseFigure.show=pshow;namespace['_capture_display']=display
 try:
  for i,c in enumerate(n.cells):
   c.id=f'cell-{i:02d}'
   if c.cell_type!='code':continue
   count+=1;outputs.clear();stdout=io.StringIO();stderr=io.StringIO()
   print(path.name,'cell',i,flush=True)
   try:
    with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
     tree=ast.parse(c.source)
     if tree.body and isinstance(tree.body[-1],ast.Expr):
      tree.body[-1]=ast.Expr(value=ast.Call(func=ast.Name(id='_capture_display',ctx=ast.Load()),args=[tree.body[-1].value],keywords=[]));ast.fix_missing_locations(tree)
     exec(compile(tree,str(path)+':'+str(i),'exec'),namespace)
   except Exception:
    print(stderr.getvalue(),file=sys.stderr);print(traceback.format_exc(),file=sys.stderr);raise
   c.execution_count=count;c.outputs=[]
   if stdout.getvalue():c.outputs.append(new_output('stream',name='stdout',text=stdout.getvalue()))
   if stderr.getvalue():c.outputs.append(new_output('stream',name='stderr',text=stderr.getvalue()))
   c.outputs.extend(outputs)
 finally:ipdisplay.display,ipdisplay.clear_output,plt.show,plotly.basedatatypes.BaseFigure.show=orig
 n.metadata['execution_record']={'executed_utc':started,'runner':'in-process Python: saved display outputs and initial widget callbacks; optional extensions explicitly disabled','executed_cells':count,'python':sys.version.split()[0],'optional_extensions':False}
 nbformat.write(n,path)
 exporter=HTMLExporter(template_name='lab');exporter.exclude_input_prompt=True;exporter.exclude_output_prompt=True
 html,_=exporter.from_notebook_node(n)
 banner='<div style="padding:18px;background:#edf5f6;color:#20343b;font:16px sans-serif">Executed core results · '+started+' · Python widgets require Colab/Jupyter; JS charts retain their supported browser interactions. Optional extensions are labeled in source.</div>'
 html=html.replace('<body>','<body>'+banner)
 target=path.with_suffix('.html');target.write_text(html)
 record={**n.metadata['execution_record'],'notebook_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'html_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'notebook':path.name,'html':target.name}
 path.with_suffix('.execution.json').write_text(json.dumps(record,indent=2)+'\n')
 print('PASS',path.name,count,'cells',flush=True)

if __name__=='__main__':
 paths=[Path(arg).resolve() for arg in sys.argv[1:]]
 for path in paths:execute(path)

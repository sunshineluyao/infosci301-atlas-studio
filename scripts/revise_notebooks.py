"""Revise teaching source while preserving all original demonstrations."""
from pathlib import Path
import base64, gzip, hashlib, json, textwrap
ROOT=Path(__file__).resolve().parents[1]
WATER=(ROOT/'notebooks').is_dir()
FOLDER=ROOT/('notebooks' if WATER else 'public/notebooks')
def src(c):return ''.join(c['source'])
def put(c,s):c['source']=s.strip().splitlines(keepends=True)
def cell(kind,s,key):return {'cell_type':kind,'id':key,'metadata':{'infosci_generated':True},'source':s.strip().splitlines(keepends=True),**({'outputs':[],'execution_count':None} if kind=='code' else {})}
def embedded(files):
    raw={name:(ROOT/'public/data'/name).read_bytes() for name in files}
    values={name:base64.b64encode(gzip.compress(value,mtime=0)).decode() for name,value in raw.items()}
    hashes={name:hashlib.sha256(value).hexdigest() for name,value in raw.items()}
    return f'''import base64,gzip,hashlib,json
SNAPSHOT_B64={values!r}
SNAPSHOT_HASHES={hashes!r}
def bundled_json(name):
    raw=gzip.decompress(base64.b64decode(SNAPSHOT_B64[name]))
    assert hashlib.sha256(raw).hexdigest()==SNAPSHOT_HASHES[name]
    return json.loads(raw)
'''
STYLE='''import matplotlib.pyplot as plt
from pathlib import Path
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':14,'axes.labelsize':11,'xtick.labelsize':10,'ytick.labelsize':10,'figure.dpi':120,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
LESSON_OUTPUT=Path('lesson_outputs');LESSON_OUTPUT.mkdir(exist_ok=True)
def save_lesson_figure(fig,name):
    for fmt in ('svg','pdf','png'):fig.savefig(LESSON_OUTPUT/(name+'.'+fmt),bbox_inches='tight',dpi=160)
    plt.show()
'''
INTRO='''## Read, explore, revise, and explain / 阅读、探索、修改与解释

Follow **Domain → Data/Task → Idiom → Algorithm**, and validate each decision.
从领域与人群出发，依次说明数据与任务、视觉表达、算法，并逐层检验。

1. **Core route:** inspect the bundled evidence, run a baseline, compare the named idioms, then change one meaningful parameter while keeping the other records and scales fixed.
2. **Optional depth:** specialist cells retain their original source. Set `RUN_PACKAGE_EXTENSIONS=True` and install the documented package only when your question needs it. A skipped cell is not an executed algorithm.
3. **Your contribution:** explain three human design decisions, one supported reading, one limitation, and the next test. Peer-feedback fields remain empty until someone actually tests the artifact.

Vercel displays a **saved execution generated from this notebook**. Python widgets require a Colab session. Static figures preserve the evidence when widgets or GPU views are unavailable. Package installation and external browser renderers may need internet; the core lesson data require no live API or key.
Vercel 展示由本笔记本生成的已保存结果。Python 控件需在 Colab 中运行；静态图保留相同数据与证据边界。
'''
NAMES={
'network':{4:'Shared plotting style',6:'Karate Club source table',7:'Node-link layout small multiples',10:'Node metric table',11:'Community-colored node-link diagram',13:'Interactive node-link inspection',14:'Physics-enabled node-link diagram',15:'Directed process diagram',16:'Inter-community chord diagram',18:'Rasterized node-link exploration',20:'OpenAlex source table',21:'Heterogeneous knowledge-graph construction',22:'Heterogeneous node-link diagram',23:'Sparse-graph PageRank comparison',25:'Optional live refresh',29:'Paper–topic source table',31:'Topic-count baseline and node-link diagram',32:'Graph consistency tests'},
'spatial':{4:'Shared plotting style',5:'Event-geometry snapshot',7:'Spatial evidence audit',9:'Geographic point map',10:'Robinson projected point map',13:'Temporal line chart',14:'Animated geographic point map',15:'Time-aware point map',16:'GPU point layer',18:'Rasterized count-density view',19:'H3 hexagonal aggregation',20:'Spatial autocorrelation',21:'Georeferenced count raster',23:'Repeated-geometry trajectory summary',24:'Linked geographic inspection',26:'Coordinate-derived graph',27:'Optional tiled basemap',33:'Heritage source table',34:'Timeline and geographic point map',35:'Time and group filter'},
'interaction':{7:'Globe with projection controls',9:'Pitched geographic path map',11:'Categorical matrix with linked selection',13:'Month-controlled temporal chart',15:'Brushed overview and detail',17:'Four-level decision navigator',19:'Authored evidence card',21:'Palette before/after comparison',25:'Student innovation record'},
'color':{5:'Color-space comparison',7:'Palette-family construction',9:'Contrast and color-vision preview',10:'Color, shape, and label redundancy',12:'Palette audit ledger',14:'Research-pattern palette gallery',16:'Design-token and ASE export',18:'3D scalar surface and lighting',20:'Authored palette decision card',23:'Student innovation record'}}
OPTIONAL={'network':{14,15,16,18,23},'spatial':{10,15,16,18,19,20,21,23,24,26,27}}
def guide(title,detail='Inspect, compare, or explain the stated evidence.',boundary='A display does not establish causality, consent, or community value.'):
    return f'''### {title}

| Decision / 决策 | This cell / 本单元 |
|---|---|
| Idiom / 视觉表达 | {title} |
| Task / 任务 | {detail} |
| Algorithm / 算法 | Inspect the named implementation and parameters in the following cell. |
| Data and units / 数据与单位 | Use the adjacent source note, units, sample, exclusions, and baseline. |
| Evidence boundary / 证据边界 | {boundary} |

**Try and explain / 尝试并解释:** keep the baseline, change one documented parameter, and explain which reading changes. Retain the original and revised outputs.
'''
def setup(kind,old):
    names=['pandas','numpy','matplotlib','plotly']+({'network':['networkx','sklearn'],'spatial':['geopandas','shapely'],'interaction':['altair','pydeck','ipywidgets'],'color':['ipywidgets','coloraide','colorspacious']}[kind])
    requirements={n:('scikit-learn' if n=='sklearn' else n) for n in names}
    s=f'''# Install only missing core libraries. Data are bundled; package downloads may need internet.
import importlib.util,subprocess,sys
RUN_PACKAGE_EXTENSIONS=False
_extension_status={{}}
requirements={requirements!r}
missing=[pkg for module,pkg in requirements.items() if importlib.util.find_spec(module) is None]
if missing:subprocess.check_call([sys.executable,'-m','pip','install','-q',*missing])
print('Core environment ready; no live data API or key is required.')
'''
    return s if kind in ('network','spatial') else s+old[old.index('import json'):]

NETWORK=STYLE+'''import networkx as nx,pandas as pd,numpy as np,textwrap
NETWORK_PARAMETERS={'maxPapers':30,'since':2019,'seed':301,'metric':'degree'}
papers=[p for p in bundled_json('emerging-tech.json') if p['year']>=NETWORK_PARAMETERS['since']][:NETWORK_PARAMETERS['maxPapers']]
paper_topic=nx.Graph()
for p in papers:
    paper_topic.add_node(p['id'],kind='paper',label=p['title'])
    for t in p['topics']:
        paper_topic.add_node(t['id'],kind='topic',label=t['label']);paper_topic.add_edge(p['id'],t['id'],relation='classified under',source=p['url'])
paper_ids=[p['id'] for p in papers]
topic_ids=sorted([n for n,d in paper_topic.nodes(data=True) if d['kind']=='topic'],key=lambda n:(-paper_topic.degree(n),n))
print(len(papers),'papers;',len(topic_ids),'topics;',paper_topic.number_of_edges(),'provider-assigned links')
assert all(paper_topic.nodes[a]['kind']!=paper_topic.nodes[b]['kind'] for a,b in paper_topic.edges())
assert sum(dict(paper_topic.degree()).values())==2*paper_topic.number_of_edges()
paper_dictionary=pd.DataFrame([{'paper_label':f'P{i+1:02d}','id':p['id'],'year':p['year'],'title':p['title'],'url':p['url']} for i,p in enumerate(papers)])
topic_dictionary=pd.DataFrame([{'topic_label':f'T{i+1:02d}','id':n,'topic':paper_topic.nodes[n]['label'],'assignments':paper_topic.degree(n)} for i,n in enumerate(topic_ids)])
display(HTML('<details><summary>Inspect the paper dictionary</summary>'+paper_dictionary.to_html(index=False,escape=True)+'</details>'))
paper_dictionary.to_csv(LESSON_OUTPUT/'paper_dictionary.csv',index=False);topic_dictionary.to_csv(LESSON_OUTPUT/'topic_dictionary.csv',index=False)
fig,ax=plt.subplots(figsize=(11,5.6),layout='constrained');top=topic_ids[:8][::-1]
ax.barh([textwrap.fill(paper_topic.nodes[n]['label'],38) for n in top],[paper_topic.degree(n) for n in top],color='#14877D')
ax.set(title='Top 8 topic-assignment counts in the fixed sample',xlabel='Paper–topic links (count)');save_lesson_figure(fig,'network_topic_counts')
fig,ax=plt.subplots(figsize=(9,11),layout='constrained')
pos={n:(0,1-i/max(1,len(paper_ids)-1)) for i,n in enumerate(paper_ids)};pos.update({n:(1,1-i/max(1,len(topic_ids)-1)) for i,n in enumerate(topic_ids)})
nx.draw_networkx_edges(paper_topic,pos,ax=ax,edge_color='#9BAEB5',alpha=.55,width=.8)
for kind,color,shape in [('paper','#14877D','o'),('topic','#D97706','s')]:
    nodes=[n for n,d in paper_topic.nodes(data=True) if d['kind']==kind];nx.draw_networkx_nodes(paper_topic,pos,nodelist=nodes,node_color=color,node_shape=shape,node_size=95,ax=ax,label=kind.title())
for i,n in enumerate(paper_ids):ax.text(-.03,pos[n][1],f'P{i+1:02d}',ha='right',va='center',fontsize=10)
for i,n in enumerate(topic_ids):ax.text(1.03,pos[n][1],f'T{i+1:02d}',ha='left',va='center',fontsize=10)
ax.set_title('Ordered bipartite node-link diagram · the same assignments');ax.set_xlim(-.12,1.12);ax.set_ylim(-.06,1.07)
ax.text(.5,-.055,'P/T IDs match the downloadable source dictionaries',ha='center',fontsize=10);ax.legend(frameon=False);ax.axis('off');save_lesson_figure(fig,'network_paper_topic')
adjacency=pd.DataFrame([[int(paper_topic.has_edge(p,t)) for t in topic_ids] for p in paper_ids],index=paper_ids,columns=topic_ids);adjacency.to_csv(LESSON_OUTPUT/'paper_topic_full_matrix.csv')
shown=topic_ids[:12];fig,ax=plt.subplots(figsize=(12,9),layout='constrained')
ax.imshow(adjacency[shown].values,aspect='auto',cmap=__import__('matplotlib').colors.ListedColormap(['#F3F6F7','#14877D']),vmin=0,vmax=1)
ax.set_yticks(range(len(paper_ids)),[f'P{i+1:02d}' for i in range(len(paper_ids))]);ax.set_xticks(range(len(shown)),[textwrap.fill(paper_topic.nodes[n]['label'],20) for n in shown],rotation=45,ha='right')
ax.set(title=f'Bipartite matrix · {len(shown)} of {len(topic_ids)} topics shown',ylabel='Paper ID (same source-table order)',xlabel='Topics ranked by assignment count · teal = assigned');save_lesson_figure(fig,'network_bipartite_matrix')
print('Topic assignment is not citation. NetworkX and D3 layouts differ numerically; IDs and edges agree, coordinates need not.')
'''
HERITAGE=STYLE+'''import pandas as pd,numpy as np
heritage=pd.DataFrame(bundled_json('heritage.json'));assert heritage.id.is_unique
assert heritage.lon.between(-180,180).all() and heritage.lat.between(-90,90).all()
HERITAGE_PARAMETERS={'from':int(heritage.year.min()),'to':int(heritage.year.max()),'group':'All'}
visible=heritage[heritage.year.between(HERITAGE_PARAMETERS['from'],HERITAGE_PARAMETERS['to'])].copy()
if HERITAGE_PARAMETERS['group']!='All':visible=visible[visible.group==HERITAGE_PARAMETERS['group']]
print(len(visible),'of',len(heritage),'unique designation IDs; designation dates are not construction dates.')
groups=sorted(heritage.group.unique());colors=dict(zip(groups,['#14877D','#D97706','#6A5983','#C2413A','#368BC5']));markers=dict(zip(groups,['o','s','^','D','P']))
fig,axes=plt.subplots(1,2,figsize=(14,6.2),layout='constrained');count=visible.groupby('year').size().reindex(range(HERITAGE_PARAMETERS['from'],HERITAGE_PARAMETERS['to']+1),fill_value=0)
axes[0].plot(count.index,count.values,color='#14877D',linewidth=2);axes[0].set(title='Timeline · retained designation IDs',xlabel='Designation year',ylabel='Designation IDs (count)')
for group in groups:
    rows=visible[visible.group==group];axes[1].scatter(rows.lon,rows.lat,s=12,alpha=.6,color=colors[group],marker=markers[group],label=group)
axes[1].set(title='Geographic point map · the same records',xlabel='Longitude (degrees)',ylabel='Latitude (degrees)',xlim=(heritage.lon.min()-.015,heritage.lon.max()+.015),ylim=(heritage.lat.min()-.015,heritage.lat.max()+.015));axes[1].set_aspect(1/np.cos(np.deg2rad(40.7)));axes[1].legend(title='Borough',fontsize=9,frameon=False);save_lesson_figure(fig,'heritage_map_timeline')
fig=plt.figure(figsize=(11,7));ax=fig.add_subplot(111,projection='3d')
for group in groups:
    rows=visible[visible.group==group];ax.scatter(rows.lon,rows.lat,rows.year,s=10,alpha=.65,color=colors[group],marker=markers[group],label=group)
ax.set(xlabel='Longitude (degrees)',ylabel='Latitude (degrees)',xlim=(heritage.lon.min(),heritage.lon.max()),ylim=(heritage.lat.min(),heritage.lat.max()),zlim=(heritage.year.min(),heritage.year.max()),title='Space-time cube · height encodes designation year')
ax.text2D(1.04,.62,'Designation year',transform=ax.transAxes,rotation=90);ax.view_init(elev=24,azim=-62);ax.legend(fontsize=9);fig.subplots_adjust(left=.03,right=.87,bottom=.04,top=.93);save_lesson_figure(fig,'heritage_space_time_cube')
visible[['id','title','group','date','year','lon','lat','url']].to_csv(LESSON_OUTPUT/'heritage_selected_records.csv',index=False)
print('Geographic coordinates do not measure community value; use a declared CRS for distance/area work.')
'''
PALETTE='''def oklch_hex(L,C,h):
    import math
    def convert(chroma):
        a,b=chroma*math.cos(math.radians(h)),chroma*math.sin(math.radians(h))
        l,m,s=(L+.3963377774*a+.2158037573*b)**3,(L-.1055613458*a-.0638541728*b)**3,(L-.0894841775*a-1.291485548*b)**3
        v=[4.0767416621*l-3.3077115913*m+.2309699292*s,-1.2684380046*l+2.6097574011*m-.3413193965*s,-.0041960863*l-.7034186147*m+1.707614701*s]
        return [255*(12.92*x if x<=.0031308 else 1.055*max(x,0)**(1/2.4)-.055) for x in v]
    rgb=convert(C)
    for _ in range(28):
        if all(0<=v<=255 for v in rgb):break
        C*=.92;rgb=convert(C)
    return '#'+''.join(f'{int(math.floor(min(255,max(0,v))+.5)):02X}' for v in rgb)
def make_palette(kind,n,h,c,l_span):
    result=[]
    for i in range(n):
        t=.5 if n==1 else i/(n-1)
        if kind=='qualitative':L=.7+(-.045 if i%2 else .025);C=c;H=h+i*(360/n)
        elif kind=='sequential':L=.94-t*l_span/100;C=c*(.38+.62*t);H=h
        else:
            distance=abs(t-.5)*2;L=.94-distance*l_span/100;C=max(.012,c*distance);H=h if t<=.5 else h+180
        result.append(oklch_hex(L,C,H))
    return result
'''
INTERACTION=STYLE+'''import numpy as np,pandas as pd
from matplotlib.lines import Line2D
fig,ax=plt.subplots(figsize=(11,5.6),layout='constrained')
for f in waterways['features']:
    coords=np.asarray(f['geometry']['coordinates']);ax.plot(coords[:,0],coords[:,1],color='#245C70',linewidth=.7,alpha=.6)
ax.scatter([120.98],[31.39],marker='D',s=70,color='#D97706',label='Kunshan city coordinate');ax.set(title='Geographic path map · bundled OSM waterways',xlabel='Longitude (degrees)',ylabel='Latitude (degrees)');ax.set_aspect(1/np.cos(np.deg2rad(31.3)));ax.legend(frameon=False);save_lesson_figure(fig,'interaction_waterway_paths')
rain_saved=pd.DataFrame(rainfall['records']);annual=rain_saved[rain_saved.year==2025].sort_values('month');assert len(annual)==12
fig,ax=plt.subplots(figsize=(11,5.5),layout='constrained');ax.bar(annual.month,annual.mm_per_day,color='#245C70');ax.set_xticks(range(1,13));ax.set(title='Temporal bar chart · 2025 monthly precipitation',xlabel='Month',ylabel='Monthly mean precipitation (mm/day)',ylim=(0,float(rain_saved.mm_per_day.max())*1.05));save_lesson_figure(fig,'interaction_rainfall')
levels=np.array([[0 if x==0 else 2 if x==1 else 1 for x in r['values']] for r in mandara['signatures']]);fig,ax=plt.subplots(figsize=(12,4.7),layout='constrained')
ax.imshow(levels,cmap=__import__('matplotlib').colors.ListedColormap(['#E5EDEF','#D97706','#245C70']),vmin=0,vmax=2,aspect='auto')
for row in range(levels.shape[0]):
    for col in range(levels.shape[1]):ax.text(col,row,['—','S','D'][levels[row,col]],ha='center',va='center',color='white' if levels[row,col]==2 else '#18343E',fontsize=10)
ax.set_xticks(range(len(mandara['culture_periods'])),mandara['culture_periods']);ax.set_yticks(range(len(mandara['signatures'])),[r['group'] for r in mandara['signatures']]);ax.set(title='Categorical assertion matrix · paper-derived teaching layer',xlabel='CP model identifier (not chronology)')
ax.legend(handles=[Line2D([],[],marker='s',linestyle='',color=c,label=l,markersize=9) for c,l in [('#E5EDEF','— Not asserted'),('#D97706','S Smaller reported'),('#245C70','D Dominant reported')]],loc='upper center',bbox_to_anchor=(.5,-.22),ncol=3,frameon=False);save_lesson_figure(fig,'interaction_assertion_matrix');annual.to_csv(LESSON_OUTPUT/'rainfall_2025.csv',index=False)
print('Mapped geometry is not water flow. Paper-derived assertions are qualitative, not counts or probabilities.')
'''
COLOR=STYLE+'''from matplotlib.colors import ListedColormap,TwoSlopeNorm
palette_parameters={'family':family.value,'count':steps.value,'hue':base_hue.value,'chroma':palette_chroma.value,'span':span.value}
palette_state={'schema_version':1,'parameters':palette_parameters,'colors':export_colors}
Path('INFOSCI301_palette_state.json').write_text(json.dumps(palette_state,indent=2))
color_rain=pd.DataFrame(bundled_json('kunshan-precipitation.json')['records']);annual=color_rain[color_rain.year==2025].sort_values('month');baseline=color_rain.groupby('month').mm_per_day.mean().reindex(annual.month);delta=annual.mm_per_day.to_numpy()-baseline.to_numpy()
p=palette_parameters;seq=export_colors if p['family']=='sequential' else make_palette('sequential',p['count'],p['hue'],p['chroma'],p['span']);div=export_colors if p['family']=='diverging' else make_palette('diverging',p['count'],p['hue'],p['chroma'],p['span'])
fig,axes=plt.subplots(2,1,figsize=(11,9),layout='constrained');norm=__import__('matplotlib').colors.Normalize(vmin=0,vmax=float(color_rain.mm_per_day.max()))
axes[0].bar(annual.month,annual.mm_per_day,color=ListedColormap(seq)(norm(annual.mm_per_day)));axes[0].set(title='Sequential palette · monthly precipitation in 2025',ylabel='Monthly mean precipitation (mm/day)',ylim=(0,float(color_rain.mm_per_day.max())*1.05))
limit=max(abs(delta).max(),.1);axes[1].bar(annual.month,delta,color=ListedColormap(div)(TwoSlopeNorm(vmin=-limit,vcenter=0,vmax=limit)(delta)));axes[1].axhline(0,color='#20343B',linewidth=1);axes[1].set(title='Diverging palette · departure from the 2001–2025 same-month mean',ylabel='Departure (mm/day)',xlabel='Month',ylim=(-limit*1.15,limit*1.15))
for ax in axes:ax.set_xticks(range(1,13))
save_lesson_figure(fig,'color_real_data_families');fig,axes=plt.subplots(2,1,figsize=(11,4.7),layout='constrained')
for ax,mode in zip(axes,['normal','grayscale']):
    colors=[simulate_color(c,mode) for c in export_colors];ax.imshow([np.arange(len(colors))],cmap=ListedColormap(colors),aspect='auto',vmin=0,vmax=max(1,len(colors)-1));ax.set_xticks(range(len(colors)),export_colors,rotation=25);ax.set_yticks([]);ax.set_title('Selected palette · '+mode)
save_lesson_figure(fig,'color_palette_and_grayscale');display(audit_palette(export_colors,palette_parameters['family']));annual.to_csv(LESSON_OUTPUT/'rainfall_2025.csv',index=False)
'''
def revise(path,kind):
    n=json.loads(path.read_text());original=[]
    for c in n['cells']:
        if c.get('metadata',{}).get('infosci_generated'):continue
        if 'infosci_original_source' in c.get('metadata',{}):put(c,c['metadata']['infosci_original_source'])
        original.append(c)
    for i,c in enumerate(original,1):
        c['id']=f'{kind}-original-{i:02d}'
        if c['cell_type']!='code':continue
        s=src(c);c['metadata']['infosci_original_source']=s
        if i==3:s=setup(kind,s)
        if kind=='network' and i==11:
            a=s.index('import igraph');b=s.index('summary =');s=s[:a]+"# Specialist Leiden comparison is optional; the core plot uses Louvain.\nleiden=louvain\nif RUN_PACKAGE_EXTENSIONS:\n"+textwrap.indent(s[a:b],'    ')+s[b:];s=s.replace('["Leiden", len(leiden), nx.community.modularity(G, leiden)],','').replace('Leiden communities;','Louvain communities;')
        if kind=='spatial' and i==9:s=s[s.index('fig, ax'):].replace('world.plot(ax=ax, color="#EEF2F3", edgecolor="#A8B5B9", linewidth=.4)','ax.set_facecolor("#EEF2F3") # Coordinate map without a basemap download.')
        if kind=='spatial' and i==10:
            a=s.index('try:');b=s.index('ax.scatter');s=s[:a]+'# Projected marks remain the evidence; no Natural Earth download.\n'+s[b:]
        if kind=='spatial' and i==23:s=s.replace('length_degrees','observed_geometry_path_meters').replace('t.get_length()','t.get_length(units="m")')
        if kind=='interaction' and i==3:
            a=s.index('BASE =');b=s.index('display(HTML',a);s=s[:a]+embedded(['kunshan-waterways.geojson','kunshan-precipitation.json','mandara-teaching.json'])+"waterways=bundled_json('kunshan-waterways.geojson')\nrainfall=bundled_json('kunshan-precipitation.json')\nmandara=bundled_json('mandara-teaching.json')\n"+s[b:]
        if kind=='interaction' and i==11:
            s=s.replace('fields=["CP"], on="click", clear="dblclick"','fields=["CP"], value=[{"CP":"CP1"}], empty=False, on="click", clear="dblclick"')
            s=s.replace('color=alt.Color("value:Q", scale=alt.Scale(domain=[0,1], range=["#e5edef","#245c70"]), legend=None),','color=alt.Color("status:N", scale=alt.Scale(domain=["not asserted / 未作断言","smaller reported / 报告为次要","dominant reported / 报告为主要"], range=["#e5edef","#D97706","#245c70"]),legend=alt.Legend(title="Teaching assertion")),')
            s=s[:s.index('detail = alt.Chart')]+"detail=alt.Chart(cp).transform_filter(pick).mark_text(align='left').encode(y=alt.Y('group:N',title='Group / 分组'),text='status:N',tooltip=['group','sites','CP','status']).properties(width=760,height=110,title='Selected categorical assertion; not a count or probability')\nmatrix & detail\n"
        if kind=='interaction' and i in (13,15):s=s.replace('rangemode="tozero", fixedrange=False','range=[0,float(rain.mm_per_day.max())*1.05], fixedrange=False').replace('scale=alt.Scale(zero=True)','scale=alt.Scale(domain=[0,float(rain.mm_per_day.max())*1.05])')
        if kind=='color' and i==7:
            a=s.index('def make_palette(');b=s.index('def relative_luminance(');s=s[:a]+PALETTE+'\n'+s[b:]
            s=s.replace('value=.14','value=.16').replace('value=52','value=48').replace('max=11','max=9').replace('max=.24','max=.28').replace('description="Family / 类型")','description="Family / 类型",value="sequential")')
            at=s.index('palette_output =');s=s[:at]+"_imported_palette=None\n_state=Path('INFOSCI301_palette_state.json')\nif _state.exists():\n    _imported_palette=json.loads(_state.read_text());p=_imported_palette['parameters'];assert len(_imported_palette['colors'])==int(p['count'])\n    family.value=p['family'];steps.value=int(p['count']);base_hue.value=int(p['hue']);palette_chroma.value=float(p['chroma']);span.value=int(p['span'])\n"+s[at:]
        if kind=='color' and i==9:s=s.replace('cspace_convert(rgb,"sRGB1",{"name":"sRGB1+CVD","cvd_type":mode,"severity":100})','cspace_convert(rgb,{"name":"sRGB1+CVD","cvd_type":mode,"severity":100},"sRGB1")')
        if kind=='color' and i==16:
            at=s.index('semantic_names=');s=s[:at]+"if globals().get('_imported_palette') is not None:\n    p=_imported_palette['parameters']\n    if (family.value,steps.value,base_hue.value,palette_chroma.value,span.value)==(p['family'],p['count'],p['hue'],p['chroma'],p['span']):export_colors=_imported_palette['colors']\n"+s[at:]
        if i in OPTIONAL.get(kind,set()):
            label=NAMES[kind][i];s=f"# Optional package extension: {label}\nif RUN_PACKAGE_EXTENSIONS:\n    try:\n"+textwrap.indent(s,'        ')+f"\n        _extension_status[{label!r}]='completed'\n    except Exception as exc:\n        _extension_status[{label!r}]='unavailable: '+type(exc).__name__\n        print('Extension unavailable:',str(exc)[:240])\nelse:\n    _extension_status[{label!r}]='not run (optional)'\n    print({label!r},'not run; enable extensions and install its package to explore.')"
        put(c,s);c['outputs']=[];c['execution_count']=None
    out=[original[0],cell('markdown',INTRO,kind+'-route')]
    for i,c in enumerate(original[1:],2):
        if c['cell_type']=='code' and i!=3:out.append(cell('markdown',guide(NAMES[kind].get(i,'Source inspection and design reasoning')),f'{kind}-guide-{i:02d}'))
        out.append(c)
        if i==4 and kind in ('network','spatial'):
            title='App-matched paper–topic comparison' if kind=='network' else 'App-matched heritage map, timeline, and cube'
            code=embedded(['emerging-tech.json','provenance.json'] if kind=='network' else ['heritage.json','provenance.json'])+(NETWORK if kind=='network' else HERITAGE)
            out.extend([cell('markdown',guide(title,'Compare identical records across views.','Topic assignment is not citation; designation is not construction or cultural importance.'),kind+'-core-guide'),cell('code',code,kind+'-core-output')])
    if kind in ('interaction','color'):
        code=INTERACTION if kind=='interaction' else embedded(['kunshan-precipitation.json','mandara-teaching.json'])+COLOR
        block=[cell('markdown',guide('Saved counterparts on the same project evidence','Inspect exact records, fixed baselines, and static alternatives.','Precipitation does not measure water flow; qualitative assertions are not probabilities.'),kind+'-saved-guide'),cell('code',code,kind+'-saved-output')]
        at=next((i for i,c in enumerate(out) if c['cell_type']=='markdown' and src(c).startswith('## References')),len(out));out[at:at]=block
    export=f'''import json,platform,zipfile
from pathlib import Path
STUDENT_DESIGN={{'audience':'','question':'','human_decisions':[],'supported_reading':'','limitation':'','actual_peer_feedback':'','next_test':''}}
record={{'lesson':{kind!r},'student_design':STUDENT_DESIGN,'snapshot_hashes':globals().get('SNAPSHOT_HASHES',{{}}),'parameters':globals().get('NETWORK_PARAMETERS',globals().get('HERITAGE_PARAMETERS',globals().get('palette_parameters',{{}}))),'extensions':globals().get('_extension_status',{{}}),'python':platform.python_version()}}
Path('INFOSCI301_{kind}_design_record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
with zipfile.ZipFile('INFOSCI301_{kind}_design_bundle.zip','w',zipfile.ZIP_DEFLATED) as z:
    for folder in ('lesson_outputs','outputs'):
        if Path(folder).exists():
            for p in Path(folder).glob('*'):
                if p.is_file():z.write(p)
    for p in Path('.').glob('INFOSCI301_*'):
        if p.is_file() and p.suffix!='.zip':z.write(p)
print('Exported figures and your design record. Complete your own interpretation before sharing.')
'''
    out.extend([cell('markdown','## Export your design and evidence / 导出设计与证据\n\nEdit the empty fields below. Empty feedback means not collected; it is not instructor approval. Retain source records, original and revised outputs, and a next test.',kind+'-export-guide'),cell('code',export,kind+'-export')])
    n['cells']=out;n['metadata']['infosci301']={'revision':'2026-10-13','lesson':kind,'source_generation':'scripts/revise_notebooks.py','preview':'saved execution; widgets run in Colab'};path.write_text(json.dumps(n,ensure_ascii=False,indent=1)+'\n');print(path.name,len(out),'cells; original demonstrations preserved')
if __name__=='__main__':
    files={'interaction':'INFOSCI301_Interaction_Design_Companion.ipynb','color':'INFOSCI301_Color_Palette_Accessibility_Studio.ipynb'} if WATER else {'network':'INFOSCI301_Week4_Network_Studio_Colab.ipynb','spatial':'INFOSCI301_Week4_Spatiotemporal_Studio_Colab.ipynb'}
    for kind,name in files.items():revise(FOLDER/name,kind)

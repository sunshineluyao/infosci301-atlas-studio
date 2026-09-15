"""Append executed, self-contained Atlas Studio lessons; preserve original outputs."""
from pathlib import Path
import base64, gzip, json, sys
import nbformat as nbf
from nbconvert import HTMLExporter
ROOT = Path(__file__).resolve().parents[1]
import notebook_executor as runner
runner.TUTORIAL = ROOT / 'public/notebooks'

def embed(name):
    return base64.b64encode(gzip.compress((ROOT/'public/data'/name).read_bytes())).decode()

common = '''## Atlas Studio enhancement · four levels, four validation tests

**Domain → Data/Task → Idiom → Algorithm. Validation belongs at every level; it is not a fifth level.**

Keep the original package experiments below/above as optional depth. The new cells connect them to a real communication or community question. The self-contained snapshots are embedded, so downloading just this notebook is enough for the new data examples. No live API call is required.

| Level | Decision | Validation evidence | Project addition |
|---|---|---|---|
| Domain | Audience/community, need and task | Observation/interview; whose need is not established? | Refined shared research question |
| Data/Task | Unit, relationship, time, coverage | Source record checks; domain-informed abstraction review | Data dictionary and provenance |
| Idiom | Basic baseline + advanced view | Observed task comparison, errors, accessibility | Justified linked-view design |
| Algorithm | Transformation, parameters and computation | Tests, reproducibility, sensitivity | Working MVP and evidence record |

**Week 4 → Week 5 → Week 6 → Week 7:** individual evidence and Reflection 1 → proposal plus MVP → demonstration/user study/feedback/response (15%) → future-roadmap roundtable (5%) and Reflection 2. These 15% and 5% are the split of the existing 20% component, not extra grading weight.
'''

network = [nbf.v4.new_markdown_cell(common + '''
### Scientific communication of emerging technology

**Domain:** A museum educator wants to explain geospatial AI. What misunderstanding should the communication prevent? Ask an audience member; do not treat this hypothetical persona as validated need.

**Data/Task:** The new snapshot contains 60 OpenAlex results for “geospatial artificial intelligence,” filtered from 2019. Every link below means **provider-assigned topic**, not citation, causal claim or a verified NLP relation. Topic score is not our accuracy estimate.

Source: https://api.openalex.org/works?search=geospatial%20artificial%20intelligence&filter=from_publication_date:2019-01-01&per-page=60. Retrieved 2026-09-14. Metadata CC0; sample is not a systematic review.
'''),nbf.v4.new_code_cell(f'''import base64, gzip, json
import networkx as nx, pandas as pd, matplotlib.pyplot as plt
from IPython.display import display
emerging_papers = json.loads(gzip.decompress(base64.b64decode({embed('emerging-tech.json')!r})))
print('Real OpenAlex records:', len(emerging_papers))
display(pd.DataFrame([{{'id':p['id'], 'year':p['year'], 'title':p['title'], 'url':p['url']}} for p in emerging_papers]).head(5))
'''),nbf.v4.new_markdown_cell('''### Idiom comparison: count chart versus paper–topic graph

Keep the first 20 papers fixed. Compare the basic topic-count bar chart with a bipartite network. Ask a peer to identify a topic with several supporting papers, locate an original source, and explain what the graph cannot establish. Record errors and confidence; do not fill in fictional user-study results.
'''),nbf.v4.new_code_cell('''sample = emerging_papers[:20]
comm_graph = nx.Graph()
for p in sample:
    comm_graph.add_node(p['id'], kind='paper', label=p['title'])
    for t in p['topics']:
        comm_graph.add_node(t['id'], kind='topic', label=t['label'])
        comm_graph.add_edge(p['id'], t['id'], relation='classified under', source=p['url'])
topics = sorted((n for n,d in comm_graph.nodes(data=True) if d['kind']=='topic'), key=lambda n:comm_graph.degree(n), reverse=True)
fig, axes = plt.subplots(1,2, figsize=(15,7))
top = topics[:7]
axes[0].barh([comm_graph.nodes[n]['label'][:35] for n in top][::-1], [comm_graph.degree(n) for n in top][::-1], color='#0b8c86')
axes[0].set_title('Basic baseline: topic-assignment counts')
axes[0].set_xlabel('Direct connections in the fixed sample')
pos = nx.bipartite_layout(comm_graph, [p['id'] for p in sample])
nx.draw(comm_graph, pos, ax=axes[1], node_size=55, width=.6, alpha=.8, node_color=['#0b8c86' if d['kind']=='paper' else '#ce8440' for _,d in comm_graph.nodes(data=True)])
axes[1].set_title('Papers (cyan) ↔ topics (amber); edge = classification')
plt.tight_layout(); plt.show()
'''),nbf.v4.new_code_cell('''# Algorithm-level tests, not evidence of communication effectiveness.
rank = nx.pagerank(comm_graph, alpha=.85)
assert abs(sum(rank.values())-1) < 1e-8
assert sum(dict(comm_graph.degree()).values()) == 2*comm_graph.number_of_edges()
assert all(comm_graph.nodes[a]['kind'] != comm_graph.nodes[b]['kind'] for a,b in comm_graph.edges())
first_paper = sample[0]['id']
two_hop = nx.single_source_shortest_path_length(comm_graph, first_paper, cutoff=2)
print('Nodes:', comm_graph.number_of_nodes(), 'Edges:', comm_graph.number_of_edges())
print('Two-hop reachable nodes:', len(two_hop), '| Algorithm checks passed.')
'''),nbf.v4.new_markdown_cell('''### Innovation output: a source-grounded communication brief

1. Name the audience, decision and misconception.
2. Link one selected paper; distinguish its demonstrated finding from a hoped-for application.
3. State why the basic chart and the network are both needed.
4. For an NLP knowledge graph, attach source spans, extraction method, inferred/verified status and a human-check sample to every relation. Entity co-occurrence is not factual entailment.
5. Record a peer's actual interpretation and the change it prompted. Bring this brief and the data dictionary into the Week 5 MVP.
''')]

spatial=[nbf.v4.new_markdown_cell(common + '''
### Human-centered spatial–temporal intelligence for digital humanities

**Domain:** An archive or community heritage team wants to understand recognition over time and ask which stories are absent. Official data cannot answer community value, accessibility, consent or lived experience by itself.

**Data/Task:** 1,457 unique NYC individual-landmark designation IDs. Source had 2,065 building records; 74 missing/invalid coordinate/date records were excluded, then IDs deduplicated. We retain the first valid building coordinate and count of remaining building records. A designation date is **not** a construction date.

Source: https://data.cityofnewyork.us/Housing-Development/Designated-and-Calendared-Buildings-and-Sites/ncre-qhxs. Retrieved 2026-09-14. Public metadata under NYC Open Data terms; no photographs copied. These NYC data do not establish Jinxi community needs.
'''),nbf.v4.new_code_cell(f'''import base64, gzip, json
import pandas as pd, geopandas as gpd, matplotlib.pyplot as plt
from IPython.display import display
heritage_records = json.loads(gzip.decompress(base64.b64decode({embed('heritage.json')!r})))
heritage_df = pd.DataFrame(heritage_records)
heritage_df['date'] = pd.to_datetime(heritage_df['date'], errors='raise')
assert heritage_df['id'].is_unique
assert heritage_df.lon.between(-180,180).all() and heritage_df.lat.between(-90,90).all()
heritage_geo = gpd.GeoDataFrame(heritage_df, geometry=gpd.points_from_xy(heritage_df.lon,heritage_df.lat), crs='EPSG:4326')
print(len(heritage_geo), 'unique designation IDs; coordinate system:', heritage_geo.crs)
display(heritage_df[['title','group','date','buildingRecords','url']].head(5))
'''),nbf.v4.new_code_cell('''# A linked basic timeline and spatial view: all retained records, same unit.
fig, axes = plt.subplots(1,2, figsize=(14,6))
heritage_df.groupby('year').size().plot(ax=axes[0], color='#0b8c86')
axes[0].set_title('Basic baseline: designation IDs by year')
axes[0].set_ylabel('Count of retained designation IDs')
heritage_geo.plot(ax=axes[1], column='group', markersize=7, legend=True, cmap='tab10')
axes[1].set_title('Advanced idiom: place linked to designation time')
axes[1].set_xlabel('Longitude'); axes[1].set_ylabel('Latitude')
plt.tight_layout(); plt.show()
'''),nbf.v4.new_code_cell('''# Configurable temporal comparison; this is not a community-impact test.
start_year, end_year, selected_borough = 1965, 1980, 'Brooklyn'
chosen = heritage_geo[heritage_geo.year.between(start_year,end_year) & (heritage_geo.group==selected_borough)]
assert len(chosen) <= len(heritage_geo)
assert chosen.year.between(start_year,end_year).all()
print('Filtered records:', len(chosen), '|', selected_borough, start_year, 'through', end_year)
display(chosen[['title','date','url']].head(8))
# If you calculate distance or area, select a suitable projected CRS first.
# Counts on this map do not establish preservation quality or cultural worth.
'''),nbf.v4.new_markdown_cell('''### Transfer to fieldwork and human-centered GeoAI

- Before Jinxi fieldwork: define one observable question, one inference to avoid, whose permission is required, and which details must not be published.
- After fieldwork: separate observed evidence, interpretation and a question still requiring community input. Do not infer consent from a public location.
- Explain what a basic timeline, a relationship network and a place/time view each add to the same group question.
- Test a 2D map/timeline against the optional 3D space–time cube. Height means year—not importance. Record actual task success and misreadings.
- Advanced frontier: NASA Prithvi, Earth Engine, IEEE GRSS SAR temporal storytelling, Cesium or OpenDroneMap. Choose one only if the research question requires it; verify access, data rights, ground truth, generalization and human oversight. None is evidence that the browser app performs AI inference.
- Week 6: log demonstration, peer feedback and responses. Week 7: propose one next model/data/user validation that could change the result; distinguish completed work from the roadmap.
''')]

for kind,extra in [('Network',network),('Spatiotemporal',spatial)]:
    path=ROOT/'public/notebooks'/f'INFOSCI301_Week4_{kind}_Studio_Colab.ipynb'
    original=nbf.read(path,as_version=4)
    # Idempotent append on reruns.
    cut=next((i for i,c in enumerate(original.cells) if c.cell_type=='markdown' and c.source.startswith('## Atlas Studio enhancement')),len(original.cells))
    original.cells=original.cells[:cut]
    for c in original.cells:
        if c.cell_type=='markdown':
            c.source=c.source.replace('Domain -> Data and Task -> Idiom -> Algorithm -> Validate','Domain -> Data and Task -> Idiom -> Algorithm (validate each level)')
    block=nbf.v4.new_notebook(cells=extra)
    runner.InProcessNotebookExecutor(block).execute()
    original.cells.extend(block.cells)
    nbf.write(original,path)
    exporter=HTMLExporter(); exporter.template_name='lab'
    body,_=exporter.from_notebook_node(original)
    path.with_name(path.stem.replace('_Colab','_Executed')+'.html').write_text(body)
    print(kind, 'new code cells executed:',sum(c.cell_type=='code' for c in block.cells))

import fs from 'node:fs';
import path from 'node:path';
const root=process.cwd();
const out=path.join(root,'public/data');
fs.mkdirSync(out,{recursive:true});
const save=(name,data)=>fs.writeFileSync(path.join(out,name),JSON.stringify(data,null,2));
const raw=JSON.parse(fs.readFileSync(path.join(root,'source_data/openalex_emerging.json')));
const papers=raw.results.map(w=>({id:w.id.split('/').at(-1),title:w.title,year:w.publication_year,url:w.doi||w.id,citations:w.cited_by_count,
  topics:(w.topics||[]).slice(0,3).map(t=>({id:t.id.split('/').at(-1),label:t.display_name,score:t.score})),
  keywords:(w.keywords||[]).slice(0,6).map(t=>t.display_name),
  authors:(w.authorships||[]).slice(0,3).map(a=>a.author.display_name)}));
save('emerging-tech.json',papers);
const landmarks=JSON.parse(fs.readFileSync(path.join(root,'source_data/nyc_landmarks.json')));
const grouped=new Map(); let invalid=0;
for(const r of landmarks){
  const lon=Number(r.longitude),lat=Number(r.latitude),bits=(r.desdate||'').split('/');
  if(!Number.isFinite(lon)||!Number.isFinite(lat)||!r.longitude||!r.latitude||bits.length!==3){invalid++;continue;}
  const id=r.lp_number;
  if(grouped.has(id)){grouped.get(id).buildingRecords++;continue;}
  grouped.set(id,{id,title:r.lm_name,group:({MN:'Manhattan',BK:'Brooklyn',BX:'Bronx',QN:'Queens',SI:'Staten Island'})[r.boroughid]||r.boroughid,
    date:`${bits[2]}-${bits[0].padStart(2,'0')}-${bits[1].padStart(2,'0')}`,year:Number(bits[2]),lon,lat,buildingRecords:1,
    url:'https://data.cityofnewyork.us/resource/ncre-qhxs.json?lp_number='+encodeURIComponent(id)});
}
save('heritage.json',[...grouped.values()]);
const eonet=JSON.parse(fs.readFileSync(path.join(root,'public/notebooks/data/nasa_eonet_events.json')));
save('earth-events.json',eonet.map((r,i)=>({id:r.event_id+'-'+i,eventId:r.event_id,title:r.title,group:r.category,date:r.date.slice(0,10),year:Number(r.date.slice(0,4)),lon:r.longitude,lat:r.latitude,url:r.event_url})));
fs.copyFileSync(path.join(root,'node_modules/world-atlas/countries-110m.json'),path.join(out,'world.json'));
save('provenance.json',{
  snapshotDate:'2026-09-14',
  emergingTech:{provider:'OpenAlex',url:'https://api.openalex.org/works?search=geospatial%20artificial%20intelligence&filter=from_publication_date:2019-01-01&per-page=60',
    records:papers.length,population:'First 60 API search results, not a systematic review; retrieval order retained.',unit:'Publication',
    transform:'Up to three provider-assigned topics per paper; bipartite paper-topic edges are classifications, not citations or verified NLP triples.',
    license:'OpenAlex metadata is CC0. See https://docs.openalex.org/additional-help/faq'},
  heritage:{provider:'NYC Landmarks Preservation Commission / NYC Open Data',url:'https://data.cityofnewyork.us/Housing-Development/Designated-and-Calendared-Buildings-and-Sites/ncre-qhxs',
    query:"https://data.cityofnewyork.us/resource/ncre-qhxs.json?$where=status=%27DESIGNATED%27%20AND%20lm_type=%27Individual%20Landmark%27&$limit=5000&$order=lp_number,bin_number&$select=lp_number,lm_name,boroughid,desdate,latitude,longitude,bin_number",
    inputBuildingRecords:landmarks.length,invalidDropped:invalid,records:grouped.size,unit:'Individual-landmark designation ID',
    transform:'Filter DESIGNATED + Individual Landmark. Deduplicate lp_number; first valid building coordinate retained; retain buildingRecords count. Designation date is not construction date or community value.',
    license:'Public NYC Open Data metadata; governed by NYC Open Data Terms of Use, not a blanket CC0 claim. No photographs copied.',
    boundary:'Administrative designations reflect institutional selection, not the full universe of cultural heritage. NYC observations do not establish Jinxi community needs.'},
  earth:{provider:'NASA EONET v3',records:eonet.length,unit:'Dated event geometry, not unique event or people affected',url:'https://eonet.gsfc.nasa.gov/docs/v3',
    transform:'Reuse documented closed-event category snapshots from the Week 4 notebook; not a complete hazard census.',
    boundary:'Source coverage and event definition vary; absence is not safety and point count is not impact.'},
  world:{provider:'Natural Earth via world-atlas',url:'https://github.com/topojson/world-atlas',license:'Natural Earth public domain; simplified cartography for context, not boundary adjudication.'}
});
console.log({papers:papers.length,landmarks:grouped.size,rawLandmarks:landmarks.length,invalid,earth:eonet.length});

export function buildGraph(papers,maxPapers=30,minYear=2019,search=''){
  const chosen=papers.filter(p=>p.year>=minYear&&`${p.title} ${p.topics.map(t=>t.label).join(' ')}`.toLowerCase().includes(search.toLowerCase())).slice(0,maxPapers);
  const nodes=chosen.map(p=>({...p,type:'paper',label:p.title})),links=[],topics=new Map();
  for(const p of chosen)for(const t of p.topics){topics.set(t.id,{...t,type:'topic',title:t.label});links.push({source:p.id,target:t.id,relation:'classified under',confidence:t.score});}
  nodes.push(...topics.values());
  const metrics=centralities(nodes,links);
  return {nodes:nodes.map(n=>({...n,degree:metrics.degree[n.id],pagerank:metrics.pagerank[n.id]})),links,paperCount:chosen.length};
}
export function centralities(nodes,links){
  const degree=Object.fromEntries(nodes.map(n=>[n.id,0]));
  const adjacency=Object.fromEntries(nodes.map(n=>[n.id,[]]));
  links.forEach(e=>{const a=typeof e.source==='object'?e.source.id:e.source,b=typeof e.target==='object'?e.target.id:e.target;if(adjacency[a]&&adjacency[b]){adjacency[a].push(b);adjacency[b].push(a);degree[a]++;degree[b]++;}});
  const N=nodes.length;if(!N)return {degree,pagerank:{}};
  let rank=Object.fromEntries(nodes.map(n=>[n.id,1/N]));
  for(let k=0;k<80;k++){
    const dangling=nodes.filter(n=>!degree[n.id]).reduce((s,n)=>s+rank[n.id],0);
    rank=Object.fromEntries(nodes.map(n=>[n.id,(1-.85)/N+.85*(dangling/N+adjacency[n.id].reduce((s,id)=>s+rank[id]/degree[id],0))]));
  }
  return {degree,pagerank:rank};
}
export function neighborsWithin(graph,start,depth=1){
  const seen=new Set(start?[start]:[]);let front=[...seen];
  for(let k=0;k<depth;k++){const next=[];for(const v of front)for(const e of graph.links){const a=e.source.id||e.source,b=e.target.id||e.target;const n=a===v?b:b===v?a:null;if(n&&!seen.has(n)){seen.add(n);next.push(n);}}front=next;}
  return seen;
}
export function filterPlaces(data,{from=-Infinity,to=Infinity,group='All',search=''}={}){
  return data.filter(d=>d.year>=from&&d.year<=to&&(group==='All'||d.group===group)&&`${d.title} ${d.group}`.toLowerCase().includes(search.toLowerCase()));
}
export function countBy(rows,key){return [...rows.reduce((m,r)=>m.set(r[key],(m.get(r[key])||0)+1),new Map())].sort((a,b)=>a[0]<b[0]?-1:1);}
export function safeUrl(url){try{const u=new URL(url);return ['http:','https:'].includes(u.protocol)?u.href:'';}catch{return '';}}
export function validateConfig(input){
  const keys=['courseTitle','semester','instructor','defaultStudio','defaultTheme','enable3D','maxVisiblePapers','allowLocalData','githubRepo','githubBranch','notebookPath','spaceUrl','vercelUrl'];
  const out={};for(const k of keys)if(k in input)out[k]=input[k];
  for(const k of ['courseTitle','semester','instructor','defaultStudio','defaultTheme','githubRepo','githubBranch','notebookPath','spaceUrl','vercelUrl'])if(k in out&&(typeof out[k]!=='string'||out[k].length>500))throw Error(k+' must be a string of at most 500 characters.');
  if(out.defaultStudio&&!['network','spatial'].includes(out.defaultStudio))throw Error('defaultStudio must be network or spatial.');
  if(out.defaultTheme&&!['light','dark'].includes(out.defaultTheme))throw Error('defaultTheme must be light or dark.');
  for(const k of ['enable3D','allowLocalData'])if(k in out&&typeof out[k]!=='boolean')throw Error(k+' must be true or false.');
  if('maxVisiblePapers'in out&&(!Number.isInteger(out.maxVisiblePapers)||out.maxVisiblePapers<5||out.maxVisiblePapers>60))throw Error('maxVisiblePapers must be an integer from 5 to 60.');
  for(const k of ['spaceUrl','vercelUrl'])if(out[k]&&!safeUrl(out[k]))throw Error(k+' must be an http(s) URL.');
  if(out.githubRepo&&!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(out.githubRepo))throw Error('githubRepo must be owner/repository (no URL).');
  return out;
}
export function validateLocalPlaces(input){
  if(!Array.isArray(input)||input.length===0||input.length>5000)throw Error('Use a JSON array with 1 to 5,000 records.');
  const ids=new Set();return input.map((r,i)=>{
    const lon=Number(r.lon),lat=Number(r.lat),id=String(r.id||'local-'+i),date=String(r.date||'');
    if(r.lon===null||r.lat===null||r.lon===''||r.lat===''||!Number.isFinite(lon)||!Number.isFinite(lat)||lon<-180||lon>180||lat<-90||lat>90||!/^\d{4}-\d{2}-\d{2}$/.test(date)||Number.isNaN(Date.parse(date))||new Date(date).toISOString().slice(0,10)!==date)throw Error('Row '+(i+1)+': valid lon, lat and YYYY-MM-DD date required.');
    if(ids.has(id))throw Error('Duplicate id: '+id);ids.add(id);
    return {id,title:String(r.title||id),group:String(r.group||'Local'),lon,lat,date,year:Number(date.slice(0,4)),url:safeUrl(r.url||'')};
  });
}

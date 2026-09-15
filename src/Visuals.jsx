import React,{useMemo,useState} from 'react';
import * as d3 from 'd3';
import {feature} from 'topojson-client';
import {neighborsWithin,countBy} from './engine.js';
export const COLORS=['#0b8c86','#ce8440','#6873c7','#b65773','#368bc5','#657d44','#845bb1','#a66f40'];
export function layoutGraph(graph,layout='force',width=900,height=480){
  const nodes=graph.nodes.map(n=>({...n})),links=graph.links.map(e=>({...e}));
  if(layout==='force'){
    d3.forceSimulation(nodes).randomSource(d3.randomLcg(.42)).force('link',d3.forceLink(links).id(d=>d.id).distance(75)).force('charge',d3.forceManyBody().strength(-115)).force('center',d3.forceCenter(width/2,height/2)).force('collide',d3.forceCollide(12)).stop().tick(180);
    const mx=Math.min(115,width*.128),my=Math.min(55,height*.115),xs=d3.extent(nodes,d=>d.x),ys=d3.extent(nodes,d=>d.y),sx=d3.scaleLinear().domain(xs).range([mx,width-mx]),sy=d3.scaleLinear().domain(ys).range([my,height-my]);
    nodes.forEach(n=>{n.x=sx(n.x);n.y=sy(n.y);});
  }else if(layout==='bipartite'){
    const left=nodes.filter(n=>n.type==='paper'),right=nodes.filter(n=>n.type==='topic');
    [left,right].forEach((arr,k)=>arr.forEach((n,i)=>{n.x=k?width*.76:width*.24;n.y=35+(height-70)*(i+.5)/arr.length;}));
  }else nodes.forEach((n,i)=>{n.x=width/2+Math.cos(i/nodes.length*2*Math.PI)*Math.min(width,height)*.40;n.y=height/2+Math.sin(i/nodes.length*2*Math.PI)*Math.min(width,height)*.40;});
  const map=new Map(nodes.map(n=>[n.id,n]));
  return {nodes,links:links.map(e=>({...e,source:map.get(e.source.id||e.source),target:map.get(e.target.id||e.target)}))};
}
export function NetworkView({graph,layout,metric,selected,onSelect,depth,labels}){
  const [zoom,setZoom]=useState(1);
  const pos=useMemo(()=>layoutGraph(graph,layout),[graph,layout]);
  const highlighted=useMemo(()=>neighborsWithin(graph,selected?.id,depth),[graph,selected?.id,depth]);
  const max=d3.max(graph.nodes,n=>n[metric])||1;
  const labelPositions=useMemo(()=>{
    const placed=new Map(),boxes=[];
    const eligible=pos.nodes.filter(n=>n.id===selected?.id||labels&&(n.type==='topic'&&n.degree>=3||graph.paperCount<=10)).sort((a,b)=>(b.id===selected?.id?1:0)-(a.id===selected?.id?1:0)||b.degree-a.degree);
    const overlap=(a,b)=>a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y;
    for(const n of eligible){const text=n.label.length>32?n.label.slice(0,30)+'…':n.label,w=text.length*6.6;
      const candidates=[[0,-28],[0,34],[w/2+20,4],[-w/2-20,4],[0,-49],[0,55],[w/2+20,-23],[-w/2-20,28]];
      for(const [dx,dy] of candidates){const x=n.x+dx,y=n.y+dy,box={x:x-w/2-3,y:y-13,w:w+6,h:18};
        if(box.x<10||box.x+box.w>890||box.y<6||box.y+box.h>470||boxes.some(b=>overlap(box,b))||pos.nodes.some(other=>overlap(box,{x:other.x-16,y:other.y-16,w:32,h:32})))continue;
        placed.set(n.id,{x:dx,y:dy,text});boxes.push(box);break;
      }
    }
    return placed;
  },[pos,labels,selected?.id,graph.paperCount]);
  const matrix=layout==='matrix',size=370,n=graph.nodes.length,cell=size/Math.max(1,n),idx=new Map(graph.nodes.map((n,i)=>[n.id,i]));
  return <div className="chart-wrap"><svg viewBox="0 0 900 480" role="img" aria-label="Interactive paper-topic graph. Equivalent selectable records are available in the data table.">
    <defs><pattern id="netgrid" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="currentColor" opacity=".12"/></pattern></defs>
    <rect width="900" height="480" fill="url(#netgrid)"/>
    {!n?<text x="450" y="240" textAnchor="middle" className="svg-label">No matching papers. Broaden your filters.</text>:matrix?<g transform="translate(265,35)">
      {graph.nodes.map((node,i)=><g key={node.id}><text className="svg-label" x="-8" y={i*cell+cell*.8} textAnchor="end" fontSize={Math.min(12,cell*.9)}>{node.id}</text><line x1="0" x2={size} y1={i*cell} y2={i*cell} stroke="currentColor" opacity=".09"/></g>)}
      {graph.links.flatMap((e,i)=>[[e.source,e.target],[e.target,e.source]].map(([a,b],j)=><rect key={i+'-'+j} x={idx.get(a)*cell} y={idx.get(b)*cell} width={cell*.95} height={cell*.95} fill="#0b8c86" onClick={()=>onSelect(graph.nodes[idx.get(a)])}><title>{`${a} ↔ ${b}: classified under`}</title></rect>))}
      <text x={size/2} y={size+30} textAnchor="middle" className="svg-label">Same node order on both axes · cell = connection</text>
    </g>:<g transform={`translate(${450*(1-zoom)},${240*(1-zoom)}) scale(${zoom})`}>
      {pos.links.map((e,i)=><line key={i} x1={e.source.x} y1={e.source.y} x2={e.target.x} y2={e.target.y} stroke="#7895a5" strokeWidth={highlighted.has(e.source.id)&&highlighted.has(e.target.id)?2:1} opacity={!selected||highlighted.has(e.source.id)&&highlighted.has(e.target.id)?.45:.07}/>)}
      {pos.nodes.map(node=><g key={node.id} transform={`translate(${node.x},${node.y})`} role="button" tabIndex="0" aria-label={`${node.type}: ${node.label}. Degree ${node.degree}.`} onClick={()=>onSelect(node)} onKeyDown={e=>{if(['Enter',' '].includes(e.key)){e.preventDefault();onSelect(node);}}} className="node" opacity={!selected||highlighted.has(node.id)?1:.2}>
        {selected?.id===node.id&&<circle r="22" fill="none" stroke="#d4a151" strokeWidth="2"/>}
        {node.type==='topic'?<rect x={-5-9*Math.sqrt(node[metric]/max)} y={-5-9*Math.sqrt(node[metric]/max)} width={10+18*Math.sqrt(node[metric]/max)} height={10+18*Math.sqrt(node[metric]/max)} rx="4" fill="#d19a4e" stroke="var(--panel)" strokeWidth="2"/>:<circle r={5+9*Math.sqrt(node[metric]/max)} fill="#0b9e96" stroke="var(--panel)" strokeWidth="2"/>}
        <title>{`${node.label}\n${node.type} · degree ${node.degree} · PageRank ${node.pagerank.toFixed(4)}`}</title>
        {labelPositions.has(node.id)&&<text x={labelPositions.get(node.id).x} y={labelPositions.get(node.id).y} textAnchor="middle" className="svg-label" fontSize="11">{labelPositions.get(node.id).text}</text>}
      </g>)}
    </g>}
  </svg><div className="chart-legend"><span><i className="dot teal"/> Paper</span><span><i className="square gold"/> Topic</span><span>Size: {metric==='degree'?'degree':'PageRank'} · position: {layout}, not geography</span></div>{!matrix&&<div className="zoom"><button onClick={()=>setZoom(Math.min(2,zoom+.2))} aria-label="Zoom network in">+</button><button onClick={()=>setZoom(Math.max(.6,zoom-.2))} aria-label="Zoom network out">−</button><button onClick={()=>{setZoom(1);onSelect(null);}}>Reset view</button></div>}</div>;
}
export function SpatialView({allData,rows,world,dataset,projection,encoding,selected,onSelect}){
  const [zoom,setZoom]=useState(1);
  const {proj,path}=useMemo(()=>{
    const p=projection==='equalEarth'||allData.some(r=>Math.abs(r.lat)>85)?d3.geoEqualEarth():d3.geoMercator();
    const geo={type:'FeatureCollection',features:allData.map(r=>({type:'Feature',geometry:{type:'Point',coordinates:[r.lon,r.lat]}}))};
    if(dataset==='earth')p.fitExtent([[20,20],[880,445]],{type:'Sphere'});else if(allData.length&&new Set(allData.map(r=>r.lon+','+r.lat)).size===1)p.center([allData[0].lon,allData[0].lat]).scale(350).translate([450,240]);else if(allData.length)p.fitExtent([[75,45],[825,430]],geo);
    return {proj:p,path:d3.geoPath(p)};
  },[allData,dataset,projection]);
  const groups=[...new Set(allData.map(r=>r.group))].sort(),color=g=>COLORS[groups.indexOf(g)%COLORS.length];
  const bins=new Map();rows.forEach(r=>{const p=proj([r.lon,r.lat]);if(!p)return;const key=Math.floor(p[0]/18)+','+Math.floor(p[1]/18);if(!bins.has(key))bins.set(key,{x:Math.floor(p[0]/18)*18,y:Math.floor(p[1]/18)*18,rows:[]});bins.get(key).rows.push(r);});
  const max=Math.max(1,...[...bins.values()].map(b=>b.rows.length));
  return <div className="chart-wrap"><svg viewBox="0 0 900 480" role="img" aria-label="Interactive place and time map. Use year controls and the equivalent records table.">
    <g transform={`translate(${450*(1-zoom)},${240*(1-zoom)}) scale(${zoom})`}>
      {dataset==='earth'&&world&&<path d={path(feature(world,world.objects.countries))} fill="var(--land)" stroke="var(--line)" strokeWidth=".65"/>}
      {dataset==='earth'?<path d={path(d3.geoGraticule10())} fill="none" stroke="var(--line)" opacity=".5"/>:<>
        {d3.ticks(d3.min(allData,d=>d.lon)||-74.2,d3.max(allData,d=>d.lon)||-73.7,6).map(v=>{const x=proj([v,allData[0]?.lat||40.7])[0];return <g key={v}><line x1={x} x2={x} y1="20" y2="442" stroke="var(--line)"/><text x={x} y="464" textAnchor="middle" className="svg-label" fontSize="11">{v.toFixed(2)}°</text></g>;})}
        {d3.ticks(d3.min(allData,d=>d.lat)||40.5,d3.max(allData,d=>d.lat)||40.9,5).map(v=>{const y=proj([allData[0]?.lon||-74,v])[1];return <g key={v}><line x1="45" x2="865" y1={y} y2={y} stroke="var(--line)"/><text x="42" y={y-5} className="svg-label" fontSize="11">{v.toFixed(2)}°</text></g>;})}
      </>}
      {encoding==='grid'?[...bins.values()].map((b,i)=><rect key={i} x={b.x} y={b.y} width="17" height="17" fill="#0b9e96" opacity={.18+.82*Math.sqrt(b.rows.length/max)} onClick={()=>onSelect(b.rows[0])}><title>{`${b.rows.length} records in this screen cell. Select to inspect the first record.`}</title></rect>):rows.map(r=>{const p=proj([r.lon,r.lat]);return p&&<circle key={r.id} cx={p[0]} cy={p[1]} r={selected?.id===r.id?8:dataset==='earth'?4.5:3.8} fill={color(r.group)} opacity={selected&&selected.id!==r.id?.35:.76} stroke={selected?.id===r.id?'var(--ink)':'var(--panel)'} strokeWidth={selected?.id===r.id?2:.5} onClick={()=>onSelect(r)}><title>{`${r.title} · ${r.date} · ${r.group}`}</title></circle>;})}
      {selected&&<g transform={`translate(${proj([selected.lon,selected.lat])})`}><circle r="13" fill="none" stroke="var(--ink)" strokeWidth="1.5"/></g>}
    </g>
  </svg><div className="chart-legend">{groups.slice(0,8).map(g=><span key={g}><i className="dot" style={{background:color(g)}}/>{g}</span>)}</div><div className="zoom"><button onClick={()=>setZoom(Math.min(3,zoom+.3))} aria-label="Zoom map in">+</button><button onClick={()=>setZoom(Math.max(.7,zoom-.3))} aria-label="Zoom map out">−</button><button onClick={()=>{setZoom(1);onSelect(null);}}>Reset view</button></div><p className="micro chart-note">{dataset==='earth'?'Global context; simplified Natural Earth boundaries.':'Longitude / latitude grid; no basemap tiles or personal location data.'} {encoding==='grid'?'Darker = more records per screen cell; NOT equal-area density.':''}</p></div>;
}
export function BarSummary({rows,network,onChoose}){
  const values=network?rows.nodes.filter(n=>n.type==='topic').sort((a,b)=>b.degree-a.degree).slice(0,5).map(n=>[n.label,n.degree,n]):countBy(rows,'year');
  const max=Math.max(1,...values.map(v=>v[1]));
  return <div className="summary-chart"><h3>{network?'Basic baseline · topic counts':'Basic baseline · timeline'}</h3><p className="micro">{network?'Direct links in the current sample; not scientific impact.':'Filtered record counts by year; not community importance.'}</p>{network?<div className="barlist">{values.map(([label,value,node])=><button key={label} onClick={()=>onChoose(node)} className="barrow"><span>{label}</span><i style={{width:Math.max(3,value/max*100)+'%'}}/><b>{value}</b></button>)}</div>:<svg viewBox="0 0 620 120" role="img" aria-label="Counts per year for the filtered data">{values.map(([year,value],i)=><g key={year}><rect x={i/values.length*600+10} y={95-value/max*80} width={Math.max(2,600/values.length-2)} height={value/max*80} fill="#0b9e96"><title>{`${year}: ${value} records`}</title></rect>{(i===0||i===values.length-1||values.length<8)&&<text x={i/values.length*600+10} y="115" className="svg-label" fontSize="12">{year}</text>}</g>)}</svg>}</div>;
}

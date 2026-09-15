// Pure data-to-position model, also tested without WebGL.
export function spatialModel(rows,reference=rows){
  const extent=key=>reference.length?[Math.min(...reference.map(r=>r[key])),Math.max(...reference.map(r=>r[key]))]:[0,1];
  const longitude=extent('lon'),latitude=extent('lat'),year=extent('year');
  const scale=(v,[a,b],span,center=true)=>b===a?0:(v-a)/(b-a)*span-(center?span/2:0);
  return {longitude,latitude,year,positions:rows.map(d=>[scale(d.lon,longitude,320),12+scale(d.year,year,200,false),-scale(d.lat,latitude,290)])};
}

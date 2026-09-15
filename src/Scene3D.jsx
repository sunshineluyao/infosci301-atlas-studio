import React,{useEffect,useRef,useState} from 'react';
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {layoutGraph,COLORS} from './Visuals.jsx';
import {spatialModel} from './sceneModel.js';
export default function Scene3D({graph,rows,allRows,network,onSelect,onFallback,resetKey}){
  const host=useRef(null),[status,setStatus]=useState('Preparing 3D view…');
  useEffect(()=>{
    const el=host.current;let renderer,controls,observer,cleanup=()=>{};
    try{
      renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(window.devicePixelRatio,1.6));renderer.setClearColor('#0b1423');
      el.appendChild(renderer.domElement);renderer.domElement.setAttribute('aria-label','3D data scene. Drag to orbit, scroll to zoom. Use the data table for keyboard selection.');renderer.domElement.setAttribute('role','img');
      const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(44,1,.1,2500);camera.position.set(300,250,390);
      controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,60,0);controls.enableDamping=false;controls.minDistance=80;controls.maxDistance=1100;
      const ambient=new THREE.AmbientLight(0xffffff,2.5),light=new THREE.DirectionalLight(0xa2d9ff,3);light.position.set(80,160,100);scene.add(ambient,light);
      const grid=new THREE.GridHelper(380,20,0x54728b,0x243449);scene.add(grid);
      const axes=new THREE.AxesHelper(190);scene.add(axes);
      let data,positions,timeRange='';
      if(network){const p=layoutGraph(graph,'force',340,300);data=p.nodes;const year0=Math.min(...data.filter(n=>n.year).map(n=>n.year),2019);positions=data.map(n=>new THREE.Vector3(n.x-170,n.type==='paper'?25+(n.year-year0)*22:12,n.y-150));
        const map=new Map(data.map((d,i)=>[d.id,positions[i]])),coords=[];p.links.forEach(e=>{coords.push(...map.get(e.source.id).toArray(),...map.get(e.target.id).toArray());});
        const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(coords,3));scene.add(new THREE.LineSegments(geometry,new THREE.LineBasicMaterial({color:0x5c8996,transparent:true,opacity:.38})));
      }else{
        data=rows;const model=spatialModel(data,allRows);positions=model.positions.map(p=>new THREE.Vector3(...p));timeRange=`Fixed year axis: ${model.year[0]}–${model.year[1]}`;
        const stems=[];positions.forEach(p=>stems.push(p.x,0,p.z,p.x,p.y,p.z));const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(stems,3));scene.add(new THREE.LineSegments(geometry,new THREE.LineBasicMaterial({color:0x337d80,transparent:true,opacity:.10})));
      }
      const geometry=new THREE.SphereGeometry(network?4.5:2,12,8),material=new THREE.MeshStandardMaterial({roughness:.32,metalness:.15});
      const mesh=new THREE.InstancedMesh(geometry,material,data.length),dummy=new THREE.Object3D(),groups=[...new Set(data.map(d=>d.group))].sort();
      data.forEach((d,i)=>{dummy.position.copy(positions[i]);dummy.scale.setScalar(network?Math.sqrt(1+(d.degree||0)*.12):1);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);mesh.setColorAt(i,new THREE.Color(network?(d.type==='paper'?'#22b9b1':'#f1b564'):COLORS[groups.indexOf(d.group)%COLORS.length]));});scene.add(mesh);
      function label(text,position){const c=document.createElement('canvas');c.width=512;c.height=64;const ctx=c.getContext('2d');ctx.font='28px system-ui';ctx.fillStyle='#c9dde8';ctx.fillText(text,6,40);const tex=new THREE.CanvasTexture(c),mat=new THREE.SpriteMaterial({map:tex,transparent:true});const sprite=new THREE.Sprite(mat);sprite.position.copy(position);sprite.scale.set(130,16,1);scene.add(sprite);}
      label(network?'X/Z: graph layout':'X: longitude →',new THREE.Vector3(120,0,205));label(network?'Y: publication year ↑':'Y: year ↑',new THREE.Vector3(-200,245,0));label(network?'topics at base plane':'Z: latitude (north is −Z)',new THREE.Vector3(-130,0,-195));
      if(!network){const years=spatialModel(data,allRows).year;label(String(years[0]),new THREE.Vector3(-195,12,0));label(String(years[1]),new THREE.Vector3(-195,212,0));}
      const render=()=>renderer.render(scene,camera);const resize=()=>{renderer.setSize(el.clientWidth,480);camera.aspect=el.clientWidth/480;camera.updateProjectionMatrix();render();};observer=new ResizeObserver(resize);observer.observe(el);controls.addEventListener('change',render);resize();
      let down=null;const pointerDown=e=>{down=[e.clientX,e.clientY];};
      const pick=e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;const rect=renderer.domElement.getBoundingClientRect(),pointer=new THREE.Vector2((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1),ray=new THREE.Raycaster();ray.setFromCamera(pointer,camera);const hit=ray.intersectObject(mesh)[0];if(hit&&hit.instanceId!==undefined)onSelect(data[hit.instanceId]);};
      renderer.domElement.addEventListener('pointerdown',pointerDown);renderer.domElement.addEventListener('pointerup',pick);
      setStatus(`${data.length} selectable ${network?'nodes':'records'} · ${timeRange} · drag to orbit · scroll to zoom`);
      cleanup=()=>{renderer.domElement.removeEventListener('pointerdown',pointerDown);renderer.domElement.removeEventListener('pointerup',pick);scene.traverse(o=>{o.geometry?.dispose();if(o.material){for(const m of Array.isArray(o.material)?o.material:[o.material]){m.map?.dispose();m.dispose();}}});};
    }catch(error){setStatus('3D is unavailable on this browser. The 2D view and record table preserve the lesson.');console.warn('WebGL unavailable',error);}
    return()=>{observer?.disconnect();controls?.dispose();cleanup();renderer?.dispose();el.replaceChildren();};
  },[graph,rows,allRows,network,resetKey]);
  return <div className="scene"><div ref={host} className="scene-host"/><div className="scene-caption"><span>{status}</span><button onClick={onFallback}>Use 2D alternative</button></div><div className="scene-key">{network?'Cyan: papers · Gold: topics · Height: publication year; topics on base plane.':'Height: year · X/Z: longitude/latitude, independently normalized—not metric distance.'} No animation autoplay. Selection details appear below.</div></div>;
}

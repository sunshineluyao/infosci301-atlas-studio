import {readFileSync,writeFileSync,mkdirSync} from 'node:fs'
import {dirname} from 'node:path'
import {gunzipSync,inflateRawSync} from 'node:zlib'
import {createHash} from 'node:crypto'
const files=JSON.parse(readFileSync('public/notebooks/packed.json','utf8'))
const hash=raw=>createHash('sha256').update(raw).digest('hex')
function normalizeIds(base,replacements={}){
 const keys=Object.keys(replacements);if(!keys.length)return base
 if(keys.some(key=>!/^([mp][0-9a-f]{10})$/.test(key)||!/^([mp][0-9a-f]{10})$/.test(replacements[key])))throw new Error('Invalid SVG identifier patch')
 return Buffer.from(base.toString('utf8').replace(new RegExp(keys.join('|'),'g'),key=>replacements[key]))
}
function applyPatch(base,operations){
 return Buffer.concat(operations.map(op=>{
  if(op.copy){const [start,length]=op.copy;if(!Number.isInteger(start)||!Number.isInteger(length)||start<0||length<0||start+length>base.length)throw new Error('Invalid output patch range');return base.subarray(start,start+length)}
  if(typeof op.text==='string')return Buffer.from(op.text,'utf8')
  if(typeof op.base64==='string')return Buffer.from(op.base64,'base64')
  throw new Error('Invalid output patch operation')
 }))
}
function restoreDelta(base,recipe){
 if(hash(base)!==recipe.base_sha256)throw new Error('Published base checksum mismatch')
 if(recipe.kind==='text')return applyPatch(normalizeIds(base,recipe.replacements),recipe.operations)
 if(recipe.kind!=='zip-stored')throw new Error('Unsupported output patch')
 const entries=new Map(recipe.entries.map(entry=>{
  const slice=base.subarray(entry.offset,entry.offset+entry.length)
  const previous=entry.compression===8?inflateRawSync(slice):slice
  if(hash(previous)!==entry.base_sha256)throw new Error('Published ZIP entry checksum mismatch: '+entry.name)
  const result=applyPatch(normalizeIds(previous,entry.replacements),entry.operations)
  if(hash(result)!==entry.sha256)throw new Error('ZIP entry patch checksum mismatch: '+entry.name)
  return [entry.name,result]
 }))
 return Buffer.concat(recipe.segments.map(segment=>segment.entry?entries.get(segment.entry):Buffer.from(segment.base64,'base64')))
}
for(const file of files){
 const encoded=file.parts.map(path=>readFileSync(path,'utf8').trim()).join('')
 const base=gunzipSync(Buffer.from(encoded,'base64'))
 const raw=file.patch?restoreDelta(base,JSON.parse(readFileSync(file.patch,'utf8'))):base
 if(createHash('sha256').update(raw).digest('hex')!==file.sha256)throw new Error('Notebook output checksum mismatch: '+file.target)
 mkdirSync(dirname(file.target),{recursive:true});writeFileSync(file.target,raw)
}
console.log('Restored '+files.length+' verified notebook output/download assets.')

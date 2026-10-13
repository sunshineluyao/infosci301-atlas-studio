import {readFileSync,writeFileSync,mkdirSync} from 'node:fs'
import {dirname} from 'node:path'
import {gunzipSync} from 'node:zlib'
import {createHash} from 'node:crypto'
const files=JSON.parse(readFileSync('public/notebooks/packed.json','utf8'))
for(const file of files){
 const encoded=file.parts.map(path=>readFileSync(path,'utf8').trim()).join('')
 const raw=gunzipSync(Buffer.from(encoded,'base64'))
 if(createHash('sha256').update(raw).digest('hex')!==file.sha256)throw new Error('Notebook output checksum mismatch: '+file.target)
 mkdirSync(dirname(file.target),{recursive:true});writeFileSync(file.target,raw)
}
console.log('Restored '+files.length+' verified notebook output/download assets.')

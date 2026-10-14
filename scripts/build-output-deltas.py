"""Describe changed outputs against the existing public main artifacts.

Unchanged source records and asset bytes are reused with checksums. Human-readable
text patches expose the dependency/receipt changes instead of opaque archives.
The Node materializer validates the exact reconstructed output and ZIP entries.
"""
import base64,copy,difflib,gzip,hashlib,io,json,re,struct,subprocess,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'public/notebooks'
digest=lambda data:hashlib.sha256(data).hexdigest()

def previous(path):
    return subprocess.check_output(['git','show','origin/main:'+path],cwd=ROOT)

def normalize_ids(before,after):
    try:a,b=before.decode('utf8'),after.decode('utf8')
    except UnicodeDecodeError:return before,{}
    old=re.findall(r'id="([mp][0-9a-f]{10})"',a)
    new=re.findall(r'id="([mp][0-9a-f]{10})"',b)
    if len(old)!=len(new):return before,{}
    replacements={}
    for x,y in zip(old,new):
        if x in replacements and replacements[x]!=y:return before,{}
        if x!=y:replacements[x]=y
    if replacements:a=re.sub('|'.join(map(re.escape,replacements)),lambda m:replacements[m.group()],a)
    return a.encode('utf8'),replacements

def operations(before,after):
    if before==after:return [{'copy':[0,len(before)]}]
    try:
        a=before.decode('utf8').splitlines(keepends=True)
        b=after.decode('utf8').splitlines(keepends=True)
    except UnicodeDecodeError:
        prefix=0
        while prefix<min(len(before),len(after)) and before[prefix]==after[prefix]:prefix+=1
        suffix=0
        while suffix<min(len(before),len(after))-prefix and before[-suffix-1]==after[-suffix-1]:suffix+=1
        output=[]
        if prefix:output.append({'copy':[0,prefix]})
        if len(after)-prefix-suffix:output.append({'base64':base64.b64encode(after[prefix:len(after)-suffix if suffix else None]).decode()})
        if suffix:output.append({'copy':[len(before)-suffix,suffix]})
        return output
    offsets=[0]
    for line in a:offsets.append(offsets[-1]+len(line.encode('utf8')))
    output=[]
    for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
        if tag=='equal':output.append({'copy':[offsets[i],offsets[j]-offsets[i]]})
        elif tag in ('insert','replace'):output.append({'text':''.join(b[k:l])})
    return output

def zip_recipe(before,after):
    output=io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(after)) as source,zipfile.ZipFile(output,'w',compression=zipfile.ZIP_STORED) as target:
        for info in source.infolist():
            data=source.read(info.filename);stored=copy.copy(info)
            stored.compress_type=zipfile.ZIP_STORED;target.writestr(stored,data)
    desired=output.getvalue();entries=[];segments=[];cursor=0
    with zipfile.ZipFile(io.BytesIO(before)) as old,zipfile.ZipFile(io.BytesIO(desired)) as new:
        for info in new.infolist():
            offset=info.header_offset
            name_length,extra_length=struct.unpack_from('<HH',desired,offset+26)
            start=offset+30+name_length+extra_length
            segments.append({'base64':base64.b64encode(desired[cursor:start]).decode()})
            segments.append({'entry':info.filename});cursor=start+info.file_size
            base_info=old.getinfo(info.filename)
            old_name,old_extra=struct.unpack_from('<HH',before,base_info.header_offset+26)
            a=old.read(info.filename);b=new.read(info.filename);normalized,replacements=normalize_ids(a,b)
            entries.append({'name':info.filename,'offset':base_info.header_offset+30+old_name+old_extra,'length':base_info.compress_size,'compression':base_info.compress_type,'base_sha256':digest(a),'sha256':digest(b),'replacements':replacements,'operations':operations(normalized,b)})
    segments.append({'base64':base64.b64encode(desired[cursor:]).decode()})
    return desired,{'kind':'zip-stored','entries':entries,'segments':segments}

def main():
    old_rows=json.loads(previous('public/notebooks/packed.json'))
    rows=json.loads((PUBLIC/'packed.json').read_text())
    old={r['target']:r for r in old_rows}
    folder=PUBLIC/'patches';folder.mkdir(exist_ok=True)
    base_commit=subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip()
    for row in rows:
        if not any(word in row['target'] for word in ('Week4_Network','Week4_Spatiotemporal')):continue
        if not (row['target'].endswith('saved_assets.zip') or row['target'].endswith('Network_Studio_Executed.html')):continue
        base=old[row['target']]
        before=gzip.decompress(base64.b64decode(b''.join(previous(p) for p in base['parts'])))
        after=(ROOT/row['target']).read_bytes()
        if row['target'].endswith('.zip'):after,recipe=zip_recipe(before,after)
        else:
            normalized,replacements=normalize_ids(before,after)
            recipe={'kind':'text','replacements':replacements,'operations':operations(normalized,after)}
        recipe.update(base_sha256=digest(before),source_repository='https://github.com/sunshineluyao/infosci301-atlas-studio',source_commit=base_commit,target=row['target'])
        name=Path(row['target']).parent.name if row['target'].endswith('.zip') else Path(row['target']).stem
        patch=folder/(name+'.json');patch.write_text(json.dumps(recipe,ensure_ascii=False,separators=(',',':'))+'\n')
        row.update(parts=base['parts'],sha256=digest(after),patch=str(patch.relative_to(ROOT)))
        (ROOT/row['target']).write_bytes(after)
        print(name,'auditable patch bytes',patch.stat().st_size)
    (PUBLIC/'packed.json').write_text(json.dumps(rows,indent=2))
    # Keep the published base objects; they are referenced by the patches.
    for row in old_rows:
        for path in row['parts']:(ROOT/path).write_bytes(previous(path))

if __name__=='__main__':main()

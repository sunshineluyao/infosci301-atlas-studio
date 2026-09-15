from pathlib import Path
import hashlib, json, shutil, zipfile, sys
root=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else root/'release'
out.mkdir(parents=True,exist_ok=True)
def archive(source,target,prefix='',exclude=()):
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for file in sorted(source.rglob('*')):
            if file.is_file() and not any(p in exclude for p in file.relative_to(source).parts):
                z.write(file, str(Path(prefix)/file.relative_to(source)))
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        print(target.name, 'files',len(z.namelist()),'bytes',target.stat().st_size)

# Release notices accompany prebuilt files as well as source.
for name in ['QA_REPORT.md','THIRD_PARTY_NOTICES.md']:
    shutil.copy2(root/name,root/'dist-hf'/name)
    shutil.copy2(root/name,root/'dist-vercel'/name)
archive(root/'dist-hf',out/'INFOSCI301_HuggingFace_Ready.zip')
archive(root,out/'INFOSCI301_Atlas_Studio_Source.zip','infosci301-atlas-studio',('node_modules','dist','dist-hf','dist-vercel','.test-cache','__pycache__','.git','release'))
shutil.copy2(root/'public/DEPLOYMENT_GUIDE.html',out/'INFOSCI301_Atlas_Studio_Deployment_Guide.html')
shutil.copy2(root/'DEPLOYMENT_GUIDE.md',out/'INFOSCI301_Atlas_Studio_Deployment_Guide.md')
for kind in ['Network','Spatiotemporal']:
    for suffix,ext in [('Colab','ipynb'),('Executed','html')]:
        name=f'INFOSCI301_Week4_{kind}_Studio_{suffix}.{ext}'
        shutil.copy2(root/'public/notebooks'/name,out/name)
manifest=[]
for file in sorted(out.iterdir()):
    if file.is_file() and file.name!='RELEASE_MANIFEST.json':
        manifest.append({'file':file.name,'size':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
(out/'RELEASE_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
print('Release directory:',out)

from pathlib import Path
import markdown
root=Path(__file__).resolve().parents[1]
body=markdown.markdown((root/'DEPLOYMENT_GUIDE.md').read_text(),extensions=['tables','fenced_code','toc'])
css='''body{font:17px/1.65 Georgia,serif;color:#203540;background:#f5f7f5;max-width:1100px;margin:auto;padding:40px 5%}h1,h2,h3{font-family:system-ui,sans-serif;line-height:1.25;letter-spacing:-.5px}h1{font-size:38px;border-bottom:3px solid #087c77;padding-bottom:24px}h2{font-size:26px;margin-top:45px}h3{font-size:20px}a{color:#087c77}table{border-collapse:collapse;width:100%;font:14px/1.5 system-ui,sans-serif;margin:20px 0;background:#fff}th,td{padding:12px;border:1px solid #d7e2dd;text-align:left;vertical-align:top}th{background:#e5efe9}pre{background:#132b39;color:#e2eeed;padding:20px;border-radius:6px;overflow:auto;font-size:14px}code{font-family:ui-monospace,monospace}li{margin:9px 0}strong{color:#163c47}@media(max-width:700px){body{padding:22px 5%;font-size:16px}h1{font-size:29px}table{font-size:12px;display:block;overflow:auto}th,td{min-width:100px;padding:8px}}@media print{body{background:white;font-size:12pt;padding:0}h2,h3{break-after:avoid}pre,table{break-inside:avoid}a{color:#184658}}'''
html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>INFOSCI301 Atlas Studio — Deployment Guide</title><style>'+css+'</style></head><body>'+body+'</body></html>'
(root/'public/DEPLOYMENT_GUIDE.html').write_text(html)
print('Rendered guide to public/DEPLOYMENT_GUIDE.html')

from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for script in ('revise_notebooks.py','publish_notebooks.py'):
    subprocess.run([sys.executable,str(root/script)],check=True)

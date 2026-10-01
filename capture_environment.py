"""Run this in the exact manuscript environment before the GitHub release."""
import platform, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parent
(root/'PYTHON_VERSION.txt').write_text(sys.version+'\n'+platform.platform()+'\n',encoding='utf-8')
with (root/'requirements-lock.txt').open('w',encoding='utf-8') as f:
    subprocess.run([sys.executable,'-m','pip','freeze'],stdout=f,check=True)
print('Created PYTHON_VERSION.txt and requirements-lock.txt')

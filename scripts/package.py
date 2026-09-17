"""Deterministic, per-skill archives from tracked release inputs only."""
from pathlib import Path
import hashlib
import re
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
version=sys.argv[1]
if not re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+',version):
    raise SystemExit('Expected vMAJOR.MINOR.PATCH')
paths=subprocess.check_output(['git','ls-files','-z','skills'],cwd=ROOT).decode().split('\0')
paths=[Path(p) for p in paths if p]
out=ROOT/'dist';out.mkdir(exist_ok=True)
sums=[]
for name in sorted({p.parts[1] for p in paths}):
    archive=out/f'{name}-{version}.zip'
    members=[(p,Path(*p.parts[1:])) for p in paths if p.parts[1]==name]
    members.append((Path('LICENSE'),Path(name)/'LICENSE'))
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for source,dest in sorted(members):
            file=ROOT/source
            if file.is_symlink() or not file.is_file():raise SystemExit('Nonregular release input')
            info=zipfile.ZipInfo(dest.as_posix(),date_time=(2026,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644 << 16
            z.writestr(info,file.read_bytes())
    sums.append(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name)
(out/'SHA256SUMS').write_text('\n'.join(sums)+'\n')

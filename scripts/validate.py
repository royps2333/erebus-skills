"""Validate portable skill structure and run each skill's offline tests."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for skill in sorted((ROOT/'skills').iterdir()):
    if not skill.is_dir():continue
    text=(skill/'SKILL.md').read_text()
    assert text.startswith('---\n'),skill
    front=text.split('---',2)[1]
    assert re.search(r'^name: '+re.escape(skill.name)+r'$',front,re.M),skill
    assert re.search(r'^description:',front,re.M),skill
    for path in skill.rglob('*'):
        assert not path.is_symlink(),path
        if path.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
                if target.startswith('https://'):continue
                resolved=(path.parent/target.split('#')[0]).resolve()
                assert resolved.is_relative_to(skill.resolve()),target
                assert resolved.exists(),target
    tests=skill/'scripts'
    if tests.exists():
        subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(tests),'-p','test_*.py'],check=True)
print('Skill structure, local links and offline tests passed.')

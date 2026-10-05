"""Prepare a local review ZIP. Does not commit, publish or submit anything."""
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = {'api-tests', 'config', 'data-validation', 'datasets', 'demo',
               'docs', 'lib', 'observations', 'scripts', 'tests', 'ui-tests'}
TOP_LEVEL = {'.gitattributes', '.gitignore', 'README.md', 'package.json', 'package-lock.json', 'playwright.config.mjs'}
DESTINATION = ROOT / 'artifacts/rhombus-ai-take-home-review-20261005.zip'
files = []
for p in sorted(ROOT.rglob('*')):
    if not p.is_file():
        continue
    relative = p.relative_to(ROOT)
    if relative.parts[0] not in DIRECTORIES and str(relative) not in TOP_LEVEL:
        continue
    if '__pycache__' in relative.parts or p.suffix in {'.pyc', '.har'}:
        continue
    if relative.as_posix() == 'config/live.json' or p.name.endswith('.proposed.json'):
        continue
    if p.is_symlink() or not p.resolve().is_relative_to(ROOT):
        raise ValueError(f'Unsupported link: {relative}')
    # Refuse recognizable real credential material; do not print matched bytes.
    if p.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.mp4'}:
        text = p.read_text(encoding='utf-8-sig')
        patterns = [r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
                    r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                    r'\bgh[pousr]_[A-Za-z0-9]{20,}\b',
                    r'\bgithub_pat_[A-Za-z0-9_]{30,}\b']
        if any(re.search(pattern, text) for pattern in patterns):
            raise ValueError(f'Credential-pattern review required in {relative}')
    files.append((p, relative.as_posix()))

manifest = [{'file': name, 'bytes': p.stat().st_size,
             'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p, name in files]
DESTINATION.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(DESTINATION, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for p, name in files:
        archive.write(p, 'rhombus-ai-take-home/' + name)
    archive.writestr('rhombus-ai-take-home/REVIEW-MANIFEST.json', json.dumps(manifest, indent=2)+'\n')
with zipfile.ZipFile(DESTINATION) as archive:
    if archive.testzip() is not None:
        raise ValueError('ZIP integrity check failed')
    forbidden = {'.auth', 'node_modules', 'artifacts', '.aws', '.git'}
    if any(forbidden.intersection(Path(n).parts) for n in archive.namelist()):
        raise ValueError('Private/runtime directory entered the archive')
print(json.dumps({'zip': str(DESTINATION), 'files': len(manifest),
                  'bytes': DESTINATION.stat().st_size,
                  'sha256': hashlib.sha256(DESTINATION.read_bytes()).hexdigest(),
                  'integrity_checked': True, 'publishing_or_sending_performed_by_this_script': False}, indent=2))

"""Fail visibly while mandatory submission evidence is incomplete.

This is a completeness check, not an automated truthfulness/reviewer substitute.
"""
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT):
    status = json.loads((root / 'config/submission-status.json').read_text(encoding='utf-8'))
    cases = set(json.loads((root / 'datasets/manifest.json').read_text(encoding='utf-8'))) - {'baseline'}
    missing = []
    cloud = status.get('cloud_requirement', {})
    if cloud.get('destination_provider') != 'gcs':
        if not cloud.get('employer_exception_confirmed'):
            missing.append('Original GCS requirement unmet; destination substitution has no confirmed employer exception')
    if set(status.get('drift_cases', {})) != cases:
        missing.append('Drift case coverage does not match the dataset manifest')
    entries = {key: status.get(key, {}) for key in ('baseline', 'ui_journey', 'api_tests')}
    entries.update(status.get('drift_cases', {}))
    for name, item in entries.items():
        if item.get('status') != 'complete':
            missing.append(f'{name}: {item.get("status", "missing")}')
        if not item.get('evidence'):
            missing.append(f'{name}: no linked execution evidence')
        for link in item.get('evidence', []):
            path = (root / link).resolve()
            if not path.is_relative_to(root.resolve()) or not path.is_file() or not path.stat().st_size:
                missing.append(f'{name}: invalid/empty evidence path {link}')
    demo = status.get('demo', {})
    parsed = urlparse(demo.get('url', ''))
    if demo.get('status') != 'complete' or parsed.scheme != 'https' or not parsed.netloc:
        missing.append('Demo video link missing or not complete')
    for case in sorted(cases):
        text = (root / 'observations' / f'{case}.md').read_text(encoding='utf-8')
        if 'Status: NOT RUN' in text:
            missing.append(f'{case}: observation still a not-run template')
    return missing


if __name__ == '__main__':
    gaps = check()
    print(json.dumps({'ready': not gaps, 'gaps': gaps,
                      'note': 'Also manually review evidence, redaction, reviewer access and demo playback.'}, indent=2))
    raise SystemExit(1 if gaps else 0)

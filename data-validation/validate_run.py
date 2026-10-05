"""Validate independent scheduled-run provenance AND input/output data.

Manifests come from snapshot_cloud.py after inspecting the platform run record.
This verifies internal evidence consistency; it does not cryptographically attest
that user-entered run metadata was emitted by Rhombus. Preserve redacted run logs.
"""
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from validate import digest, validate


def instant(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('all timestamps must include a UTC offset')
    return parsed


def check_provenance(manifests):
    errors, source_paths, output_paths, ids, generations, inputs, configs = [], [], [], set(), set(), set(), set()
    scenarios, providers = set(), set()
    for file in manifests:
        path = Path(file)
        item = json.loads(path.read_text(encoding='utf-8'))
        scenarios.add(item['scenario'])
        run = item['run']
        if not run.get('id') or run['id'] in ids:
            errors.append('run IDs must be present and unique')
        ids.add(run.get('id'))
        configs.add(run.get('configuration_sha256'))
        if run.get('trigger') != 'scheduled':
            errors.append('run trigger must be scheduled')
        if run.get('status') != 'success':
            errors.append(f"run {run.get('id')} did not succeed; retain failure as an observation")
        if not run.get('schedule_id'):
            errors.append('schedule ID missing')
        start, end = instant(run['started_at']), instant(run['finished_at'])
        if end < start:
            errors.append('run finished before it started')
        source = item['source']
        source_path = path.parent / source['file']
        source_paths.append(source_path)
        actual_input = digest(source_path)
        inputs.add(actual_input)
        if actual_input != source['sha256']:
            errors.append('S3 snapshot hash mismatch')
        if not source.get('version_id') or source['version_id'] == 'null':
            errors.append('S3 version ID is required to bind the source snapshot')
        if instant(source['last_modified']) > start:
            errors.append('S3 source version was written after run start')
        output = item.get('output')
        if not output:
            errors.append('no destination output; data correctness and determinism not established')
            continue
        provider = output.get('provider', 'gcs')
        providers.add(provider)
        if provider not in ('gcs', 's3'):
            errors.append('unsupported output provider')
        output_path = path.parent / output['file']
        output_paths.append(output_path)
        version = output.get('version_id') if provider == 's3' else output.get('generation')
        generation = (provider, output.get('bucket'), output.get('key'), version)
        if not all(generation) or version == 'null' or generation in generations:
            errors.append('destination object version/generation must be present and unique per run')
        generations.add(generation)
        if digest(output_path) != output['sha256']:
            errors.append('destination snapshot hash mismatch')
        updated = instant(output['updated_at'])
        if not (start <= updated <= end + timedelta(seconds=60)):
            errors.append('destination output is stale or falls outside the run window')
    if len(providers) > 1:
        errors.append('determinism group must use one destination provider')
    if len(manifests) < 3:
        errors.append('three independent scheduled runs required for this determinism group')
    if len(scenarios) != 1 or len(inputs) != 1 or len(configs) != 1:
        errors.append('determinism group must share scenario, input hash and configuration hash')
    if not configs or any(not isinstance(c, str) or len(c) != 64 or any(x not in '0123456789abcdef' for x in c) for c in configs):
        errors.append('configuration_sha256 must identify the frozen pipeline configuration')
    return errors, source_paths, output_paths, next(iter(scenarios), None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', nargs='+', type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    try:
        errors, sources, outputs, scenario = check_provenance(args.manifest)
        report = {'provenance_passed': not errors, 'provenance_errors': errors,
                  'data': validate(sources[0], outputs, scenario) if sources else None}
        report['passed'] = not errors and report['data']['passed']
        code = 0 if report['passed'] else 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        report = {'passed': False, 'error': str(error)}
        code = 2
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'report': str(args.report), 'exit_code': code}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())

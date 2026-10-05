import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'data-validation'))
from validate import digest
from validate_run import check_provenance


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        (ROOT / 'artifacts').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'artifacts')
        self.folder = Path(self.temp.name)
        (self.folder / 'input.csv').write_bytes((ROOT / 'datasets/baseline.csv').read_bytes())
        (self.folder / 'output.csv').write_bytes((ROOT / 'datasets/expected/baseline-clean.csv').read_bytes())
        self.base = {
            'scenario': 'baseline',
            'run': {'id': 'test-only-1', 'schedule_id': 'test-only-schedule', 'trigger': 'scheduled',
                    'status': 'success', 'configuration_sha256': 'a'*64,
                    'started_at': '2026-09-30T08:00:00Z', 'finished_at': '2026-09-30T08:00:20Z'},
            'source': {'file': 'input.csv', 'sha256': digest(self.folder / 'input.csv'),
                       'version_id': 'test-only-version', 'last_modified': '2026-09-30T07:59:00Z'},
            'output': {'file': 'output.csv', 'sha256': digest(self.folder / 'output.csv'),
                       'bucket': 'test-only', 'key': 'output.csv', 'generation': '1',
                       'updated_at': '2026-09-30T08:00:15Z'}}

    def tearDown(self):
        self.temp.cleanup()

    def group(self, mutate=None):
        paths = []
        for index in range(3):
            item = copy.deepcopy(self.base)
            item['run']['id'] = f'test-only-{index}'
            item['output']['generation'] = str(index + 1)
            if mutate:
                mutate(item, index)
            path = self.folder / f'{index}.json'
            path.write_text(json.dumps(item), encoding='utf-8')
            paths.append(path)
        return paths

    def test_consistent_independent_manifests(self):
        self.assertFalse(check_provenance(self.group())[0])

    def test_s3_versions_supported_without_claiming_gcs(self):
        def s3(item, index):
            item['output']['provider'] = 's3'
            item['output']['version_id'] = f'version-{index}'
            del item['output']['generation']
        self.assertFalse(check_provenance(self.group(s3))[0])

    def test_s3_unversioned_output_rejected(self):
        def unversioned(item, index):
            item['output'].update(provider='s3', version_id='null')
        self.assertTrue(any('version' in e for e in check_provenance(self.group(unversioned))[0]))

    def test_mixing_output_providers_rejected(self):
        def mixed(item, index):
            if index == 1:
                item['output'].update(provider='s3', version_id='distinct-s3-version')
        self.assertTrue(any('one destination' in e for e in check_provenance(self.group(mixed))[0]))

    def test_reusing_same_run_and_generation_fails(self):
        paths = self.group()
        errors = check_provenance([paths[0]] * 3)[0]
        self.assertTrue(any('unique' in e for e in errors))

    def test_stale_destination_fails(self):
        paths = self.group(lambda item, _: item['output'].update(updated_at='2026-09-29T08:00:15Z'))
        self.assertTrue(any('stale' in e for e in check_provenance(paths)[0]))

    def test_manual_trigger_fails(self):
        paths = self.group(lambda item, _: item['run'].update(trigger='manual'))
        self.assertTrue(any('trigger' in e for e in check_provenance(paths)[0]))

    def test_changed_config_is_not_determinism(self):
        paths = self.group(lambda item, i: item['run'].update(configuration_sha256=str(i)*64))
        self.assertTrue(any('configuration' in e for e in check_provenance(paths)[0]))

    def test_modified_snapshot_fails(self):
        paths = self.group()
        with (self.folder / 'output.csv').open('a') as handle:
            handle.write('tampered\n')
        self.assertTrue(any('hash mismatch' in e for e in check_provenance(paths)[0]))

    def test_source_written_after_run_start_fails(self):
        paths = self.group(lambda item, _: item['source'].update(last_modified='2026-09-30T08:01:00Z'))
        self.assertTrue(any('after run start' in e for e in check_provenance(paths)[0]))

    def test_missing_output_is_explicit(self):
        paths = self.group(lambda item, _: item.pop('output'))
        self.assertTrue(any('no destination output' in e for e in check_provenance(paths)[0]))

    def test_naive_timestamp_is_rejected(self):
        paths = self.group(lambda item, _: item['run'].update(started_at='2026-09-30T08:00:00'))
        with self.assertRaises(ValueError):
            check_provenance(paths)

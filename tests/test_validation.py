import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v = load('validator', ROOT / 'data-validation/validate.py')
g = load('generator', ROOT / 'scripts/generate_datasets.py')


class ValidationTests(unittest.TestCase):
    def setUp(self):
        (ROOT / 'artifacts').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'artifacts')
        self.folder = Path(self.temp.name)
        self.golden = ROOT / 'datasets/expected/baseline-clean.csv'

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, rows, headers=None):
        path = self.folder / name
        g.write_csv(path, headers or v.FIELDS, rows)
        return path

    def validate(self, case='baseline', outputs=None):
        return v.validate(ROOT / 'datasets' / f'{case}.csv',
                          outputs if outputs is not None else [self.golden] * 3, case)

    def check(self, report, suffix):
        return next(c for c in report['checks'] if c['check'].endswith(suffix))

    def test_baseline_matches_independently_reviewed_golden(self):
        report = self.validate()
        self.assertTrue(report['passed'])
        self.assertEqual(report['source']['rows'], 12)
        self.assertEqual(report['oracle']['accepted'], 6)
        self.assertEqual(len(report['oracle']['rejected']), 5)
        self.assertEqual(len(report['oracle']['duplicates']), 1)

    def test_normalization_missing_fields_and_duplicate_rule(self):
        _, rows = v.read_csv(ROOT / 'datasets/baseline.csv')
        cleaned, _, _ = v.clean(rows)
        self.assertEqual(cleaned[0]['amount'], '120.00')
        self.assertEqual(cleaned[0]['email'], 'alice@example.com')
        self.assertEqual(cleaned[1]['email'], 'unknown@example.com')
        self.assertEqual(cleaned[3]['customer_name'], 'Unknown')

    def test_duplicate_keeps_first_valid_not_first_invalid(self):
        row = dict(zip(v.FIELDS, g.BASE[0]))
        invalid = dict(row, amount='NaN')
        altered = dict(row, amount='150.00')
        cleaned, rejected, duplicates = v.clean([invalid, row, altered])
        self.assertEqual(cleaned[0]['amount'], '120.00')
        self.assertEqual(len(rejected), 1)
        self.assertEqual(len(duplicates), 1)

    def test_nonfinite_precision_range_rejected(self):
        for amount in ('NaN', 'Infinity', '-Infinity', '1.001', '-1', '0', '10000.01'):
            with self.subTest(amount=amount):
                cleaned, rejected, _ = v.clean([dict(zip(v.FIELDS, g.BASE[0]), amount=amount)])
                self.assertFalse(cleaned)
                self.assertIn('invalid_amount', rejected[0]['reasons'])

    def test_email_country_date_contract(self):
        for field, value in [('email', 'no-at-sign'), ('country', 'UK'), ('order_date', '2026-09-01')]:
            with self.subTest(field=field):
                cleaned, rejected, _ = v.clean([dict(dict(zip(v.FIELDS, g.BASE[0])), **{field: value})])
                self.assertFalse(cleaned)
                self.assertTrue(rejected)

    def test_each_schema_mutation_is_detected(self):
        for case in ('schema-drop-column', 'schema-rename-column', 'schema-add-column', 'schema-combined'):
            with self.subTest(case=case):
                self.assertFalse(self.check(self.validate(case), 'source_schema')['passed'])

    def test_type_drift_is_not_silently_coerced(self):
        report = self.validate('schema-change-type')
        self.assertEqual(report['oracle']['accepted'], 0)
        self.assertFalse(self.check(report, 'output_1.cleaning_rules')['passed'])

    def test_semantic_cents_detected_even_when_values_are_in_range(self):
        report = self.validate('semantic-cents')
        self.assertTrue(self.check(report, 'semantic_input_detection')['passed'])
        self.assertIn({'order_id': 'O1003', 'signal': 'amount_100x'}, report['semantic_signals'])
        # 9.99 becomes 999.00, still inside the valid numeric range.
        _, source = v.read_csv(ROOT / 'datasets/semantic-cents.csv')
        naive, _, _ = v.clean(source)
        path = self.write('naive.csv', [[r[f] for f in v.FIELDS] for r in naive])
        self.assertFalse(self.check(self.validate('semantic-cents', [path]*3), 'output_1.business_correctness')['passed'])

    def test_semantic_dates_parse_both_ways_but_business_check_fails(self):
        _, source = v.read_csv(ROOT / 'datasets/semantic-date-order.csv')
        naive, _, _ = v.clean(source)
        path = self.write('naive.csv', [[r[f] for f in v.FIELDS] for r in naive])
        report = self.validate('semantic-date-order', [path]*3)
        self.assertTrue(self.check(report, 'semantic_input_detection')['passed'])
        self.assertFalse(self.check(report, 'output_1.business_correctness')['passed'])

    def test_corrected_semantic_output_passes(self):
        for case in ('semantic-cents', 'semantic-date-order'):
            with self.subTest(case=case):
                self.assertTrue(self.validate(case)['passed'])

    def test_empty_output_is_not_a_success(self):
        path = self.write('empty.csv', [])
        self.assertFalse(self.validate(outputs=[path]*3)['passed'])
        self.assertFalse(self.validate(outputs=[])['passed'])

    def test_missing_duplicate_and_changed_rows_fail(self):
        changed = copy.deepcopy(g.GOLDEN)
        changed[0][3] = '120.01'
        for rows in (g.GOLDEN[:-1], g.GOLDEN + [g.GOLDEN[0]], changed):
            with self.subTest(rows=rows):
                path = self.write('bad.csv', rows)
                self.assertFalse(self.validate(outputs=[path]*3)['passed'])

    def test_reordering_content_determinism_separate_from_sort_rule(self):
        path = self.write('reverse.csv', list(reversed(g.GOLDEN)))
        report = self.validate(outputs=[self.golden, path, self.golden])
        self.assertTrue(self.check(report, 'determinism_content')['passed'])
        self.assertFalse(self.check(report, 'output_2.sorted_ids')['passed'])

    def test_determinism_catches_value_difference(self):
        changed = copy.deepcopy(g.GOLDEN)
        changed[0][3] = '120.01'
        path = self.write('changed.csv', changed)
        self.assertFalse(self.check(self.validate(outputs=[self.golden, path, self.golden]), 'determinism_content')['passed'])

    def test_one_run_cannot_establish_determinism(self):
        report = self.validate(outputs=[self.golden])
        self.assertFalse(self.check(report, 'determinism_sample_count')['passed'])
        self.assertFalse(self.check(report, 'determinism_content')['passed'])

    def test_malformed_csv_rejected(self):
        for content in ('a,a\n1,2\n', 'a,b\n1,2,3\n', 'a,b\n1\n', ''):
            path = self.folder / 'bad.csv'
            path.write_text(content, encoding='utf-8')
            with self.assertRaises(ValueError):
                v.read_csv(path)

    def test_wrong_scenario_cannot_masquerade_as_valid_run(self):
        report = v.validate(ROOT / 'datasets/baseline.csv', [self.golden]*3, 'semantic-cents')
        self.assertFalse(self.check(report, 'source_fixture_identity')['passed'])
        self.assertFalse(self.check(report, 'semantic_input_detection')['passed'])

    def test_generator_reproducibility_and_mutation_isolation(self):
        manifest = g.generate(self.folder)
        self.assertEqual(manifest, json.loads((ROOT / 'datasets/manifest.json').read_text()))
        for case in ('semantic-cents', 'semantic-date-order'):
            self.assertEqual(manifest[case]['columns'], v.FIELDS)
            self.assertEqual(manifest[case]['rows'], 12)


if __name__ == '__main__':
    unittest.main()

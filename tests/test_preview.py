import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'data-validation'))
from validate import FIELDS, ROOT, read_csv
from validate_preview import validate_preview


class PreviewEvidenceTests(unittest.TestCase):
    def evidence(self):
        return {'scenario': 'baseline', 'columns': FIELDS,
                'rows': read_csv(ROOT / 'datasets/expected/baseline-clean.csv')[1]}

    def test_numeric_display_pass_does_not_certify_csv_or_schedule(self):
        evidence = self.evidence()
        evidence['rows'][0]['amount'] = '120'
        result = validate_preview(evidence)
        self.assertTrue(result['business_preview_passed'])
        self.assertFalse(result['csv_bytes_verified'])
        self.assertFalse(result['scheduled_run_verified'])
        self.assertFalse(result['determinism_verified'])

    def test_cents_and_row_loss_cannot_pass_successful_preview(self):
        evidence = self.evidence()
        evidence['rows'].pop(0)
        evidence['rows'][0]['amount'] = '2550'
        result = validate_preview(evidence)
        self.assertFalse(result['business_preview_passed'])
        self.assertFalse(next(c for c in result['checks'] if c['check'] == 'preview_business_values')['passed'])

    def test_swapped_date_and_wrong_schema_are_detected(self):
        evidence = self.evidence()
        evidence['rows'][0]['order_date'] = '2026-01-09'
        self.assertFalse(validate_preview(evidence)['business_preview_passed'])
        evidence = copy.deepcopy(self.evidence())
        evidence['columns'] = FIELDS + ['campaign']
        self.assertFalse(validate_preview(evidence)['business_preview_passed'])

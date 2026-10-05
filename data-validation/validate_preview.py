"""Supplementary UI-preview checks; never certify CSV bytes or cloud delivery."""
import argparse
import json
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

from validate import FIELDS, ROOT, read_csv


def validate_preview(evidence):
    _, expected = read_csv(ROOT / 'datasets/expected/baseline-clean.csv')
    rows = evidence['rows']
    checks = []

    def add(name, passed, **detail):
        checks.append({'check': name, 'passed': bool(passed), **detail})

    add('preview_schema', evidence['columns'] == FIELDS and
        all(set(row) == set(FIELDS) for row in rows))
    add('preview_row_count', len(rows) == len(expected), expected=len(expected), actual=len(rows))
    ids = [row.get('order_id') for row in rows]
    add('preview_unique_ids', len(set(ids)) == len(ids))
    add('preview_sorted_ids', all(isinstance(i, str) for i in ids) and ids == sorted(ids, key=str))

    def normalized(row):
        result = dict(row)
        amount = Decimal(result['amount'])
        if not amount.is_finite():
            raise ValueError('Non-finite amount')
        # Numeric display is compared exactly, without float rounding. Do not
        # infer the number of decimal places in an unavailable serialized CSV.
        return tuple(amount if field == 'amount' else result[field] for field in FIELDS)

    try:
        wanted = Counter(normalized(row) for row in expected)
        actual = Counter(normalized(row) for row in rows)
        add('preview_business_values', wanted == actual,
            missing_rows=[list(row) for row in (wanted - actual).elements()],
            unexpected_rows=[list(row) for row in (actual - wanted).elements()])
    except (KeyError, ValueError, InvalidOperation, TypeError) as error:
        add('preview_business_values', False, error=str(error))
    return {
        'scenario': evidence['scenario'],
        'scope': 'Rendered output-node preview only; supplementary evidence',
        'business_preview_passed': all(c['passed'] for c in checks),
        'csv_bytes_verified': False,
        'scheduled_run_verified': False,
        'determinism_verified': False,
        'checks': checks,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    report = validate_preview(json.loads(args.evidence.read_text(encoding='utf-8')))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, default=str) + '\n', encoding='utf-8')
    print(json.dumps({'business_preview_passed': report['business_preview_passed'],
                      'csv_bytes_verified': False, 'report': str(args.report)}))
    return 0 if report['business_preview_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

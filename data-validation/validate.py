"""Independent CSV contract validator. Python standard library only.

Exit 0 = every required check passed; 1 = data/coverage findings; 2 = input/CLI error.
Semantic drift detection is separate from output acceptance. No network or writes
to a platform. Generated reference data is never represented as cloud evidence.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

FIELDS = ['order_id', 'customer_name', 'email', 'amount', 'order_date', 'country']
ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_csv(path):
    with Path(path).open(newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle, strict=True)
        fields = reader.fieldnames
        if not fields or len(fields) != len(set(fields)) or any(not f for f in fields):
            raise ValueError(f'{path}: empty, missing or duplicate CSV headers')
        rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            raise ValueError(f'{path}: row width differs from header')
        return fields, rows


def clean(rows):
    """Strict baseline contract. Never guesses a renamed column or new units."""
    result, rejected, duplicates, seen = [], [], [], set()
    for line, raw in enumerate(rows, start=2):
        row = {f: raw[f].strip() for f in FIELDS}
        row['order_id'] = row['order_id'].upper()
        row['country'] = row['country'].upper()
        row['customer_name'] = row['customer_name'] or 'Unknown'
        row['email'] = (row['email'] or 'unknown@example.com').lower()
        reasons = []
        if not row['order_id']:
            reasons.append('missing_order_id')
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', row['email']):
            reasons.append('invalid_email')
        if row['country'] not in {'AU', 'US', 'NZ'}:
            reasons.append('invalid_country')
        try:
            value = Decimal(row['amount'].replace('$', '').replace(',', ''))
            if not value.is_finite() or not (0 < value <= 10000) or value != value.quantize(Decimal('0.01')):
                raise ValueError('amount outside contract')
            row['amount'] = f'{value:.2f}'
        except (InvalidOperation, ValueError):
            reasons.append('invalid_amount')
        try:
            # strptime alone accepts single-digit components: require the source format too.
            if not re.fullmatch(r'\d{2}/\d{2}/\d{4}', row['order_date']):
                raise ValueError('date format')
            row['order_date'] = datetime.strptime(row['order_date'], '%m/%d/%Y').date().isoformat()
        except ValueError:
            reasons.append('invalid_date')
        if reasons:
            rejected.append({'line': line, 'order_id': row['order_id'], 'reasons': reasons})
        elif row['order_id'] in seen:
            duplicates.append({'line': line, 'order_id': row['order_id']})
        else:
            seen.add(row['order_id'])
            result.append(row)
    return sorted(result, key=lambda r: r['order_id']), rejected, duplicates


def canonical(rows):
    # Ignore row ordering for content determinism, but retain duplicates and exact values.
    return Counter(tuple(row[f] for f in FIELDS) for row in rows)


def differences(expected, actual):
    wanted, got = canonical(expected), canonical(actual)
    return {'missing_rows': [list(r) for r in (wanted - got).elements()],
            'unexpected_rows': [list(r) for r in (got - wanted).elements()]}


def validate(source, outputs, scenario, reference=None, require_repeats=3):
    manifest = json.loads((ROOT / 'datasets/manifest.json').read_text(encoding='utf-8'))
    if scenario not in manifest:
        raise ValueError(f'unknown scenario: {scenario}')
    source = Path(source)
    headers, rows = read_csv(source)
    checks = []

    def add(name, passed, **detail):
        checks.append({'check': name, 'passed': bool(passed), **detail})

    add('source_fixture_identity', digest(source) == manifest[scenario]['sha256'],
        note='Actual S3 snapshot must match the named controlled experiment.')
    add('source_schema', headers == FIELDS, expected=FIELDS, actual=headers)
    missing = sorted(set(FIELDS) - set(headers))
    oracle, rejected, duplicates = (None, [], []) if missing else clean(rows)
    reference = Path(reference or ROOT / 'datasets/expected/baseline-clean.csv')
    gold_headers, golden = read_csv(reference)
    if gold_headers != FIELDS or len({r['order_id'] for r in golden}) != len(golden):
        raise ValueError('golden reference must have exact headers and unique order IDs')

    semantic_signals = []
    if not missing:
        gold_by_id = {r['order_id']: r for r in golden}
        for row in rows:
            key = row['order_id'].strip().upper()
            if key not in gold_by_id:
                continue
            original = gold_by_id[key]
            try:
                amount = Decimal(row['amount'].strip().replace('$', '').replace(',', ''))
                if amount.is_finite() and amount == Decimal(original['amount']) * 100:
                    semantic_signals.append({'order_id': key, 'signal': 'amount_100x'})
            except InvalidOperation:
                pass
            try:
                md = datetime.strptime(row['order_date'].strip(), '%m/%d/%Y').date().isoformat()
                dm = datetime.strptime(row['order_date'].strip(), '%d/%m/%Y').date().isoformat()
                if md != original['order_date'] and dm == original['order_date']:
                    semantic_signals.append({'order_id': key, 'signal': 'date_order_swapped'})
            except ValueError:
                pass
    expected_signal = {'semantic-cents': 'amount_100x', 'semantic-date-order': 'date_order_swapped'}.get(scenario)
    if expected_signal:
        add('semantic_input_detection', any(s['signal'] == expected_signal for s in semantic_signals),
            signals=semantic_signals)

    # Post-drift business acceptance is the known intended six-order result.
    # Also report ordinary cleaning equality separately to expose semantic blind spots.
    records, usable = [], []
    for index, output in enumerate(outputs, start=1):
        output = Path(output)
        out_headers, actual = read_csv(output)
        prefix = f'output_{index}'
        add(f'{prefix}.schema', out_headers == FIELDS, expected=FIELDS, actual=out_headers)
        add(f'{prefix}.row_count', len(actual) == len(golden), expected=len(golden), actual=len(actual))
        if out_headers == FIELDS:
            add(f'{prefix}.unique_ids', len({r['order_id'] for r in actual}) == len(actual))
            add(f'{prefix}.sorted_ids', [r['order_id'] for r in actual] == sorted(r['order_id'] for r in actual))
            diff = differences(golden, actual)
            add(f'{prefix}.business_correctness', not any(diff.values()), **diff)
            # Invalid schema means baseline cleaning cannot be evaluated, not an invented pass.
            if oracle is not None:
                oracle_diff = differences(oracle, actual)
                # For semantic scenarios a corrected output SHOULD differ from the unchanged parser.
                if not expected_signal:
                    add(f'{prefix}.cleaning_rules', not any(oracle_diff.values()), **oracle_diff)
            usable.append(actual)
        records.append({'file': str(output), 'sha256': digest(output), 'rows': len(actual)})
    add('outputs_present', bool(outputs), actual=len(outputs))
    add('determinism_sample_count', len(outputs) >= require_repeats,
        required=require_repeats, actual=len(outputs))
    if len(usable) >= 2:
        add('determinism_content', all(canonical(r) == canonical(usable[0]) for r in usable[1:]),
            comparisons=[differences(usable[0], r) for r in usable[1:]])
    else:
        add('determinism_content', False, note='Need at least two valid output CSVs; use three independent runs.')
    return {
        'scenario': scenario, 'scope': 'file validation; cloud provenance is verified separately',
        'passed': all(c['passed'] for c in checks),
        'source': {'file': str(source), 'sha256': digest(source), 'rows': len(rows)},
        'reference_sha256': digest(reference), 'outputs': records,
        'oracle': {'accepted': None if oracle is None else len(oracle),
                   'rejected': rejected, 'duplicates': duplicates, 'missing_columns': missing},
        'semantic_signals': semantic_signals, 'checks': checks,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path, help='Downloaded S3 input snapshot')
    parser.add_argument('--output', action='append', default=[], type=Path, help='Downloaded GCS output; repeat for independent runs')
    parser.add_argument('--scenario', required=True)
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    try:
        report = validate(args.input, args.output, args.scenario, args.reference)
    except (OSError, ValueError, csv.Error, KeyError) as error:
        report = {'passed': False, 'error': str(error), 'scenario': args.scenario}
        code = 2
    else:
        code = 0 if report['passed'] else 1
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'report': str(args.report), 'exit_code': code}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())

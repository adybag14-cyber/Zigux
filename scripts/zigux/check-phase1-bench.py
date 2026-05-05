#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[2]
EXPECTATIONS = ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_bench_expectations.json'
EXPECTED_ITERATIONS = {
    'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS': 20000,
    'PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS': 20000,
    'PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS': 20000,
    'PHASE1_BENCH_STRING_ITERATIONS': 40000,
    'PHASE1_BENCH_HWEIGHT_ITERATIONS': 100000,
    'PHASE1_BENCH_LIST_SORT_ITERATIONS': 1000,
    'PHASE1_BENCH_RBTREE_ITERATIONS': 4000,
}
EXPECTED_CHECKSUMS = [
    'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM',
    'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM',
    'PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM',
    'PHASE1_BENCH_STRING_CHECKSUM',
    'PHASE1_BENCH_HWEIGHT_CHECKSUM',
    'PHASE1_BENCH_LIST_SORT_CHECKSUM',
    'PHASE1_BENCH_RBTREE_CHECKSUM',
]
REQUIRED_EXACT_CHECKSUMS = {
    'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM',
    'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM',
}


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    zig = shutil.which('zig')
    if zig:
        return zig
    raise SystemExit('zig not found; pass --zig or add zig to PATH')


def parse_output(stdout: str) -> tuple[dict[str, str], dict[str, int]]:
    parsed: dict[str, str] = {}
    counts: dict[str, int] = {}
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line or '=' not in line:
            continue
        key, value = line.split('=', 1)
        parsed[key] = value
        counts[key] = counts.get(key, 0) + 1
    return parsed, counts


def load_expectations(path: Path) -> object:
    return load_expectations_text(path.read_text(encoding='utf-8'))


def load_expectations_text(text: str) -> object:
    return json.loads(
        text,
        object_pairs_hook=DuplicateTrackingDict,
    )


def validate_expectations(expectations: object) -> tuple[str, object]:
    if not isinstance(expectations, dict):
        return ('expectations_type', type(expectations).__name__)

    if isinstance(expectations, DuplicateTrackingDict) and expectations.duplicate_keys:
        return ('expectations_duplicate_keys', expectations.duplicate_keys)

    if expectations.get('status') != 'pass':
        return ('expectations_status', expectations.get('status'))

    iterations = expectations.get('iterations')
    if not isinstance(iterations, dict):
        return ('expectations_iterations_type', type(iterations).__name__)
    if isinstance(iterations, DuplicateTrackingDict) and iterations.duplicate_keys:
        return ('expectations_duplicate_iteration_keys', iterations.duplicate_keys)

    actual_iteration_keys = set()
    for key, value in iterations.items():
        if not isinstance(key, str):
            return ('expectations_iteration_key_type', type(key).__name__)
        if not isinstance(value, int):
            return ('expectations_iteration_value_type', (key, type(value).__name__))
        actual_iteration_keys.add(key)
        expected_value = EXPECTED_ITERATIONS.get(key)
        if expected_value is None:
            return ('expectations_unexpected_iteration', key)
        if value != expected_value:
            return ('expectations_iteration_value', (key, expected_value, value))

    missing_iterations = sorted(set(EXPECTED_ITERATIONS) - actual_iteration_keys)
    if missing_iterations:
        return ('expectations_missing_iterations', missing_iterations)

    checksums = expectations.get('checksums')
    if not isinstance(checksums, list):
        return ('expectations_checksums_type', type(checksums).__name__)

    seen: set[str] = set()
    duplicates: list[str] = []
    actual_checksums: list[str] = []
    for item in checksums:
        if not isinstance(item, str):
            return ('expectations_checksum_type', type(item).__name__)
        actual_checksums.append(item)
        if item in seen and item not in duplicates:
            duplicates.append(item)
        seen.add(item)

    if duplicates:
        return ('expectations_duplicate_checksums', duplicates)

    actual_checksum_set = set(actual_checksums)
    missing_checksums = sorted(set(EXPECTED_CHECKSUMS) - actual_checksum_set)
    if missing_checksums:
        return ('expectations_missing_checksums', missing_checksums)

    unexpected_checksums = sorted(actual_checksum_set - set(EXPECTED_CHECKSUMS))
    if unexpected_checksums:
        return ('expectations_unexpected_checksums', unexpected_checksums)

    exact_checksums = expectations.get('exact_checksums')
    if not isinstance(exact_checksums, dict):
        return ('expectations_exact_checksums_type', type(exact_checksums).__name__)
    if isinstance(exact_checksums, DuplicateTrackingDict) and exact_checksums.duplicate_keys:
        return ('expectations_duplicate_exact_checksum_keys', exact_checksums.duplicate_keys)

    actual_exact_checksum_keys = set()
    for key, value in exact_checksums.items():
        if not isinstance(key, str):
            return ('expectations_exact_checksum_key_type', type(key).__name__)
        if not isinstance(value, int):
            return ('expectations_exact_checksum_value_type', (key, type(value).__name__))
        if value <= 0:
            return ('expectations_exact_checksum_nonpositive', (key, value))
        if key not in actual_checksum_set:
            return ('expectations_exact_checksum_not_listed', key)
        actual_exact_checksum_keys.add(key)

    missing_exact_checksums = sorted(REQUIRED_EXACT_CHECKSUMS - actual_exact_checksum_keys)
    if missing_exact_checksums:
        return ('expectations_missing_exact_checksums', missing_exact_checksums)

    unexpected_exact_checksums = sorted(actual_exact_checksum_keys - REQUIRED_EXACT_CHECKSUMS)
    if unexpected_exact_checksums:
        return ('expectations_unexpected_exact_checksums', unexpected_exact_checksums)

    return ('pass', expectations)


def validate_output(expectations: dict[str, object], stdout: str) -> tuple[str, object]:
    parsed, counts = parse_output(stdout)
    exact_checksums: dict[str, int] = expectations['exact_checksums']
    required_keys = {
        'PHASE1_BENCH',
        *expectations['iterations'].keys(),
        *expectations['checksums'],
    }
    duplicate = sorted(key for key in required_keys if counts.get(key, 0) > 1)
    if duplicate:
        return ('duplicate', duplicate)

    unexpected = sorted(
        key
        for key in parsed
        if key.startswith('PHASE1_BENCH') and key not in required_keys
    )
    if unexpected:
        return ('unexpected', unexpected)

    actual_status = parsed.get('PHASE1_BENCH')
    if actual_status != expectations['status']:
        return ('status', (expectations['status'], actual_status))

    missing = []
    for key, value in expectations['iterations'].items():
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        try:
            actual_value = int(actual)
        except ValueError:
            return ('iteration_value_type', (key, actual))
        if actual_value != int(value):
            return ('iteration_mismatch', (key, value, actual))

    for key in expectations['checksums']:
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        try:
            actual_value = int(actual)
        except ValueError:
            return ('checksum_value_type', (key, actual))
        if actual_value <= 0:
            return ('nonpositive_checksum', (key, actual))
        expected_exact_value = exact_checksums.get(key)
        if expected_exact_value is not None and actual_value != expected_exact_value:
            return ('exact_checksum_mismatch', (key, expected_exact_value, actual_value))

    if missing:
        return ('missing', missing)

    return ('pass', parsed)


def print_command_output(label: str, output: str | None) -> None:
    if not output:
        return
    print(f'{label}_START')
    text = output.rstrip('\n')
    if text:
        print(text)
    print(f'{label}_END')


def run_self_test() -> None:
    expectations = {
        'status': 'pass',
        'iterations': {
            'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS': 20000,
        },
        'checksums': [
            'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM',
            'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM',
        ],
        'exact_checksums': {
            'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM': 7,
            'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM': 9,
        },
    }
    full_expectations = {
        'status': 'pass',
        'iterations': dict(EXPECTED_ITERATIONS),
        'checksums': list(EXPECTED_CHECKSUMS),
        'exact_checksums': {
            'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM': 2260000,
            'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM': 620000,
        },
    }

    ok_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
        'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=9',
    ])
    ignored_key_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
        'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=9',
        'IGNORED_KEY=1',
    ])
    duplicate_status_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
        'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=9',
    ])
    duplicate_iteration_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
        'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=9',
    ])
    duplicate_checksum_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=11',
        'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=9',
    ])
    unexpected_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
        'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=9',
        'PHASE1_BENCH_FAKE_CHECKSUM=13',
    ])
    bad_status_output = '\n'.join([
        'PHASE1_BENCH=fail',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
        'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=9',
    ])
    iteration_mismatch_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=19999',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
        'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=9',
    ])
    invalid_iteration_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=not-a-number',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
        'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=9',
    ])
    missing_checksum_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=9',
    ])
    zero_checksum_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=0',
        'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=9',
    ])
    invalid_checksum_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=not-a-number',
        'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=9',
    ])
    exact_checksum_mismatch_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=8',
        'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=9',
    ])

    kind, _ = validate_output(expectations, ok_output)
    assert kind == 'pass'

    kind, _ = validate_output(expectations, ignored_key_output)
    assert kind == 'pass'

    kind, payload = validate_output(expectations, duplicate_status_output)
    assert kind == 'duplicate'
    assert payload == ['PHASE1_BENCH']

    kind, payload = validate_output(expectations, duplicate_iteration_output)
    assert kind == 'duplicate'
    assert payload == ['PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS']

    kind, payload = validate_output(expectations, duplicate_checksum_output)
    assert kind == 'duplicate'
    assert payload == ['PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM']

    kind, payload = validate_output(expectations, unexpected_output)
    assert kind == 'unexpected'
    assert payload == ['PHASE1_BENCH_FAKE_CHECKSUM']

    kind, payload = validate_output(expectations, bad_status_output)
    assert kind == 'status'
    assert payload == ('pass', 'fail')

    kind, payload = validate_output(expectations, iteration_mismatch_output)
    assert kind == 'iteration_mismatch'
    assert payload == ('PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS', 20000, '19999')

    kind, payload = validate_output(expectations, invalid_iteration_output)
    assert kind == 'iteration_value_type'
    assert payload == ('PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS', 'not-a-number')

    kind, payload = validate_output(expectations, missing_checksum_output)
    assert kind == 'missing'
    assert payload == ['PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM']

    kind, payload = validate_output(expectations, zero_checksum_output)
    assert kind == 'nonpositive_checksum'
    assert payload == ('PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM', '0')

    kind, payload = validate_output(expectations, invalid_checksum_output)
    assert kind == 'checksum_value_type'
    assert payload == ('PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM', 'not-a-number')

    kind, payload = validate_output(expectations, exact_checksum_mismatch_output)
    assert kind == 'exact_checksum_mismatch'
    assert payload == ('PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM', 7, 8)

    kind, _ = validate_expectations(full_expectations)
    assert kind == 'pass'

    kind, payload = validate_expectations([])
    assert kind == 'expectations_type'
    assert payload == 'list'

    kind, payload = validate_expectations({'status': 'fail', 'iterations': {}, 'checksums': [], 'exact_checksums': {}})
    assert kind == 'expectations_status'
    assert payload == 'fail'

    kind, payload = validate_expectations({'status': 'pass', 'iterations': [], 'checksums': [], 'exact_checksums': {}})
    assert kind == 'expectations_iterations_type'
    assert payload == 'list'

    missing_iteration_expectations = {
        'status': 'pass',
        'iterations': dict(EXPECTED_ITERATIONS),
        'checksums': list(EXPECTED_CHECKSUMS),
        'exact_checksums': dict(full_expectations['exact_checksums']),
    }
    del missing_iteration_expectations['iterations']['PHASE1_BENCH_RBTREE_ITERATIONS']
    kind, payload = validate_expectations(missing_iteration_expectations)
    assert kind == 'expectations_missing_iterations'
    assert payload == ['PHASE1_BENCH_RBTREE_ITERATIONS']

    unexpected_iteration_expectations = {
        'status': 'pass',
        'iterations': dict(EXPECTED_ITERATIONS),
        'checksums': list(EXPECTED_CHECKSUMS),
        'exact_checksums': dict(full_expectations['exact_checksums']),
    }
    unexpected_iteration_expectations['iterations']['PHASE1_BENCH_FAKE_ITERATIONS'] = 1
    kind, payload = validate_expectations(unexpected_iteration_expectations)
    assert kind == 'expectations_unexpected_iteration'
    assert payload == 'PHASE1_BENCH_FAKE_ITERATIONS'

    wrong_iteration_value_expectations = {
        'status': 'pass',
        'iterations': dict(EXPECTED_ITERATIONS),
        'checksums': list(EXPECTED_CHECKSUMS),
        'exact_checksums': dict(full_expectations['exact_checksums']),
    }
    wrong_iteration_value_expectations['iterations']['PHASE1_BENCH_STRING_ITERATIONS'] = 1
    kind, payload = validate_expectations(wrong_iteration_value_expectations)
    assert kind == 'expectations_iteration_value'
    assert payload == ('PHASE1_BENCH_STRING_ITERATIONS', 40000, 1)

    duplicate_checksum_expectations = {
        'status': 'pass',
        'iterations': dict(EXPECTED_ITERATIONS),
        'checksums': list(EXPECTED_CHECKSUMS) + [EXPECTED_CHECKSUMS[0]],
        'exact_checksums': dict(full_expectations['exact_checksums']),
    }
    kind, payload = validate_expectations(duplicate_checksum_expectations)
    assert kind == 'expectations_duplicate_checksums'
    assert payload == [EXPECTED_CHECKSUMS[0]]

    missing_checksum_expectations = {
        'status': 'pass',
        'iterations': dict(EXPECTED_ITERATIONS),
        'checksums': list(EXPECTED_CHECKSUMS[:-1]),
        'exact_checksums': dict(full_expectations['exact_checksums']),
    }
    kind, payload = validate_expectations(missing_checksum_expectations)
    assert kind == 'expectations_missing_checksums'
    assert payload == ['PHASE1_BENCH_RBTREE_CHECKSUM']

    unexpected_checksum_expectations = {
        'status': 'pass',
        'iterations': dict(EXPECTED_ITERATIONS),
        'checksums': list(EXPECTED_CHECKSUMS) + ['PHASE1_BENCH_FAKE_CHECKSUM'],
        'exact_checksums': dict(full_expectations['exact_checksums']),
    }
    kind, payload = validate_expectations(unexpected_checksum_expectations)
    assert kind == 'expectations_unexpected_checksums'
    assert payload == ['PHASE1_BENCH_FAKE_CHECKSUM']

    missing_exact_checksum_expectations = {
        'status': 'pass',
        'iterations': dict(EXPECTED_ITERATIONS),
        'checksums': list(EXPECTED_CHECKSUMS),
        'exact_checksums': {
            'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM': 2260000,
        },
    }
    kind, payload = validate_expectations(missing_exact_checksum_expectations)
    assert kind == 'expectations_missing_exact_checksums'
    assert payload == ['PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM']

    unexpected_exact_checksum_expectations = {
        'status': 'pass',
        'iterations': dict(EXPECTED_ITERATIONS),
        'checksums': list(EXPECTED_CHECKSUMS),
        'exact_checksums': {
            'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM': 2260000,
            'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM': 620000,
            'PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM': 1,
        },
    }
    kind, payload = validate_expectations(unexpected_exact_checksum_expectations)
    assert kind == 'expectations_unexpected_exact_checksums'
    assert payload == ['PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM']

    exact_checksum_not_listed_expectations = {
        'status': 'pass',
        'iterations': dict(EXPECTED_ITERATIONS),
        'checksums': list(EXPECTED_CHECKSUMS[1:]),
        'exact_checksums': {
            'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM': 2260000,
            'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM': 620000,
        },
    }
    kind, payload = validate_expectations(exact_checksum_not_listed_expectations)
    assert kind == 'expectations_missing_checksums'
    assert payload == ['PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM']

    nonpositive_exact_checksum_expectations = {
        'status': 'pass',
        'iterations': dict(EXPECTED_ITERATIONS),
        'checksums': list(EXPECTED_CHECKSUMS),
        'exact_checksums': {
            'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM': 0,
            'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM': 620000,
        },
    }
    kind, payload = validate_expectations(nonpositive_exact_checksum_expectations)
    assert kind == 'expectations_exact_checksum_nonpositive'
    assert payload == ('PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM', 0)

    duplicate_root_key_expectations = load_expectations_text(
        '{"status":"pass","status":"fail","iterations":{"PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS":20000,"PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS":20000,"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS":20000,"PHASE1_BENCH_STRING_ITERATIONS":40000,"PHASE1_BENCH_HWEIGHT_ITERATIONS":100000,"PHASE1_BENCH_LIST_SORT_ITERATIONS":1000,"PHASE1_BENCH_RBTREE_ITERATIONS":4000},"checksums":["PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM","PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM","PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM","PHASE1_BENCH_STRING_CHECKSUM","PHASE1_BENCH_HWEIGHT_CHECKSUM","PHASE1_BENCH_LIST_SORT_CHECKSUM","PHASE1_BENCH_RBTREE_CHECKSUM"],"exact_checksums":{"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM":2260000,"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM":620000}}'
    )
    kind, payload = validate_expectations(duplicate_root_key_expectations)
    assert kind == 'expectations_duplicate_keys'
    assert payload == ['status']

    duplicate_iteration_key_expectations = load_expectations_text(
        '{"status":"pass","iterations":{"PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS":20000,"PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS":20001,"PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS":20000,"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS":20000,"PHASE1_BENCH_STRING_ITERATIONS":40000,"PHASE1_BENCH_HWEIGHT_ITERATIONS":100000,"PHASE1_BENCH_LIST_SORT_ITERATIONS":1000,"PHASE1_BENCH_RBTREE_ITERATIONS":4000},"checksums":["PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM","PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM","PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM","PHASE1_BENCH_STRING_CHECKSUM","PHASE1_BENCH_HWEIGHT_CHECKSUM","PHASE1_BENCH_LIST_SORT_CHECKSUM","PHASE1_BENCH_RBTREE_CHECKSUM"],"exact_checksums":{"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM":2260000,"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM":620000}}'
    )
    kind, payload = validate_expectations(duplicate_iteration_key_expectations)
    assert kind == 'expectations_duplicate_iteration_keys'
    assert payload == ['PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS']

    duplicate_exact_checksum_key_expectations = load_expectations_text(
        '{"status":"pass","iterations":{"PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS":20000,"PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS":20000,"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS":20000,"PHASE1_BENCH_STRING_ITERATIONS":40000,"PHASE1_BENCH_HWEIGHT_ITERATIONS":100000,"PHASE1_BENCH_LIST_SORT_ITERATIONS":1000,"PHASE1_BENCH_RBTREE_ITERATIONS":4000},"checksums":["PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM","PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM","PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM","PHASE1_BENCH_STRING_CHECKSUM","PHASE1_BENCH_HWEIGHT_CHECKSUM","PHASE1_BENCH_LIST_SORT_CHECKSUM","PHASE1_BENCH_RBTREE_CHECKSUM"],"exact_checksums":{"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM":2260000,"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM":2260001,"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM":620000}}'
    )
    kind, payload = validate_expectations(duplicate_exact_checksum_key_expectations)
    assert kind == 'expectations_duplicate_exact_checksum_keys'
    assert payload == ['PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM']

    exact_checksum_wrong_type_expectations = {
        'status': 'pass',
        'iterations': dict(EXPECTED_ITERATIONS),
        'checksums': list(EXPECTED_CHECKSUMS),
        'exact_checksums': {
            'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM': '2260000',
            'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM': 620000,
        },
    }
    kind, payload = validate_expectations(exact_checksum_wrong_type_expectations)
    assert kind == 'expectations_exact_checksum_value_type'
    assert payload == ('PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM', 'str')

    print('PHASE1_BENCH_CHECK_SELF_TEST=pass')
    print('PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT=29')


def main() -> int:
    parser = argparse.ArgumentParser(description='Run and validate the bounded Phase 1 benchmark smoke output.')
    parser.add_argument('--zig', help='Path to Zig executable')
    parser.add_argument('--self-test', action='store_true', help='Run checker self-test cases without invoking Zig.')
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        expectations = load_expectations(EXPECTATIONS)
    except json.JSONDecodeError as exc:
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_JSON_ERROR={exc.msg}')
        print(f'EXPECTATIONS_JSON_LINE={exc.lineno}')
        print(f'EXPECTATIONS_JSON_COLUMN={exc.colno}')
        return 1

    kind, payload = validate_expectations(expectations)
    if kind == 'expectations_type':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_TYPE={payload}')
        return 1
    if kind == 'expectations_status':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_STATUS={payload}')
        return 1
    if kind == 'expectations_duplicate_keys':
        print('PHASE1_BENCH_CHECK=fail')
        print('DUPLICATE_EXPECTATION_KEYS_START')
        for key in payload:
            print(key)
        print('DUPLICATE_EXPECTATION_KEYS_END')
        return 1
    if kind == 'expectations_iterations_type':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_ITERATIONS_TYPE={payload}')
        return 1
    if kind == 'expectations_duplicate_iteration_keys':
        print('PHASE1_BENCH_CHECK=fail')
        print('DUPLICATE_EXPECTATION_ITERATION_KEYS_START')
        for key in payload:
            print(key)
        print('DUPLICATE_EXPECTATION_ITERATION_KEYS_END')
        return 1
    if kind == 'expectations_iteration_key_type':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_ITERATION_KEY_TYPE={payload}')
        return 1
    if kind == 'expectations_iteration_value_type':
        key, value_type = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_ITERATION_VALUE_KEY={key}')
        print(f'EXPECTATIONS_ITERATION_VALUE_TYPE={value_type}')
        return 1
    if kind == 'expectations_unexpected_iteration':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'UNEXPECTED_EXPECTATION_ITERATION={payload}')
        return 1
    if kind == 'expectations_iteration_value':
        key, expected, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_ITERATION_VALUE_MISMATCH={key}')
        print(f'EXPECTED={expected}')
        print(f'ACTUAL={actual}')
        return 1
    if kind == 'expectations_missing_iterations':
        print('PHASE1_BENCH_CHECK=fail')
        print('MISSING_EXPECTATION_ITERATIONS_START')
        for key in payload:
            print(key)
        print('MISSING_EXPECTATION_ITERATIONS_END')
        return 1
    if kind == 'expectations_checksums_type':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_CHECKSUMS_TYPE={payload}')
        return 1
    if kind == 'expectations_checksum_type':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_CHECKSUM_TYPE={payload}')
        return 1
    if kind == 'expectations_duplicate_checksums':
        print('PHASE1_BENCH_CHECK=fail')
        print('DUPLICATE_EXPECTATION_CHECKSUMS_START')
        for key in payload:
            print(key)
        print('DUPLICATE_EXPECTATION_CHECKSUMS_END')
        return 1
    if kind == 'expectations_missing_checksums':
        print('PHASE1_BENCH_CHECK=fail')
        print('MISSING_EXPECTATION_CHECKSUMS_START')
        for key in payload:
            print(key)
        print('MISSING_EXPECTATION_CHECKSUMS_END')
        return 1
    if kind == 'expectations_unexpected_checksums':
        print('PHASE1_BENCH_CHECK=fail')
        print('UNEXPECTED_EXPECTATION_CHECKSUMS_START')
        for key in payload:
            print(key)
        print('UNEXPECTED_EXPECTATION_CHECKSUMS_END')
        return 1
    if kind == 'expectations_exact_checksums_type':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_EXACT_CHECKSUMS_TYPE={payload}')
        return 1
    if kind == 'expectations_duplicate_exact_checksum_keys':
        print('PHASE1_BENCH_CHECK=fail')
        print('DUPLICATE_EXPECTATION_EXACT_CHECKSUM_KEYS_START')
        for key in payload:
            print(key)
        print('DUPLICATE_EXPECTATION_EXACT_CHECKSUM_KEYS_END')
        return 1
    if kind == 'expectations_exact_checksum_key_type':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_EXACT_CHECKSUM_KEY_TYPE={payload}')
        return 1
    if kind == 'expectations_exact_checksum_value_type':
        key, value_type = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_EXACT_CHECKSUM_VALUE_KEY={key}')
        print(f'EXPECTATIONS_EXACT_CHECKSUM_VALUE_TYPE={value_type}')
        return 1
    if kind == 'expectations_exact_checksum_nonpositive':
        key, value = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_EXACT_CHECKSUM_NONPOSITIVE_KEY={key}')
        print(f'ACTUAL={value}')
        return 1
    if kind == 'expectations_exact_checksum_not_listed':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_EXACT_CHECKSUM_NOT_LISTED={payload}')
        return 1
    if kind == 'expectations_missing_exact_checksums':
        print('PHASE1_BENCH_CHECK=fail')
        print('MISSING_EXPECTATION_EXACT_CHECKSUMS_START')
        for key in payload:
            print(key)
        print('MISSING_EXPECTATION_EXACT_CHECKSUMS_END')
        return 1
    if kind == 'expectations_unexpected_exact_checksums':
        print('PHASE1_BENCH_CHECK=fail')
        print('UNEXPECTED_EXPECTATION_EXACT_CHECKSUMS_START')
        for key in payload:
            print(key)
        print('UNEXPECTED_EXPECTATION_EXACT_CHECKSUMS_END')
        return 1

    zig = find_zig(args.zig)

    result = subprocess.run(
        [zig, 'build', 'bench', '--build-file', 'zigux/tests/build.zig', '-Doptimize=ReleaseSafe'],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print('PHASE1_BENCH_CHECK=fail')
        print(f'BENCH_COMMAND_EXIT={result.returncode}')
        print_command_output('PHASE1_BENCH_STDOUT', result.stdout)
        print_command_output('PHASE1_BENCH_STDERR', result.stderr)
        return 1

    kind, payload = validate_output(expectations, result.stdout)
    if kind == 'duplicate':
        print('PHASE1_BENCH_CHECK=fail')
        print('DUPLICATE_PHASE1_BENCH_KEYS_START')
        for key in payload:
            print(key)
        print('DUPLICATE_PHASE1_BENCH_KEYS_END')
        return 1
    if kind == 'unexpected':
        print('PHASE1_BENCH_CHECK=fail')
        print('UNEXPECTED_PHASE1_BENCH_KEYS_START')
        for key in payload:
            print(key)
        print('UNEXPECTED_PHASE1_BENCH_KEYS_END')
        return 1
    if kind == 'status':
        expected, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTED_STATUS={expected}')
        print(f'ACTUAL_STATUS={actual}')
        return 1
    if kind == 'iteration_mismatch':
        key, expected, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'ITERATION_MISMATCH={key}')
        print(f'EXPECTED={expected}')
        print(f'ACTUAL={actual}')
        return 1
    if kind == 'iteration_value_type':
        key, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'ITERATION_VALUE_TYPE={key}')
        print(f'ACTUAL={actual}')
        return 1
    if kind == 'nonpositive_checksum':
        key, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'NONPOSITIVE_CHECKSUM={key}')
        print(f'ACTUAL={actual}')
        return 1
    if kind == 'checksum_value_type':
        key, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'CHECKSUM_VALUE_TYPE={key}')
        print(f'ACTUAL={actual}')
        return 1
    if kind == 'exact_checksum_mismatch':
        key, expected, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXACT_CHECKSUM_MISMATCH={key}')
        print(f'EXPECTED={expected}')
        print(f'ACTUAL={actual}')
        return 1
    if kind == 'missing':
        print('PHASE1_BENCH_CHECK=fail')
        print('MISSING_PHASE1_BENCH_KEYS_START')
        for key in payload:
            print(key)
        print('MISSING_PHASE1_BENCH_KEYS_END')
        return 1

    print('PHASE1_BENCH_CHECK=pass')
    print(f'PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}')
    print(f'PHASE1_BENCH_ZIG={zig}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

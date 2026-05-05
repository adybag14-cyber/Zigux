#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
EXPECTATIONS = ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_bench_expectations.json'


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


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


def validate_output(expectations: dict[str, object], stdout: str) -> tuple[str, object]:
    parsed, counts = parse_output(stdout)
    required_keys = {
        'PHASE1_BENCH',
        *expectations['iterations'].keys(),
        *expectations['checksums'],
    }
    duplicate = sorted(key for key in required_keys if counts.get(key, 0) > 1)
    if duplicate:
        return ('duplicate', duplicate)

    actual_status = parsed.get('PHASE1_BENCH')
    if actual_status != expectations['status']:
        return ('status', (expectations['status'], actual_status))

    missing = []
    for key, value in expectations['iterations'].items():
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        if int(actual) != int(value):
            return ('iteration_mismatch', (key, value, actual))

    for key in expectations['checksums']:
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        if int(actual) <= 0:
            return ('nonpositive_checksum', (key, actual))

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
        ],
    }

    ok_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
    ])
    duplicate_status_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
    ])
    duplicate_iteration_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
    ])
    duplicate_checksum_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=11',
    ])
    bad_status_output = '\n'.join([
        'PHASE1_BENCH=fail',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
    ])
    iteration_mismatch_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=19999',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=7',
    ])
    missing_checksum_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
    ])
    zero_checksum_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=0',
    ])

    kind, _ = validate_output(expectations, ok_output)
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

    kind, payload = validate_output(expectations, bad_status_output)
    assert kind == 'status'
    assert payload == ('pass', 'fail')

    kind, payload = validate_output(expectations, iteration_mismatch_output)
    assert kind == 'iteration_mismatch'
    assert payload == ('PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS', 20000, '19999')

    kind, payload = validate_output(expectations, missing_checksum_output)
    assert kind == 'missing'
    assert payload == ['PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM']

    kind, payload = validate_output(expectations, zero_checksum_output)
    assert kind == 'nonpositive_checksum'
    assert payload == ('PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM', '0')

    print('PHASE1_BENCH_CHECK_SELF_TEST=pass')
    print('PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT=8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Run and validate the bounded Phase 1 benchmark smoke output.')
    parser.add_argument('--zig', help='Path to Zig executable')
    parser.add_argument('--self-test', action='store_true', help='Run checker self-test cases without invoking Zig.')
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    zig = find_zig(args.zig)
    expectations = json.loads(EXPECTATIONS.read_text(encoding='utf-8'))

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
    if kind == 'nonpositive_checksum':
        key, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'NONPOSITIVE_CHECKSUM={key}')
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

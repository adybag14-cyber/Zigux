#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[2]
EXPECTATIONS = ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_bench_expectations.json'
BENCH_BUILD_FILE = 'zigux/tests/build.zig'


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    zig = shutil.which('zig')
    if zig:
        return zig
    raise SystemExit('zig not found; pass --zig or add zig to PATH')


def parse_output(stdout: str) -> tuple[dict[str, str], list[str]]:
    parsed: dict[str, str] = {}
    duplicates: set[str] = set()
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line or '=' not in line:
            continue
        key, value = line.split('=', 1)
        if key in parsed:
            duplicates.add(key)
        parsed[key] = value
    return parsed, sorted(duplicates)


def expected_metric_keys(expectations: dict[str, object]) -> set[str]:
    exact_checksums = expectations.get('exact_checksums', {})
    return (
        set(expectations['iterations'])
        | set(exact_checksums)
        | set(expectations['checksums'])
    )


def iteration_key_for_exact_checksum(key: str) -> str | None:
    if not key.endswith('_CHECKSUM'):
        return None
    return key.removesuffix('_CHECKSUM') + '_ITERATIONS'


def validate_expectations_shape(expectations: dict[str, object]) -> None:
    iterations = expectations.get('iterations')
    exact_checksums = expectations.get('exact_checksums')
    checksums = expectations.get('checksums')

    if not isinstance(iterations, dict):
        raise SystemExit('phase1-bench:expectations:iterations:expected_object')
    if not isinstance(exact_checksums, dict):
        raise SystemExit('phase1-bench:expectations:exact_checksums:expected_object')
    if not isinstance(checksums, list):
        raise SystemExit('phase1-bench:expectations:checksums:expected_list')

    reserved_key = 'PHASE1_BENCH'
    metric_groups = {
        'iterations': set(iterations),
        'exact_checksums': set(exact_checksums),
        'checksums': set(checksums),
    }
    for group_name, keys in metric_groups.items():
        for key in keys:
            if not isinstance(key, str):
                raise SystemExit(f'phase1-bench:expectations:{group_name}:non_string_key')
            if key == reserved_key:
                raise SystemExit(f'phase1-bench:expectations:{group_name}:reserved_key:{key}')
            if not key.startswith('PHASE1_BENCH_'):
                raise SystemExit(f'phase1-bench:expectations:{group_name}:bad_prefix:{key}')

    overlap = metric_groups['iterations'] & metric_groups['exact_checksums']
    if overlap:
        overlap_key = sorted(overlap)[0]
        raise SystemExit(f'phase1-bench:expectations:overlap:iterations_exact_checksums:{overlap_key}')

    overlap = metric_groups['iterations'] & metric_groups['checksums']
    if overlap:
        overlap_key = sorted(overlap)[0]
        raise SystemExit(f'phase1-bench:expectations:overlap:iterations_checksums:{overlap_key}')

    overlap = metric_groups['exact_checksums'] & metric_groups['checksums']
    if overlap:
        overlap_key = sorted(overlap)[0]
        raise SystemExit(f'phase1-bench:expectations:overlap:exact_checksums_checksums:{overlap_key}')

    optional_bitmap_checksum = next(
        (
            key
            for key in sorted(metric_groups['checksums'])
            if key.startswith('PHASE1_BENCH_BITMAP_')
        ),
        None,
    )
    if optional_bitmap_checksum is not None:
        raise SystemExit(
            'phase1-bench:expectations:checksums:bitmap_exact_required:'
            f'{optional_bitmap_checksum}'
        )

    optional_find_bit_checksum = next(
        (
            key
            for key in sorted(metric_groups['checksums'])
            if key.startswith('PHASE1_BENCH_FIND_')
        ),
        None,
    )
    if optional_find_bit_checksum is not None:
        raise SystemExit(
            'phase1-bench:expectations:checksums:find_bit_exact_required:'
            f'{optional_find_bit_checksum}'
        )

    optional_rbtree_checksum = next(
        (
            key
            for key in sorted(metric_groups['checksums'])
            if key.startswith('PHASE1_BENCH_RBTREE_')
        ),
        None,
    )
    if optional_rbtree_checksum is not None:
        raise SystemExit(
            'phase1-bench:expectations:checksums:rbtree_exact_required:'
            f'{optional_rbtree_checksum}'
        )

    for bitmap_exact_checksum in sorted(metric_groups['exact_checksums']):
        if not bitmap_exact_checksum.startswith('PHASE1_BENCH_BITMAP_'):
            continue
        iteration_key = iteration_key_for_exact_checksum(bitmap_exact_checksum)
        if iteration_key is None or iteration_key not in metric_groups['iterations']:
            raise SystemExit(
                'phase1-bench:expectations:iterations:bitmap_required:'
                f'{iteration_key or bitmap_exact_checksum}'
            )

    find_bit_required_iterations = {
        'PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS': {
            'PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM',
            'PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM',
            'PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM',
        },
        'PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS': {
            'PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM',
        },
        'PHASE1_BENCH_FIND_NEXT_ZERO_BIT_ITERATIONS': {
            'PHASE1_BENCH_FIND_NEXT_ZERO_BIT_CHECKSUM',
        },
        'PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS': {
            'PHASE1_BENCH_FIND_NEXT_AND_BIT_CHECKSUM',
        },
    }
    for iteration_key, exact_checksum_keys in find_bit_required_iterations.items():
        present_exact_checksums = metric_groups['exact_checksums'] & exact_checksum_keys
        if present_exact_checksums and iteration_key not in metric_groups['iterations']:
            checksum_key = sorted(present_exact_checksums)[0]
            raise SystemExit(
                'phase1-bench:expectations:iterations:find_bit_required:'
                f'{iteration_key}:{checksum_key}'
            )
        if iteration_key in metric_groups['iterations']:
            missing_exact_checksums = sorted(
                exact_checksum_keys - metric_groups['exact_checksums']
            )
            if missing_exact_checksums:
                raise SystemExit(
                    'phase1-bench:expectations:exact_checksums:find_bit_required:'
                    f'{iteration_key}:{missing_exact_checksums[0]}'
                )

    rbtree_exact_checksum = next(
        (
            key
            for key in sorted(metric_groups['exact_checksums'])
            if key.startswith('PHASE1_BENCH_RBTREE_')
        ),
        None,
    )
    if (
        rbtree_exact_checksum is not None
        and 'PHASE1_BENCH_RBTREE_ITERATIONS' not in metric_groups['iterations']
    ):
        raise SystemExit(
            'phase1-bench:expectations:iterations:rbtree_required:'
            'PHASE1_BENCH_RBTREE_ITERATIONS'
        )


def unexpected_phase1_bench_keys(
    parsed: dict[str, str], expectations: dict[str, object]
) -> list[str]:
    known_metrics = expected_metric_keys(expectations)
    known_metrics.add('PHASE1_BENCH')
    return sorted(
        key
        for key in parsed
        if key.startswith('PHASE1_BENCH_') and key not in known_metrics
    )


def assert_equal(label: str, actual, expected) -> None:
    if actual != expected:
        raise SystemExit(f'phase1-bench:self-test:{label}:expected={expected!r}:actual={actual!r}')


def run_self_test() -> int:
    expectations = {
        'status': 'pass',
        'iterations': {
            'PHASE1_BENCH_SAMPLE_ITERATIONS': 7,
        },
        'exact_checksums': {
            'PHASE1_BENCH_SAMPLE_CHECKSUM': 13,
        },
        'checksums': [
            'PHASE1_BENCH_OPTIONAL_CHECKSUM',
        ],
    }

    parsed, duplicates = parse_output(
        '\n'.join([
            'noise',
            'PHASE1_BENCH=pass',
            'PHASE1_BENCH_SAMPLE_ITERATIONS=7',
            'PHASE1_BENCH_SAMPLE_CHECKSUM=13',
            'PHASE1_BENCH_OPTIONAL_CHECKSUM=19',
            'PHASE1_BENCH_SAMPLE_CHECKSUM=23',
            '',
        ])
    )
    assert_equal('duplicate_keys', duplicates, ['PHASE1_BENCH_SAMPLE_CHECKSUM'])
    assert_equal('parse_output_overwrite', parsed['PHASE1_BENCH_SAMPLE_CHECKSUM'], '23')
    assert_equal(
        'expected_metric_keys',
        expected_metric_keys(expectations),
        {
            'PHASE1_BENCH_SAMPLE_ITERATIONS',
            'PHASE1_BENCH_SAMPLE_CHECKSUM',
            'PHASE1_BENCH_OPTIONAL_CHECKSUM',
        },
    )
    assert_equal(
        'iteration_key_for_exact_checksum',
        iteration_key_for_exact_checksum('PHASE1_BENCH_BITMAP_COPY_CHECKSUM'),
        'PHASE1_BENCH_BITMAP_COPY_ITERATIONS',
    )
    assert_equal(
        'unexpected_keys_empty',
        unexpected_phase1_bench_keys(
            {
                'PHASE1_BENCH': 'pass',
                'PHASE1_BENCH_SAMPLE_ITERATIONS': '7',
                'PHASE1_BENCH_SAMPLE_CHECKSUM': '13',
                'PHASE1_BENCH_OPTIONAL_CHECKSUM': '19',
            },
            expectations,
        ),
        [],
    )
    assert_equal(
        'unexpected_keys_sorted',
        unexpected_phase1_bench_keys(
            {
                'PHASE1_BENCH': 'pass',
                'PHASE1_BENCH_ZETA': '1',
                'PHASE1_BENCH_ALPHA': '2',
            },
            expectations,
        ),
        ['PHASE1_BENCH_ALPHA', 'PHASE1_BENCH_ZETA'],
    )
    bitmap_expectations = {
        'status': 'pass',
        'iterations': {
            'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS': 20000,
        },
        'exact_checksums': {
            'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM': 2260000,
        },
        'checksums': [],
    }
    assert_equal(
        'unexpected_bitmap_alias_metric',
        unexpected_phase1_bench_keys(
            {
                'PHASE1_BENCH': 'pass',
                'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS': '20000',
                'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM': '2260000',
                'PHASE1_BENCH_BITMAP_ALIAS_CHECKSUM': '5',
            },
            bitmap_expectations,
        ),
        ['PHASE1_BENCH_BITMAP_ALIAS_CHECKSUM'],
    )
    find_bit_expectations = {
        'status': 'pass',
        'iterations': {
            'PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS': 20000,
            'PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS': 20000,
            'PHASE1_BENCH_FIND_NEXT_ZERO_BIT_ITERATIONS': 20000,
            'PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS': 20000,
        },
        'exact_checksums': {
            'PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM': 15621472,
            'PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM': 17862764,
            'PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM': 8124000,
            'PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM': 2200000,
            'PHASE1_BENCH_FIND_NEXT_ZERO_BIT_CHECKSUM': 1929133,
            'PHASE1_BENCH_FIND_NEXT_AND_BIT_CHECKSUM': 1925492,
        },
        'checksums': [],
    }
    assert_equal(
        'unexpected_find_bit_metric',
        unexpected_phase1_bench_keys(
            {
                'PHASE1_BENCH': 'pass',
                'PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS': '20000',
                'PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS': '20000',
                'PHASE1_BENCH_FIND_NEXT_ZERO_BIT_ITERATIONS': '20000',
                'PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS': '20000',
                'PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM': '15621472',
                'PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM': '17862764',
                'PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM': '8124000',
                'PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM': '2200000',
                'PHASE1_BENCH_FIND_NEXT_ZERO_BIT_CHECKSUM': '1929133',
                'PHASE1_BENCH_FIND_NEXT_AND_BIT_CHECKSUM': '1925492',
                'PHASE1_BENCH_FIND_INCLUSIVE_TAIL_CHECKSUM': '7',
            },
            find_bit_expectations,
        ),
        ['PHASE1_BENCH_FIND_INCLUSIVE_TAIL_CHECKSUM'],
    )
    rbtree_expectations = {
        'status': 'pass',
        'iterations': {
            'PHASE1_BENCH_RBTREE_ITERATIONS': 4000,
        },
        'exact_checksums': {
            'PHASE1_BENCH_RBTREE_CHECKSUM': 1308000,
            'PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM': 1188000,
            'PHASE1_BENCH_RBTREE_CACHED_CHECKSUM': 196000,
            'PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM': 3484000,
            'PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM': 1488000,
        },
        'checksums': [],
    }
    assert_equal(
        'unexpected_rbtree_metric',
        unexpected_phase1_bench_keys(
            {
                'PHASE1_BENCH': 'pass',
                'PHASE1_BENCH_RBTREE_ITERATIONS': '4000',
                'PHASE1_BENCH_RBTREE_CHECKSUM': '1308000',
                'PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM': '1188000',
                'PHASE1_BENCH_RBTREE_CACHED_CHECKSUM': '196000',
                'PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM': '3484000',
                'PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM': '1488000',
                'PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM': '7',
            },
            rbtree_expectations,
        ),
        ['PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM'],
    )
    assert_equal('find_zig_explicit', find_zig('/tmp/zig-self-test'), '/tmp/zig-self-test')

    validate_expectations_shape(expectations)
    validate_expectations_shape(bitmap_expectations)
    validate_expectations_shape(find_bit_expectations)
    validate_expectations_shape(rbtree_expectations)

    invalid_overlap = {
        **expectations,
        'checksums': ['PHASE1_BENCH_SAMPLE_CHECKSUM'],
    }
    try:
        validate_expectations_shape(invalid_overlap)
    except SystemExit as exc:
        assert_equal(
            'invalid_overlap',
            str(exc),
            'phase1-bench:expectations:overlap:exact_checksums_checksums:PHASE1_BENCH_SAMPLE_CHECKSUM',
        )
    else:
        raise SystemExit('phase1-bench:self-test:invalid_overlap:unexpected_pass')

    invalid_prefix = {
        **expectations,
        'iterations': {
            'BENCH_SAMPLE_ITERATIONS': 7,
        },
    }
    try:
        validate_expectations_shape(invalid_prefix)
    except SystemExit as exc:
        assert_equal(
            'invalid_prefix',
            str(exc),
            'phase1-bench:expectations:iterations:bad_prefix:BENCH_SAMPLE_ITERATIONS',
        )
    else:
        raise SystemExit('phase1-bench:self-test:invalid_prefix:unexpected_pass')

    invalid_reserved = {
        **expectations,
        'checksums': ['PHASE1_BENCH'],
    }
    try:
        validate_expectations_shape(invalid_reserved)
    except SystemExit as exc:
        assert_equal(
            'invalid_reserved',
            str(exc),
            'phase1-bench:expectations:checksums:reserved_key:PHASE1_BENCH',
        )
    else:
        raise SystemExit('phase1-bench:self-test:invalid_reserved:unexpected_pass')

    invalid_bitmap_optional = {
        **bitmap_expectations,
        'exact_checksums': {},
        'checksums': ['PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM'],
    }
    try:
        validate_expectations_shape(invalid_bitmap_optional)
    except SystemExit as exc:
        assert_equal(
            'invalid_bitmap_optional',
            str(exc),
            'phase1-bench:expectations:checksums:bitmap_exact_required:PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM',
        )
    else:
        raise SystemExit('phase1-bench:self-test:invalid_bitmap_optional:unexpected_pass')

    invalid_find_bit_missing_exact_checksum = {
        **find_bit_expectations,
        'exact_checksums': {
            key: value
            for key, value in find_bit_expectations['exact_checksums'].items()
            if key != 'PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM'
        },
    }
    try:
        validate_expectations_shape(invalid_find_bit_missing_exact_checksum)
    except SystemExit as exc:
        assert_equal(
            'invalid_find_bit_missing_exact_checksum',
            str(exc),
            'phase1-bench:expectations:exact_checksums:find_bit_required:PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS:PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM',
        )
    else:
        raise SystemExit('phase1-bench:self-test:invalid_find_bit_missing_exact_checksum:unexpected_pass')

    invalid_find_bit_optional = {
        **find_bit_expectations,
        'exact_checksums': {
            key: value
            for key, value in find_bit_expectations['exact_checksums'].items()
            if key != 'PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM'
        },
        'checksums': ['PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM'],
    }
    try:
        validate_expectations_shape(invalid_find_bit_optional)
    except SystemExit as exc:
        assert_equal(
            'invalid_find_bit_optional',
            str(exc),
            'phase1-bench:expectations:checksums:find_bit_exact_required:PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM',
        )
    else:
        raise SystemExit('phase1-bench:self-test:invalid_find_bit_optional:unexpected_pass')

    invalid_find_bit_missing_next_iterations = {
        **find_bit_expectations,
        'iterations': {
            'PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS': 20000,
            'PHASE1_BENCH_FIND_NEXT_ZERO_BIT_ITERATIONS': 20000,
            'PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS': 20000,
        },
    }
    try:
        validate_expectations_shape(invalid_find_bit_missing_next_iterations)
    except SystemExit as exc:
        assert_equal(
            'invalid_find_bit_missing_next_iterations',
            str(exc),
            'phase1-bench:expectations:iterations:find_bit_required:PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS:PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM',
        )
    else:
        raise SystemExit('phase1-bench:self-test:invalid_find_bit_missing_next_iterations:unexpected_pass')

    invalid_find_bit_missing_zero_iterations = {
        **find_bit_expectations,
        'iterations': {
            'PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS': 20000,
            'PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS': 20000,
            'PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS': 20000,
        },
    }
    try:
        validate_expectations_shape(invalid_find_bit_missing_zero_iterations)
    except SystemExit as exc:
        assert_equal(
            'invalid_find_bit_missing_zero_iterations',
            str(exc),
            'phase1-bench:expectations:iterations:find_bit_required:PHASE1_BENCH_FIND_NEXT_ZERO_BIT_ITERATIONS:PHASE1_BENCH_FIND_NEXT_ZERO_BIT_CHECKSUM',
        )
    else:
        raise SystemExit('phase1-bench:self-test:invalid_find_bit_missing_zero_iterations:unexpected_pass')

    invalid_rbtree_optional = {
        **rbtree_expectations,
        'exact_checksums': {
            key: value
            for key, value in rbtree_expectations['exact_checksums'].items()
            if key != 'PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM'
        },
        'checksums': ['PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM'],
    }
    try:
        validate_expectations_shape(invalid_rbtree_optional)
    except SystemExit as exc:
        assert_equal(
            'invalid_rbtree_optional',
            str(exc),
            'phase1-bench:expectations:checksums:rbtree_exact_required:PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM',
        )
    else:
        raise SystemExit('phase1-bench:self-test:invalid_rbtree_optional:unexpected_pass')

    invalid_rbtree_missing_iterations = {
        **rbtree_expectations,
        'iterations': {},
    }
    try:
        validate_expectations_shape(invalid_rbtree_missing_iterations)
    except SystemExit as exc:
        assert_equal(
            'invalid_rbtree_missing_iterations',
            str(exc),
            'phase1-bench:expectations:iterations:rbtree_required:PHASE1_BENCH_RBTREE_ITERATIONS',
        )
    else:
        raise SystemExit('phase1-bench:self-test:invalid_rbtree_missing_iterations:unexpected_pass')

    print('PHASE1_BENCH_SELF_TEST=pass')
    print('PHASE1_BENCH_SELF_TEST_CASE_COUNT=19')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Run and validate the bounded Phase 1 benchmark smoke output.')
    parser.add_argument('--zig', help='Path to Zig executable')
    parser.add_argument('--self-test', action='store_true', help='Run built-in parser and manifest checks')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    zig = find_zig(args.zig)
    expectations = json.loads(EXPECTATIONS.read_text(encoding='utf-8'))
    validate_expectations_shape(expectations)

    result = run(
        [zig, 'build', 'bench', '--build-file', BENCH_BUILD_FILE, '-Doptimize=ReleaseSafe'],
        cwd=str(ROOT),
        capture_output=True,
    )

    parsed, duplicates = parse_output(result.stdout)

    if duplicates:
        print('PHASE1_BENCH_CHECK=fail')
        print('DUPLICATE_PHASE1_BENCH_KEYS_START')
        for key in duplicates:
            print(key)
        print('DUPLICATE_PHASE1_BENCH_KEYS_END')
        return 1

    if parsed.get('PHASE1_BENCH') != expectations['status']:
        print('PHASE1_BENCH_CHECK=fail')
        print(f"EXPECTED_STATUS={expectations['status']}")
        print(f"ACTUAL_STATUS={parsed.get('PHASE1_BENCH')}")
        return 1

    unexpected_keys = unexpected_phase1_bench_keys(parsed, expectations)
    if unexpected_keys:
        print('PHASE1_BENCH_CHECK=fail')
        print('UNDECLARED_PHASE1_BENCH_KEYS_START')
        for key in unexpected_keys:
            print(key)
        print('UNDECLARED_PHASE1_BENCH_KEYS_END')
        return 1

    missing = []
    for key, value in expectations['iterations'].items():
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        if int(actual) != int(value):
            print('PHASE1_BENCH_CHECK=fail')
            print(f'ITERATION_MISMATCH={key}')
            print(f'EXPECTED={value}')
            print(f'ACTUAL={actual}')
            return 1

    for key, value in expectations.get('exact_checksums', {}).items():
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        if int(actual) != int(value):
            print('PHASE1_BENCH_CHECK=fail')
            print(f'CHECKSUM_MISMATCH={key}')
            print(f'EXPECTED={value}')
            print(f'ACTUAL={actual}')
            return 1

    for key in expectations['checksums']:
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        if int(actual) <= 0:
            print('PHASE1_BENCH_CHECK=fail')
            print(f'NONPOSITIVE_CHECKSUM={key}')
            print(f'ACTUAL={actual}')
            return 1

    if missing:
        print('PHASE1_BENCH_CHECK=fail')
        print('MISSING_PHASE1_BENCH_KEYS_START')
        for key in missing:
            print(key)
        print('MISSING_PHASE1_BENCH_KEYS_END')
        return 1

    print('PHASE1_BENCH_CHECK=pass')
    print(f'PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}')
    print(f'PHASE1_BENCH_ZIG={zig}')
    print(f'PHASE1_BENCH_BUILD_FILE={BENCH_BUILD_FILE}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
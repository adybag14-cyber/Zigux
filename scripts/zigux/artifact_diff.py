#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def canonical_json(path: Path):
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValueError(f'{path}:{exc.lineno}:{exc.colno}: {exc.msg}') from exc


def sha256_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_artifacts(mode: str, expected: Path, actual: Path) -> tuple[bool, dict[str, object]]:
    details: dict[str, object] = {
        'mode': mode,
        'expected': str(expected),
        'actual': str(actual),
    }

    if not expected.exists() or not actual.exists():
        details['expected_exists'] = expected.exists()
        details['actual_exists'] = actual.exists()
        return False, details

    if mode == 'text':
        expected_value = read_text(expected)
        actual_value = read_text(actual)
    elif mode == 'json':
        try:
            expected_value = canonical_json(expected)
        except ValueError as exc:
            details['expected_json_error'] = str(exc)
            return False, details
        try:
            actual_value = canonical_json(actual)
        except ValueError as exc:
            details['actual_json_error'] = str(exc)
            return False, details
    else:
        expected_value = sha256_digest(expected)
        actual_value = sha256_digest(actual)

    if mode == 'sha256':
        details['expected_sha256'] = expected_value
        details['actual_sha256'] = actual_value

    return expected_value == actual_value, details


def emit_result(matched: bool, details: dict[str, object]) -> int:
    if not matched:
        print('ARTIFACT_DIFF=fail')
        if 'mode' in details:
            print(f"MODE={details['mode']}")
        if 'expected' in details:
            print(f"EXPECTED={details['expected']}")
        if 'actual' in details:
            print(f"ACTUAL={details['actual']}")
        if 'expected_exists' in details:
            print(f"EXPECTED_EXISTS={details['expected_exists']}")
        if 'actual_exists' in details:
            print(f"ACTUAL_EXISTS={details['actual_exists']}")
        if 'expected_json_error' in details:
            print(f"EXPECTED_JSON_ERROR={details['expected_json_error']}")
        if 'actual_json_error' in details:
            print(f"ACTUAL_JSON_ERROR={details['actual_json_error']}")
        if 'expected_sha256' in details:
            print(f"EXPECTED_SHA256={details['expected_sha256']}")
        if 'actual_sha256' in details:
            print(f"ACTUAL_SHA256={details['actual_sha256']}")
        return 1

    print('ARTIFACT_DIFF=pass')
    print(f"MODE={details['mode']}")
    print(f"EXPECTED={details['expected']}")
    print(f"ACTUAL={details['actual']}")
    if 'expected_sha256' in details:
        print(f"SHA256={details['expected_sha256']}")
    return 0


def capture_emit_result(matched: bool, details: dict[str, object]) -> tuple[int, list[str]]:
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        exit_code = emit_result(matched, details)
    return exit_code, stream.getvalue().splitlines()


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_artifact_diff_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        text_a = tmp_dir / 'text-a.txt'
        text_b = tmp_dir / 'text-b.txt'
        json_a = tmp_dir / 'json-a.json'
        json_b = tmp_dir / 'json-b.json'
        invalid_json = tmp_dir / 'json-invalid.json'
        blob_a = tmp_dir / 'blob-a.bin'
        blob_b = tmp_dir / 'blob-b.bin'
        missing = tmp_dir / 'missing.txt'

        text_a.write_text('alpha\nbeta\n', encoding='utf-8', newline='\n')
        text_b.write_text('alpha\nbeta\n', encoding='utf-8', newline='\n')
        matched, details = compare_artifacts('text', text_a, text_b)
        assert matched
        assert details['mode'] == 'text'
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 0
        assert lines == [
            'ARTIFACT_DIFF=pass',
            'MODE=text',
            f'EXPECTED={text_a}',
            f'ACTUAL={text_b}',
        ]

        text_b.write_text('alpha\nBETA\n', encoding='utf-8', newline='\n')
        matched, details = compare_artifacts('text', text_a, text_b)
        assert not matched
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == [
            'ARTIFACT_DIFF=fail',
            'MODE=text',
            f'EXPECTED={text_a}',
            f'ACTUAL={text_b}',
        ]

        json_a.write_text('{"alpha": 1, "beta": [2, 3]}\n', encoding='utf-8', newline='\n')
        json_b.write_text('{\n  "beta": [2, 3],\n  "alpha": 1\n}\n', encoding='utf-8', newline='\n')
        matched, details = compare_artifacts('json', json_a, json_b)
        assert matched
        assert details['mode'] == 'json'
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 0
        assert lines == [
            'ARTIFACT_DIFF=pass',
            'MODE=json',
            f'EXPECTED={json_a}',
            f'ACTUAL={json_b}',
        ]

        invalid_json.write_text('{"alpha": 1,\n', encoding='utf-8', newline='\n')
        matched, details = compare_artifacts('json', invalid_json, json_a)
        assert not matched
        assert str(invalid_json) in details['expected_json_error']
        assert 'line 2 column 1' not in details['expected_json_error']

        matched, details = compare_artifacts('json', json_a, invalid_json)
        assert not matched
        assert str(invalid_json) in details['actual_json_error']

        blob_a.write_bytes(b'zigux-artifact-diff')
        blob_b.write_bytes(b'zigux-artifact-diff')
        matched, details = compare_artifacts('sha256', blob_a, blob_b)
        assert matched
        assert details['expected_sha256'] == details['actual_sha256']
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 0
        assert lines == [
            'ARTIFACT_DIFF=pass',
            'MODE=sha256',
            f'EXPECTED={blob_a}',
            f'ACTUAL={blob_b}',
            f"SHA256={details['expected_sha256']}",
        ]

        matched, details = compare_artifacts('text', missing, text_a)
        assert not matched
        assert details['expected_exists'] is False
        assert details['actual_exists'] is True
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == [
            'ARTIFACT_DIFF=fail',
            'MODE=text',
            f'EXPECTED={missing}',
            f'ACTUAL={text_a}',
            'EXPECTED_EXISTS=False',
            'ACTUAL_EXISTS=True',
        ]

    print('ARTIFACT_DIFF_SELF_TEST=pass')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Compare two artifacts in a stable mode.')
    parser.add_argument('--mode', choices=['text', 'json', 'sha256'])
    parser.add_argument('--self-test', action='store_true', help='Run built-in deterministic comparison checks.')
    parser.add_argument('expected', nargs='?')
    parser.add_argument('actual', nargs='?')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.mode is None or args.expected is None or args.actual is None:
        parser.error('--mode, expected, and actual are required unless --self-test is set')

    matched, details = compare_artifacts(args.mode, Path(args.expected), Path(args.actual))
    return emit_result(matched, details)


if __name__ == '__main__':
    raise SystemExit(main())
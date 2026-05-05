#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def canonical_json(path: Path):
    return json.loads(read_text(path))


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
            actual_value = canonical_json(actual)
        except json.JSONDecodeError:
            return False, details
    else:
        expected_value = sha256_digest(expected)
        actual_value = sha256_digest(actual)

    if mode == 'sha256':
        details['expected_sha256'] = expected_value
        details['actual_sha256'] = actual_value

    return expected_value == actual_value, details


def render_result_lines(matched: bool, details: dict[str, object]) -> list[str]:
    lines = ['ARTIFACT_DIFF=pass' if matched else 'ARTIFACT_DIFF=fail']
    if 'mode' in details:
        lines.append(f"MODE={details['mode']}")
    if 'expected' in details:
        lines.append(f"EXPECTED={details['expected']}")
    if 'actual' in details:
        lines.append(f"ACTUAL={details['actual']}")

    if not matched:
        if 'expected_exists' in details:
            lines.append(f"EXPECTED_EXISTS={details['expected_exists']}")
        if 'actual_exists' in details:
            lines.append(f"ACTUAL_EXISTS={details['actual_exists']}")
        if 'expected_sha256' in details:
            lines.append(f"EXPECTED_SHA256={details['expected_sha256']}")
        if 'actual_sha256' in details:
            lines.append(f"ACTUAL_SHA256={details['actual_sha256']}")
        return lines

    if 'expected_sha256' in details:
        lines.append(f"SHA256={details['expected_sha256']}")
    return lines


def emit_result(matched: bool, details: dict[str, object]) -> int:
    for line in render_result_lines(matched, details):
        print(line)
    if not matched:
        return 1
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_artifact_diff_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        text_a = tmp_dir / 'text-a.txt'
        text_b = tmp_dir / 'text-b.txt'
        json_a = tmp_dir / 'json-a.json'
        json_b = tmp_dir / 'json-b.json'
        blob_a = tmp_dir / 'blob-a.bin'
        blob_b = tmp_dir / 'blob-b.bin'
        missing = tmp_dir / 'missing.txt'

        text_a.write_text('alpha\nbeta\n', encoding='utf-8', newline='\n')
        text_b.write_text('alpha\nbeta\n', encoding='utf-8', newline='\n')
        matched, details = compare_artifacts('text', text_a, text_b)
        assert matched
        assert details['mode'] == 'text'
        assert render_result_lines(matched, details) == [
            'ARTIFACT_DIFF=pass',
            'MODE=text',
            f'EXPECTED={text_a}',
            f'ACTUAL={text_b}',
        ]

        text_b.write_text('alpha\nBETA\n', encoding='utf-8', newline='\n')
        matched, details = compare_artifacts('text', text_a, text_b)
        assert not matched
        assert render_result_lines(matched, details) == [
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
        assert render_result_lines(matched, details) == [
            'ARTIFACT_DIFF=pass',
            'MODE=json',
            f'EXPECTED={json_a}',
            f'ACTUAL={json_b}',
        ]

        json_b.write_text('{"beta": [2, }\n', encoding='utf-8', newline='\n')
        matched, details = compare_artifacts('json', json_a, json_b)
        assert not matched
        assert details['mode'] == 'json'
        assert render_result_lines(matched, details) == [
            'ARTIFACT_DIFF=fail',
            'MODE=json',
            f'EXPECTED={json_a}',
            f'ACTUAL={json_b}',
        ]

        blob_a.write_bytes(b'zigux-artifact-diff')
        blob_b.write_bytes(b'zigux-artifact-diff')
        matched, details = compare_artifacts('sha256', blob_a, blob_b)
        assert matched
        assert details['expected_sha256'] == details['actual_sha256']
        assert render_result_lines(matched, details) == [
            'ARTIFACT_DIFF=pass',
            'MODE=sha256',
            f'EXPECTED={blob_a}',
            f'ACTUAL={blob_b}',
            f"SHA256={details['expected_sha256']}",
        ]

        blob_b.write_bytes(b'zigux-artifact-DRIFT')
        matched, details = compare_artifacts('sha256', blob_a, blob_b)
        assert not matched
        assert details['expected_sha256'] != details['actual_sha256']
        assert render_result_lines(matched, details) == [
            'ARTIFACT_DIFF=fail',
            'MODE=sha256',
            f'EXPECTED={blob_a}',
            f'ACTUAL={blob_b}',
            f"EXPECTED_SHA256={details['expected_sha256']}",
            f"ACTUAL_SHA256={details['actual_sha256']}",
        ]

        matched, details = compare_artifacts('text', missing, text_a)
        assert not matched
        assert details['expected_exists'] is False
        assert details['actual_exists'] is True
        assert render_result_lines(matched, details) == [
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

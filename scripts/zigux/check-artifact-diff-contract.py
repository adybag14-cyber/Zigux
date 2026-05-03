#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF = ROOT / 'scripts' / 'zigux' / 'artifact_diff.py'
EXPECTED_CONTRACT_CASES = [
    'helper_self_test',
    'helper_self_test_repeat',
    'cli_missing_required_args',
    'text_pass',
    'text_pass_repeat',
    'text_mismatch',
    'text_missing_expected',
    'text_missing_actual',
    'text_missing_both',
    'json_pass',
    'json_mismatch',
    'json_mismatch_repeat',
    'json_missing_expected',
    'json_missing_actual',
    'json_missing_both',
    'json_invalid_expected',
    'json_invalid_actual',
    'json_invalid_both',
    'sha256_pass',
    'sha256_missing_expected',
    'sha256_missing_actual',
    'sha256_missing_both',
    'sha256_drift',
    'sha256_drift_repeat',
]
REPEAT_CONTRACT_CASES = [
    'helper_self_test_repeat',
    'text_pass_repeat',
    'json_mismatch_repeat',
    'sha256_drift_repeat',
]
BASE_CONTRACT_CASES = [
    case for case in EXPECTED_CONTRACT_CASES if case not in REPEAT_CONTRACT_CASES
]


def run_contract_case(
    args: list[str],
    expected_exit: int,
    expected_lines: list[str],
    *,
    repeat_count: int = 1,
) -> None:
    if repeat_count < 1:
        raise ValueError(f'repeat_count must be positive, got {repeat_count}')

    for attempt in range(1, repeat_count + 1):
        completed = subprocess.run(
            [sys.executable, str(ARTIFACT_DIFF), *args],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        lines = completed.stdout.splitlines()
        if completed.returncode != expected_exit:
            raise AssertionError(
                f'attempt {attempt}: expected exit {expected_exit}, got {completed.returncode}: {lines}'
            )
        if lines != expected_lines:
            raise AssertionError(f'attempt {attempt}: unexpected output lines: {lines}')
        if completed.stderr:
            raise AssertionError(f'attempt {attempt}: unexpected stderr: {completed.stderr!r}')


def run_error_contract_case(
    args: list[str],
    expected_exit: int,
    expected_stdout_lines: list[str],
    *,
    expected_stderr_markers: list[str],
    expected_stderr_last_line: str,
) -> None:
    completed = subprocess.run(
        [sys.executable, str(ARTIFACT_DIFF), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    stdout_lines = completed.stdout.splitlines()
    stderr_lines = completed.stderr.splitlines()
    stderr_text = completed.stderr
    if completed.returncode != expected_exit:
        raise AssertionError(
            f'expected exit {expected_exit}, got {completed.returncode}: stdout={stdout_lines} stderr={stderr_lines}'
        )
    if stdout_lines != expected_stdout_lines:
        raise AssertionError(f'unexpected stdout lines: {stdout_lines}')
    if not stderr_lines:
        raise AssertionError('expected parser stderr output, got none')
    for marker in expected_stderr_markers:
        if marker not in stderr_text:
            raise AssertionError(
                f'missing stderr marker {marker!r} in parser contract output: {stderr_lines}'
            )
    if stderr_lines[-1] != expected_stderr_last_line:
        raise AssertionError(
            'unexpected parser error line: '
            f'expected {expected_stderr_last_line!r}, got {stderr_lines[-1]!r}'
        )


def assert_contract_catalog_shape() -> None:
    if len(set(EXPECTED_CONTRACT_CASES)) != len(EXPECTED_CONTRACT_CASES):
        raise AssertionError(
            f'artifact-diff contract cases must stay unique: {EXPECTED_CONTRACT_CASES}'
        )
    if len(set(REPEAT_CONTRACT_CASES)) != len(REPEAT_CONTRACT_CASES):
        raise AssertionError(
            f'artifact-diff repeat contract cases must stay unique: {REPEAT_CONTRACT_CASES}'
        )
    missing_repeat_cases = [
        case for case in REPEAT_CONTRACT_CASES if case not in EXPECTED_CONTRACT_CASES
    ]
    if missing_repeat_cases:
        raise AssertionError(
            'artifact-diff repeat contract cases drifted outside the published catalog: '
            f'{missing_repeat_cases}'
        )
    if len(BASE_CONTRACT_CASES) + len(REPEAT_CONTRACT_CASES) != len(
        EXPECTED_CONTRACT_CASES
    ):
        raise AssertionError(
            'artifact-diff base and repeat case partition drifted: '
            f'base={BASE_CONTRACT_CASES} repeat={REPEAT_CONTRACT_CASES} '
            f'all={EXPECTED_CONTRACT_CASES}'
        )


def main() -> int:
    assert_contract_catalog_shape()
    covered_cases: list[str] = []

    # Replaying the helper's own self-test twice keeps the published case
    # catalog and count deterministic, not just the leaf comparison modes.
    run_contract_case(
        ['--self-test'],
        0,
        [
            'ARTIFACT_DIFF_SELF_TEST=pass',
            'ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=18',
            'ARTIFACT_DIFF_SELF_TEST_CASES=text_pass,text_mismatch,json_pass,json_mismatch,json_invalid_expected,json_invalid_actual,json_invalid_both,json_missing_expected,json_missing_actual,json_missing_both,sha256_pass,sha256_drift,text_missing_expected,text_missing_actual,text_missing_both,sha256_missing_expected,sha256_missing_actual,sha256_missing_both',
        ],
        repeat_count=2,
    )
    covered_cases.append('helper_self_test')
    covered_cases.append('helper_self_test_repeat')

    run_error_contract_case(
        [],
        2,
        [],
        expected_stderr_markers=[
            'usage: artifact_diff.py',
            '--mode {text,json,sha256}',
            'artifact_diff.py: error: --mode, expected, and actual are required unless --self-test is set',
        ],
        expected_stderr_last_line='artifact_diff.py: error: --mode, expected, and actual are required unless --self-test is set',
    )
    covered_cases.append('cli_missing_required_args')

    with tempfile.TemporaryDirectory(prefix='zigux_artifact_diff_contract_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        expected = tmp_dir / 'expected.txt'
        actual = tmp_dir / 'actual.txt'
        missing = tmp_dir / 'missing.txt'
        other_missing = tmp_dir / 'other-missing.txt'
        expected_json = tmp_dir / 'expected.json'
        actual_json = tmp_dir / 'actual.json'
        actual_json_mismatch = tmp_dir / 'actual-mismatch.json'
        invalid_expected_json = tmp_dir / 'expected-invalid.json'
        invalid_actual_json = tmp_dir / 'actual-invalid.json'
        blob_a = tmp_dir / 'blob-a.bin'
        blob_b = tmp_dir / 'blob-b.bin'

        expected.write_text('alpha\nbeta\n', encoding='utf-8', newline='\n')
        actual.write_text('alpha\nbeta\n', encoding='utf-8', newline='\n')
        run_contract_case(
            ['--mode', 'text', str(expected), str(actual)],
            0,
            [
                'ARTIFACT_DIFF=pass',
                'MODE=text',
                f'EXPECTED={expected}',
                f'ACTUAL={actual}',
            ],
            repeat_count=2,
        )
        covered_cases.append('text_pass')
        covered_cases.append('text_pass_repeat')

        actual.write_text('alpha\nBETA\n', encoding='utf-8', newline='\n')
        run_contract_case(
            ['--mode', 'text', str(expected), str(actual)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=text',
                f'EXPECTED={expected}',
                f'ACTUAL={actual}',
            ],
        )
        covered_cases.append('text_mismatch')
        actual.write_text('alpha\nbeta\n', encoding='utf-8', newline='\n')

        run_contract_case(
            ['--mode', 'text', str(missing), str(actual)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=text',
                f'EXPECTED={missing}',
                f'ACTUAL={actual}',
                'EXPECTED_EXISTS=False',
                'ACTUAL_EXISTS=True',
            ],
        )
        covered_cases.append('text_missing_expected')

        run_contract_case(
            ['--mode', 'text', str(expected), str(missing)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=text',
                f'EXPECTED={expected}',
                f'ACTUAL={missing}',
                'EXPECTED_EXISTS=True',
                'ACTUAL_EXISTS=False',
            ],
        )
        covered_cases.append('text_missing_actual')

        run_contract_case(
            ['--mode', 'text', str(missing), str(other_missing)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=text',
                f'EXPECTED={missing}',
                f'ACTUAL={other_missing}',
                'EXPECTED_EXISTS=False',
                'ACTUAL_EXISTS=False',
            ],
        )
        covered_cases.append('text_missing_both')

        expected_json.write_text('{"alpha": 1, "beta": [2, 3]}\n', encoding='utf-8', newline='\n')
        actual_json.write_text('{\n  "beta": [2, 3],\n  "alpha": 1\n}\n', encoding='utf-8', newline='\n')
        actual_json_mismatch.write_text('{"alpha": 1, "beta": [2, 4]}\n', encoding='utf-8', newline='\n')
        invalid_expected_json.write_text('{"alpha": 1,\n', encoding='utf-8', newline='\n')
        invalid_actual_json.write_text('{"alpha": 1,\n', encoding='utf-8', newline='\n')

        run_contract_case(
            ['--mode', 'json', str(expected_json), str(actual_json)],
            0,
            [
                'ARTIFACT_DIFF=pass',
                'MODE=json',
                f'EXPECTED={expected_json}',
                f'ACTUAL={actual_json}',
            ],
        )
        covered_cases.append('json_pass')

        run_contract_case(
            ['--mode', 'json', str(expected_json), str(actual_json_mismatch)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=json',
                f'EXPECTED={expected_json}',
                f'ACTUAL={actual_json_mismatch}',
            ],
            repeat_count=2,
        )
        covered_cases.append('json_mismatch')
        covered_cases.append('json_mismatch_repeat')

        run_contract_case(
            ['--mode', 'json', str(missing), str(actual_json)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=json',
                f'EXPECTED={missing}',
                f'ACTUAL={actual_json}',
                'EXPECTED_EXISTS=False',
                'ACTUAL_EXISTS=True',
            ],
        )
        covered_cases.append('json_missing_expected')

        run_contract_case(
            ['--mode', 'json', str(expected_json), str(missing)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=json',
                f'EXPECTED={expected_json}',
                f'ACTUAL={missing}',
                'EXPECTED_EXISTS=True',
                'ACTUAL_EXISTS=False',
            ],
        )
        covered_cases.append('json_missing_actual')

        run_contract_case(
            ['--mode', 'json', str(missing), str(other_missing)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=json',
                f'EXPECTED={missing}',
                f'ACTUAL={other_missing}',
                'EXPECTED_EXISTS=False',
                'ACTUAL_EXISTS=False',
            ],
        )
        covered_cases.append('json_missing_both')

        run_contract_case(
            ['--mode', 'json', str(invalid_expected_json), str(actual_json)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=json',
                f'EXPECTED={invalid_expected_json}',
                f'ACTUAL={actual_json}',
                f'EXPECTED_JSON_ERROR={invalid_expected_json}:2:1: Expecting property name enclosed in double quotes',
            ],
        )
        covered_cases.append('json_invalid_expected')

        run_contract_case(
            ['--mode', 'json', str(expected_json), str(invalid_actual_json)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=json',
                f'EXPECTED={expected_json}',
                f'ACTUAL={invalid_actual_json}',
                f'ACTUAL_JSON_ERROR={invalid_actual_json}:2:1: Expecting property name enclosed in double quotes',
            ],
        )
        covered_cases.append('json_invalid_actual')

        run_contract_case(
            ['--mode', 'json', str(invalid_expected_json), str(invalid_actual_json)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=json',
                f'EXPECTED={invalid_expected_json}',
                f'ACTUAL={invalid_actual_json}',
                f'EXPECTED_JSON_ERROR={invalid_expected_json}:2:1: Expecting property name enclosed in double quotes',
            ],
        )
        covered_cases.append('json_invalid_both')

        blob_a.write_bytes(b'zigux-artifact-diff')
        blob_b.write_bytes(b'zigux-artifact-diff')
        run_contract_case(
            ['--mode', 'sha256', str(blob_a), str(blob_b)],
            0,
            [
                'ARTIFACT_DIFF=pass',
                'MODE=sha256',
                f'EXPECTED={blob_a}',
                f'ACTUAL={blob_b}',
                'SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576',
            ],
        )
        covered_cases.append('sha256_pass')

        run_contract_case(
            ['--mode', 'sha256', str(missing), str(blob_b)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=sha256',
                f'EXPECTED={missing}',
                f'ACTUAL={blob_b}',
                'EXPECTED_EXISTS=False',
                'ACTUAL_EXISTS=True',
            ],
        )
        covered_cases.append('sha256_missing_expected')

        run_contract_case(
            ['--mode', 'sha256', str(blob_a), str(missing)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=sha256',
                f'EXPECTED={blob_a}',
                f'ACTUAL={missing}',
                'EXPECTED_EXISTS=True',
                'ACTUAL_EXISTS=False',
            ],
        )
        covered_cases.append('sha256_missing_actual')

        run_contract_case(
            ['--mode', 'sha256', str(missing), str(other_missing)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=sha256',
                f'EXPECTED={missing}',
                f'ACTUAL={other_missing}',
                'EXPECTED_EXISTS=False',
                'ACTUAL_EXISTS=False',
            ],
        )
        covered_cases.append('sha256_missing_both')

        blob_b.write_bytes(b'zigux-artifact-DRIFT')
        run_contract_case(
            ['--mode', 'sha256', str(blob_a), str(blob_b)],
            1,
            [
                'ARTIFACT_DIFF=fail',
                'MODE=sha256',
                f'EXPECTED={blob_a}',
                f'ACTUAL={blob_b}',
                'EXPECTED_SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576',
                'ACTUAL_SHA256=bfc83f8f1f4369ce3cfabfdff0699ae3bf7a15b89f1702b690e56c6f35f1ee94',
            ],
            repeat_count=2,
        )
        covered_cases.append('sha256_drift')
        covered_cases.append('sha256_drift_repeat')

    if covered_cases != EXPECTED_CONTRACT_CASES:
        raise AssertionError(
            'artifact-diff contract case catalog drifted: '
            f'expected {EXPECTED_CONTRACT_CASES}, got {covered_cases}'
        )

    print('ARTIFACT_DIFF_CONTRACT=pass')
    print(f'ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={len(BASE_CONTRACT_CASES)}')
    print('ARTIFACT_DIFF_CONTRACT_BASE_CASES=' + ','.join(BASE_CONTRACT_CASES))
    print(f'ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(REPEAT_CONTRACT_CASES)}')
    print('ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=' + ','.join(REPEAT_CONTRACT_CASES))
    print(f'ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}')
    print('ARTIFACT_DIFF_CONTRACT_CASES=' + ','.join(EXPECTED_CONTRACT_CASES))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

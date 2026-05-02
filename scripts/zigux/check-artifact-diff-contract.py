#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF = ROOT / 'scripts' / 'zigux' / 'artifact_diff.py'


def run_contract_case(args: list[str], expected_exit: int, expected_lines: list[str]) -> None:
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
            f'expected exit {expected_exit}, got {completed.returncode}: {lines}'
        )
    if lines != expected_lines:
        raise AssertionError(f'unexpected output lines: {lines}')
    if completed.stderr:
        raise AssertionError(f'unexpected stderr: {completed.stderr!r}')


def main() -> int:
    covered_cases: list[str] = []

    run_contract_case(['--self-test'], 0, ['ARTIFACT_DIFF_SELF_TEST=pass'])
    covered_cases.append('helper_self_test')

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
        )
        covered_cases.append('text_pass')

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
        )
        covered_cases.append('json_mismatch')

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
        )
        covered_cases.append('sha256_drift')

    print('ARTIFACT_DIFF_CONTRACT=pass')
    print(f'ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(covered_cases)}')
    print('ARTIFACT_DIFF_CONTRACT_CASES=' + ','.join(covered_cases))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

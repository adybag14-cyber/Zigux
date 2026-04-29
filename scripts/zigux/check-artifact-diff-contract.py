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
    with tempfile.TemporaryDirectory(prefix='zigux_artifact_diff_contract_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        expected = tmp_dir / 'expected.txt'
        actual = tmp_dir / 'actual.txt'
        missing = tmp_dir / 'missing.txt'
        expected_json = tmp_dir / 'expected.json'
        actual_json = tmp_dir / 'actual.json'
        invalid_expected_json = tmp_dir / 'expected-invalid.json'
        invalid_actual_json = tmp_dir / 'actual-invalid.json'

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

        expected_json.write_text('{"alpha": 1, "beta": [2, 3]}\n', encoding='utf-8', newline='\n')
        actual_json.write_text('{\n  "beta": [2, 3],\n  "alpha": 1\n}\n', encoding='utf-8', newline='\n')
        invalid_expected_json.write_text('{"alpha": 1,\n', encoding='utf-8', newline='\n')
        invalid_actual_json.write_text('{"alpha": 1,\n', encoding='utf-8', newline='\n')
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

    print('ARTIFACT_DIFF_CONTRACT=pass')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
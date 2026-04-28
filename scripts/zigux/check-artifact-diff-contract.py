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

    print('ARTIFACT_DIFF_CONTRACT=pass')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
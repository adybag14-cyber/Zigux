#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF = ROOT / 'scripts' / 'zigux' / 'artifact_diff.py'
ARTIFACT_DIFF_NOTE = ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md'

EXPECTED_CONTRACT_CASES = [
    'helper_self_test',
    'helper_self_test_repeat',
    'cli_missing_required_args',
    'cli_missing_actual_operand',
    'cli_invalid_mode',
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
REQUIRED_REVIEW_NOTE_MARKERS = [
    '- owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`',
    '- rollback owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`',
    '- fallback rule: if `scripts/zigux/artifact_diff.py` regresses, keep the committed expected artifact plus the current authoritative C or documented replay command as the source of truth until the helper contract is repaired',
    '- deterministic replay entrypoint: `python3 scripts/zigux/check-artifact-diff-contract.py` is the reviewable contract rerun for the shared host-side helper and should stay aligned with the outward line rules below',
    '- review rule: any change to the helper\'s emitted `ARTIFACT_DIFF=*`, `MODE=*`, path, or SHA-256 lines must update this note in the same change so the published host-side artifact packet stays reviewable',
    '- boundary: keep this note scoped to the shared host-side diff helper; Phase 4 gate ownership for `zigux/tests/*.zig` still belongs in `Documentation/zigux/phase4-validation-matrix.md`',
    '- deterministic helper contract: `ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL[,SHA256|EXPECTED_EXISTS|ACTUAL_EXISTS|EXPECTED_JSON_ERROR|ACTUAL_JSON_ERROR]`',
    '- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_TEXT` must prove both the stable text pass shape and the direct text mismatch fail shape',
    '- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_JSON` must prove canonical JSON equivalence while `ARTIFACT_DIFF_SELF_TEST_JSON_INVALID` proves malformed JSON fails without inventing digest or exists markers',
    '- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_SHA256` must prove both the shared digest pass line and the exact expected-vs-actual digest drift lines',
    '- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_MISSING` must prove missing-path failures emit only the EXISTS markers',
]
EXPECTED_SELF_TEST_CASES = [
    'catalog_shape',
    'review_note_marker_round_trip',
    'review_note_marker_drift',
    'helper_summary_round_trip',
    'contract_summary_round_trip',
    'helper_summary_status_drift',
    'helper_summary_count_drift',
    'helper_summary_duplicate_case_drift',
    'helper_summary_case_order_drift',
    'contract_summary_status_drift',
    'contract_summary_base_count_drift',
    'contract_summary_base_case_order_drift',
    'contract_summary_repeat_count_drift',
    'contract_summary_repeat_case_order_drift',
    'contract_summary_case_count_drift',
    'contract_summary_duplicate_case_drift',
    'contract_summary_case_order_drift',
]


def helper_self_test_expected_lines() -> list[str]:
    return [
        'ARTIFACT_DIFF_SELF_TEST=pass',
        'ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=19',
        'ARTIFACT_DIFF_SELF_TEST_CASES=text_pass,text_mismatch,json_pass,json_mismatch,json_invalid_expected,json_invalid_actual,json_invalid_both,json_missing_expected,json_missing_actual,json_missing_both,sha256_pass,sha256_drift,text_missing_expected,text_missing_actual,text_missing_both,sha256_missing_expected,sha256_missing_actual,sha256_missing_both,invalid_mode_rejected',
    ]


def expected_contract_summary_lines() -> list[str]:
    return [
        'ARTIFACT_DIFF_CONTRACT=pass',
        f'ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={len(BASE_CONTRACT_CASES)}',
        'ARTIFACT_DIFF_CONTRACT_BASE_CASES=' + ','.join(BASE_CONTRACT_CASES),
        f'ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(REPEAT_CONTRACT_CASES)}',
        'ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=' + ','.join(REPEAT_CONTRACT_CASES),
        f'ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}',
        'ARTIFACT_DIFF_CONTRACT_CASES=' + ','.join(EXPECTED_CONTRACT_CASES),
    ]


def extract_output_value(lines: list[str], prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :]
    raise AssertionError(f'missing output line with prefix {prefix!r}: {lines}')


def parse_case_catalog(lines: list[str], count_prefix: str, list_prefix: str) -> list[str]:
    count_text = extract_output_value(lines, count_prefix)
    expected_count = int(count_text)
    cases_text = extract_output_value(lines, list_prefix)
    cases = [] if not cases_text else cases_text.split(',')
    if len(cases) != expected_count:
        raise AssertionError(
            f'count/list drift for {count_prefix!r} and {list_prefix!r}: count={expected_count} cases={cases}'
        )
    if len(set(cases)) != len(cases):
        raise AssertionError(f'duplicate cases in {list_prefix!r}: {cases}')
    return cases


def assert_helper_self_test_output(lines: list[str]) -> None:
    if extract_output_value(lines, 'ARTIFACT_DIFF_SELF_TEST=') != 'pass':
        raise AssertionError(f'unexpected helper self-test status: {lines}')
    expected_cases = helper_self_test_expected_lines()[2].split('=', 1)[1].split(',')
    cases = parse_case_catalog(
        lines,
        'ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=',
        'ARTIFACT_DIFF_SELF_TEST_CASES=',
    )
    if cases != expected_cases:
        raise AssertionError(
            f'artifact-diff helper self-test catalog drifted: expected {expected_cases}, got {cases}'
        )


def assert_contract_output(lines: list[str]) -> None:
    if extract_output_value(lines, 'ARTIFACT_DIFF_CONTRACT=') != 'pass':
        raise AssertionError(f'unexpected contract status: {lines}')
    if parse_case_catalog(lines, 'ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=', 'ARTIFACT_DIFF_CONTRACT_BASE_CASES=') != BASE_CONTRACT_CASES:
        raise AssertionError('artifact-diff base contract catalog drifted')
    if parse_case_catalog(lines, 'ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=', 'ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=') != REPEAT_CONTRACT_CASES:
        raise AssertionError('artifact-diff repeat contract catalog drifted')
    if parse_case_catalog(lines, 'ARTIFACT_DIFF_CONTRACT_CASE_COUNT=', 'ARTIFACT_DIFF_CONTRACT_CASES=') != EXPECTED_CONTRACT_CASES:
        raise AssertionError('artifact-diff full contract catalog drifted')


def assert_review_note_markers(note_text: str) -> None:
    missing = [marker for marker in REQUIRED_REVIEW_NOTE_MARKERS if note_text.count(marker) != 1]
    if missing:
        raise AssertionError(f'artifact-diff review note marker drifted: {missing}')


def run_contract_case(
    args: list[str],
    expected_exit: int,
    expected_lines: list[str],
    *,
    repeat_count: int = 1,
) -> None:
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
                f'attempt {attempt}: expected exit {expected_exit}, got {completed.returncode}: stdout={lines} stderr={completed.stderr.splitlines()}'
            )
        if lines != expected_lines:
            raise AssertionError(f'attempt {attempt}: unexpected output lines: {lines}')
        if completed.stderr:
            raise AssertionError(f'attempt {attempt}: unexpected stderr: {completed.stderr!r}')


def run_error_contract_case(
    args: list[str],
    expected_stderr_normalized: str,
    *,
    repeat_count: int = 1,
) -> None:
    for attempt in range(1, repeat_count + 1):
        completed = subprocess.run(
            [sys.executable, str(ARTIFACT_DIFF), *args],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        if completed.returncode != 2:
            raise AssertionError(
                f'attempt {attempt}: expected exit 2, got {completed.returncode}: stdout={completed.stdout.splitlines()} stderr={completed.stderr.splitlines()}'
            )
        if completed.stdout.splitlines():
            raise AssertionError(f'attempt {attempt}: expected empty stdout')
        normalized_stderr = ' '.join(completed.stderr.split())
        if normalized_stderr != expected_stderr_normalized:
            raise AssertionError(
                f'attempt {attempt}: unexpected normalized parser stderr: expected {expected_stderr_normalized!r}, got {normalized_stderr!r}'
            )


def run_self_test() -> int:
    if len(set(EXPECTED_CONTRACT_CASES)) != len(EXPECTED_CONTRACT_CASES):
        raise AssertionError('artifact-diff contract cases must stay unique')
    if len(set(REPEAT_CONTRACT_CASES)) != len(REPEAT_CONTRACT_CASES):
        raise AssertionError('artifact-diff repeat contract cases must stay unique')
    if len(set(REQUIRED_REVIEW_NOTE_MARKERS)) != len(REQUIRED_REVIEW_NOTE_MARKERS):
        raise AssertionError('artifact-diff review note markers must stay unique')
    if len(set(EXPECTED_SELF_TEST_CASES)) != len(EXPECTED_SELF_TEST_CASES):
        raise AssertionError('artifact-diff self-test cases must stay unique')
    if len(BASE_CONTRACT_CASES) + len(REPEAT_CONTRACT_CASES) != len(EXPECTED_CONTRACT_CASES):
        raise AssertionError('artifact-diff base/repeat partition drifted')

    assert_review_note_markers('\n'.join(REQUIRED_REVIEW_NOTE_MARKERS))
    assert_helper_self_test_output(helper_self_test_expected_lines())
    assert_contract_output(expected_contract_summary_lines())

    print('ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass')
    print(f'ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT={len(EXPECTED_SELF_TEST_CASES)}')
    print('ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=' + ','.join(EXPECTED_SELF_TEST_CASES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Check the published artifact-diff CLI contract and summary shapes.'
    )
    parser.add_argument(
        '--self-test',
        action='store_true',
        help='Run built-in checker self-tests without replaying the live artifact-diff helper.',
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    run_self_test()
    note_text = ARTIFACT_DIFF_NOTE.read_text(encoding='utf-8')
    assert_review_note_markers(note_text)
    covered_cases: list[str] = []

    run_contract_case(['--self-test'], 0, helper_self_test_expected_lines(), repeat_count=2)
    covered_cases.extend(['helper_self_test', 'helper_self_test_repeat'])

    run_contract_case(
        ['-h'],
        0,
        [
            'usage: artifact_diff.py [-h] [--mode {text,json,sha256}] [--self-test]',
            '                        [expected] [actual]',
            '',
            'Compare two artifacts in a stable mode.',
            '',
            'positional arguments:',
            '  expected',
            '  actual',
            '',
            'options:',
            '  -h, --help            show this help message and exit',
            '  --mode {text,json,sha256}',
            '  --self-test           Run built-in deterministic comparison checks.',
        ],
        repeat_count=2,
    )

    parser_error = (
        'usage: artifact_diff.py [-h] [--mode {text,json,sha256}] [--self-test] [expected] [actual] '
        'artifact_diff.py: error: --mode, expected, and actual are required unless --self-test is set'
    )
    run_error_contract_case([], parser_error, repeat_count=2)
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

        run_error_contract_case(['--mode', 'text', str(expected)], parser_error, repeat_count=2)
        covered_cases.append('cli_missing_actual_operand')

        run_error_contract_case(
            ['--mode', 'yaml', str(expected), str(actual)],
            "usage: artifact_diff.py [-h] [--mode {text,json,sha256}] [--self-test] [expected] [actual] artifact_diff.py: error: argument --mode: invalid choice: 'yaml' (choose from text, json, sha256)",
            repeat_count=2,
        )
        covered_cases.append('cli_invalid_mode')

        run_contract_case(
            ['--mode', 'text', str(expected), str(actual)],
            0,
            ['ARTIFACT_DIFF=pass', 'MODE=text', f'EXPECTED={expected}', f'ACTUAL={actual}'],
            repeat_count=2,
        )
        covered_cases.extend(['text_pass', 'text_pass_repeat'])

        actual.write_text('alpha\nBETA\n', encoding='utf-8', newline='\n')
        run_contract_case(
            ['--mode', 'text', str(expected), str(actual)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=text', f'EXPECTED={expected}', f'ACTUAL={actual}'],
        )
        covered_cases.append('text_mismatch')
        actual.write_text('alpha\nbeta\n', encoding='utf-8', newline='\n')

        run_contract_case(
            ['--mode', 'text', str(missing), str(actual)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=text', f'EXPECTED={missing}', f'ACTUAL={actual}', 'EXPECTED_EXISTS=False', 'ACTUAL_EXISTS=True'],
        )
        covered_cases.append('text_missing_expected')

        run_contract_case(
            ['--mode', 'text', str(expected), str(missing)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=text', f'EXPECTED={expected}', f'ACTUAL={missing}', 'EXPECTED_EXISTS=True', 'ACTUAL_EXISTS=False'],
        )
        covered_cases.append('text_missing_actual')

        run_contract_case(
            ['--mode', 'text', str(missing), str(other_missing)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=text', f'EXPECTED={missing}', f'ACTUAL={other_missing}', 'EXPECTED_EXISTS=False', 'ACTUAL_EXISTS=False'],
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
            ['ARTIFACT_DIFF=pass', 'MODE=json', f'EXPECTED={expected_json}', f'ACTUAL={actual_json}'],
        )
        covered_cases.append('json_pass')

        run_contract_case(
            ['--mode', 'json', str(expected_json), str(actual_json_mismatch)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=json', f'EXPECTED={expected_json}', f'ACTUAL={actual_json_mismatch}'],
            repeat_count=2,
        )
        covered_cases.extend(['json_mismatch', 'json_mismatch_repeat'])

        run_contract_case(
            ['--mode', 'json', str(missing), str(actual_json)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=json', f'EXPECTED={missing}', f'ACTUAL={actual_json}', 'EXPECTED_EXISTS=False', 'ACTUAL_EXISTS=True'],
        )
        covered_cases.append('json_missing_expected')

        run_contract_case(
            ['--mode', 'json', str(expected_json), str(missing)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=json', f'EXPECTED={expected_json}', f'ACTUAL={missing}', 'EXPECTED_EXISTS=True', 'ACTUAL_EXISTS=False'],
        )
        covered_cases.append('json_missing_actual')

        run_contract_case(
            ['--mode', 'json', str(missing), str(other_missing)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=json', f'EXPECTED={missing}', f'ACTUAL={other_missing}', 'EXPECTED_EXISTS=False', 'ACTUAL_EXISTS=False'],
        )
        covered_cases.append('json_missing_both')

        run_contract_case(
            ['--mode', 'json', str(invalid_expected_json), str(actual_json)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=json', f'EXPECTED={invalid_expected_json}', f'ACTUAL={actual_json}', f'EXPECTED_JSON_ERROR={invalid_expected_json}:2:1: Expecting property name enclosed in double quotes'],
        )
        covered_cases.append('json_invalid_expected')

        run_contract_case(
            ['--mode', 'json', str(expected_json), str(invalid_actual_json)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=json', f'EXPECTED={expected_json}', f'ACTUAL={invalid_actual_json}', f'ACTUAL_JSON_ERROR={invalid_actual_json}:2:1: Expecting property name enclosed in double quotes'],
        )
        covered_cases.append('json_invalid_actual')

        run_contract_case(
            ['--mode', 'json', str(invalid_expected_json), str(invalid_actual_json)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=json', f'EXPECTED={invalid_expected_json}', f'ACTUAL={invalid_actual_json}', f'EXPECTED_JSON_ERROR={invalid_expected_json}:2:1: Expecting property name enclosed in double quotes'],
        )
        covered_cases.append('json_invalid_both')

        blob_a.write_bytes(b'zigux-artifact-diff')
        blob_b.write_bytes(b'zigux-artifact-diff')
        run_contract_case(
            ['--mode', 'sha256', str(blob_a), str(blob_b)],
            0,
            ['ARTIFACT_DIFF=pass', 'MODE=sha256', f'EXPECTED={blob_a}', f'ACTUAL={blob_b}', 'SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576'],
        )
        covered_cases.append('sha256_pass')

        run_contract_case(
            ['--mode', 'sha256', str(missing), str(blob_b)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=sha256', f'EXPECTED={missing}', f'ACTUAL={blob_b}', 'EXPECTED_EXISTS=False', 'ACTUAL_EXISTS=True'],
        )
        covered_cases.append('sha256_missing_expected')

        run_contract_case(
            ['--mode', 'sha256', str(blob_a), str(missing)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=sha256', f'EXPECTED={blob_a}', f'ACTUAL={missing}', 'EXPECTED_EXISTS=True', 'ACTUAL_EXISTS=False'],
        )
        covered_cases.append('sha256_missing_actual')

        run_contract_case(
            ['--mode', 'sha256', str(missing), str(other_missing)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=sha256', f'EXPECTED={missing}', f'ACTUAL={other_missing}', 'EXPECTED_EXISTS=False', 'ACTUAL_EXISTS=False'],
        )
        covered_cases.append('sha256_missing_both')

        blob_b.write_bytes(b'zigux-artifact-DRIFT')
        run_contract_case(
            ['--mode', 'sha256', str(blob_a), str(blob_b)],
            1,
            ['ARTIFACT_DIFF=fail', 'MODE=sha256', f'EXPECTED={blob_a}', f'ACTUAL={blob_b}', 'EXPECTED_SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576', 'ACTUAL_SHA256=bfc83f8f1f4369ce3cfabfdff0699ae3bf7a15b89f1702b690e56c6f35f1ee94'],
            repeat_count=2,
        )
        covered_cases.extend(['sha256_drift', 'sha256_drift_repeat'])

    if covered_cases != EXPECTED_CONTRACT_CASES:
        raise AssertionError(
            f'artifact-diff contract case catalog drifted: expected {EXPECTED_CONTRACT_CASES}, got {covered_cases}'
        )

    for line in expected_contract_summary_lines():
        print(line)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

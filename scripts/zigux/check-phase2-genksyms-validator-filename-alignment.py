#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile

SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
VALIDATOR_REL = Path('scripts/zigux/validate-phase2.py')
CASES_REL = Path('zigux/tests/fixtures/genksyms_bridge/cases.json')
CASE_NAME = 'abbreviated_missing_long_dump_types_argument'
EXPECTED_FIXTURE = 'abbreviated_missing_long_dump_types_argument_expected.json'


def resolve_root() -> Path:
    parser = argparse.ArgumentParser(
        description='Check the Phase 2 shared validator genksyms bridge filename contract.'
    )
    parser.add_argument('--root', type=Path, default=DEFAULT_ROOT)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    return args.root.resolve(), args.self_test


def extract_validator_expected(source: str) -> str | None:
    pattern = re.compile(
        rf"'{CASE_NAME}'\s*:\s*'([^']+)'",
        re.MULTILINE,
    )
    match = pattern.search(source)
    if not match:
        return None
    return match.group(1)


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    validator_path = root / VALIDATOR_REL
    cases_path = root / CASES_REL

    if not validator_path.exists():
        return [f'missing:{VALIDATOR_REL}']
    if not cases_path.exists():
        return [f'missing:{CASES_REL}']

    validator_expected = extract_validator_expected(
        validator_path.read_text(encoding='utf-8')
    )
    if validator_expected is None:
        issues.append(f'validator:missing_case:{CASE_NAME}')
    elif validator_expected != EXPECTED_FIXTURE:
        issues.append(
            f'validator:{CASE_NAME}:expected={validator_expected!r}:required={EXPECTED_FIXTURE!r}'
        )

    payload = json.loads(cases_path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict):
        issues.append('cases:expected_top_level_object')
        return issues
    cases = payload.get('cases')
    if not isinstance(cases, list):
        issues.append('cases:expected_list')
        return issues

    manifest_expected: str | None = None
    for case in cases:
        if not isinstance(case, dict):
            issues.append('cases:entry:expected_object')
            continue
        if case.get('name') == CASE_NAME:
            manifest_expected = case.get('expected')
            break
    if manifest_expected is None:
        issues.append(f'cases:missing_case:{CASE_NAME}')
    elif manifest_expected != EXPECTED_FIXTURE:
        issues.append(
            f'cases:{CASE_NAME}:expected={manifest_expected!r}:required={EXPECTED_FIXTURE!r}'
        )

    return issues


def write_fixture_tree(root: Path, validator_expected: str, case_expected: str) -> None:
    validator_path = root / VALIDATOR_REL
    cases_path = root / CASES_REL
    validator_path.parent.mkdir(parents=True, exist_ok=True)
    cases_path.parent.mkdir(parents=True, exist_ok=True)
    validator_path.write_text(
        '\n'.join(
            [
                'def validate_expected_genksyms_bridge_cases(_path):',
                '    expected_cases = {',
                f"        '{CASE_NAME}': '{validator_expected}',",
                '    }',
                '    return expected_cases',
                '',
            ]
        ),
        encoding='utf-8',
    )
    cases_path.write_text(
        json.dumps(
            {
                'cases': [
                    {
                        'name': CASE_NAME,
                        'expected': case_expected,
                    }
                ]
            },
            indent=2,
        )
        + '\n',
        encoding='utf-8',
    )


def expect_issue(label: str, root: Path, expected_issue: str) -> None:
    issues = validate(root)
    if expected_issue not in issues:
        raise SystemExit(
            f'phase2-genksyms-validator-filename-selftest:{label}:expected={expected_issue!r}:actual={issues!r}'
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_phase2_genksyms_validator_filename_') as tmp:
        root = Path(tmp)

        write_fixture_tree(root, EXPECTED_FIXTURE, EXPECTED_FIXTURE)
        baseline = validate(root)
        if baseline:
            raise SystemExit(
                f'phase2-genksyms-validator-filename-selftest:baseline_failed:{baseline!r}'
            )

        write_fixture_tree(
            root,
            'abbreviated_missing_LONG_dump_types_argument_expected.json',
            EXPECTED_FIXTURE,
        )
        expect_issue(
            'validator_typo',
            root,
            "validator:abbreviated_missing_long_dump_types_argument:expected='abbreviated_missing_LONG_dump_types_argument_expected.json':required='abbreviated_missing_long_dump_types_argument_expected.json'",
        )

        write_fixture_tree(root, EXPECTED_FIXTURE, 'wrong_expected.json')
        expect_issue(
            'manifest_drift',
            root,
            "cases:abbreviated_missing_long_dump_types_argument:expected='wrong_expected.json':required='abbreviated_missing_long_dump_types_argument_expected.json'",
        )

        write_fixture_tree(root, EXPECTED_FIXTURE, EXPECTED_FIXTURE)
        cases_path = root / CASES_REL
        cases_path.write_text(json.dumps({'cases': []}, indent=2) + '\n', encoding='utf-8')
        expect_issue(
            'missing_case',
            root,
            'cases:missing_case:abbreviated_missing_long_dump_types_argument',
        )

    print('PHASE2_GENKSYMS_VALIDATOR_FILENAME_ALIGNMENT_SELF_TEST=pass')
    print('PHASE2_GENKSYMS_VALIDATOR_FILENAME_ALIGNMENT_SELF_TEST_CASE_COUNT=4')
    return 0


def main() -> int:
    root, self_test = resolve_root()
    if self_test:
        return run_self_test()

    issues = validate(root)
    if issues:
        print('PHASE2_GENKSYMS_VALIDATOR_FILENAME_ALIGNMENT=fail')
        print('PHASE2_GENKSYMS_VALIDATOR_FILENAME_ALIGNMENT_ISSUES_START')
        for issue in issues:
            print(issue)
        print('PHASE2_GENKSYMS_VALIDATOR_FILENAME_ALIGNMENT_ISSUES_END')
        return 1

    print('PHASE2_GENKSYMS_VALIDATOR_FILENAME_ALIGNMENT=pass')
    print(f'PHASE2_GENKSYMS_VALIDATOR_FILENAME_ALIGNMENT_ROOT={root}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
REQUIRED_FILES = {
    'bridge_checker': 'scripts/zigux/check-genksyms-bridge.py',
    'readme': 'scripts/zigux/README.md',
    'closure_doc': 'Documentation/zigux/phase2-closure.md',
    'closure_validator': 'scripts/zigux/validate-phase2-closure.py',
    'validator': 'scripts/zigux/validate-phase2.py',
    'workflow': '.github/workflows/zigux-bootstrap.yml',
    'cases': 'zigux/tests/fixtures/genksyms_bridge/cases.json',
}
EXPECTED_CASE_NAMES = [
    'minimal',
    'debug_reference_types',
    'short_inline_reference_dump_types',
    'clustered_short_inline_reference',
    'long_options',
    'abbreviated_long_options',
    'quiet_overrides_warning',
    'explicit_option_terminator',
    'positional_passthrough',
    'lone_dash_passthrough',
    'explicit_terminator_positional_passthrough',
    'help',
    'version',
    'invalid_option',
    'missing_reference_argument',
    'missing_dump_types_argument',
    'unsupported_long_option',
    'ambiguous_abbreviated_long_option',
    'empty_long_option_name',
    'unexpected_long_option_argument',
    'abbreviated_unexpected_long_option_argument',
    'missing_long_reference_argument',
    'abbreviated_missing_long_reference_argument',
    'missing_long_dump_types_argument',
    'abbreviated_missing_long_dump_types_argument',
    'too_many_reference_files',
]
BRIDGE_CHECKER_MARKERS = [
    "print('PHASE2_GENKSYMS_BRIDGE_SELF_TEST=pass')",
    "print('PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=26')",
]
README_MARKERS = [
    '`check-genksyms-bridge.py --self-test` exercises the bounded `genksyms` bridge checker packet itself before the Linux-style `phase2-tools` entrypoint replays live bridge artifacts, so missing-expected-fixture drift, duplicate expected-fixture wiring, stderr-mode contract drift, and repeat-run compare coverage cannot hide behind a locally passing parity run.',
    'that same committed bridge packet currently spans 26 reviewable cases under `zigux/tests/fixtures/genksyms_bridge/`, including the minimal, clustered short-inline, abbreviated long-option, lone-dash passthrough, explicit-terminator positional, missing-argument, and reference-limit fixtures that keep the widened wrapper-first surface explicit.',
]
CLOSURE_DOC_MARKERS = [
    '- `python3 scripts/zigux/check-genksyms-bridge.py --self-test`',
    '- `PHASE2_GENKSYMS_BRIDGE_CASE_COUNT=26`',
    '- `PHASE2_GENKSYMS_BRIDGE_STDERR_POLICY=success-path stderr silence plus repeat-run stderr determinism are required for closure`',
]
CLOSURE_VALIDATOR_MARKERS = [
    "'python3 scripts/zigux/check-genksyms-bridge.py --self-test': 1,",
    "'python3 scripts/zigux/check-genksyms-bridge.py': 1,",
    '\'self_test_case_count_marker\': "print(\\\'PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=26\\\')",',
    "'PHASE2_GENKSYMS_BRIDGE_CASE_COUNT=26',",
]
VALIDATOR_MARKERS = [
    "'python3 scripts/zigux/check-genksyms-bridge.py --self-test': 1,",
    "'python3 scripts/zigux/check-genksyms-bridge.py': 1,",
    '\'self_test_case_count_marker\': "print(\\\'PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=26\\\')",',
    "'check-genksyms-bridge.py --self-test',",
]
WORKFLOW_RUN_COUNTS = {
    'python3 scripts/zigux/check-genksyms-bridge.py --self-test': 1,
    'python3 scripts/zigux/check-genksyms-bridge.py': 1,
}


def resolve_root() -> Path:
    args = sys.argv[1:]
    if '--root' in args:
        index = args.index('--root')
        try:
            return Path(args[index + 1]).resolve()
        except IndexError as exc:
            raise SystemExit('--root requires a path') from exc
    if 'ZIGUX_PHASE2_ROOT' in os.environ:
        return Path(os.environ['ZIGUX_PHASE2_ROOT']).resolve()
    return DEFAULT_ROOT


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding='utf-8')


def validate_cases(root: Path) -> list[str]:
    issues: list[str] = []
    payload = json.loads(read_text(root, REQUIRED_FILES['cases']))
    if not isinstance(payload, dict):
        return ['cases:expected_top_level_object']
    cases = payload.get('cases')
    if not isinstance(cases, list):
        return ['cases:expected_list']
    names = [case.get('name') for case in cases if isinstance(case, dict)]
    if len(cases) != 26:
        issues.append(f'cases:count={len(cases)}:expected=26')
    if names != EXPECTED_CASE_NAMES:
        issues.append('cases:names=expected_exact_phase2_genksyms_bridge_case_list')
    return issues


def validate_workflow(workflow_text: str) -> list[str]:
    issues: list[str] = []
    for command, expected_count in WORKFLOW_RUN_COUNTS.items():
        expected_line = f'run: {command}'
        count = sum(1 for line in workflow_text.splitlines() if line.strip() == expected_line)
        if count != expected_count:
            issues.append(f'workflow:{command}:count={count}:expected={expected_count}')
    return issues


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for label, rel_path in REQUIRED_FILES.items():
        if not (root / rel_path).exists():
            issues.append(f'missing:{label}:{rel_path}')
    if issues:
        return issues

    bridge_checker = read_text(root, REQUIRED_FILES['bridge_checker'])
    readme = read_text(root, REQUIRED_FILES['readme'])
    closure_doc = read_text(root, REQUIRED_FILES['closure_doc'])
    closure_validator = read_text(root, REQUIRED_FILES['closure_validator'])
    validator = read_text(root, REQUIRED_FILES['validator'])
    workflow = read_text(root, REQUIRED_FILES['workflow'])

    for marker in BRIDGE_CHECKER_MARKERS:
        if marker not in bridge_checker:
            issues.append(f'bridge_checker:{marker}')
    for marker in README_MARKERS:
        if marker not in readme:
            issues.append(f'readme:{marker}')
    for marker in CLOSURE_DOC_MARKERS:
        if marker not in closure_doc:
            issues.append(f'closure_doc:{marker}')
    for marker in CLOSURE_VALIDATOR_MARKERS:
        if marker not in closure_validator:
            issues.append(f'closure_validator:{marker}')
    for marker in VALIDATOR_MARKERS:
        if marker not in validator:
            issues.append(f'validator:{marker}')
    issues.extend(validate_workflow(workflow))
    issues.extend(validate_cases(root))
    return issues


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / 'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py'), '--root', str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def clone_fixture_root(destination_root: Path) -> None:
    script_target = destination_root / 'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py'
    script_target.parent.mkdir(parents=True, exist_ok=True)
    script_target.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')

    for key in ('bridge_checker', 'readme', 'closure_doc', 'closure_validator', 'validator', 'workflow', 'cases'):
        (destination_root / REQUIRED_FILES[key]).parent.mkdir(parents=True, exist_ok=True)

    (destination_root / REQUIRED_FILES['bridge_checker']).write_text(
        "print('PHASE2_GENKSYMS_BRIDGE_SELF_TEST=pass')\nprint('PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=26')\n",
        encoding='utf-8',
    )
    (destination_root / REQUIRED_FILES['readme']).write_text('\n'.join(README_MARKERS) + '\n', encoding='utf-8')
    (destination_root / REQUIRED_FILES['closure_doc']).write_text('\n'.join(CLOSURE_DOC_MARKERS) + '\n', encoding='utf-8')
    (destination_root / REQUIRED_FILES['closure_validator']).write_text('\n'.join(CLOSURE_VALIDATOR_MARKERS) + '\n', encoding='utf-8')
    (destination_root / REQUIRED_FILES['validator']).write_text('\n'.join(VALIDATOR_MARKERS) + '\n', encoding='utf-8')
    workflow_lines = [f'run: {command}' for command in WORKFLOW_RUN_COUNTS]
    (destination_root / REQUIRED_FILES['workflow']).write_text('\n'.join(workflow_lines) + '\n', encoding='utf-8')
    (destination_root / REQUIRED_FILES['cases']).write_text(
        json.dumps({'cases': [{'name': name} for name in EXPECTED_CASE_NAMES]}, indent=2) + '\n',
        encoding='utf-8',
    )


def expect_issue(label: str, root: Path, needle: str) -> None:
    result = run_checker(root)
    if result.returncode == 0:
        raise SystemExit(f'phase2-genksyms-selftest-alignment:{label}:unexpected_pass')
    if needle not in result.stdout:
        actual = result.stdout.strip() or 'none'
        raise SystemExit(
            f'phase2-genksyms-selftest-alignment:{label}:expected:{needle}:actual:{actual}'
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_phase2_genksyms_selftest_alignment_') as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                'phase2-genksyms-selftest-alignment:baseline_failed:'
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        bridge_checker_path = tmp_root / REQUIRED_FILES['bridge_checker']
        original_bridge_checker = bridge_checker_path.read_text(encoding='utf-8')
        bridge_checker_path.write_text(
            original_bridge_checker.replace('PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=26', 'PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=25', 1),
            encoding='utf-8',
        )
        expect_issue('bridge_checker_count', tmp_root, "bridge_checker:print('PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=26')")
        bridge_checker_path.write_text(original_bridge_checker, encoding='utf-8')

        workflow_path = tmp_root / REQUIRED_FILES['workflow']
        original_workflow = workflow_path.read_text(encoding='utf-8')
        workflow_path.write_text(
            original_workflow.replace('run: python3 scripts/zigux/check-genksyms-bridge.py --self-test\n', '', 1),
            encoding='utf-8',
        )
        expect_issue('workflow_self_test', tmp_root, 'workflow:python3 scripts/zigux/check-genksyms-bridge.py --self-test:count=0:expected=1')
        workflow_path.write_text(original_workflow, encoding='utf-8')

        cases_path = tmp_root / REQUIRED_FILES['cases']
        cases_payload = json.loads(cases_path.read_text(encoding='utf-8'))
        cases_payload['cases'].pop()
        cases_path.write_text(json.dumps(cases_payload, indent=2) + '\n', encoding='utf-8')
        expect_issue('case_count', tmp_root, 'cases:count=25:expected=26')
        clone_fixture_root(tmp_root)

        closure_validator_path = tmp_root / REQUIRED_FILES['closure_validator']
        original_closure_validator = closure_validator_path.read_text(encoding='utf-8')
        closure_validator_path.write_text(
            original_closure_validator.replace(CLOSURE_VALIDATOR_MARKERS[-1] + '\n', '', 1),
            encoding='utf-8',
        )
        expect_issue('closure_validator_marker', tmp_root, f'closure_validator:{CLOSURE_VALIDATOR_MARKERS[-1]}')
        clone_fixture_root(tmp_root)

        validator_path = tmp_root / REQUIRED_FILES['validator']
        original_validator = validator_path.read_text(encoding='utf-8')
        validator_path.write_text(
            original_validator.replace(VALIDATOR_MARKERS[2] + '\n', '', 1),
            encoding='utf-8',
        )
        expect_issue('validator_case_count_marker', tmp_root, f'validator:{VALIDATOR_MARKERS[2]}')

    print('PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST=pass')
    print('PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT=5')
    return 0


if '--self-test' in sys.argv[1:]:
    raise SystemExit(run_self_test())


ROOT = resolve_root()
problems = validate(ROOT)
if problems:
    print('PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=fail')
    print('PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_MISSING_START')
    for problem in problems:
        print(problem)
    print('PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_MISSING_END')
    raise SystemExit(1)

print('PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=pass')
print(f'PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_ROOT={ROOT}')
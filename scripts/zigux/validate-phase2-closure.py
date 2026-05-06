#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT = ROOT / 'scripts' / 'zigux' / 'check-phase2-cross-selftest-alignment.py'
CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE = ROOT / 'scripts' / 'zigux' / 'check-phase2-toolchain-pin-scope.py'
CHECK_PHASE2_TESTS_README_ALIGNMENT = ROOT / 'scripts' / 'zigux' / 'check-phase2-tests-readme-alignment.py'
DOCS_ROOT_README = ROOT / 'Documentation' / 'zigux' / 'README.md'
REVIEW_CHECKLIST = ROOT / 'Documentation' / 'zigux' / 'review-checklist.md'
TOOLCHAIN_NOTES = ROOT / 'Documentation' / 'zigux' / 'phase2-toolchain-bootstrap-notes.md'
TOOLCHAIN_POLICY = ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json'
GENKSYMS_CASES = (
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'cases.json'
)

PHASE2_CROSS_ALIGNMENT_REQUIRED_SOURCE_MARKERS = [
    'PHASE2_CROSS_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test',
    'PHASE2_CROSS_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py',
]
PHASE2_TOOLCHAIN_PIN_SCOPE_REQUIRED_SOURCE_MARKERS = [
    'PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test',
    'PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py',
]
PHASE2_TESTS_README_ALIGNMENT_REQUIRED_SOURCE_MARKERS = [
    'PHASE2_TESTS_README_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-tests-readme-alignment.py',
]
PHASE2_MAKEFILE_RUN_COUNTS = {
    'scripts/zigux/check-fixdep-diff.py --self-test': 1,
    'scripts/zigux/check-fixdep-diff.py': 1,
    'scripts/zigux/validate-phase2.py': 1,
    'scripts/zigux/validate-phase2-closure.py': 1,
    'scripts/zigux/check-phase2-tests-readme-alignment.py': 1,
    'scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test': 1,
    'scripts/zigux/check-phase2-toolchain-pin-scope.py': 1,
}
PHASE2_WORKFLOW_RUN_COUNTS = {
    'python3 scripts/zigux/validate-phase2.py': 1,
    'python3 scripts/zigux/validate-phase2-closure.py': 1,
    'python3 scripts/zigux/check-phase2-tests-readme-alignment.py': 1,
    'python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}': 1,
    'python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test': 1,
    'python3 scripts/zigux/check-phase2-cross-selftest-alignment.py': 1,
    'python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test': 1,
    'python3 scripts/zigux/check-phase2-toolchain-pin-scope.py': 1,
}


def run_self_test() -> int:
    make_ok = '\n'.join([
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py',
    ])
    workflow_ok = '\n'.join([
        'run: python3 scripts/zigux/validate-phase2.py',
        'run: python3 scripts/zigux/validate-phase2-closure.py',
        'run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py',
        'run: python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}',
        'run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test',
        'run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py',
        'run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test',
        'run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py',
    ]) + '\n'
    cases = [
        ('make_ok', validate_exact_makefile_runs(make_ok), []),
        (
            'make_duplicate_fixdep_self_test',
            validate_exact_makefile_runs(
                make_ok
                + '\ncd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test'
            ),
            ['make_exact_run:scripts/zigux/check-fixdep-diff.py --self-test:count=2:expected=1'],
        ),
        (
            'make_duplicate_fixdep_gate',
            validate_exact_makefile_runs(
                make_ok
                + '\ncd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py'
            ),
            ['make_exact_run:scripts/zigux/check-fixdep-diff.py:count=2:expected=1'],
        ),
        (
            'make_duplicate_validate_phase2',
            validate_exact_makefile_runs(
                make_ok
                + '\ncd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py'
            ),
            ['make_exact_run:scripts/zigux/validate-phase2.py:count=2:expected=1'],
        ),
        (
            'make_duplicate_validate_phase2_closure',
            validate_exact_makefile_runs(
                make_ok
                + '\ncd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py'
            ),
            ['make_exact_run:scripts/zigux/validate-phase2-closure.py:count=2:expected=1'],
        ),
        (
            'make_duplicate_tests_readme_alignment',
            validate_exact_makefile_runs(
                make_ok
                + '\ncd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py'
            ),
            ['make_exact_run:scripts/zigux/check-phase2-tests-readme-alignment.py:count=2:expected=1'],
        ),
        ('workflow_ok', validate_exact_workflow_runs(workflow_ok), []),
        (
            'workflow_duplicate_validate_phase2',
            validate_exact_workflow_runs(
                workflow_ok + 'run: python3 scripts/zigux/validate-phase2.py\n'
            ),
            ['workflow_exact_run:python3 scripts/zigux/validate-phase2.py:count=2:expected=1'],
        ),
        (
            'workflow_duplicate_validate_phase2_closure',
            validate_exact_workflow_runs(
                workflow_ok + 'run: python3 scripts/zigux/validate-phase2-closure.py\n'
            ),
            ['workflow_exact_run:python3 scripts/zigux/validate-phase2-closure.py:count=2:expected=1'],
        ),
        (
            'workflow_duplicate_tests_readme_alignment',
            validate_exact_workflow_runs(
                workflow_ok + 'run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py\n'
            ),
            ['workflow_exact_run:python3 scripts/zigux/check-phase2-tests-readme-alignment.py:count=2:expected=1'],
        ),
        (
            'workflow_duplicate_phase2_cross_matrix_gate',
            validate_exact_workflow_runs(
                workflow_ok
                + 'run: python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}\n'
            ),
            ['workflow_exact_run:python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}:count=2:expected=1'],
        ),
        (
            'workflow_duplicate_cross_alignment_self_test',
            validate_exact_workflow_runs(
                workflow_ok
                + 'run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\n'
            ),
            ['workflow_exact_run:python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test:count=2:expected=1'],
        ),
        (
            'workflow_duplicate_cross_alignment_gate',
            validate_exact_workflow_runs(
                workflow_ok + 'run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\n'
            ),
            ['workflow_exact_run:python3 scripts/zigux/check-phase2-cross-selftest-alignment.py:count=2:expected=1'],
        ),
        (
            'workflow_duplicate_toolchain_pin_scope_self_test',
            validate_exact_workflow_runs(
                workflow_ok
                + 'run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test\n'
            ),
            ['workflow_exact_run:python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test:count=2:expected=1'],
        ),
        (
            'workflow_duplicate_toolchain_pin_scope_gate',
            validate_exact_workflow_runs(
                workflow_ok + 'run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py\n'
            ),
            ['workflow_exact_run:python3 scripts/zigux/check-phase2-toolchain-pin-scope.py:count=2:expected=1'],
        ),
    ]

    failures: list[str] = []
    for name, actual, expected in cases:
        if actual != expected:
            failures.append(f'{name}:expected={expected}:actual={actual}')

    if failures:
        print('PHASE2_CLOSURE_SELF_TEST=fail')
        print('PHASE2_CLOSURE_SELF_TEST_FAILURES_START')
        for failure in failures:
            print(failure)
        print('PHASE2_CLOSURE_SELF_TEST_FAILURES_END')
        return 1

    print('PHASE2_CLOSURE_SELF_TEST=pass')
    print(f'PHASE2_CLOSURE_SELF_TEST_CASE_COUNT={len(cases)}')
    return 0

required_files = [
    ROOT / 'Documentation' / 'zigux' / 'phase2-closure.md',
    DOCS_ROOT_README,
    REVIEW_CHECKLIST,
    TOOLCHAIN_NOTES,
    ROOT / 'scripts' / 'zigux' / 'check-genksyms-bridge.py',
    ROOT / 'scripts' / 'zigux' / 'check-kconfig-bridge.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase2-cross.py',
    CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT,
    CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE,
    CHECK_PHASE2_TESTS_README_ALIGNMENT,
    ROOT / 'scripts' / 'zigux' / 'validate-phase2-closure.py',
    ROOT / 'scripts' / 'zigux' / 'genksyms.zig',
    ROOT / 'scripts' / 'zigux' / 'kconfig' / 'conf_bridge.zig',
    ROOT / 'scripts' / 'zigux' / 'kconfig' / 'confdata_bridge.zig',
    ROOT / 'zigux' / 'Makefile',
    TOOLCHAIN_POLICY,
    GENKSYMS_CASES,
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge' / 'cases.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge' / 'alldefconfig_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge' / 'olddefconfig_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge' / 'syncconfig_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge' / 'sample.config',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge' / 'sample_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_tool_manifest.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_cross_targets.json',
]


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict):
        raise SystemExit(f'{label}:expected_object')
    return payload


def collect_genksyms_expected_files(cases_payload: dict[str, object]) -> tuple[list[Path], list[str]]:
    issues: list[str] = []
    cases = cases_payload.get('cases')
    if not isinstance(cases, list):
        return [], ['genksyms_cases:cases:expected_list']
    if not cases:
        return [], ['genksyms_cases:cases:empty']

    expected_files: list[Path] = []
    seen_expected: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            issues.append(f'genksyms_cases:cases[{index}]:expected_object')
            continue

        name = case.get('name')
        if not isinstance(name, str) or not name:
            issues.append(f'genksyms_cases:cases[{index}]:name:expected_nonempty_string')
            continue

        expected = case.get('expected')
        if not isinstance(expected, str) or not expected:
            issues.append(f'genksyms_cases:{name}:expected:expected_nonempty_string')
            continue
        if expected in seen_expected:
            issues.append(f'genksyms_cases:{name}:expected:duplicate_reference:{expected}')
            continue
        seen_expected.add(expected)
        expected_files.append(GENKSYMS_CASES.parent / expected)

    return expected_files, issues


def validate_exact_makefile_runs(text: str) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in PHASE2_MAKEFILE_RUN_COUNTS.items():
        expected_line = f'cd $(ZIGUX_ROOT) && $(PYTHON) {command}'
        count = sum(1 for line in lines if line == expected_line)
        if count != expected_count:
            issues.append(
                f'make_exact_run:{command}:count={count}:expected={expected_count}'
            )
    return issues


def validate_exact_workflow_runs(text: str) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in PHASE2_WORKFLOW_RUN_COUNTS.items():
        expected_line = f'run: {command}'
        count = sum(1 for line in lines if line == expected_line)
        if count != expected_count:
            issues.append(
                f'workflow_exact_run:{command}:count={count}:expected={expected_count}'
            )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    if missing:
        print('PHASE2_CLOSURE_VALIDATION=fail')
        print('MISSING_PHASE2_CLOSURE_FILES_START')
        for item in missing:
            print(item)
        print('MISSING_PHASE2_CLOSURE_FILES_END')
        return 1

    genksyms_cases_payload = load_json_object(GENKSYMS_CASES, label='genksyms_cases')
    genksyms_expected_files, genksyms_case_issues = collect_genksyms_expected_files(
        genksyms_cases_payload
    )
    if genksyms_case_issues:
        print('PHASE2_CLOSURE_VALIDATION=fail')
        print('MISSING_PHASE2_CLOSURE_MARKERS_START')
        for item in genksyms_case_issues:
            print(item)
        print('MISSING_PHASE2_CLOSURE_MARKERS_END')
        return 1

    missing_genksyms_expected = [
        str(path.relative_to(ROOT)) for path in genksyms_expected_files if not path.exists()
    ]
    if missing_genksyms_expected:
        print('PHASE2_CLOSURE_VALIDATION=fail')
        print('MISSING_PHASE2_CLOSURE_FILES_START')
        for item in missing_genksyms_expected:
            print(item)
        print('MISSING_PHASE2_CLOSURE_FILES_END')
        return 1

    closure = (ROOT / 'Documentation' / 'zigux' / 'phase2-closure.md').read_text(encoding='utf-8')
    workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
    ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
    script_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')
    artifact_doc = (ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md').read_text(encoding='utf-8')
    makefile = (ROOT / 'zigux' / 'Makefile').read_text(encoding='utf-8')
    tool_manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_tool_manifest.json').read_text(encoding='utf-8'))
    targets_manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_cross_targets.json').read_text(encoding='utf-8'))

    required_closure_markers = [
        'PHASE2_STATUS=closed',
        'PHASE2_TOOL_COUNT=6',
        'PHASE2_CROSS_TARGET_COUNT=3',
        'PHASE2_FIXDEP_SELF_TEST=python3 scripts/zigux/check-fixdep-diff.py --self-test',
        'PHASE2_GENKSYMS_BRIDGE_GATE=python3 scripts/zigux/check-genksyms-bridge.py',
        'PHASE2_KCONFIG_BRIDGE_GATE=python3 scripts/zigux/check-kconfig-bridge.py',
        'PHASE2_CROSS_SELF_TEST=python3 scripts/zigux/check-phase2-cross.py --self-test',
        'PHASE2_CROSS_GATE=python3 scripts/zigux/check-phase2-cross.py',
        'PHASE2_CROSS_MANIFEST_POLICY=check-phase2-cross.py rejects duplicate tool entries, duplicate requested targets, unexpected explicit targets, duplicate manifest targets, and manifest-count drift before live compile replay',
        'PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=scripts/zigux/zig-toolchain-policy.json',
        'scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test',
        'scripts/zigux/check-phase2-toolchain-pin-scope.py',
        'x86_64-linux',
        'PHASE2_CLOSURE_GATE=python3 scripts/zigux/validate-phase2-closure.py',
        'PHASE2_FIXDEP_EMBEDDED_NUL_GUARD=fixdep.zig truncates depfile parsing at the first embedded NUL and keeps dep parsing skips bytes after the first embedded NUL as the bounded parser guard',
        'PHASE2_ROLLBACK=keep C kbuild tools authoritative and remove failing Zigux bridge/tool from workflow wiring',
    ]
    required_closure_markers.extend(PHASE2_CROSS_ALIGNMENT_REQUIRED_SOURCE_MARKERS)
    required_closure_markers.extend(PHASE2_TOOLCHAIN_PIN_SCOPE_REQUIRED_SOURCE_MARKERS)
    required_closure_markers.extend(PHASE2_TESTS_README_ALIGNMENT_REQUIRED_SOURCE_MARKERS)
    required_workflow_markers = [
        'python3 scripts/zigux/check-genksyms-bridge.py',
        'python3 scripts/zigux/check-kconfig-bridge.py',
        'python3 scripts/zigux/check-phase2-tests-readme-alignment.py',
        'python3 scripts/zigux/check-phase2-cross.py --target',
        'python3 scripts/zigux/validate-phase2-closure.py',
        'zig test scripts/zigux/genksyms.zig',
        'zig test scripts/zigux/kconfig/conf_bridge.zig',
        'zig test scripts/zigux/kconfig/confdata_bridge.zig',
    ]
    required_ledger_markers = [
        'feat(scripts/zigux): add bounded Phase 2 genksyms wrapper lane',
        'ci(zigux): widen Phase 2 closure matrix',
        'docs(zigux): reopen and close broadened Phase 2 tranche',
        'feat(scripts/zigux): add bounded Phase 2 kconfig bridge scaffolding',
        'ci(zigux): add Phase 2 cross-arch build matrix',
        'docs(zigux): close bounded Phase 2 toolchain tranche',
    ]
    required_readme_markers = [
        'check-genksyms-bridge.py',
        'check-kconfig-bridge.py',
        'check-phase2-cross.py',
        'genksyms.zig',
        'kconfig/conf_bridge.zig',
        'kconfig/confdata_bridge.zig',
    ]
    required_doc_markers = [
        'genksyms_bridge',
        'kconfig_bridge',
        'phase2_cross_targets.json',
    ]
    required_makefile_markers = [
        'phase2-validate:',
        'phase2-kconfig:',
        'phase2-cross:',
        'check-phase2-tests-readme-alignment.py',
        'check-phase2-cross-selftest-alignment.py --self-test',
        'check-phase2-cross-selftest-alignment.py',
        'check-phase2-toolchain-pin-scope.py --self-test',
        'check-phase2-toolchain-pin-scope.py',
        'check-genksyms-bridge.py',
        '$(ZIG) test scripts/zigux/genksyms.zig',
    ]

    missing_markers = []
    for marker in required_closure_markers:
        if marker not in closure:
            missing_markers.append(f'closure:{marker}')
    for marker in required_workflow_markers:
        if marker not in workflow:
            missing_markers.append(f'workflow:{marker}')
    for marker in required_ledger_markers:
        if marker not in ledger:
            missing_markers.append(f'ledger:{marker}')
    for marker in required_readme_markers:
        if marker not in script_readme:
            missing_markers.append(f'scripts:{marker}')
    for marker in required_doc_markers:
        if marker not in artifact_doc:
            missing_markers.append(f'doc:{marker}')
    for marker in required_makefile_markers:
        if marker not in makefile:
            missing_markers.append(f'make:{marker}')
    missing_markers.extend(validate_exact_makefile_runs(makefile))
    missing_markers.extend(validate_exact_workflow_runs(workflow))

    if tool_manifest.get('phase') != 'Phase 2':
        missing_markers.append('manifest:phase=Phase 2')
    if tool_manifest.get('status') != 'closed':
        missing_markers.append('manifest:status=closed')
    if tool_manifest.get('tool_count') != 6:
        missing_markers.append('manifest:tool_count=6')
    if len(tool_manifest.get('tools', [])) != 6:
        missing_markers.append(f'manifest:tools_len={len(tool_manifest.get("tools", []))}')
    for rel in tool_manifest.get('tools', []):
        if not (ROOT / rel).exists():
            missing_markers.append(f'manifest_file:{rel}')

    if targets_manifest.get('phase') != 'Phase 2':
        missing_markers.append('targets:phase=Phase 2')
    if targets_manifest.get('status') != 'closed':
        missing_markers.append('targets:status=closed')
    if targets_manifest.get('target_count') != 3:
        missing_markers.append('targets:target_count=3')
    if len(targets_manifest.get('targets', [])) != 3:
        missing_markers.append(f'targets:len={len(targets_manifest.get("targets", []))}')

    if missing_markers:
        print('PHASE2_CLOSURE_VALIDATION=fail')
        print('MISSING_PHASE2_CLOSURE_MARKERS_START')
        for marker in missing_markers:
            print(marker)
        print('MISSING_PHASE2_CLOSURE_MARKERS_END')
        return 1

    print('PHASE2_CLOSURE_VALIDATION=pass')
    print(f'PHASE2_CLOSURE_REQUIRED_FILE_COUNT={len(required_files) + len(genksyms_expected_files)}')
    print(f'PHASE2_CLOSURE_REQUIRED_MARKER_COUNT={len(required_closure_markers) + len(required_workflow_markers) + len(required_ledger_markers) + len(required_readme_markers) + len(required_doc_markers) + len(required_makefile_markers)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

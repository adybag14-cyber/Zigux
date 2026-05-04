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
    'bridge_checker': 'scripts/zigux/check-kconfig-bridge.py',
    'workflow': '.github/workflows/zigux-phase2-kconfig-alignment.yml',
    'cases': 'zigux/tests/fixtures/kconfig_bridge/cases.json',
}
EXPECTED_CONF_MODES = [
    'oldaskconfig',
    'oldconfig',
    'syncconfig',
    'defconfig',
    'savedefconfig',
    'allnoconfig',
    'allyesconfig',
    'allmodconfig',
    'alldefconfig',
    'randconfig',
    'listnewconfig',
    'helpnewconfig',
    'olddefconfig',
    'yes2modconfig',
    'mod2yesconfig',
    'mod2noconfig',
]
EXPECTED_CONFDATA_CASES = [
    'duplicate_assignments',
    'empty_string',
    'empty_symbol_names',
    'escaped_control_sequences',
    'escaped_low_control_bytes',
    'escaped_strings',
    'explicit_n_tristate',
    'final_trailing_carriage_return',
    'final_unterminated_unset_comment',
    'ignore_non_config_lines',
    'malformed_quoted_string',
    'negative_signed_numeric_kinds',
    'numeric_kinds',
    'quoted_suffix_bytes',
    'sample',
    'sample_crlf',
    'signed_numeric_kinds',
    'trailing_escaped_backslash',
]
BRIDGE_CHECKER_MARKERS = [
    "print('KCONFIG_BRIDGE_SELF_TEST=pass')",
]
WORKFLOW_RUN_COUNTS = {
    'python3 scripts/zigux/check-phase2-kconfig-bridge-selftest-alignment.py --self-test': 1,
    'python3 scripts/zigux/check-phase2-kconfig-bridge-selftest-alignment.py': 1,
}
WORKFLOW_ORDERED_COMMANDS = [
    'python3 scripts/zigux/check-phase2-kconfig-bridge-selftest-alignment.py --self-test',
    'python3 scripts/zigux/check-phase2-kconfig-bridge-selftest-alignment.py',
]


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


def validate_ordered_commands(
    stripped_lines: list[str],
    ordered_commands: list[str],
    prefix: str,
    *,
    find_position,
) -> list[str]:
    issues: list[str] = []
    positions: dict[str, int] = {}
    for command in ordered_commands:
        position = find_position(stripped_lines, command)
        if position is None:
            continue
        positions[command] = position
    for before, after in zip(ordered_commands, ordered_commands[1:]):
        if before in positions and after in positions and positions[before] >= positions[after]:
            issues.append(f'{prefix}_order:{before}:before:{after}')
    return issues


def validate_workflow(workflow_text: str) -> list[str]:
    issues: list[str] = []
    stripped_lines = [line.strip() for line in workflow_text.splitlines()]
    for command, expected_count in WORKFLOW_RUN_COUNTS.items():
        expected_line = f'run: {command}'
        count = sum(1 for line in stripped_lines if line == expected_line)
        if count != expected_count:
            issues.append(f'workflow:{command}:count={count}:expected={expected_count}')
    issues.extend(
        validate_ordered_commands(
            stripped_lines,
            WORKFLOW_ORDERED_COMMANDS,
            'workflow',
            find_position=lambda lines, command: next(
                (index for index, line in enumerate(lines) if line == f'run: {command}'),
                None,
            ),
        )
    )
    return issues


def validate_cases(root: Path) -> list[str]:
    issues: list[str] = []
    payload = json.loads(read_text(root, REQUIRED_FILES['cases']))
    if not isinstance(payload, dict):
        return ['cases:expected_top_level_object']

    conf_cases = payload.get('conf_cases')
    confdata_cases = payload.get('confdata_cases')
    if not isinstance(conf_cases, list):
        issues.append('cases:conf_cases:expected_list')
        conf_cases = []
    if not isinstance(confdata_cases, list):
        issues.append('cases:confdata_cases:expected_list')
        confdata_cases = []

    actual_conf_modes = [case.get('mode') for case in conf_cases if isinstance(case, dict)]
    actual_confdata_names = [case.get('name') for case in confdata_cases if isinstance(case, dict)]

    if len(conf_cases) != 16:
        issues.append(f'cases:conf_count={len(conf_cases)}:expected=16')
    if len(confdata_cases) != 18:
        issues.append(f'cases:confdata_count={len(confdata_cases)}:expected=18')
    if actual_conf_modes != EXPECTED_CONF_MODES:
        issues.append('cases:conf_modes=expected_exact_kconfig_conf_mode_list')
    if actual_confdata_names != EXPECTED_CONFDATA_CASES:
        issues.append('cases:confdata_names=expected_exact_kconfig_confdata_case_list')

    return issues


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for label, rel_path in REQUIRED_FILES.items():
        if not (root / rel_path).exists():
            issues.append(f'missing:{label}:{rel_path}')
    if issues:
        return issues

    bridge_checker = read_text(root, REQUIRED_FILES['bridge_checker'])
    workflow = read_text(root, REQUIRED_FILES['workflow'])

    for marker in BRIDGE_CHECKER_MARKERS:
        if marker not in bridge_checker:
            issues.append(f'bridge_checker:{marker}')
    issues.extend(validate_workflow(workflow))
    issues.extend(validate_cases(root))
    return issues


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / 'scripts/zigux/check-phase2-kconfig-bridge-selftest-alignment.py'), '--root', str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def clone_fixture_root(destination_root: Path) -> None:
    script_target = destination_root / 'scripts/zigux/check-phase2-kconfig-bridge-selftest-alignment.py'
    script_target.parent.mkdir(parents=True, exist_ok=True)
    script_target.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')

    for key in REQUIRED_FILES.values():
        (destination_root / key).parent.mkdir(parents=True, exist_ok=True)

    (destination_root / REQUIRED_FILES['bridge_checker']).write_text(
        '\n'.join(BRIDGE_CHECKER_MARKERS) + '\n',
        encoding='utf-8',
    )
    workflow_lines = [
        'run: python3 scripts/zigux/check-phase2-kconfig-bridge-selftest-alignment.py --self-test',
        'run: python3 scripts/zigux/check-phase2-kconfig-bridge-selftest-alignment.py',
    ]
    (destination_root / REQUIRED_FILES['workflow']).write_text('\n'.join(workflow_lines) + '\n', encoding='utf-8')
    (destination_root / REQUIRED_FILES['cases']).write_text(
        json.dumps(
            {
                'conf_cases': [
                    {'mode': mode}
                    for mode in EXPECTED_CONF_MODES
                ],
                'confdata_cases': [
                    {'name': name}
                    for name in EXPECTED_CONFDATA_CASES
                ],
            },
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )


def expect_issue(label: str, root: Path, needle: str) -> None:
    result = run_checker(root)
    if result.returncode == 0:
        raise SystemExit(f'phase2-kconfig-selftest-alignment:{label}:unexpected_pass')
    if needle not in result.stdout:
        actual = result.stdout.strip() or 'none'
        raise SystemExit(
            f'phase2-kconfig-selftest-alignment:{label}:expected:{needle}:actual:{actual}'
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_phase2_kconfig_selftest_alignment_') as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                'phase2-kconfig-selftest-alignment:baseline_failed:'
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        workflow_path = tmp_root / REQUIRED_FILES['workflow']
        original_workflow = workflow_path.read_text(encoding='utf-8')
        workflow_path.write_text(
            original_workflow.replace(
                'run: python3 scripts/zigux/check-phase2-kconfig-bridge-selftest-alignment.py --self-test\n',
                '',
                1,
            ),
            encoding='utf-8',
        )
        expect_issue(
            'workflow_self_test',
            tmp_root,
            'workflow:python3 scripts/zigux/check-phase2-kconfig-bridge-selftest-alignment.py --self-test:count=0:expected=1',
        )
        clone_fixture_root(tmp_root)

        workflow_lines = original_workflow.splitlines()
        self_test_line = 'run: python3 scripts/zigux/check-phase2-kconfig-bridge-selftest-alignment.py --self-test'
        live_line = 'run: python3 scripts/zigux/check-phase2-kconfig-bridge-selftest-alignment.py'
        self_test_index = workflow_lines.index(self_test_line)
        live_index = workflow_lines.index(live_line)
        workflow_lines[self_test_index], workflow_lines[live_index] = workflow_lines[live_index], workflow_lines[self_test_index]
        workflow_path.write_text('\n'.join(workflow_lines) + '\n', encoding='utf-8')
        expect_issue(
            'workflow_order',
            tmp_root,
            'workflow_order:python3 scripts/zigux/check-phase2-kconfig-bridge-selftest-alignment.py --self-test:before:python3 scripts/zigux/check-phase2-kconfig-bridge-selftest-alignment.py',
        )
        clone_fixture_root(tmp_root)

        cases_path = tmp_root / REQUIRED_FILES['cases']
        payload = json.loads(cases_path.read_text(encoding='utf-8'))
        payload['conf_cases'].pop()
        cases_path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
        expect_issue('conf_case_count', tmp_root, 'cases:conf_count=15:expected=16')
        clone_fixture_root(tmp_root)

        payload = json.loads(cases_path.read_text(encoding='utf-8'))
        payload['confdata_cases'].pop()
        cases_path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
        expect_issue('confdata_case_count', tmp_root, 'cases:confdata_count=17:expected=18')
        clone_fixture_root(tmp_root)

        payload = json.loads(cases_path.read_text(encoding='utf-8'))
        payload['confdata_cases'][0], payload['confdata_cases'][1] = payload['confdata_cases'][1], payload['confdata_cases'][0]
        cases_path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
        expect_issue(
            'confdata_order',
            tmp_root,
            'cases:confdata_names=expected_exact_kconfig_confdata_case_list',
        )

    print('PHASE2_KCONFIG_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST=pass')
    print('PHASE2_KCONFIG_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT=5')
    return 0


if '--self-test' in sys.argv[1:]:
    raise SystemExit(run_self_test())


ROOT = resolve_root()
problems = validate(ROOT)
if problems:
    print('PHASE2_KCONFIG_BRIDGE_SELFTEST_ALIGNMENT=fail')
    print('PHASE2_KCONFIG_BRIDGE_SELFTEST_ALIGNMENT_MISSING_START')
    for problem in problems:
        print(problem)
    print('PHASE2_KCONFIG_BRIDGE_SELFTEST_ALIGNMENT_MISSING_END')
    raise SystemExit(1)

print('PHASE2_KCONFIG_BRIDGE_SELFTEST_ALIGNMENT=pass')
print(f'PHASE2_KCONFIG_BRIDGE_SELFTEST_ALIGNMENT_ROOT={ROOT}')
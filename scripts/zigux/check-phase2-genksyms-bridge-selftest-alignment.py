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
    'makefile': 'zigux/Makefile',
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
EXPECTED_CASE_SPECS = {
    'minimal': {
        'argv': [],
        'expected': 'minimal_expected.json',
        'mode': 'stdout_json',
        'normalize_stderr': False,
    },
    'debug_reference_types': {
        'argv': ['-d', '-d', '-D', '-w', '-p', '-r', 'foo.symref', '-r', 'bar.symref', '-T', 'out.symtypes'],
        'expected': 'debug_reference_types_expected.json',
        'mode': 'stdout_json',
        'normalize_stderr': False,
    },
    'short_inline_reference_dump_types': {
        'argv': ['-d', '-rfoo.symref', '-Tout.symtypes', '-p'],
        'expected': 'short_inline_reference_dump_types_expected.json',
        'mode': 'stdout_json',
        'normalize_stderr': False,
    },
    'clustered_short_inline_reference': {
        'argv': ['-dwrfoo.symref', '-Tout.symtypes', '-p'],
        'expected': 'clustered_short_inline_reference_expected.json',
        'mode': 'stdout_json',
        'normalize_stderr': False,
    },
    'long_options': {
        'argv': ['--debug', '--warnings', '--reference=foo.symref', '--dump-types', 'types.symtypes', '--preserve'],
        'expected': 'long_options_expected.json',
        'mode': 'stdout_json',
        'normalize_stderr': False,
    },
    'abbreviated_long_options': {
        'argv': ['--deb', '--war', '--qui', '--ref=foo.symref', '--dump-t', 'types.symtypes', '--pres'],
        'expected': 'abbreviated_long_options_expected.json',
        'mode': 'stdout_json',
        'normalize_stderr': False,
    },
    'quiet_overrides_warning': {
        'argv': ['-w', '-q'],
        'expected': 'quiet_overrides_warning_expected.json',
        'mode': 'stdout_json',
        'normalize_stderr': False,
    },
    'explicit_option_terminator': {
        'argv': ['--', '--leftover', 'positional'],
        'expected': 'explicit_option_terminator_expected.json',
        'mode': 'stdout_json',
        'normalize_stderr': False,
    },
    'positional_passthrough': {
        'argv': ['leftover.c', '-d', 'rightover.h', '-r', 'foo.symref'],
        'expected': 'positional_passthrough_expected.json',
        'mode': 'stdout_json',
        'normalize_stderr': False,
    },
    'lone_dash_passthrough': {
        'argv': ['-', '-d', 'tail'],
        'expected': 'lone_dash_passthrough_expected.json',
        'mode': 'stdout_json',
        'normalize_stderr': False,
    },
    'explicit_terminator_positional_passthrough': {
        'argv': ['leftover.c', '-d', '--', 'tail.h'],
        'expected': 'explicit_terminator_positional_passthrough_expected.json',
        'mode': 'stdout_json',
        'normalize_stderr': False,
    },
    'help': {
        'argv': ['--hel'],
        'expected': 'help_expected.json',
        'mode': 'process_json',
        'normalize_stderr': False,
    },
    'version': {
        'argv': ['--ver'],
        'expected': 'version_expected.json',
        'mode': 'process_json',
        'normalize_stderr': False,
    },
    'invalid_option': {
        'argv': ['-x'],
        'expected': 'invalid_option_expected.json',
        'mode': 'process_json',
        'normalize_stderr': True,
    },
    'missing_reference_argument': {
        'argv': ['-r'],
        'expected': 'missing_reference_argument_expected.json',
        'mode': 'process_json',
        'normalize_stderr': True,
    },
    'missing_dump_types_argument': {
        'argv': ['-T'],
        'expected': 'missing_dump_types_argument_expected.json',
        'mode': 'process_json',
        'normalize_stderr': True,
    },
    'unsupported_long_option': {
        'argv': ['--bogus'],
        'expected': 'unsupported_long_option_expected.json',
        'mode': 'process_json',
        'normalize_stderr': True,
    },
    'ambiguous_abbreviated_long_option': {
        'argv': ['--dum'],
        'expected': 'ambiguous_abbreviated_long_option_expected.json',
        'mode': 'process_json',
        'normalize_stderr': True,
    },
    'empty_long_option_name': {
        'argv': ['--=value'],
        'expected': 'empty_long_option_name_expected.json',
        'mode': 'process_json',
        'normalize_stderr': True,
    },
    'unexpected_long_option_argument': {
        'argv': ['--debug=extra'],
        'expected': 'unexpected_long_option_argument_expected.json',
        'mode': 'process_json',
        'normalize_stderr': True,
    },
    'abbreviated_unexpected_long_option_argument': {
        'argv': ['--deb=extra'],
        'expected': 'abbreviated_unexpected_long_option_argument_expected.json',
        'mode': 'process_json',
        'normalize_stderr': True,
    },
    'missing_long_reference_argument': {
        'argv': ['--reference'],
        'expected': 'missing_long_reference_argument_expected.json',
        'mode': 'process_json',
        'normalize_stderr': True,
    },
    'abbreviated_missing_long_reference_argument': {
        'argv': ['--ref'],
        'expected': 'abbreviated_missing_long_reference_argument_expected.json',
        'mode': 'process_json',
        'normalize_stderr': True,
    },
    'missing_long_dump_types_argument': {
        'argv': ['--dump-types'],
        'expected': 'missing_long_dump_types_argument_expected.json',
        'mode': 'process_json',
        'normalize_stderr': True,
    },
    'abbreviated_missing_long_dump_types_argument': {
        'argv': ['--dump-t'],
        'expected': 'abbreviated_missing_long_dump_types_argument_expected.json',
        'mode': 'process_json',
        'normalize_stderr': True,
    },
    'too_many_reference_files': {
        'argv': [
            '-r', 'ref00.symref',
            '-r', 'ref01.symref',
            '-r', 'ref02.symref',
            '-r', 'ref03.symref',
            '-r', 'ref04.symref',
            '-r', 'ref05.symref',
            '-r', 'ref06.symref',
            '-r', 'ref07.symref',
            '-r', 'ref08.symref',
            '-r', 'ref09.symref',
            '-r', 'ref10.symref',
            '-r', 'ref11.symref',
            '-r', 'ref12.symref',
            '-r', 'ref13.symref',
            '-r', 'ref14.symref',
            '-r', 'ref15.symref',
            '-r', 'ref16.symref',
        ],
        'expected': 'too_many_reference_files_expected.json',
        'mode': 'process_json',
        'normalize_stderr': False,
    },
}
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
MAKEFILE_MARKERS = [
    'phase2-validate:',
    'phase2-tools:',
]
MAKEFILE_VALIDATE_RUN_COUNTS = {
    'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test': 1,
    'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py': 1,
    'scripts/zigux/validate-phase2.py': 1,
    'scripts/zigux/validate-phase2-closure.py': 1,
}
MAKEFILE_VALIDATE_ORDERED_COMMANDS = [
    'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test',
    'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py',
    'scripts/zigux/validate-phase2.py',
    'scripts/zigux/validate-phase2-closure.py',
]
MAKEFILE_TOOL_RUN_COUNTS = {
    'scripts/zigux/check-genksyms-bridge.py --self-test': 1,
    'scripts/zigux/check-genksyms-bridge.py': 1,
    '$(ZIG) test scripts/zigux/genksyms.zig': 1,
}
MAKEFILE_TOOL_ORDERED_COMMANDS = [
    'scripts/zigux/check-genksyms-bridge.py --self-test',
    'scripts/zigux/check-genksyms-bridge.py',
    '$(ZIG) test scripts/zigux/genksyms.zig',
]
WORKFLOW_RUN_COUNTS = {
    'python3 scripts/zigux/check-genksyms-bridge.py --self-test': 1,
    'python3 scripts/zigux/check-genksyms-bridge.py': 1,
    'python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test': 1,
    'python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py': 1,
    'python3 scripts/zigux/validate-phase2.py': 1,
    'python3 scripts/zigux/validate-phase2-closure.py': 1,
}
WORKFLOW_ORDERED_COMMANDS = [
    'python3 scripts/zigux/validate-phase2.py',
    'python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test',
    'python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py',
    'python3 scripts/zigux/validate-phase2-closure.py',
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


def validate_cases(root: Path) -> list[str]:
    issues: list[str] = []
    payload = json.loads(read_text(root, REQUIRED_FILES['cases']))
    if not isinstance(payload, dict):
        return ['cases:expected_top_level_object']
    cases = payload.get('cases')
    if not isinstance(cases, list):
        return ['cases:expected_list']

    actual_names: list[str] = []
    seen_names: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            issues.append('cases:entry:expected_object')
            continue

        name = case.get('name')
        if not isinstance(name, str) or not name:
            issues.append('cases:missing_name')
            continue
        if name in seen_names:
            issues.append(f'cases:duplicate_name:{name}')
            continue
        seen_names.add(name)
        actual_names.append(name)

        spec = EXPECTED_CASE_SPECS.get(name)
        if spec is None:
            issues.append(f'cases:unexpected_name:{name}')
            continue

        actual_argv = case.get('argv')
        if actual_argv != spec['argv']:
            issues.append(
                f"cases:{name}:argv={actual_argv!r}:expected_argv={spec['argv']!r}"
            )

        actual_expected = case.get('expected')
        if actual_expected != spec['expected']:
            issues.append(
                f"cases:{name}:expected={actual_expected!r}:expected_file={spec['expected']!r}"
            )

        actual_mode = case.get('mode', 'stdout_json')
        if actual_mode != spec['mode']:
            issues.append(
                f"cases:{name}:mode={actual_mode!r}:expected_mode={spec['mode']!r}"
            )

        actual_normalize_stderr = case.get('normalize_stderr', False)
        if actual_normalize_stderr != spec['normalize_stderr']:
            issues.append(
                f'cases:{name}:normalize_stderr={actual_normalize_stderr!r}:'
                f"expected_normalize_stderr={spec['normalize_stderr']!r}"
            )

    if len(cases) != 26:
        issues.append(f'cases:count={len(cases)}:expected=26')
    if actual_names != EXPECTED_CASE_NAMES:
        issues.append('cases:names=expected_exact_phase2_genksyms_bridge_case_list')

    missing_names = sorted(set(EXPECTED_CASE_SPECS) - seen_names)
    for name in missing_names:
        issues.append(f'cases:missing_name:{name}')

    return issues


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


def validate_makefile(makefile_text: str) -> list[str]:
    issues: list[str] = []
    stripped_lines = [line.strip() for line in makefile_text.splitlines()]
    for command, expected_count in MAKEFILE_VALIDATE_RUN_COUNTS.items():
        count = sum(1 for line in stripped_lines if line.endswith(command))
        if count != expected_count:
            issues.append(f'makefile_validate_run:{command}:count={count}:expected={expected_count}')
    issues.extend(
        validate_ordered_commands(
            stripped_lines,
            MAKEFILE_VALIDATE_ORDERED_COMMANDS,
            'makefile_validate',
            find_position=lambda lines, command: next(
                (index for index, line in enumerate(lines) if line.endswith(command)),
                None,
            ),
        )
    )
    for command, expected_count in MAKEFILE_TOOL_RUN_COUNTS.items():
        count = sum(1 for line in stripped_lines if line.endswith(command))
        if count != expected_count:
            issues.append(f'makefile_tool_run:{command}:count={count}:expected={expected_count}')
    issues.extend(
        validate_ordered_commands(
            stripped_lines,
            MAKEFILE_TOOL_ORDERED_COMMANDS,
            'makefile_tool',
            find_position=lambda lines, command: next(
                (index for index, line in enumerate(lines) if line.endswith(command)),
                None,
            ),
        )
    )
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
    makefile = read_text(root, REQUIRED_FILES['makefile'])

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
    for marker in MAKEFILE_MARKERS:
        if marker not in makefile:
            issues.append(f'makefile:{marker}')
    issues.extend(validate_workflow(workflow))
    issues.extend(validate_makefile(makefile))
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

    for key in ('bridge_checker', 'readme', 'closure_doc', 'closure_validator', 'validator', 'workflow', 'makefile', 'cases'):
        (destination_root / REQUIRED_FILES[key]).parent.mkdir(parents=True, exist_ok=True)

    (destination_root / REQUIRED_FILES['bridge_checker']).write_text(
        "print('PHASE2_GENKSYMS_BRIDGE_SELF_TEST=pass')\nprint('PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=26')\n",
        encoding='utf-8',
    )
    (destination_root / REQUIRED_FILES['readme']).write_text('\n'.join(README_MARKERS) + '\n', encoding='utf-8')
    (destination_root / REQUIRED_FILES['closure_doc']).write_text('\n'.join(CLOSURE_DOC_MARKERS) + '\n', encoding='utf-8')
    (destination_root / REQUIRED_FILES['closure_validator']).write_text('\n'.join(CLOSURE_VALIDATOR_MARKERS) + '\n', encoding='utf-8')
    (destination_root / REQUIRED_FILES['validator']).write_text('\n'.join(VALIDATOR_MARKERS) + '\n', encoding='utf-8')
    workflow_lines = [
        'run: python3 scripts/zigux/check-genksyms-bridge.py --self-test',
        'run: python3 scripts/zigux/check-genksyms-bridge.py',
        'run: python3 scripts/zigux/validate-phase2.py',
        'run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test',
        'run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py',
        'run: python3 scripts/zigux/validate-phase2-closure.py',
    ]
    (destination_root / REQUIRED_FILES['workflow']).write_text('\n'.join(workflow_lines) + '\n', encoding='utf-8')
    makefile_lines = [
        'phase2-validate:',
        'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test',
        'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py',
        'scripts/zigux/validate-phase2.py',
        'scripts/zigux/validate-phase2-closure.py',
        'phase2-tools:',
        'scripts/zigux/check-genksyms-bridge.py --self-test',
        'scripts/zigux/check-genksyms-bridge.py',
        '$(ZIG) test scripts/zigux/genksyms.zig',
    ]
    (destination_root / REQUIRED_FILES['makefile']).write_text('\n'.join(makefile_lines) + '\n', encoding='utf-8')
    (destination_root / REQUIRED_FILES['cases']).write_text(
        json.dumps(
            {
                'cases': [
                    {
                        'name': name,
                        'argv': EXPECTED_CASE_SPECS[name]['argv'],
                        'expected': EXPECTED_CASE_SPECS[name]['expected'],
                        'mode': EXPECTED_CASE_SPECS[name]['mode'],
                        'normalize_stderr': EXPECTED_CASE_SPECS[name]['normalize_stderr'],
                    }
                    for name in EXPECTED_CASE_NAMES
                ]
            },
            indent=2,
        ) + '\n',
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

        readme_path = tmp_root / REQUIRED_FILES['readme']
        original_readme = readme_path.read_text(encoding='utf-8')
        readme_path.write_text(
            original_readme.replace(README_MARKERS[0] + '\n', '', 1),
            encoding='utf-8',
        )
        expect_issue('readme_marker', tmp_root, f'readme:{README_MARKERS[0]}')
        readme_path.write_text(original_readme, encoding='utf-8')

        closure_doc_path = tmp_root / REQUIRED_FILES['closure_doc']
        original_closure_doc = closure_doc_path.read_text(encoding='utf-8')
        closure_doc_path.write_text(
            original_closure_doc.replace(CLOSURE_DOC_MARKERS[1] + '\n', '', 1),
            encoding='utf-8',
        )
        expect_issue('closure_doc_marker', tmp_root, f'closure_doc:{CLOSURE_DOC_MARKERS[1]}')
        closure_doc_path.write_text(original_closure_doc, encoding='utf-8')

        workflow_path = tmp_root / REQUIRED_FILES['workflow']
        original_workflow = workflow_path.read_text(encoding='utf-8')
        workflow_path.write_text(
            original_workflow.replace('run: python3 scripts/zigux/check-genksyms-bridge.py --self-test\n', '', 1),
            encoding='utf-8',
        )
        expect_issue('workflow_bridge_self_test', tmp_root, 'workflow:python3 scripts/zigux/check-genksyms-bridge.py --self-test:count=0:expected=1')
        workflow_path.write_text(original_workflow, encoding='utf-8')

        workflow_path.write_text(
            original_workflow.replace('run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test\n', '', 1),
            encoding='utf-8',
        )
        expect_issue(
            'workflow_alignment_self_test',
            tmp_root,
            'workflow:python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test:count=0:expected=1',
        )
        workflow_path.write_text(original_workflow, encoding='utf-8')

        workflow_path.write_text(
            original_workflow.replace('run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py\n', '', 1),
            encoding='utf-8',
        )
        expect_issue(
            'workflow_alignment_live',
            tmp_root,
            'workflow:python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py:count=0:expected=1',
        )
        workflow_path.write_text(original_workflow, encoding='utf-8')

        workflow_lines = original_workflow.splitlines()
        self_test_line = 'run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test'
        live_line = 'run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py'
        self_test_index = workflow_lines.index(self_test_line)
        live_index = workflow_lines.index(live_line)
        workflow_lines[self_test_index], workflow_lines[live_index] = workflow_lines[live_index], workflow_lines[self_test_index]
        workflow_path.write_text('\n'.join(workflow_lines) + '\n', encoding='utf-8')
        expect_issue(
            'workflow_alignment_order',
            tmp_root,
            'workflow_order:python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test:before:python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py',
        )
        workflow_path.write_text(original_workflow, encoding='utf-8')

        workflow_lines = original_workflow.splitlines()
        closure_line = 'run: python3 scripts/zigux/validate-phase2-closure.py'
        closure_index = workflow_lines.index(closure_line)
        live_index = workflow_lines.index(live_line)
        workflow_lines[closure_index], workflow_lines[live_index] = workflow_lines[live_index], workflow_lines[closure_index]
        workflow_path.write_text('\n'.join(workflow_lines) + '\n', encoding='utf-8')
        expect_issue(
            'workflow_closure_order',
            tmp_root,
            'workflow_order:python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py:before:python3 scripts/zigux/validate-phase2-closure.py',
        )
        workflow_path.write_text(original_workflow, encoding='utf-8')

        makefile_path = tmp_root / REQUIRED_FILES['makefile']
        original_makefile = makefile_path.read_text(encoding='utf-8')
        makefile_path.write_text(
            original_makefile.replace('scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test\n', '', 1),
            encoding='utf-8',
        )
        expect_issue(
            'makefile_self_test',
            tmp_root,
            'makefile_validate_run:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test:count=0:expected=1',
        )
        makefile_path.write_text(original_makefile, encoding='utf-8')

        makefile_lines = original_makefile.splitlines()
        makefile_path.write_text(
            '\n'.join(
                line
                for line in makefile_lines
                if line != 'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py'
            ) + '\n',
            encoding='utf-8',
        )
        expect_issue(
            'makefile_live',
            tmp_root,
            'makefile_validate_run:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py:count=0:expected=1',
        )
        makefile_path.write_text(original_makefile, encoding='utf-8')

        makefile_lines = original_makefile.splitlines()
        self_test_line = 'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test'
        live_line = 'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py'
        self_test_index = makefile_lines.index(self_test_line)
        live_index = makefile_lines.index(live_line)
        makefile_lines[self_test_index], makefile_lines[live_index] = makefile_lines[live_index], makefile_lines[self_test_index]
        makefile_path.write_text('\n'.join(makefile_lines) + '\n', encoding='utf-8')
        expect_issue(
            'makefile_alignment_order',
            tmp_root,
            'makefile_validate_order:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test:before:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py',
        )
        makefile_path.write_text(original_makefile, encoding='utf-8')

        makefile_lines = original_makefile.splitlines()
        validator_line = 'scripts/zigux/validate-phase2.py'
        validator_index = makefile_lines.index(validator_line)
        live_index = makefile_lines.index(live_line)
        makefile_lines[validator_index], makefile_lines[live_index] = makefile_lines[live_index], makefile_lines[validator_index]
        makefile_path.write_text('\n'.join(makefile_lines) + '\n', encoding='utf-8')
        expect_issue(
            'makefile_validator_order',
            tmp_root,
            'makefile_validate_order:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py:before:scripts/zigux/validate-phase2.py',
        )
        makefile_path.write_text(original_makefile, encoding='utf-8')

        makefile_path.write_text(
            original_makefile.replace('scripts/zigux/check-genksyms-bridge.py --self-test\n', '', 1),
            encoding='utf-8',
        )
        expect_issue(
            'makefile_tool_self_test',
            tmp_root,
            'makefile_tool_run:scripts/zigux/check-genksyms-bridge.py --self-test:count=0:expected=1',
        )
        makefile_path.write_text(original_makefile, encoding='utf-8')

        makefile_lines = original_makefile.splitlines()
        makefile_path.write_text(
            '\n'.join(
                line
                for line in makefile_lines
                if line != 'scripts/zigux/check-genksyms-bridge.py'
            ) + '\n',
            encoding='utf-8',
        )
        expect_issue(
            'makefile_tool_live',
            tmp_root,
            'makefile_tool_run:scripts/zigux/check-genksyms-bridge.py:count=0:expected=1',
        )
        makefile_path.write_text(original_makefile, encoding='utf-8')

        makefile_lines = original_makefile.splitlines()
        tool_self_test_line = 'scripts/zigux/check-genksyms-bridge.py --self-test'
        tool_live_line = 'scripts/zigux/check-genksyms-bridge.py'
        tool_self_test_index = makefile_lines.index(tool_self_test_line)
        tool_live_index = makefile_lines.index(tool_live_line)
        makefile_lines[tool_self_test_index], makefile_lines[tool_live_index] = makefile_lines[tool_live_index], makefile_lines[tool_self_test_index]
        makefile_path.write_text('\n'.join(makefile_lines) + '\n', encoding='utf-8')
        expect_issue(
            'makefile_tool_order',
            tmp_root,
            'makefile_tool_order:scripts/zigux/check-genksyms-bridge.py --self-test:before:scripts/zigux/check-genksyms-bridge.py',
        )
        makefile_path.write_text(original_makefile, encoding='utf-8')

        makefile_lines = original_makefile.splitlines()
        tool_live_index = makefile_lines.index(tool_live_line)
        zig_test_line = '$(ZIG) test scripts/zigux/genksyms.zig'
        zig_test_index = makefile_lines.index(zig_test_line)
        makefile_lines[tool_live_index], makefile_lines[zig_test_index] = makefile_lines[zig_test_index], makefile_lines[tool_live_index]
        makefile_path.write_text('\n'.join(makefile_lines) + '\n', encoding='utf-8')
        expect_issue(
            'makefile_tool_unit_order',
            tmp_root,
            'makefile_tool_order:scripts/zigux/check-genksyms-bridge.py:before:$(ZIG) test scripts/zigux/genksyms.zig',
        )
        makefile_path.write_text(original_makefile, encoding='utf-8')

        live_prefixed_makefile_lines = [
            'phase2-validate:',
            'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test',
            'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py',
            'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py',
            'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py',
            'phase2-tools:',
            'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test',
            'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py',
            'cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig',
        ]
        makefile_path.write_text('\n'.join(live_prefixed_makefile_lines) + '\n', encoding='utf-8')
        live_prefixed_baseline = run_checker(tmp_root)
        if live_prefixed_baseline.returncode != 0:
            raise SystemExit(
                'phase2-genksyms-selftest-alignment:live_prefixed_makefile_baseline_failed:'
                f"{live_prefixed_baseline.stdout.strip() or live_prefixed_baseline.stderr.strip() or 'no_output'}"
            )

        live_prefixed_makefile_lines[1], live_prefixed_makefile_lines[2] = (
            live_prefixed_makefile_lines[2],
            live_prefixed_makefile_lines[1],
        )
        makefile_path.write_text('\n'.join(live_prefixed_makefile_lines) + '\n', encoding='utf-8')
        expect_issue(
            'live_prefixed_makefile_alignment_order',
            tmp_root,
            'makefile_validate_order:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test:before:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py',
        )
        clone_fixture_root(tmp_root)

        cases_path = tmp_root / REQUIRED_FILES['cases']
        cases_payload = json.loads(cases_path.read_text(encoding='utf-8'))
        cases_payload['cases'].pop()
        cases_path.write_text(json.dumps(cases_payload, indent=2) + '\n', encoding='utf-8')
        expect_issue('case_count', tmp_root, 'cases:count=25:expected=26')
        clone_fixture_root(tmp_root)

        cases_payload = json.loads(cases_path.read_text(encoding='utf-8'))
        cases_payload['cases'][0]['expected'] = 'help_expected.json'
        cases_path.write_text(json.dumps(cases_payload, indent=2) + '\n', encoding='utf-8')
        expect_issue(
            'case_expected_fixture',
            tmp_root,
            "cases:minimal:expected='help_expected.json':expected_file='minimal_expected.json'",
        )
        clone_fixture_root(tmp_root)

        cases_payload = json.loads(cases_path.read_text(encoding='utf-8'))
        cases_payload['cases'][0]['argv'] = ['--bogus']
        cases_path.write_text(json.dumps(cases_payload, indent=2) + '\n', encoding='utf-8')
        expect_issue(
            'case_argv_contract',
            tmp_root,
            "cases:minimal:argv=['--bogus']:expected_argv=[]",
        )
        clone_fixture_root(tmp_root)

        cases_payload = json.loads(cases_path.read_text(encoding='utf-8'))
        cases_payload['cases'][11]['normalize_stderr'] = True
        cases_path.write_text(json.dumps(cases_payload, indent=2) + '\n', encoding='utf-8')
        expect_issue(
            'case_normalize_stderr_contract',
            tmp_root,
            'cases:help:normalize_stderr=True:expected_normalize_stderr=False',
        )
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
    print('PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT=24')
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
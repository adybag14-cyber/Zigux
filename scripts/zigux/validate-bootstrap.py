#!/usr/bin/env python3
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
required_files = [
    ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml',
    ROOT / 'zigux-alpha' / 'README.md',
    ROOT / 'zigux-alpha' / 'ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md',
    ROOT / 'Documentation' / 'zigux' / 'README.md',
    ROOT / 'Documentation' / 'zigux' / 'review-checklist.md',
    ROOT / 'Documentation' / 'zigux' / 'freeze-map.md',
    ROOT / 'Documentation' / 'zigux' / 'phase2-toolchain-bootstrap-notes.md',
    ROOT / 'Documentation' / 'zigux' / 'phase2-closure.md',
    ROOT / 'scripts' / 'zigux' / 'README.md',
    ROOT / 'scripts' / 'zigux' / 'check-zig-toolchain.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase2-toolchain-pin-scope.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase2-tests-readme-alignment.py',
    ROOT / 'scripts' / 'zigux' / 'install-zig.py',
    ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json',
    ROOT / 'scripts' / 'zigux' / 'validate-phase2.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase6.py',
    ROOT / 'zigux' / 'tests' / 'README.md',
    ROOT / 'zigux' / 'Makefile',
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_FILES_START')
    for item in missing:
        print(item)
    print('MISSING_FILES_END')
    sys.exit(1)

roadmap = (ROOT / 'zigux-alpha' / 'ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md').read_text(encoding='utf-8')
required_markers = [
    '## Non-Negotiable Product Rules',
    '## Product Features by Phase',
    '## Freeze Map for Near- and Mid-Term Planning',
    '## First Commit and Push Sequence for Zigux',
    'kernel/sched/core.c',
    'mm/page_alloc.c',
    'kernel/rcu/tree.c',
    'net/core/skbuff.c',
]
missing_markers = [marker for marker in required_markers if marker not in roadmap]
if missing_markers:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_MARKERS_START')
    for marker in missing_markers:
        print(marker)
    print('MISSING_MARKERS_END')
    sys.exit(1)

workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
required_workflow_markers = [
    'lib/**',
    'zigux-alpha/**',
    'Documentation/zigux/**',
    'scripts/zigux/**',
    'tools/lib/*.zig',
    'zigux/**',
    'include/linux/zigux.h',
    'include/zigux/**',
    '.github/workflows/zigux-bootstrap.yml',
    'Self-test Zig installer',
    'python3 scripts/zigux/install-zig.py --self-test',
    'python3 scripts/zigux/install-zig.py --dest .zig-toolchain',
    'Self-test Zig toolchain checker',
    'python3 scripts/zigux/check-zig-toolchain.py --self-test',
    'Validate Phase 6 leaf helper gates',
    'make -C zigux phase6-validate',
    'Run Phase 6 leaf helper tests',
    'zigux/tests/phase6_build.zig',
    'Run Phase 7 runtime helper tests',
    'zigux/tests/phase7_build.zig',
    'Run Phase 8 tooling tests',
    'zigux/tests/phase8_build.zig',
    'Run Phase 9 runtime helper tests',
    'zigux/tests/phase9_build.zig',
    'Self-test Phase 10 harness coverage checker',
    'python3 scripts/zigux/check-phase10-harness-coverage.py --self-test',
    'Validate Phase 10 focused harness coverage',
    'python3 scripts/zigux/check-phase10-harness-coverage.py',
    'Run Phase 10 virtio helper tests',
    'zigux/tests/phase10_build.zig',
    'Self-test Phase 11 simple-driver validator',
    'python3 scripts/zigux/validate-phase11.py --self-test',
    'Self-test Phase 11 header boundary packet checker',
    'python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test',
    'Validate Phase 11 header boundary packet',
    'python3 scripts/zigux/check-phase11-header-boundary-packet.py',
    'Validate Phase 11 simple-driver bundle',
    'make -C zigux phase11-validate',
    'Run Phase 11 watchdog and console tests',
    'zigux/tests/phase11_build.zig',
    'Run dedicated Phase 11 hvc survey replay',
    'make -C zigux phase11-hvc-survey',
    'Run Phase 12 complex driver tests',
    'zigux/tests/phase12_build.zig',
    'Run Phase 13 shared helper tests',
    'zigux/tests/phase13_build.zig',
    'Validate Phase 14 shared smoke packet',
    'make -C zigux phase14-validate',
    'Run Phase 14 smoke shard',
    'make -C zigux phase14-smoke',
    'Run Phase 14 internal bridge tests',
    'zigux/tests/phase14_build.zig',
    'Run Phase 15 governance tests',
    'make -C zigux phase15',
]
missing_workflow_markers = [marker for marker in required_workflow_markers if marker not in workflow]
if missing_workflow_markers:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_WORKFLOW_MARKERS_START')
    for marker in missing_workflow_markers:
        print(marker)
    print('MISSING_WORKFLOW_MARKERS_END')
    sys.exit(1)

toolchain_policy_command = 'python3 scripts/zigux/check-zig-toolchain.py'
toolchain_policy_self_test_command = 'python3 scripts/zigux/check-zig-toolchain.py --self-test'
toolchain_policy_step = 'Check Zig toolchain policy'
toolchain_policy_self_test_step = 'Self-test Zig toolchain checker'
workflow_toolchain_policy_command_count = len(
    re.findall(r'^\s*run:\s+python3 scripts/zigux/check-zig-toolchain\.py\s*$', workflow, flags=re.MULTILINE)
)
workflow_toolchain_policy_step_count = workflow.count(toolchain_policy_step)
workflow_toolchain_policy_self_test_command_count = workflow.count(toolchain_policy_self_test_command)
workflow_toolchain_policy_self_test_step_count = workflow.count(toolchain_policy_self_test_step)
if (
    workflow_toolchain_policy_command_count != 2
    or workflow_toolchain_policy_step_count != 2
    or workflow_toolchain_policy_self_test_command_count != 1
    or workflow_toolchain_policy_self_test_step_count != 1
):
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_WORKFLOW_TOOLCHAIN_POLICY_WIRING_START')
    print(f'workflow:toolchain_policy_command_count={workflow_toolchain_policy_command_count},expected=2')
    print(f'workflow:toolchain_policy_step_count={workflow_toolchain_policy_step_count},expected=2')
    print(
        'workflow:toolchain_policy_self_test_command_count='
        f'{workflow_toolchain_policy_self_test_command_count},expected=1'
    )
    print(
        'workflow:toolchain_policy_self_test_step_count='
        f'{workflow_toolchain_policy_self_test_step_count},expected=1'
    )
    print('MISSING_WORKFLOW_TOOLCHAIN_POLICY_WIRING_END')
    sys.exit(1)

phase11_validator_self_test_command = 'python3 scripts/zigux/validate-phase11.py --self-test'
phase11_validator_self_test_step = 'Self-test Phase 11 simple-driver validator'
phase11_header_boundary_self_test_command = 'python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test'
phase11_header_boundary_self_test_step = 'Self-test Phase 11 header boundary packet checker'
phase11_header_boundary_validate_command = 'python3 scripts/zigux/check-phase11-header-boundary-packet.py'
phase11_header_boundary_validate_step = 'Validate Phase 11 header boundary packet'
phase11_validate_command = 'make -C zigux phase11-validate'
phase11_validate_step = 'Validate Phase 11 simple-driver bundle'
phase11_hvc_survey_command = 'make -C zigux phase11-hvc-survey'
phase11_hvc_survey_step = 'Run dedicated Phase 11 hvc survey replay'
workflow_phase11_validator_self_test_command_count = len(
    re.findall(r'^\s*run:\s+python3 scripts/zigux/validate-phase11\.py --self-test\s*$', workflow, flags=re.MULTILINE)
)
workflow_phase11_validator_self_test_step_count = workflow.count(phase11_validator_self_test_step)
workflow_phase11_header_boundary_self_test_command_count = len(
    re.findall(
        r'^\s*run:\s+python3 scripts/zigux/check-phase11-header-boundary-packet\.py --self-test\s*$',
        workflow,
        flags=re.MULTILINE,
    )
)
workflow_phase11_header_boundary_self_test_step_count = workflow.count(
    phase11_header_boundary_self_test_step
)
workflow_phase11_header_boundary_validate_command_count = len(
    re.findall(
        r'^\s*run:\s+python3 scripts/zigux/check-phase11-header-boundary-packet\.py\s*$',
        workflow,
        flags=re.MULTILINE,
    )
)
workflow_phase11_header_boundary_validate_step_count = workflow.count(
    phase11_header_boundary_validate_step
)
workflow_phase11_validate_command_count = len(
    re.findall(r'^\s*run:\s+make -C zigux phase11-validate\s*$', workflow, flags=re.MULTILINE)
)
workflow_phase11_validate_step_count = workflow.count(phase11_validate_step)
workflow_phase11_hvc_survey_command_count = len(
    re.findall(r'^\s*run:\s+make -C zigux phase11-hvc-survey\s*$', workflow, flags=re.MULTILINE)
)
workflow_phase11_hvc_survey_step_count = workflow.count(phase11_hvc_survey_step)
if (
    workflow_phase11_validator_self_test_command_count != 1
    or workflow_phase11_validator_self_test_step_count != 1
    or workflow_phase11_header_boundary_self_test_command_count != 1
    or workflow_phase11_header_boundary_self_test_step_count != 1
    or workflow_phase11_header_boundary_validate_command_count != 1
    or workflow_phase11_header_boundary_validate_step_count != 1
    or workflow_phase11_validate_command_count != 1
    or workflow_phase11_validate_step_count != 1
    or workflow_phase11_hvc_survey_command_count != 1
    or workflow_phase11_hvc_survey_step_count != 1
):
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_WORKFLOW_PHASE11_WIRING_START')
    print(
        'workflow:phase11_validator_self_test_command_count='
        f'{workflow_phase11_validator_self_test_command_count},expected=1'
    )
    print(
        'workflow:phase11_validator_self_test_step_count='
        f'{workflow_phase11_validator_self_test_step_count},expected=1'
    )
    print(
        'workflow:phase11_header_boundary_self_test_command_count='
        f'{workflow_phase11_header_boundary_self_test_command_count},expected=1'
    )
    print(
        'workflow:phase11_header_boundary_self_test_step_count='
        f'{workflow_phase11_header_boundary_self_test_step_count},expected=1'
    )
    print(
        'workflow:phase11_header_boundary_validate_command_count='
        f'{workflow_phase11_header_boundary_validate_command_count},expected=1'
    )
    print(
        'workflow:phase11_header_boundary_validate_step_count='
        f'{workflow_phase11_header_boundary_validate_step_count},expected=1'
    )
    print(f'workflow:phase11_validate_command_count={workflow_phase11_validate_command_count},expected=1')
    print(f'workflow:phase11_validate_step_count={workflow_phase11_validate_step_count},expected=1')
    print(f'workflow:phase11_hvc_survey_command_count={workflow_phase11_hvc_survey_command_count},expected=1')
    print(f'workflow:phase11_hvc_survey_step_count={workflow_phase11_hvc_survey_step_count},expected=1')
    print('MISSING_WORKFLOW_PHASE11_WIRING_END')
    sys.exit(1)

phase10_harness_self_test_command = 'python3 scripts/zigux/check-phase10-harness-coverage.py --self-test'
phase10_harness_self_test_step = 'Self-test Phase 10 harness coverage checker'
phase10_harness_validate_command = 'python3 scripts/zigux/check-phase10-harness-coverage.py'
phase10_harness_validate_step = 'Validate Phase 10 focused harness coverage'
workflow_phase10_harness_self_test_command_count = len(
    re.findall(
        r'^\s*run:\s+python3 scripts/zigux/check-phase10-harness-coverage\.py --self-test\s*$',
        workflow,
        flags=re.MULTILINE,
    )
)
workflow_phase10_harness_self_test_step_count = workflow.count(phase10_harness_self_test_step)
workflow_phase10_harness_validate_command_count = len(
    re.findall(
        r'^\s*run:\s+python3 scripts/zigux/check-phase10-harness-coverage\.py\s*$',
        workflow,
        flags=re.MULTILINE,
    )
)
workflow_phase10_harness_validate_step_count = workflow.count(phase10_harness_validate_step)
if (
    workflow_phase10_harness_self_test_command_count != 1
    or workflow_phase10_harness_self_test_step_count != 1
    or workflow_phase10_harness_validate_command_count != 1
    or workflow_phase10_harness_validate_step_count != 1
):
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_WORKFLOW_PHASE10_HARNESS_WIRING_START')
    print(
        'workflow:phase10_harness_self_test_command_count='
        f'{workflow_phase10_harness_self_test_command_count},expected=1'
    )
    print(
        'workflow:phase10_harness_self_test_step_count='
        f'{workflow_phase10_harness_self_test_step_count},expected=1'
    )
    print(
        'workflow:phase10_harness_validate_command_count='
        f'{workflow_phase10_harness_validate_command_count},expected=1'
    )
    print(
        'workflow:phase10_harness_validate_step_count='
        f'{workflow_phase10_harness_validate_step_count},expected=1'
    )
    print('MISSING_WORKFLOW_PHASE10_HARNESS_WIRING_END')
    sys.exit(1)

toolchain_policy = json.loads((ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json').read_text(encoding='utf-8'))
required_policy_values = {
    'phase': 'Phase 2',
    'policy_note': 'Shared Zigux bootstrap and Phase 2 toolchain pin.',
    'archive_sha256': {
        'x86_64-linux': 'a3eae1cdb9643cf68e09e97574fb6780699e05148c270e52347faa293b80d858',
    },
}
policy_issues = []
if not isinstance(toolchain_policy, dict):
    policy_issues.append('toolchain_policy:expected_object')
else:
    for field_name, expected_value in required_policy_values.items():
        if toolchain_policy.get(field_name) != expected_value:
            policy_issues.append(
                f"toolchain_policy:{field_name}={toolchain_policy.get(field_name)!r},expected={expected_value!r}"
            )

    for field_name in ('channel', 'minimum_version'):
        value = toolchain_policy.get(field_name)
        if not isinstance(value, str) or not value:
            policy_issues.append(f'toolchain_policy:{field_name}:expected_non_empty_string')

    if (
        isinstance(toolchain_policy.get('channel'), str)
        and isinstance(toolchain_policy.get('minimum_version'), str)
        and toolchain_policy['channel'] != toolchain_policy['minimum_version']
    ):
        policy_issues.append(
            'toolchain_policy:channel_minimum_version_mismatch='
            f"{toolchain_policy['channel']!r}!={toolchain_policy['minimum_version']!r}"
        )

if policy_issues:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_TOOLCHAIN_POLICY_MARKERS_START')
    for issue in policy_issues:
        print(issue)
    print('MISSING_TOOLCHAIN_POLICY_MARKERS_END')
    sys.exit(1)

toolchain_checker = (ROOT / 'scripts' / 'zigux' / 'check-zig-toolchain.py').read_text(encoding='utf-8')
required_toolchain_markers = [
    'zig-toolchain-policy.json',
    'archive_sha256',
    'ZIG_TOOLCHAIN_REQUIRED_VERSION',
    'ZIG_TOOLCHAIN_TARGET',
    'ZIG_TOOLCHAIN_EXPECTED_SHA256',
    'status = "not_pinned"',
]
missing_toolchain_markers = [marker for marker in required_toolchain_markers if marker not in toolchain_checker]
if missing_toolchain_markers:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_TOOLCHAIN_CHECKER_MARKERS_START')
    for marker in missing_toolchain_markers:
        print(marker)
    print('MISSING_TOOLCHAIN_CHECKER_MARKERS_END')
    sys.exit(1)

installer = (ROOT / 'scripts' / 'zigux' / 'install-zig.py').read_text(encoding='utf-8')
required_installer_markers = [
    'zig-toolchain-policy.json',
    'policy version drift',
    'archive_sha256',
    'ZIG_INSTALL_EXPECTED_SHA256',
    'ZIG_INSTALL_ARCHIVE_SHA256',
    'archive sha256 mismatch for',
    "parser.add_argument('--self-test'",
]
missing_installer_markers = [marker for marker in required_installer_markers if marker not in installer]
if missing_installer_markers:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_INSTALLER_MARKERS_START')
    for marker in missing_installer_markers:
        print(marker)
    print('MISSING_INSTALLER_MARKERS_END')
    sys.exit(1)

phase2_validator = (ROOT / 'scripts' / 'zigux' / 'validate-phase2.py').read_text(encoding='utf-8')
required_phase2_validator_markers = [
    'TOOLCHAIN_PIN_SCOPE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"',
    'PHASE2_TESTS_README_ALIGNMENT_CHECKER = (',
    'label="phase2_tests_readme",',
    'str(PHASE2_TESTS_README_ALIGNMENT_CHECKER)',
    '"PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass"',
    '"PHASE2_TOOLCHAIN_PIN_SCOPE=pass"',
    'str(TOOLCHAIN_PIN_SCOPE_CHECKER)',
    'toolchain_pin_scope_checker',
]
missing_phase2_validator_markers = [
    marker for marker in required_phase2_validator_markers if marker not in phase2_validator
]
if missing_phase2_validator_markers:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_PHASE2_VALIDATOR_MARKERS_START')
    for marker in missing_phase2_validator_markers:
        print(marker)
    print('MISSING_PHASE2_VALIDATOR_MARKERS_END')
    sys.exit(1)

phase2_pin_scope_checker = (
    ROOT / 'scripts' / 'zigux' / 'check-phase2-toolchain-pin-scope.py'
).read_text(encoding='utf-8')
required_phase2_pin_scope_checker_markers = [
    'PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass',
    'PHASE2_TOOLCHAIN_PIN_SCOPE=pass',
    'TOOLCHAIN_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"',
    'CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"',
    'README_MARKERS = [',
    'def expected_toolchain_notes_markers(',
    'CLOSURE_MARKERS = [',
]
missing_phase2_pin_scope_checker_markers = [
    marker for marker in required_phase2_pin_scope_checker_markers if marker not in phase2_pin_scope_checker
]
if missing_phase2_pin_scope_checker_markers:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_PHASE2_PIN_SCOPE_CHECKER_MARKERS_START')
    for marker in missing_phase2_pin_scope_checker_markers:
        print(marker)
    print('MISSING_PHASE2_PIN_SCOPE_CHECKER_MARKERS_END')
    sys.exit(1)

scripts_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')
required_scripts_readme_pin_scope_markers = [
    'check-phase2-toolchain-pin-scope.py --self-test',
    'check-phase2-toolchain-pin-scope.py',
    'check-phase2-tests-readme-alignment.py --self-test',
    'check-phase2-tests-readme-alignment.py',
    'zig-toolchain-policy.json',
    'x86_64-linux',
]
missing_scripts_readme_pin_scope_markers = [
    marker for marker in required_scripts_readme_pin_scope_markers if marker not in scripts_readme
]
if missing_scripts_readme_pin_scope_markers:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_SCRIPTS_README_PIN_SCOPE_MARKERS_START')
    for marker in missing_scripts_readme_pin_scope_markers:
        print(marker)
    print('MISSING_SCRIPTS_README_PIN_SCOPE_MARKERS_END')
    sys.exit(1)

phase2_toolchain_notes = (
    ROOT / 'Documentation' / 'zigux' / 'phase2-toolchain-bootstrap-notes.md'
).read_text(encoding='utf-8')
required_phase2_toolchain_notes_markers = [
    'check-phase2-toolchain-pin-scope.py --self-test',
    'check-phase2-toolchain-pin-scope.py',
    'check-phase2-tests-readme-alignment.py --self-test',
    'check-phase2-tests-readme-alignment.py',
    'zig-toolchain-policy.json',
    'x86_64-linux',
    'install-zig.py --dest .zig-toolchain',
    'check-zig-toolchain.py',
]
missing_phase2_toolchain_notes_markers = [marker for marker in required_phase2_toolchain_notes_markers if marker not in phase2_toolchain_notes]
if missing_phase2_toolchain_notes_markers:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_PHASE2_TOOLCHAIN_NOTES_MARKERS_START')
    for marker in missing_phase2_toolchain_notes_markers:
        print(marker)
    print('MISSING_PHASE2_TOOLCHAIN_NOTES_MARKERS_END')
    sys.exit(1)

phase2_closure = (ROOT / 'Documentation' / 'zigux' / 'phase2-closure.md').read_text(encoding='utf-8')
required_phase2_closure_markers = [
    '## Toolchain Pin Scope',
    'scripts/zigux/zig-toolchain-policy.json',
    'scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test',
    'scripts/zigux/check-phase2-toolchain-pin-scope.py',
    'scripts/zigux/check-phase2-tests-readme-alignment.py --self-test',
    'scripts/zigux/check-phase2-tests-readme-alignment.py',
    'x86_64-linux',
    'PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=',
]
missing_phase2_closure_markers = [marker for marker in required_phase2_closure_markers if marker not in phase2_closure]
if missing_phase2_closure_markers:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_PHASE2_CLOSURE_PIN_SCOPE_MARKERS_START')
    for marker in missing_phase2_closure_markers:
        print(marker)
    print('MISSING_PHASE2_CLOSURE_PIN_SCOPE_MARKERS_END')
    sys.exit(1)

makefile = (ROOT / 'zigux' / 'Makefile').read_text(encoding='utf-8')
required_make_markers = [
    'phase6-validate:',
    'scripts/zigux/validate-phase6.py',
    'phase6-test:',
    'zigux/tests/phase6_build.zig',
    'phase10-validate:',
    'scripts/zigux/check-phase10-harness-coverage.py --self-test',
    'scripts/zigux/check-phase10-harness-coverage.py',
    'phase10-test:',
    'zigux/tests/phase10_build.zig',
    'phase14-validate:',
    'scripts/zigux/validate-phase14.py',
    'phase14-smoke:',
    'phase14-test:',
    'zigux/tests/phase14_build.zig',
    'phase15-validate:',
    'scripts/zigux/validate-phase15.py',
    'phase15-test:',
    'zigux/tests/phase15_build.zig',
]
missing_make_markers = [marker for marker in required_make_markers if marker not in makefile]
if missing_make_markers:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_MAKE_MARKERS_START')
    for marker in missing_make_markers:
        print(marker)
    print('MISSING_MAKE_MARKERS_END')
    sys.exit(1)

phase2_pin_scope_workflow_exact_counts = {
    'workflow:step:Install Zig': 2,
    'workflow:step:Check Zig toolchain policy': 2,
    'workflow:run:python3 scripts/zigux/install-zig.py --dest .zig-toolchain': 2,
    'workflow:run:python3 scripts/zigux/check-zig-toolchain.py': 2,
}
phase2_pin_scope_workflow_observed_counts = {
    'workflow:step:Install Zig': workflow.count('Install Zig'),
    'workflow:step:Check Zig toolchain policy': workflow.count('Check Zig toolchain policy'),
    'workflow:run:python3 scripts/zigux/install-zig.py --dest .zig-toolchain': len(
        re.findall(
            r'^\s*run:\s+python3 scripts/zigux/install-zig\.py --dest \.zig-toolchain\s*$',
            workflow,
            flags=re.MULTILINE,
        )
    ),
    'workflow:run:python3 scripts/zigux/check-zig-toolchain.py': len(
        re.findall(
            r'^\s*run:\s+python3 scripts/zigux/check-zig-toolchain\.py\s*$',
            workflow,
            flags=re.MULTILINE,
        )
    ),
}
phase2_pin_scope_workflow_count_issues = [
    f'{key}={phase2_pin_scope_workflow_observed_counts[key]},expected={expected}'
    for key, expected in phase2_pin_scope_workflow_exact_counts.items()
    if phase2_pin_scope_workflow_observed_counts[key] != expected
]
if phase2_pin_scope_workflow_count_issues:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_PHASE2_PIN_SCOPE_BOOTSTRAP_WORKFLOW_COUNTS_START')
    for issue in phase2_pin_scope_workflow_count_issues:
        print(issue)
    print('MISSING_PHASE2_PIN_SCOPE_BOOTSTRAP_WORKFLOW_COUNTS_END')
    sys.exit(1)

phase2_pin_scope_makefile_exact_counts = {
    'makefile:target:phase2-validate': 1,
    'makefile:run:scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test': 1,
    'makefile:run:scripts/zigux/check-phase2-toolchain-pin-scope.py': 1,
}
phase2_pin_scope_makefile_observed_counts = {
    'makefile:target:phase2-validate': len(
        re.findall(r'^phase2-validate:\s*$', makefile, flags=re.MULTILINE)
    ),
    'makefile:run:scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test': len(
        re.findall(
            r'^\s*cd \$\(ZIGUX_ROOT\) && \$\(PYTHON\) scripts/zigux/check-phase2-toolchain-pin-scope\.py --self-test\s*$',
            makefile,
            flags=re.MULTILINE,
        )
    ),
    'makefile:run:scripts/zigux/check-phase2-toolchain-pin-scope.py': len(
        re.findall(
            r'^\s*cd \$\(ZIGUX_ROOT\) && \$\(PYTHON\) scripts/zigux/check-phase2-toolchain-pin-scope\.py\s*$',
            makefile,
            flags=re.MULTILINE,
        )
    ),
}
phase2_pin_scope_makefile_count_issues = [
    f'{key}={phase2_pin_scope_makefile_observed_counts[key]},expected={expected}'
    for key, expected in phase2_pin_scope_makefile_exact_counts.items()
    if phase2_pin_scope_makefile_observed_counts[key] != expected
]
if phase2_pin_scope_makefile_count_issues:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_PHASE2_PIN_SCOPE_BOOTSTRAP_MAKEFILE_COUNTS_START')
    for issue in phase2_pin_scope_makefile_count_issues:
        print(issue)
    print('MISSING_PHASE2_PIN_SCOPE_BOOTSTRAP_MAKEFILE_COUNTS_END')
    sys.exit(1)

phase2_tests_readme_workflow_exact_counts = {
    'workflow:step:Self-test Phase 2 tests README alignment checker': 1,
    'workflow:step:Check Phase 2 tests README alignment': 1,
    'workflow:run:python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test': 1,
    'workflow:run:python3 scripts/zigux/check-phase2-tests-readme-alignment.py': 1,
}
phase2_tests_readme_workflow_observed_counts = {
    'workflow:step:Self-test Phase 2 tests README alignment checker': workflow.count(
        'Self-test Phase 2 tests README alignment checker'
    ),
    'workflow:step:Check Phase 2 tests README alignment': workflow.count(
        'Check Phase 2 tests README alignment'
    ),
    'workflow:run:python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test': len(
        re.findall(
            r'^\s*run:\s+python3 scripts/zigux/check-phase2-tests-readme-alignment\.py --self-test\s*$',
            workflow,
            flags=re.MULTILINE,
        )
    ),
    'workflow:run:python3 scripts/zigux/check-phase2-tests-readme-alignment.py': len(
        re.findall(
            r'^\s*run:\s+python3 scripts/zigux/check-phase2-tests-readme-alignment\.py\s*$',
            workflow,
            flags=re.MULTILINE,
        )
    ),
}
phase2_tests_readme_workflow_count_issues = [
    f'{key}={phase2_tests_readme_workflow_observed_counts[key]},expected={expected}'
    for key, expected in phase2_tests_readme_workflow_exact_counts.items()
    if phase2_tests_readme_workflow_observed_counts[key] != expected
]
if phase2_tests_readme_workflow_count_issues:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_PHASE2_TESTS_README_BOOTSTRAP_WORKFLOW_COUNTS_START')
    for issue in phase2_tests_readme_workflow_count_issues:
        print(issue)
    print('MISSING_PHASE2_TESTS_README_BOOTSTRAP_WORKFLOW_COUNTS_END')
    sys.exit(1)

phase2_tests_readme_makefile_exact_counts = {
    'makefile:run:scripts/zigux/check-phase2-tests-readme-alignment.py --self-test': 1,
    'makefile:run:scripts/zigux/check-phase2-tests-readme-alignment.py': 1,
}
phase2_tests_readme_makefile_observed_counts = {
    'makefile:run:scripts/zigux/check-phase2-tests-readme-alignment.py --self-test': len(
        re.findall(
            r'^\s*cd \$\(ZIGUX_ROOT\) && \$\(PYTHON\) scripts/zigux/check-phase2-tests-readme-alignment\.py --self-test\s*$',
            makefile,
            flags=re.MULTILINE,
        )
    ),
    'makefile:run:scripts/zigux/check-phase2-tests-readme-alignment.py': len(
        re.findall(
            r'^\s*cd \$\(ZIGUX_ROOT\) && \$\(PYTHON\) scripts/zigux/check-phase2-tests-readme-alignment\.py\s*$',
            makefile,
            flags=re.MULTILINE,
        )
    ),
}
phase2_tests_readme_makefile_count_issues = [
    f'{key}={phase2_tests_readme_makefile_observed_counts[key]},expected={expected}'
    for key, expected in phase2_tests_readme_makefile_exact_counts.items()
    if phase2_tests_readme_makefile_observed_counts[key] != expected
]
if phase2_tests_readme_makefile_count_issues:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_PHASE2_TESTS_README_BOOTSTRAP_MAKEFILE_COUNTS_START')
    for issue in phase2_tests_readme_makefile_count_issues:
        print(issue)
    print('MISSING_PHASE2_TESTS_README_BOOTSTRAP_MAKEFILE_COUNTS_END')
    sys.exit(1)

phase2_shared_validation_workflow_exact_counts = {
    'workflow:step:Validate Phase 2 fixdep files': 1,
    'workflow:step:Validate Phase 2 closure': 1,
    'workflow:run:python3 scripts/zigux/validate-phase2.py': 1,
    'workflow:run:python3 scripts/zigux/validate-phase2-closure.py': 1,
}
phase2_shared_validation_workflow_observed_counts = {
    'workflow:step:Validate Phase 2 fixdep files': workflow.count('Validate Phase 2 fixdep files'),
    'workflow:step:Validate Phase 2 closure': workflow.count('Validate Phase 2 closure'),
    'workflow:run:python3 scripts/zigux/validate-phase2.py': len(
        re.findall(
            r'^\s*run:\s+python3 scripts/zigux/validate-phase2\.py\s*$',
            workflow,
            flags=re.MULTILINE,
        )
    ),
    'workflow:run:python3 scripts/zigux/validate-phase2-closure.py': len(
        re.findall(
            r'^\s*run:\s+python3 scripts/zigux/validate-phase2-closure\.py\s*$',
            workflow,
            flags=re.MULTILINE,
        )
    ),
}
phase2_shared_validation_workflow_count_issues = [
    f'{key}={phase2_shared_validation_workflow_observed_counts[key]},expected={expected}'
    for key, expected in phase2_shared_validation_workflow_exact_counts.items()
    if phase2_shared_validation_workflow_observed_counts[key] != expected
]
if phase2_shared_validation_workflow_count_issues:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_PHASE2_SHARED_VALIDATION_BOOTSTRAP_WORKFLOW_COUNTS_START')
    for issue in phase2_shared_validation_workflow_count_issues:
        print(issue)
    print('MISSING_PHASE2_SHARED_VALIDATION_BOOTSTRAP_WORKFLOW_COUNTS_END')
    sys.exit(1)

phase2_shared_validation_makefile_exact_counts = {
    'makefile:run:scripts/zigux/validate-phase2.py': 1,
    'makefile:run:scripts/zigux/validate-phase2-closure.py': 1,
}
phase2_shared_validation_makefile_observed_counts = {
    'makefile:run:scripts/zigux/validate-phase2.py': len(
        re.findall(
            r'^\s*cd \$\(ZIGUX_ROOT\) && \$\(PYTHON\) scripts/zigux/validate-phase2\.py\s*$',
            makefile,
            flags=re.MULTILINE,
        )
    ),
    'makefile:run:scripts/zigux/validate-phase2-closure.py': len(
        re.findall(
            r'^\s*cd \$\(ZIGUX_ROOT\) && \$\(PYTHON\) scripts/zigux/validate-phase2-closure\.py\s*$',
            makefile,
            flags=re.MULTILINE,
        )
    ),
}
phase2_shared_validation_makefile_count_issues = [
    f'{key}={phase2_shared_validation_makefile_observed_counts[key]},expected={expected}'
    for key, expected in phase2_shared_validation_makefile_exact_counts.items()
    if phase2_shared_validation_makefile_observed_counts[key] != expected
]
if phase2_shared_validation_makefile_count_issues:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_PHASE2_SHARED_VALIDATION_BOOTSTRAP_MAKEFILE_COUNTS_START')
    for issue in phase2_shared_validation_makefile_count_issues:
        print(issue)
    print('MISSING_PHASE2_SHARED_VALIDATION_BOOTSTRAP_MAKEFILE_COUNTS_END')
    sys.exit(1)

phase10_harness_makefile_exact_counts = {
    'makefile:target:phase10-validate': 1,
    'makefile:run:scripts/zigux/check-phase10-harness-coverage.py --self-test': 1,
    'makefile:run:scripts/zigux/check-phase10-harness-coverage.py': 1,
}
phase10_harness_makefile_observed_counts = {
    'makefile:target:phase10-validate': len(
        re.findall(r'^phase10-validate:\s*$', makefile, flags=re.MULTILINE)
    ),
    'makefile:run:scripts/zigux/check-phase10-harness-coverage.py --self-test': len(
        re.findall(
            r'^\s*cd \$\(ZIGUX_ROOT\) && \$\(PYTHON\) scripts/zigux/check-phase10-harness-coverage\.py --self-test\s*$',
            makefile,
            flags=re.MULTILINE,
        )
    ),
    'makefile:run:scripts/zigux/check-phase10-harness-coverage.py': len(
        re.findall(
            r'^\s*cd \$\(ZIGUX_ROOT\) && \$\(PYTHON\) scripts/zigux/check-phase10-harness-coverage\.py\s*$',
            makefile,
            flags=re.MULTILINE,
        )
    ),
}
phase10_harness_makefile_count_issues = [
    f'{key}={phase10_harness_makefile_observed_counts[key]},expected={expected}'
    for key, expected in phase10_harness_makefile_exact_counts.items()
    if phase10_harness_makefile_observed_counts[key] != expected
]
if phase10_harness_makefile_count_issues:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_PHASE10_HARNESS_BOOTSTRAP_MAKEFILE_COUNTS_START')
    for issue in phase10_harness_makefile_count_issues:
        print(issue)
    print('MISSING_PHASE10_HARNESS_BOOTSTRAP_MAKEFILE_COUNTS_END')
    sys.exit(1)

print('BOOTSTRAP_VALIDATION=pass')
print(f'BOOTSTRAP_REQUIRED_FILE_COUNT={len(required_files)}')
print(
    'BOOTSTRAP_REQUIRED_MARKER_COUNT='
    f"{len(required_markers) + len(required_workflow_markers) + len(required_toolchain_markers) + len(required_installer_markers) + len(required_phase2_validator_markers) + len(required_phase2_pin_scope_checker_markers) + len(required_scripts_readme_pin_scope_markers) + len(required_phase2_toolchain_notes_markers) + len(required_phase2_closure_markers) + len(required_make_markers)}"
)

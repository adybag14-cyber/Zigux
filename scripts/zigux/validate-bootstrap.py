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
    ROOT / 'scripts' / 'zigux' / 'README.md',
    ROOT / 'scripts' / 'zigux' / 'check-zig-toolchain.py',
    ROOT / 'scripts' / 'zigux' / 'install-zig.py',
    ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json',
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
    'Run Phase 10 virtio helper tests',
    'zigux/tests/phase10_build.zig',
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
phase11_validate_command = 'make -C zigux phase11-validate'
phase11_validate_step = 'Validate Phase 11 simple-driver bundle'
phase11_hvc_survey_command = 'make -C zigux phase11-hvc-survey'
phase11_hvc_survey_step = 'Run dedicated Phase 11 hvc survey replay'
workflow_phase11_validator_self_test_command_count = len(
    re.findall(r'^\s*run:\s+python3 scripts/zigux/validate-phase11\.py --self-test\s*$', workflow, flags=re.MULTILINE)
)
workflow_phase11_validator_self_test_step_count = workflow.count(phase11_validator_self_test_step)
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
    print(f'workflow:phase11_validate_command_count={workflow_phase11_validate_command_count},expected=1')
    print(f'workflow:phase11_validate_step_count={workflow_phase11_validate_step_count},expected=1')
    print(f'workflow:phase11_hvc_survey_command_count={workflow_phase11_hvc_survey_command_count},expected=1')
    print(f'workflow:phase11_hvc_survey_step_count={workflow_phase11_hvc_survey_step_count},expected=1')
    print('MISSING_WORKFLOW_PHASE11_WIRING_END')
    sys.exit(1)

toolchain_policy = json.loads((ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json').read_text(encoding='utf-8'))
required_policy_values = {
    'phase': 'Phase 2',
    'policy_note': 'Shared Zigux bootstrap and Phase 2 toolchain pin.',
    'archive_sha256': {
        'x86_64-linux': '313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77',
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

makefile = (ROOT / 'zigux' / 'Makefile').read_text(encoding='utf-8')
required_make_markers = [
    'phase6-validate:',
    'scripts/zigux/validate-phase6.py',
    'phase6-test:',
    'zigux/tests/phase6_build.zig',
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

print('BOOTSTRAP_VALIDATION=pass')
print(f'BOOTSTRAP_REQUIRED_FILE_COUNT={len(required_files)}')
print(
    'BOOTSTRAP_REQUIRED_MARKER_COUNT='
    f"{len(required_markers) + len(required_workflow_markers) + len(required_toolchain_markers) + len(required_installer_markers) + len(required_make_markers)}"
)
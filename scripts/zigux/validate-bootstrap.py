#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_EXACT_RUN_COUNTS = {
    'python3 scripts/zigux/check-zig-toolchain.py --self-test': 1,
    'python3 scripts/zigux/check-zig-toolchain.py': 1,
    'python3 scripts/zigux/validate-phase1.py': 1,
    'python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test': 1,
    'python3 scripts/zigux/check-phase1-installer-review-surfaces.py': 1,
    'python3 scripts/zigux/validate-phase1-closure.py': 1,
    'python3 scripts/zigux/validate-phase2.py': 1,
    'python3 scripts/zigux/validate-phase2-closure.py': 1,
    'python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test': 1,
    'python3 scripts/zigux/check-phase2-toolchain-pin-scope.py': 1,
    'python3 scripts/zigux/check-phase6-shared-surface.py --self-test': 1,
    'python3 scripts/zigux/check-phase6-shared-surface.py': 1,
    'zig build test --build-file zigux/tests/phase6_build.zig --summary all': 1,
    'zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all': 1,
    'zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all': 1,
    'zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all': 1,
    'python3 scripts/zigux/check-phase9-build-only-surface.py --self-test': 1,
    'python3 scripts/zigux/check-phase9-build-only-surface.py': 1,
    'make -C zigux phase14-validate': 1,
    'make -C zigux phase14-smoke': 1,
    'make -C zigux phase14-test': 1,
    'make -C zigux phase15-validate': 1,
    'make -C zigux phase15-test': 1,
}
required_files = [
    ROOT / 'zigux-alpha' / 'README.md',
    ROOT / 'zigux-alpha' / 'ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md',
    ROOT / 'Documentation' / 'zigux' / 'README.md',
    ROOT / 'Documentation' / 'zigux' / 'review-checklist.md',
    ROOT / 'Documentation' / 'zigux' / 'freeze-map.md',
    ROOT / 'Documentation' / 'zigux' / 'phase2-toolchain-bootstrap-notes.md',
    ROOT / 'scripts' / 'zigux' / 'README.md',
    ROOT / 'scripts' / 'zigux' / 'check-zig-toolchain.py',
    ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json',
    ROOT / 'scripts' / 'zigux' / 'check-phase2-toolchain-pin-scope.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase1.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase1-installer-review-surfaces.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase1-closure.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase2.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase2-closure.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase6-shared-surface.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase9-build-only-surface.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase14.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase14-docs-root-smoke-summary.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase14-rollback-threshold-sequencing.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase14-release-boundary-exact-counts.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase15.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase15-scripts-readme-alignment.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase15-review-process-handoff.py',
    ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml',
    ROOT / 'zigux' / 'Makefile',
    ROOT / 'zigux' / 'tests' / 'README.md',
    ROOT / 'zigux' / 'tests' / 'phase6_build.zig',
    ROOT / 'zigux' / 'tests' / 'phase9_build.zig',
    ROOT / 'zigux' / 'tests' / 'phase14_build.zig',
    ROOT / 'zigux' / 'tests' / 'phase15_build.zig',
    ROOT / 'zigux' / 'tests' / 'runtime_loader_allocator_init_flow.zig',
]


def count_step_command_matches(workflow_text: str, step_name: str, command: str) -> int:
    step_blocks = workflow_text.split('\n      - name: ')
    matches = 0
    command_path = command.split(' ', 1)[1]
    command_leaf = command_path.rsplit('/', 1)[-1]
    for block in step_blocks[1:]:
        lines = block.splitlines()
        if not lines:
            continue
        if lines[0].strip() != step_name:
            continue
        step_text = '\n'.join(lines[1:])
        direct_line = f'run: {command}'
        if (
            direct_line in step_text
            or command in step_text
            or f'run_path("{command_path}"' in step_text
            or f"run_path('{command_path}'" in step_text
            or command_leaf in step_text
        ):
            matches += 1
    return matches


def validate_exact_workflow_runs(text: str) -> list[str]:
    issues = []
    lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in WORKFLOW_EXACT_RUN_COUNTS.items():
        expected_line = f'run: {command}'
        count = sum(1 for line in lines if line == expected_line)
        if count == 0 and command == 'python3 scripts/zigux/validate-phase1-closure.py':
            count = count_step_command_matches(text, 'Validate Phase 1 closure', command)
        if count != expected_count:
            issues.append(
                f'workflow_exact_run:{command}:count={count}:expected={expected_count}'
            )
    return issues


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
    'Validate Phase 1 helper files',
    'python3 scripts/zigux/validate-phase1.py',
    'Self-test Phase 1 installer-review surfaces',
    'python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test',
    'Check Phase 1 installer-review surfaces',
    'python3 scripts/zigux/check-phase1-installer-review-surfaces.py',
    'Validate Phase 1 closure',
    'Validate Phase 2 fixdep files',
    'python3 scripts/zigux/validate-phase2.py',
    'Validate Phase 2 closure',
    'python3 scripts/zigux/validate-phase2-closure.py',
    'Self-test Phase 2 toolchain pin scope',
    'python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test',
    'Check Phase 2 toolchain pin scope',
    'python3 scripts/zigux/check-phase2-toolchain-pin-scope.py',
    'Self-test Phase 6 shared-surface checker',
    'python3 scripts/zigux/check-phase6-shared-surface.py --self-test',
    'Check Phase 6 shared surface',
    'python3 scripts/zigux/check-phase6-shared-surface.py',
    'Run Phase 6 leaf helper tests',
    'zigux/tests/phase6_build.zig',
    'Self-test Phase 9 build-only surface checker',
    'python3 scripts/zigux/check-phase9-build-only-surface.py --self-test',
    'Check Phase 9 build-only surface',
    'python3 scripts/zigux/check-phase9-build-only-surface.py',
    'Run Phase 7 runtime helper tests',
    'Run Phase 8 tooling tests',
    'make -C zigux phase8-test',
    'Run Phase 9 runtime helper tests',
    'make -C zigux phase9',
    'Run Phase 10 checker-backed virtio helper tests',
    'make -C zigux phase10-test',
    'Run Phase 11 watchdog and console tests',
    'zigux/tests/phase11_build.zig',
    'zigux/tests/phase12_build.zig',
    'Run Phase 13 shared helper tests',
    'make -C zigux phase13-test',
    'Validate Phase 14 shared smoke packet',
    'Run focused Phase 14 smoke shard',
    'Run Phase 14 internal bridge tests',
    'Validate Phase 15 governance packet',
    'Run Phase 15 governance tests',
]
required_workflow_marker_aliases = [
    (
        'Run Phase 12 complex driver tests',
        'Run Phase 12 complex driver and libbpf tests',
    ),
    (
        'make -C zigux phase7-test',
        'zig build test --build-file zigux/tests/phase7_build.zig --summary all',
    ),
]
missing_workflow_markers = [marker for marker in required_workflow_markers if marker not in workflow]
for alias_group in required_workflow_marker_aliases:
    if not any(marker in workflow for marker in alias_group):
        missing_workflow_markers.append(
            'workflow_any_of:' + '||'.join(alias_group)
        )
missing_workflow_markers.extend(validate_exact_workflow_runs(workflow))
if missing_workflow_markers:
    print('BOOTSTRAP_VALIDATION=fail')
    print('MISSING_WORKFLOW_MARKERS_START')
    for marker in missing_workflow_markers:
        print(marker)
    print('MISSING_WORKFLOW_MARKERS_END')
    sys.exit(1)

print('BOOTSTRAP_VALIDATION=pass')
print(f'BOOTSTRAP_REQUIRED_FILE_COUNT={len(required_files)}')
print(
    'BOOTSTRAP_REQUIRED_MARKER_COUNT='
    f'{len(required_markers) + len(required_workflow_markers) + len(required_workflow_marker_aliases) + len(WORKFLOW_EXACT_RUN_COUNTS)}'
)

#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_EXACT_RUN_COUNTS = {
    'python3 scripts/zigux/check-zig-toolchain.py --self-test': 1,
    'python3 scripts/zigux/check-zig-toolchain.py': 1,
    'python3 scripts/zigux/check-phase9-build-only-surface.py --self-test': 1,
    'python3 scripts/zigux/check-phase9-build-only-surface.py': 1,
}
required_files = [
    ROOT / 'zigux-alpha' / 'README.md',
    ROOT / 'zigux-alpha' / 'ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md',
    ROOT / 'Documentation' / 'zigux' / 'README.md',
    ROOT / 'Documentation' / 'zigux' / 'review-checklist.md',
    ROOT / 'Documentation' / 'zigux' / 'freeze-map.md',
    ROOT / 'scripts' / 'zigux' / 'README.md',
    ROOT / 'scripts' / 'zigux' / 'check-zig-toolchain.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase6-shared-surface.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase9-build-only-surface.py',
    ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml',
    ROOT / 'zigux' / 'Makefile',
    ROOT / 'zigux' / 'tests' / 'README.md',
    ROOT / 'zigux' / 'tests' / 'phase6_build.zig',
    ROOT / 'zigux' / 'tests' / 'phase9_build.zig',
    ROOT / 'zigux' / 'tests' / 'runtime_loader_allocator_init_flow.zig',
]


def validate_exact_workflow_runs(text: str) -> list[str]:
    issues = []
    lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in WORKFLOW_EXACT_RUN_COUNTS.items():
        expected_line = f'run: {command}'
        count = sum(1 for line in lines if line == expected_line)
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
    'zigux/tests/phase7_build.zig',
    'Run Phase 8 tooling tests',
    'zigux/tests/phase8_build.zig',
    'Run Phase 9 runtime helper tests',
    'make -C zigux phase9',
    'Run Phase 10 virtio helper tests',
    'zigux/tests/phase10_build.zig',
    'Run Phase 11 watchdog and console tests',
    'zigux/tests/phase11_build.zig',
    'Run Phase 12 complex driver tests',
    'zigux/tests/phase12_build.zig',
    'Run Phase 13 shared helper tests',
    'make -C zigux phase13-test',
]
missing_workflow_markers = [marker for marker in required_workflow_markers if marker not in workflow]
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
    f'{len(required_markers) + len(required_workflow_markers) + len(WORKFLOW_EXACT_RUN_COUNTS)}'
)

#!/usr/bin/env python3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / 'scripts' / 'zigux' / 'validate-phase4.py',
    ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md',
    ROOT / 'Documentation' / 'zigux' / 'phase4-validation-matrix.md',
    ROOT / 'zigux' / 'Makefile',
    ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml',
    ROOT / 'zigux' / 'tests' / 'runtime_atomic64_diff.zig',
    ROOT / 'zigux' / 'tests' / 'bitmap_diff.zig',
    ROOT / 'zigux' / 'tests' / 'phase4_build.zig',
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print('PHASE4_VALIDATION=fail')
    print('MISSING_PHASE4_FILES_START')
    for item in missing:
        print(item)
    print('MISSING_PHASE4_FILES_END')
    sys.exit(1)

makefile = (ROOT / 'zigux' / 'Makefile').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
artifact_doc = (ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md').read_text(encoding='utf-8')
tests_readme = (ROOT / 'zigux' / 'tests' / 'README.md').read_text(encoding='utf-8')
script_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')
doc_readme = (ROOT / 'Documentation' / 'zigux' / 'README.md').read_text(encoding='utf-8')
phase4_matrix = (ROOT / 'Documentation' / 'zigux' / 'phase4-validation-matrix.md').read_text(encoding='utf-8')
phase4_build = (ROOT / 'zigux' / 'tests' / 'phase4_build.zig').read_text(encoding='utf-8')

phase4_gate_expectations = {
    'runtime_atomic64_diff.zig': {
        'owner': 'ABI and Runtime Team',
        'rollback_owner': 'ABI and Runtime Team',
        'threshold_posture': 'threshold_pending_until_runtime_atomic64_scope_widens',
    },
    'bitmap_diff.zig': {
        'owner': 'Shared Subsystems Pod',
        'rollback_owner': 'Shared Subsystems Pod',
        'threshold_posture': 'threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks',
    },
}

required_make_markers = [
    'PHONY += phase4-validate phase4-test phase4',
    'phase4-validate:',
    'scripts/zigux/validate-phase4.py',
    'phase4-test:',
    'zigux/tests/phase4_build.zig',
]
required_workflow_markers = [
    'python3 scripts/zigux/validate-phase4.py',
    'zig build test --build-file zigux/tests/phase4_build.zig',
]
required_doc_markers = [
    'Current Phase 4 use',
    'zigux/tests/runtime_atomic64_diff.zig',
    'zigux/tests/bitmap_diff.zig',
    'zigux/tests/phase4_build.zig',
    'scripts/zigux/validate-phase4.py',
    'Documentation/zigux/phase4-validation-matrix.md',
]
required_tests_readme_markers = [
    'zigux/tests/runtime_atomic64_diff.zig',
    'zigux/tests/bitmap_diff.zig',
    'zigux/tests/phase4_build.zig',
    'scripts/zigux/validate-phase4.py',
]
required_script_readme_markers = [
    'validate-phase4.py',
    'Phase 4 flow',
    'phase4_build.zig',
    'phase4-validation-matrix.md',
]
required_doc_readme_markers = [
    'Phase 4 notes',
    'validate-phase4.py',
    'phase4-validation-matrix.md',
]
required_phase4_matrix_markers = [
    'runtime_atomic64_diff.zig',
    'bitmap_diff.zig',
    'rollback owner',
    'lab and CI matrix',
    'perf threshold status',
    'zig build test --build-file zigux/tests/phase4_build.zig',
]
required_phase4_build_markers = [
    'runtime_atomic64_diff.zig',
    'bitmap_diff.zig',
    'phase4-runtime-atomic64-diff-tests',
    'phase4-bitmap-diff-tests',
]

missing_markers = []
for marker in required_make_markers:
    if marker not in makefile:
        missing_markers.append(f'make:{marker}')
for marker in required_workflow_markers:
    if marker not in workflow:
        missing_markers.append(f'workflow:{marker}')
for marker in required_doc_markers:
    if marker not in artifact_doc:
        missing_markers.append(f'doc:{marker}')
for marker in required_tests_readme_markers:
    if marker not in tests_readme:
        missing_markers.append(f'tests_readme:{marker}')
for marker in required_script_readme_markers:
    if marker not in script_readme:
        missing_markers.append(f'script_readme:{marker}')
for marker in required_doc_readme_markers:
    if marker not in doc_readme:
        missing_markers.append(f'doc_readme:{marker}')
for marker in required_phase4_matrix_markers:
    if marker not in phase4_matrix:
        missing_markers.append(f'phase4_matrix:{marker}')
for marker in required_phase4_build_markers:
    if marker not in phase4_build:
        missing_markers.append(f'phase4_build:{marker}')


def check_gate_matrix_alignment(gate_name: str, expectation: dict[str, str]) -> list[str]:
    gate_heading = f"### `zigux/tests/{gate_name}`"
    gate_heading_index = phase4_matrix.find(gate_heading)
    if gate_heading_index == -1:
        return [f'phase4_matrix:missing_gate_heading:{gate_name}']

    next_heading_index = phase4_matrix.find('\n### `zigux/tests/', gate_heading_index + len(gate_heading))
    matrix_heading_index = phase4_matrix.find('\n## Lab And CI Matrix', gate_heading_index + len(gate_heading))
    gate_block_end = matrix_heading_index
    if next_heading_index != -1 and next_heading_index < matrix_heading_index:
        gate_block_end = next_heading_index
    gate_block = phase4_matrix[gate_heading_index:gate_block_end]

    row_prefix = f"| `zigux/tests/{gate_name}` |"
    row = next(
        (line for line in phase4_matrix.splitlines() if line.startswith(row_prefix)),
        '',
    )

    missing = []
    if f"- owner: `{expectation['owner']}`" not in gate_block:
        missing.append(f"phase4_matrix:owner:{gate_name}:{expectation['owner']}")
    if f"- rollback owner: `{expectation['rollback_owner']}`" not in gate_block:
        missing.append(
            f"phase4_matrix:rollback_owner:{gate_name}:{expectation['rollback_owner']}"
        )
    if expectation['threshold_posture'] not in row:
        missing.append(
            f"phase4_matrix:threshold_posture:{gate_name}:{expectation['threshold_posture']}"
        )
    if expectation['owner'] not in row:
        missing.append(f"phase4_matrix:matrix_owner:{gate_name}:{expectation['owner']}")
    if expectation['rollback_owner'] not in row:
        missing.append(
            f"phase4_matrix:matrix_rollback_owner:{gate_name}:{expectation['rollback_owner']}"
        )
    return missing


for gate_name, expectation in phase4_gate_expectations.items():
    missing_markers.extend(check_gate_matrix_alignment(gate_name, expectation))

if missing_markers:
    print('PHASE4_VALIDATION=fail')
    print('MISSING_PHASE4_MARKERS_START')
    for marker in missing_markers:
        print(marker)
    print('MISSING_PHASE4_MARKERS_END')
    sys.exit(1)

print('PHASE4_VALIDATION=pass')
print(f'PHASE4_REQUIRED_FILE_COUNT={len(required_files)}')
print(
    'PHASE4_REQUIRED_MARKER_COUNT='
    f"{len(required_make_markers) + len(required_workflow_markers) + len(required_doc_markers) + len(required_tests_readme_markers) + len(required_script_readme_markers) + len(required_doc_readme_markers) + len(required_phase4_matrix_markers) + len(required_phase4_build_markers)}"
)

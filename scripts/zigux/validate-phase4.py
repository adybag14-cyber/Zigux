#!/usr/bin/env python3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / 'scripts' / 'zigux' / 'validate-phase4.py',
    ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md',
    ROOT / 'zigux' / 'Makefile',
    ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml',
    ROOT / 'zigux' / 'tests' / 'atomic64_diff.zig',
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
phase4_build = (ROOT / 'zigux' / 'tests' / 'phase4_build.zig').read_text(encoding='utf-8')

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
    'zigux/tests/atomic64_diff.zig',
    'zigux/tests/bitmap_diff.zig',
    'zigux/tests/phase4_build.zig',
    'scripts/zigux/validate-phase4.py',
]
required_tests_readme_markers = [
    'zigux/tests/atomic64_diff.zig',
    'zigux/tests/bitmap_diff.zig',
    'zigux/tests/phase4_build.zig',
    'scripts/zigux/validate-phase4.py',
]
required_script_readme_markers = [
    'validate-phase4.py',
    'Phase 4 flow',
    'phase4_build.zig',
]
required_doc_readme_markers = [
    'Phase 4 notes',
    'validate-phase4.py',
]
required_phase4_build_markers = [
    'atomic64_diff.zig',
    'bitmap_diff.zig',
    'phase4-atomic64-diff-tests',
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
for marker in required_phase4_build_markers:
    if marker not in phase4_build:
        missing_markers.append(f'phase4_build:{marker}')

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
    f"{len(required_make_markers) + len(required_workflow_markers) + len(required_doc_markers) + len(required_tests_readme_markers) + len(required_script_readme_markers) + len(required_doc_readme_markers) + len(required_phase4_build_markers)}"
)

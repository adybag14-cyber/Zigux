#!/usr/bin/env python3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / 'scripts' / 'zigux' / 'validate-phase6.py',
    ROOT / 'scripts' / 'zigux' / 'README.md',
    ROOT / 'Documentation' / 'zigux' / 'README.md',
    ROOT / 'Documentation' / 'zigux' / 'phase6-base64-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase6-bsearch-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase6-checksum-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase6-hexdump-slice.md',
    ROOT / 'zigux' / 'Makefile',
    ROOT / 'zigux' / 'tests' / 'README.md',
    ROOT / 'zigux' / 'tests' / 'phase6_base64.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_bsearch.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_checksum.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_hexdump.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_build.zig',
    ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml',
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print('PHASE6_VALIDATION=fail')
    print('MISSING_PHASE6_FILES_START')
    for item in missing:
        print(item)
    print('MISSING_PHASE6_FILES_END')
    sys.exit(1)

makefile = (ROOT / 'zigux' / 'Makefile').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
script_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')
tests_readme = (ROOT / 'zigux' / 'tests' / 'README.md').read_text(encoding='utf-8')
doc_readme = (ROOT / 'Documentation' / 'zigux' / 'README.md').read_text(encoding='utf-8')
phase6_build = (ROOT / 'zigux' / 'tests' / 'phase6_build.zig').read_text(encoding='utf-8')
phase6_hexdump = (ROOT / 'zigux' / 'tests' / 'phase6_hexdump.zig').read_text(encoding='utf-8')

slice_docs = {
    'phase6-base64-slice.md': (ROOT / 'Documentation' / 'zigux' / 'phase6-base64-slice.md').read_text(encoding='utf-8'),
    'phase6-bsearch-slice.md': (ROOT / 'Documentation' / 'zigux' / 'phase6-bsearch-slice.md').read_text(encoding='utf-8'),
    'phase6-checksum-slice.md': (ROOT / 'Documentation' / 'zigux' / 'phase6-checksum-slice.md').read_text(encoding='utf-8'),
    'phase6-hexdump-slice.md': (ROOT / 'Documentation' / 'zigux' / 'phase6-hexdump-slice.md').read_text(encoding='utf-8'),
}

required_make_markers = [
    'PHONY += phase6-validate phase6-test phase6',
    'phase6-validate:',
    'scripts/zigux/validate-phase6.py',
    'phase6-test:',
    'zigux/tests/phase6_build.zig',
]

required_workflow_markers = [
    'Validate Phase 6 leaf helper gates',
    'make -C zigux phase6-validate',
    'Run Phase 6 leaf helper tests',
    'zigux/tests/phase6_build.zig',
]

required_script_readme_markers = [
    'validate-phase6.py',
    'Phase 6 flow',
    'make -C zigux phase6-validate',
    'phase6_build.zig',
    'phase6-hexdump-slice.md',
]

required_tests_readme_markers = [
    'zigux/tests/phase6_build.zig',
    'zigux/tests/phase6_base64.zig',
    'zigux/tests/phase6_bsearch.zig',
    'zigux/tests/phase6_checksum.zig',
    'zigux/tests/phase6_hexdump.zig',
    'scripts/zigux/validate-phase6.py',
]

required_doc_readme_markers = [
    'Phase 6 notes',
    'Documentation/zigux/phase6-base64-slice.md',
    'Documentation/zigux/phase6-bsearch-slice.md',
    'Documentation/zigux/phase6-checksum-slice.md',
    'Documentation/zigux/phase6-hexdump-slice.md',
    'zigux/tests/phase6_build.zig',
    'make -C zigux phase6',
    'make -C zigux phase6-validate',
    'python3 scripts/zigux/validate-phase6.py',
]

required_phase6_build_markers = [
    '../../lib/base64.zig',
    '../../lib/bsearch.zig',
    '../../lib/checksum.zig',
    '../../lib/hexdump.zig',
    'phase6_base64.zig',
    'phase6_bsearch.zig',
    'phase6_checksum.zig',
    'phase6_hexdump.zig',
    'Run Phase 6 leaf helper tests',
]

required_hexdump_markers = [
    'phase 6 hexdump overflow contract matches truncation expectations',
    'phase 6 hexdump covers normalization and empty-buffer edge cases',
]

required_slice_markers = {
    'phase6-base64-slice.md': [
        'PHASE6_STATUS=active',
        'lib/base64.zig',
        'zigux/tests/phase6_build.zig',
    ],
    'phase6-bsearch-slice.md': [
        'PHASE6_STATUS=active',
        'lib/bsearch.zig',
        'zigux/tests/phase6_build.zig',
    ],
    'phase6-checksum-slice.md': [
        'PHASE6_STATUS=active',
        'lib/checksum.zig',
        'zigux/tests/phase6_build.zig',
    ],
    'phase6-hexdump-slice.md': [
        'PHASE6_STATUS=active',
        'lib/hexdump.zig',
        'zigux/tests/phase6_build.zig',
        'truncation behavior while still reporting the full required line length',
        'empty-buffer required-length behavior',
    ],
}

missing_markers = []

for marker in required_make_markers:
    if marker not in makefile:
        missing_markers.append(f'make:{marker}')
for marker in required_workflow_markers:
    if marker not in workflow:
        missing_markers.append(f'workflow:{marker}')
for marker in required_script_readme_markers:
    if marker not in script_readme:
        missing_markers.append(f'script_readme:{marker}')
for marker in required_tests_readme_markers:
    if marker not in tests_readme:
        missing_markers.append(f'tests_readme:{marker}')
for marker in required_doc_readme_markers:
    if marker not in doc_readme:
        missing_markers.append(f'doc_readme:{marker}')
for marker in required_phase6_build_markers:
    if marker not in phase6_build:
        missing_markers.append(f'phase6_build:{marker}')
for marker in required_hexdump_markers:
    if marker not in phase6_hexdump:
        missing_markers.append(f'phase6_hexdump:{marker}')
for doc_name, markers in required_slice_markers.items():
    doc_text = slice_docs[doc_name]
    for marker in markers:
        if marker not in doc_text:
            missing_markers.append(f'{doc_name}:{marker}')

if missing_markers:
    print('PHASE6_VALIDATION=fail')
    print('MISSING_PHASE6_MARKERS_START')
    for marker in missing_markers:
        print(marker)
    print('MISSING_PHASE6_MARKERS_END')
    sys.exit(1)

print('PHASE6_VALIDATION=pass')
print(f'PHASE6_REQUIRED_FILE_COUNT={len(required_files)}')
print(
    'PHASE6_REQUIRED_MARKER_COUNT='
    f"{len(required_make_markers) + len(required_workflow_markers) + len(required_script_readme_markers) + len(required_tests_readme_markers) + len(required_doc_readme_markers) + len(required_phase6_build_markers) + len(required_hexdump_markers) + sum(len(markers) for markers in required_slice_markers.values())}"
)

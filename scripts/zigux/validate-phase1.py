#!/usr/bin/env python3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / 'tools' / 'lib' / 'bitmap.zig',
    ROOT / 'tools' / 'lib' / 'find_bit.zig',
    ROOT / 'tools' / 'lib' / 'string.zig',
    ROOT / 'tools' / 'lib' / 'rbtree.zig',
    ROOT / 'tools' / 'lib' / 'argv_split.zig',
    ROOT / 'tools' / 'lib' / 'cmdline.zig',
    ROOT / 'tools' / 'lib' / 'ctype.zig',
    ROOT / 'tools' / 'lib' / 'hweight.zig',
    ROOT / 'tools' / 'lib' / 'slab.zig',
    ROOT / 'tools' / 'lib' / 'str_error_r.zig',
    ROOT / 'tools' / 'lib' / 'vsprintf.zig',
    ROOT / 'tools' / 'lib' / 'zalloc.zig',
    ROOT / 'scripts' / 'zigux' / 'artifact_diff.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase1-parity.py',
    ROOT / 'zigux' / 'tests' / 'build.zig',
    ROOT / 'zigux' / 'tests' / 'phase1_helpers.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helpers_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helpers.json',
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print('PHASE1_VALIDATION=fail')
    print('MISSING_PHASE1_FILES_START')
    for item in missing:
        print(item)
    print('MISSING_PHASE1_FILES_END')
    sys.exit(1)

ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
test_root = (ROOT / 'zigux' / 'tests' / 'phase1_helpers.zig').read_text(encoding='utf-8')

required_ledger_markers = [
    'feat(tools/lib): start phase-1 helper ports',
    'test(zigux): add phase-1 helper harness and workflow gate',
    'feat(tools/lib): expand phase-1 helper batch',
    'test(zigux): add phase-1 golden parity fixtures and artifact diff gate',
]
required_workflow_markers = [
    'tools/lib/*.zig',
    'python3 scripts/zigux/validate-phase1.py',
    'python3 scripts/zigux/check-phase1-parity.py',
    'zig build test --build-file zigux/tests/build.zig',
]
required_test_markers = [
    '@import("argv_split")',
    '@import("bitmap")',
    '@import("cmdline")',
    '@import("ctype")',
    '@import("find_bit")',
    '@import("hweight")',
    '@import("slab")',
    '@import("str_error_r")',
    '@import("string")',
    '@import("vsprintf")',
    '@import("zalloc")',
    '@import("rbtree")',
    '@embedFile("fixtures/phase1_helpers.json")',
]

missing_markers = []
for marker in required_ledger_markers:
    if marker not in ledger:
        missing_markers.append(f'ledger:{marker}')
for marker in required_workflow_markers:
    if marker not in workflow:
        missing_markers.append(f'workflow:{marker}')
for marker in required_test_markers:
    if marker not in test_root:
        missing_markers.append(f'test:{marker}')

if missing_markers:
    print('PHASE1_VALIDATION=fail')
    print('MISSING_PHASE1_MARKERS_START')
    for marker in missing_markers:
        print(marker)
    print('MISSING_PHASE1_MARKERS_END')
    sys.exit(1)

print('PHASE1_VALIDATION=pass')
print(f'PHASE1_REQUIRED_FILE_COUNT={len(required_files)}')
print(f'PHASE1_REQUIRED_MARKER_COUNT={len(required_ledger_markers) + len(required_workflow_markers) + len(required_test_markers)}')

#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / 'Documentation' / 'zigux' / 'phase3-abi-slice.md',
    ROOT / 'include' / 'linux' / 'zigux.h',
    ROOT / 'include' / 'zigux' / 'abi.h',
    ROOT / 'scripts' / 'zigux' / 'check-phase3-abi.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase3.py',
    ROOT / 'zigux' / 'bindings' / 'abi.zig',
    ROOT / 'zigux' / 'helpers' / 'layout_assert.zig',
    ROOT / 'zigux' / 'helpers' / 'panic_policy.zig',
    ROOT / 'zigux' / 'helpers' / 'allocator_policy.zig',
    ROOT / 'zigux' / 'helpers' / 'atomic.zig',
    ROOT / 'zigux' / 'helpers' / 'barrier.zig',
    ROOT / 'zigux' / 'helpers' / 'mmio.zig',
    ROOT / 'zigux' / 'kernel' / 'export_shim.zig',
    ROOT / 'zigux' / 'uapi' / 'version.zig',
    ROOT / 'zigux' / 'unsafe' / 'narrow.zig',
    ROOT / 'zigux' / 'tests' / 'phase3_abi.zig',
    ROOT / 'zigux' / 'tests' / 'phase3_abi_dump.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_abi' / 'phase3_abi_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_abi' / 'expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_abi_manifest.json',
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print('PHASE3_VALIDATION=fail')
    print('MISSING_PHASE3_FILES_START')
    for item in missing:
        print(item)
    print('MISSING_PHASE3_FILES_END')
    sys.exit(1)

roadmap = (ROOT / 'zigux-alpha' / 'ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md').read_text(encoding='utf-8')
phase_doc = (ROOT / 'Documentation' / 'zigux' / 'phase3-abi-slice.md').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
makefile = (ROOT / 'zigux' / 'Makefile').read_text(encoding='utf-8')
script_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')
tests_readme = (ROOT / 'zigux' / 'tests' / 'README.md').read_text(encoding='utf-8')
docs_readme = (ROOT / 'Documentation' / 'zigux' / 'README.md').read_text(encoding='utf-8')
ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
artifact_doc = (ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md').read_text(encoding='utf-8')
manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_abi_manifest.json').read_text(encoding='utf-8'))

required_markers = {
    'roadmap': [
        '## Phase 3: ABI and Interop Substrate',
        'include/linux/zigux.h',
        'include/zigux/abi.h',
        'zigux/kernel/',
        'zigux/helpers/',
        'zigux/bindings/',
    ],
    'phase_doc': [
        'PHASE3_STATUS=active',
        'PHASE3_SLICE=abi-substrate-skeleton',
        'PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py',
        'PHASE3_ABI_GATE=python3 scripts/zigux/check-phase3-abi.py',
        'PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig',
    ],
    'workflow': [
        'python3 scripts/zigux/validate-phase3.py',
        'python3 scripts/zigux/check-phase3-abi.py',
        'zig build phase3-test --build-file zigux/tests/build.zig',
    ],
    'makefile': [
        'phase3-validate:',
        'phase3-abi:',
        'phase3:',
        'check-phase3-abi.py',
        '$(ZIG) build phase3-test --build-file zigux/tests/build.zig',
    ],
    'scripts': [
        'check-phase3-abi.py',
        'validate-phase3.py',
    ],
    'tests': [
        'phase3_abi.zig',
        'phase3_abi_dump.zig',
        'phase3_abi_manifest.json',
    ],
    'docs': [
        'phase3-abi-slice.md',
    ],
    'artifact_doc': [
        'phase3_abi',
        'check-phase3-abi.py',
    ],
    'ledger': [
        'feat(zigux): start bounded Phase 3 abi substrate skeleton',
    ],
}

missing_markers: list[str] = []
for marker in required_markers['roadmap']:
    if marker not in roadmap:
        missing_markers.append(f'roadmap:{marker}')
for marker in required_markers['phase_doc']:
    if marker not in phase_doc:
        missing_markers.append(f'phase_doc:{marker}')
for marker in required_markers['workflow']:
    if marker not in workflow:
        missing_markers.append(f'workflow:{marker}')
for marker in required_markers['makefile']:
    if marker not in makefile:
        missing_markers.append(f'makefile:{marker}')
for marker in required_markers['scripts']:
    if marker not in script_readme:
        missing_markers.append(f'scripts:{marker}')
for marker in required_markers['tests']:
    if marker not in tests_readme:
        missing_markers.append(f'tests:{marker}')
for marker in required_markers['docs']:
    if marker not in docs_readme:
        missing_markers.append(f'docs:{marker}')
for marker in required_markers['artifact_doc']:
    if marker not in artifact_doc:
        missing_markers.append(f'artifact_doc:{marker}')
for marker in required_markers['ledger']:
    if marker not in ledger:
        missing_markers.append(f'ledger:{marker}')

if manifest.get('phase') != 'Phase 3':
    missing_markers.append('manifest:phase=Phase 3')
if manifest.get('status') != 'active':
    missing_markers.append('manifest:status=active')
if manifest.get('slice') != 'abi-substrate-skeleton':
    missing_markers.append('manifest:slice=abi-substrate-skeleton')
if manifest.get('file_count') != 12:
    missing_markers.append(f'manifest:file_count={manifest.get("file_count")}')
if len(manifest.get('files', [])) != 12:
    missing_markers.append(f'manifest:files_len={len(manifest.get("files", []))}')
for rel in manifest.get('files', []):
    if not (ROOT / rel).exists():
        missing_markers.append(f'manifest_file:{rel}')

if missing_markers:
    print('PHASE3_VALIDATION=fail')
    print('MISSING_PHASE3_MARKERS_START')
    for marker in missing_markers:
        print(marker)
    print('MISSING_PHASE3_MARKERS_END')
    sys.exit(1)

print('PHASE3_VALIDATION=pass')
print(f'PHASE3_REQUIRED_FILE_COUNT={len(required_files)}')
print(f'PHASE3_REQUIRED_MARKER_COUNT={sum(len(v) for v in required_markers.values())}')

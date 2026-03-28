#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / 'Documentation' / 'zigux' / 'phase3-abi-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase3-bitmap-cpumask-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase3-list-hlist-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase3-errptr-xarray-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase3-xarray-slot-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase3-idr-slot-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase3-ida-bitmap-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase3-ida-alloc-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase3-ida-range-slice.md',
    ROOT / 'include' / 'linux' / 'zigux.h',
    ROOT / 'include' / 'zigux' / 'abi.h',
    ROOT / 'scripts' / 'zigux' / 'check-phase3-abi.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase3-bitmap-cpumask.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase3-list-hlist.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase3-errptr-xarray.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase3-xarray-slot.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase3-idr-slot.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase3-ida-bitmap.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase3-ida-alloc.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase3-ida-range.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase3.py',
    ROOT / 'zigux' / 'bindings' / 'abi.zig',
    ROOT / 'zigux' / 'helpers' / 'bitmap_view.zig',
    ROOT / 'zigux' / 'helpers' / 'cpumask_view.zig',
    ROOT / 'zigux' / 'helpers' / 'list_view.zig',
    ROOT / 'zigux' / 'helpers' / 'hlist_view.zig',
    ROOT / 'zigux' / 'helpers' / 'err_ptr.zig',
    ROOT / 'zigux' / 'helpers' / 'xa_value.zig',
    ROOT / 'zigux' / 'helpers' / 'xarray_slot_view.zig',
    ROOT / 'zigux' / 'helpers' / 'idr_slot_view.zig',
    ROOT / 'zigux' / 'helpers' / 'ida_bitmap_view.zig',
    ROOT / 'zigux' / 'helpers' / 'ida_alloc_view.zig',
    ROOT / 'zigux' / 'helpers' / 'ida_range_view.zig',
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
    ROOT / 'zigux' / 'tests' / 'phase3_bitmap_cpumask_dump.zig',
    ROOT / 'zigux' / 'tests' / 'phase3_list_hlist_dump.zig',
    ROOT / 'zigux' / 'tests' / 'phase3_errptr_xarray_dump.zig',
    ROOT / 'zigux' / 'tests' / 'phase3_xarray_slot_dump.zig',
    ROOT / 'zigux' / 'tests' / 'phase3_idr_slot_dump.zig',
    ROOT / 'zigux' / 'tests' / 'phase3_ida_bitmap_dump.zig',
    ROOT / 'zigux' / 'tests' / 'phase3_ida_alloc_dump.zig',
    ROOT / 'zigux' / 'tests' / 'phase3_ida_range_dump.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_abi' / 'phase3_abi_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_abi' / 'expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_abi_manifest.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_bitmap_cpumask' / 'phase3_bitmap_cpumask_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_bitmap_cpumask' / 'expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_bitmap_cpumask_manifest.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_list_hlist' / 'phase3_list_hlist_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_list_hlist' / 'expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_list_hlist_manifest.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_errptr_xarray' / 'phase3_errptr_xarray_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_errptr_xarray' / 'expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_errptr_xarray_manifest.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_xarray_slot' / 'phase3_xarray_slot_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_xarray_slot' / 'expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_xarray_slot_manifest.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_idr_slot' / 'phase3_idr_slot_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_idr_slot' / 'expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_idr_slot_manifest.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_ida_bitmap' / 'phase3_ida_bitmap_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_ida_bitmap' / 'expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_ida_bitmap_manifest.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_ida_alloc' / 'phase3_ida_alloc_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_ida_alloc' / 'expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_ida_alloc_manifest.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_ida_range' / 'phase3_ida_range_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_ida_range' / 'expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_ida_range_manifest.json',
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
phase_bitmap_doc = (ROOT / 'Documentation' / 'zigux' / 'phase3-bitmap-cpumask-slice.md').read_text(encoding='utf-8')
phase_list_doc = (ROOT / 'Documentation' / 'zigux' / 'phase3-list-hlist-slice.md').read_text(encoding='utf-8')
phase_errptr_doc = (ROOT / 'Documentation' / 'zigux' / 'phase3-errptr-xarray-slice.md').read_text(encoding='utf-8')
phase_xarray_slot_doc = (ROOT / 'Documentation' / 'zigux' / 'phase3-xarray-slot-slice.md').read_text(encoding='utf-8')
phase_idr_slot_doc = (ROOT / 'Documentation' / 'zigux' / 'phase3-idr-slot-slice.md').read_text(encoding='utf-8')
phase_ida_bitmap_doc = (ROOT / 'Documentation' / 'zigux' / 'phase3-ida-bitmap-slice.md').read_text(encoding='utf-8')
phase_ida_alloc_doc = (ROOT / 'Documentation' / 'zigux' / 'phase3-ida-alloc-slice.md').read_text(encoding='utf-8')
phase_ida_range_doc = (ROOT / 'Documentation' / 'zigux' / 'phase3-ida-range-slice.md').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
makefile = (ROOT / 'zigux' / 'Makefile').read_text(encoding='utf-8')
script_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')
tests_readme = (ROOT / 'zigux' / 'tests' / 'README.md').read_text(encoding='utf-8')
docs_readme = (ROOT / 'Documentation' / 'zigux' / 'README.md').read_text(encoding='utf-8')
ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
artifact_doc = (ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md').read_text(encoding='utf-8')
manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_abi_manifest.json').read_text(encoding='utf-8'))
bitmap_manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_bitmap_cpumask_manifest.json').read_text(encoding='utf-8'))
list_manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_list_hlist_manifest.json').read_text(encoding='utf-8'))
errptr_manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_errptr_xarray_manifest.json').read_text(encoding='utf-8'))
xarray_slot_manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_xarray_slot_manifest.json').read_text(encoding='utf-8'))
idr_slot_manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_idr_slot_manifest.json').read_text(encoding='utf-8'))
ida_bitmap_manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_ida_bitmap_manifest.json').read_text(encoding='utf-8'))
ida_alloc_manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_ida_alloc_manifest.json').read_text(encoding='utf-8'))
ida_range_manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_ida_range_manifest.json').read_text(encoding='utf-8'))

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
    'phase_bitmap_doc': [
        'PHASE3_STATUS=active',
        'PHASE3_SLICE=bitmap-cpumask-view-interop',
        'PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py',
        'PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-bitmap-cpumask.py',
        'PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig',
    ],
    'phase_list_doc': [
        'PHASE3_STATUS=active',
        'PHASE3_SLICE=list-hlist-view-interop',
        'PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py',
        'PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-list-hlist.py',
        'PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig',
    ],
    'phase_errptr_doc': [
        'PHASE3_STATUS=active',
        'PHASE3_SLICE=errptr-xarray-value-interop',
        'PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py',
        'PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-errptr-xarray.py',
        'PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig',
    ],
    'phase_xarray_slot_doc': [
        'PHASE3_STATUS=active',
        'PHASE3_SLICE=xarray-slot-view-interop',
        'PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py',
        'PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-xarray-slot.py',
        'PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig',
    ],
    'phase_idr_slot_doc': [
        'PHASE3_STATUS=active',
        'PHASE3_SLICE=idr-slot-view-interop',
        'PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py',
        'PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-idr-slot.py',
        'PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig',
    ],
    'phase_ida_bitmap_doc': [
        'PHASE3_STATUS=active',
        'PHASE3_SLICE=ida-bitmap-view-interop',
        'PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py',
        'PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-ida-bitmap.py',
        'PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig',
    ],
    'phase_ida_alloc_doc': [
        'PHASE3_STATUS=active',
        'PHASE3_SLICE=ida-alloc-view-interop',
        'PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py',
        'PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-ida-alloc.py',
        'PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig',
    ],
    'phase_ida_range_doc': [
        'PHASE3_STATUS=active',
        'PHASE3_SLICE=ida-range-view-interop',
        'PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py',
        'PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-ida-range.py',
        'PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig',
    ],
    'workflow': [
        'python3 scripts/zigux/validate-phase3.py',
        'python3 scripts/zigux/check-phase3-abi.py',
        'python3 scripts/zigux/check-phase3-bitmap-cpumask.py',
        'python3 scripts/zigux/check-phase3-list-hlist.py',
        'python3 scripts/zigux/check-phase3-errptr-xarray.py',
        'python3 scripts/zigux/check-phase3-xarray-slot.py',
        'python3 scripts/zigux/check-phase3-idr-slot.py',
        'python3 scripts/zigux/check-phase3-ida-bitmap.py',
        'python3 scripts/zigux/check-phase3-ida-alloc.py',
        'python3 scripts/zigux/check-phase3-ida-range.py',
        'zig build phase3-test --build-file zigux/tests/build.zig',
    ],
    'makefile': [
        'phase3-validate:',
        'phase3-abi:',
        'phase3-interop:',
        'phase3:',
        'check-phase3-abi.py',
        'check-phase3-bitmap-cpumask.py',
        'check-phase3-list-hlist.py',
        'check-phase3-errptr-xarray.py',
        'check-phase3-xarray-slot.py',
        'check-phase3-idr-slot.py',
        'check-phase3-ida-bitmap.py',
        'check-phase3-ida-alloc.py',
        'check-phase3-ida-range.py',
        '$(ZIG) build phase3-test --build-file zigux/tests/build.zig',
    ],
    'scripts': [
        'check-phase3-abi.py',
        'check-phase3-bitmap-cpumask.py',
        'check-phase3-list-hlist.py',
        'check-phase3-errptr-xarray.py',
        'check-phase3-xarray-slot.py',
        'check-phase3-idr-slot.py',
        'check-phase3-ida-bitmap.py',
        'check-phase3-ida-alloc.py',
        'check-phase3-ida-range.py',
        'validate-phase3.py',
    ],
    'tests': [
        'phase3_abi.zig',
        'phase3_abi_dump.zig',
        'phase3_bitmap_cpumask_dump.zig',
        'phase3_list_hlist_dump.zig',
        'phase3_errptr_xarray_dump.zig',
        'phase3_xarray_slot_dump.zig',
        'phase3_idr_slot_dump.zig',
        'phase3_ida_bitmap_dump.zig',
        'phase3_ida_alloc_dump.zig',
        'phase3_ida_range_dump.zig',
        'phase3_abi_manifest.json',
        'phase3_bitmap_cpumask_manifest.json',
        'phase3_list_hlist_manifest.json',
        'phase3_errptr_xarray_manifest.json',
        'phase3_xarray_slot_manifest.json',
        'phase3_idr_slot_manifest.json',
        'phase3_ida_bitmap_manifest.json',
        'phase3_ida_alloc_manifest.json',
        'phase3_ida_range_manifest.json',
    ],
    'docs': [
        'phase3-abi-slice.md',
        'phase3-bitmap-cpumask-slice.md',
        'phase3-list-hlist-slice.md',
        'phase3-errptr-xarray-slice.md',
        'phase3-xarray-slot-slice.md',
        'phase3-idr-slot-slice.md',
        'phase3-ida-bitmap-slice.md',
        'phase3-ida-alloc-slice.md',
        'phase3-ida-range-slice.md',
    ],
    'artifact_doc': [
        'phase3_abi',
        'check-phase3-abi.py',
        'phase3_bitmap_cpumask',
        'check-phase3-bitmap-cpumask.py',
        'phase3_list_hlist',
        'check-phase3-list-hlist.py',
        'phase3_errptr_xarray',
        'check-phase3-errptr-xarray.py',
        'phase3_xarray_slot',
        'check-phase3-xarray-slot.py',
        'phase3_idr_slot',
        'check-phase3-idr-slot.py',
        'phase3_ida_bitmap',
        'check-phase3-ida-bitmap.py',
        'phase3_ida_alloc',
        'check-phase3-ida-alloc.py',
        'phase3_ida_range',
        'check-phase3-ida-range.py',
    ],
    'ledger': [
        'feat(zigux): start bounded Phase 3 abi substrate skeleton',
        'feat(zigux): add bounded Phase 3 bitmap/cpumask interop slice',
        'feat(zigux): add bounded Phase 3 list/hlist interop slice',
        'feat(zigux): add bounded Phase 3 err_ptr/xarray interop slice',
        'feat(zigux): add bounded Phase 3 xarray slot interop slice',
        'feat(zigux): add bounded Phase 3 idr slot interop slice',
        'feat(zigux): add bounded Phase 3 ida bitmap interop slice',
        'feat(zigux): add bounded Phase 3 ida allocation interop slice',
        'feat(zigux): add bounded Phase 3 ida range interop slice',
    ],
}

missing_markers: list[str] = []
for marker in required_markers['roadmap']:
    if marker not in roadmap:
        missing_markers.append(f'roadmap:{marker}')
for marker in required_markers['phase_doc']:
    if marker not in phase_doc:
        missing_markers.append(f'phase_doc:{marker}')
for marker in required_markers['phase_bitmap_doc']:
    if marker not in phase_bitmap_doc:
        missing_markers.append(f'phase_bitmap_doc:{marker}')
for marker in required_markers['phase_list_doc']:
    if marker not in phase_list_doc:
        missing_markers.append(f'phase_list_doc:{marker}')
for marker in required_markers['phase_errptr_doc']:
    if marker not in phase_errptr_doc:
        missing_markers.append(f'phase_errptr_doc:{marker}')
for marker in required_markers['phase_xarray_slot_doc']:
    if marker not in phase_xarray_slot_doc:
        missing_markers.append(f'phase_xarray_slot_doc:{marker}')
for marker in required_markers['phase_idr_slot_doc']:
    if marker not in phase_idr_slot_doc:
        missing_markers.append(f'phase_idr_slot_doc:{marker}')
for marker in required_markers['phase_ida_bitmap_doc']:
    if marker not in phase_ida_bitmap_doc:
        missing_markers.append(f'phase_ida_bitmap_doc:{marker}')
for marker in required_markers['phase_ida_alloc_doc']:
    if marker not in phase_ida_alloc_doc:
        missing_markers.append(f'phase_ida_alloc_doc:{marker}')
for marker in required_markers['phase_ida_range_doc']:
    if marker not in phase_ida_range_doc:
        missing_markers.append(f'phase_ida_range_doc:{marker}')
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

if bitmap_manifest.get('phase') != 'Phase 3':
    missing_markers.append('bitmap_manifest:phase=Phase 3')
if bitmap_manifest.get('status') != 'active':
    missing_markers.append('bitmap_manifest:status=active')
if bitmap_manifest.get('slice') != 'bitmap-cpumask-view-interop':
    missing_markers.append(f'bitmap_manifest:slice={bitmap_manifest.get("slice")}')
if bitmap_manifest.get('file_count') != 4:
    missing_markers.append(f'bitmap_manifest:file_count={bitmap_manifest.get("file_count")}')
if len(bitmap_manifest.get('files', [])) != 4:
    missing_markers.append(f'bitmap_manifest:files_len={len(bitmap_manifest.get("files", []))}')
for rel in bitmap_manifest.get('files', []):
    if not (ROOT / rel).exists():
        missing_markers.append(f'bitmap_manifest_file:{rel}')

if list_manifest.get('phase') != 'Phase 3':
    missing_markers.append('list_manifest:phase=Phase 3')
if list_manifest.get('status') != 'active':
    missing_markers.append('list_manifest:status=active')
if list_manifest.get('slice') != 'list-hlist-view-interop':
    missing_markers.append(f'list_manifest:slice={list_manifest.get("slice")}')
if list_manifest.get('file_count') != 4:
    missing_markers.append(f'list_manifest:file_count={list_manifest.get("file_count")}')
if len(list_manifest.get('files', [])) != 4:
    missing_markers.append(f'list_manifest:files_len={len(list_manifest.get("files", []))}')
for rel in list_manifest.get('files', []):
    if not (ROOT / rel).exists():
        missing_markers.append(f'list_manifest_file:{rel}')

if errptr_manifest.get('phase') != 'Phase 3':
    missing_markers.append('errptr_manifest:phase=Phase 3')
if errptr_manifest.get('status') != 'active':
    missing_markers.append('errptr_manifest:status=active')
if errptr_manifest.get('slice') != 'errptr-xarray-value-interop':
    missing_markers.append(f'errptr_manifest:slice={errptr_manifest.get("slice")}')
if errptr_manifest.get('file_count') != 4:
    missing_markers.append(f'errptr_manifest:file_count={errptr_manifest.get("file_count")}')
if len(errptr_manifest.get('files', [])) != 4:
    missing_markers.append(f'errptr_manifest:files_len={len(errptr_manifest.get("files", []))}')
for rel in errptr_manifest.get('files', []):
    if not (ROOT / rel).exists():
        missing_markers.append(f'errptr_manifest_file:{rel}')

if xarray_slot_manifest.get('phase') != 'Phase 3':
    missing_markers.append('xarray_slot_manifest:phase=Phase 3')
if xarray_slot_manifest.get('status') != 'active':
    missing_markers.append('xarray_slot_manifest:status=active')
if xarray_slot_manifest.get('slice') != 'xarray-slot-view-interop':
    missing_markers.append(f'xarray_slot_manifest:slice={xarray_slot_manifest.get("slice")}')
if xarray_slot_manifest.get('file_count') != 4:
    missing_markers.append(f'xarray_slot_manifest:file_count={xarray_slot_manifest.get("file_count")}')
if len(xarray_slot_manifest.get('files', [])) != 4:
    missing_markers.append(f'xarray_slot_manifest:files_len={len(xarray_slot_manifest.get("files", []))}')
for rel in xarray_slot_manifest.get('files', []):
    if not (ROOT / rel).exists():
        missing_markers.append(f'xarray_slot_manifest_file:{rel}')

if idr_slot_manifest.get('phase') != 'Phase 3':
    missing_markers.append('idr_slot_manifest:phase=Phase 3')
if idr_slot_manifest.get('status') != 'active':
    missing_markers.append('idr_slot_manifest:status=active')
if idr_slot_manifest.get('slice') != 'idr-slot-view-interop':
    missing_markers.append(f'idr_slot_manifest:slice={idr_slot_manifest.get("slice")}')
if idr_slot_manifest.get('file_count') != 4:
    missing_markers.append(f'idr_slot_manifest:file_count={idr_slot_manifest.get("file_count")}')
if len(idr_slot_manifest.get('files', [])) != 4:
    missing_markers.append(f'idr_slot_manifest:files_len={len(idr_slot_manifest.get("files", []))}')
for rel in idr_slot_manifest.get('files', []):
    if not (ROOT / rel).exists():
        missing_markers.append(f'idr_slot_manifest_file:{rel}')

if ida_bitmap_manifest.get('phase') != 'Phase 3':
    missing_markers.append('ida_bitmap_manifest:phase=Phase 3')
if ida_bitmap_manifest.get('status') != 'active':
    missing_markers.append('ida_bitmap_manifest:status=active')
if ida_bitmap_manifest.get('slice') != 'ida-bitmap-view-interop':
    missing_markers.append(f'ida_bitmap_manifest:slice={ida_bitmap_manifest.get("slice")}')
if ida_bitmap_manifest.get('file_count') != 4:
    missing_markers.append(f'ida_bitmap_manifest:file_count={ida_bitmap_manifest.get("file_count")}')
if len(ida_bitmap_manifest.get('files', [])) != 4:
    missing_markers.append(f'ida_bitmap_manifest:files_len={len(ida_bitmap_manifest.get("files", []))}')
for rel in ida_bitmap_manifest.get('files', []):
    if not (ROOT / rel).exists():
        missing_markers.append(f'ida_bitmap_manifest_file:{rel}')

if ida_alloc_manifest.get('phase') != 'Phase 3':
    missing_markers.append('ida_alloc_manifest:phase=Phase 3')
if ida_alloc_manifest.get('status') != 'active':
    missing_markers.append('ida_alloc_manifest:status=active')
if ida_alloc_manifest.get('slice') != 'ida-alloc-view-interop':
    missing_markers.append(f'ida_alloc_manifest:slice={ida_alloc_manifest.get("slice")}')
if ida_alloc_manifest.get('file_count') != 4:
    missing_markers.append(f'ida_alloc_manifest:file_count={ida_alloc_manifest.get("file_count")}')
if len(ida_alloc_manifest.get('files', [])) != 4:
    missing_markers.append(f'ida_alloc_manifest:files_len={len(ida_alloc_manifest.get("files", []))}')
for rel in ida_alloc_manifest.get('files', []):
    if not (ROOT / rel).exists():
        missing_markers.append(f'ida_alloc_manifest_file:{rel}')

if ida_range_manifest.get('phase') != 'Phase 3':
    missing_markers.append('ida_range_manifest:phase=Phase 3')
if ida_range_manifest.get('status') != 'active':
    missing_markers.append('ida_range_manifest:status=active')
if ida_range_manifest.get('slice') != 'ida-range-view-interop':
    missing_markers.append(f'ida_range_manifest:slice={ida_range_manifest.get("slice")}')
if ida_range_manifest.get('file_count') != 4:
    missing_markers.append(f'ida_range_manifest:file_count={ida_range_manifest.get("file_count")}')
if len(ida_range_manifest.get('files', [])) != 4:
    missing_markers.append(f'ida_range_manifest:files_len={len(ida_range_manifest.get("files", []))}')
for rel in ida_range_manifest.get('files', []):
    if not (ROOT / rel).exists():
        missing_markers.append(f'ida_range_manifest_file:{rel}')

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

#!/usr/bin/env python3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / 'scripts' / 'zigux' / 'validate-phase6.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase6-base64-c-parity.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase6-bsearch-c-parity.py',
    ROOT / 'scripts' / 'zigux' / 'README.md',
    ROOT / 'Documentation' / 'zigux' / 'README.md',
    ROOT / 'Documentation' / 'zigux' / 'phase6-helper-parity-catalog.md',
    ROOT / 'Documentation' / 'zigux' / 'phase6-base64-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase6-bsearch-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase6-checksum-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase6-hexdump-slice.md',
    ROOT / 'zigux' / 'Makefile',
    ROOT / 'zigux' / 'tests' / 'README.md',
    ROOT / 'zigux' / 'tests' / 'phase6_base64.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_base64_perf.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_base64_c_parity.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase6_base64_vectors.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase6_base64_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'phase6_bsearch.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_bsearch_perf.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_bsearch_c_parity.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase6_bsearch_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'phase6_checksum.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_checksum_perf.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase6_checksum_vectors.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_hexdump.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_hexdump_perf.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase6_hexdump_vectors.zig',
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
phase6_catalog = (ROOT / 'Documentation' / 'zigux' / 'phase6-helper-parity-catalog.md').read_text(encoding='utf-8')
phase6_build = (ROOT / 'zigux' / 'tests' / 'phase6_build.zig').read_text(encoding='utf-8')
phase6_base64 = (ROOT / 'zigux' / 'tests' / 'phase6_base64.zig').read_text(encoding='utf-8')
phase6_base64_perf = (ROOT / 'zigux' / 'tests' / 'phase6_base64_perf.zig').read_text(encoding='utf-8')
phase6_bsearch = (ROOT / 'zigux' / 'tests' / 'phase6_bsearch.zig').read_text(encoding='utf-8')
phase6_bsearch_perf = (ROOT / 'zigux' / 'tests' / 'phase6_bsearch_perf.zig').read_text(encoding='utf-8')
phase6_hexdump = (ROOT / 'zigux' / 'tests' / 'phase6_hexdump.zig').read_text(encoding='utf-8')

slice_docs = {
    'phase6-base64-slice.md': (ROOT / 'Documentation' / 'zigux' / 'phase6-base64-slice.md').read_text(encoding='utf-8'),
    'phase6-bsearch-slice.md': (ROOT / 'Documentation' / 'zigux' / 'phase6-bsearch-slice.md').read_text(encoding='utf-8'),
    'phase6-checksum-slice.md': (ROOT / 'Documentation' / 'zigux' / 'phase6-checksum-slice.md').read_text(encoding='utf-8'),
    'phase6-hexdump-slice.md': (ROOT / 'Documentation' / 'zigux' / 'phase6-hexdump-slice.md').read_text(encoding='utf-8'),
}

required_make_markers = [
    'PHONY += phase6-validate phase6-test phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-perf phase6',
    'phase6-validate:',
    'scripts/zigux/validate-phase6.py',
    'phase6-test:',
    'zigux/tests/phase6_build.zig',
    'phase6-base64-perf:',
    'base64-perf --build-file zigux/tests/phase6_build.zig',
    'phase6-bsearch-perf:',
    'bsearch-perf --build-file zigux/tests/phase6_build.zig',
    'phase6-checksum-perf:',
    'checksum-perf --build-file zigux/tests/phase6_build.zig',
    'phase6-hexdump-perf:',
    'hexdump-perf --build-file zigux/tests/phase6_build.zig',
]

required_workflow_markers = [
    'Validate Phase 6 leaf helper gates',
    'make -C zigux phase6-validate',
    'Run Phase 6 leaf helper tests',
    'zigux/tests/phase6_build.zig',
]

required_script_readme_markers = [
    'validate-phase6.py',
    'check-phase6-base64-c-parity.py',
    'check-phase6-bsearch-c-parity.py',
    'Phase 6 flow',
    'make -C zigux phase6-validate',
    'phase6_build.zig',
    'phase6-helper-parity-catalog.md',
    'phase6-hexdump-slice.md',
]

required_tests_readme_markers = [
    'zigux/tests/phase6_build.zig',
    'zigux/tests/phase6_base64.zig',
    'zigux/tests/phase6_base64_perf.zig',
    'zigux/tests/phase6_base64_c_parity.zig',
    'zigux/tests/fixtures/phase6_base64_vectors.zig',
    'zigux/tests/fixtures/phase6_base64_c_harness.c',
    'zigux/tests/phase6_bsearch.zig',
    'zigux/tests/phase6_bsearch_perf.zig',
    'zigux/tests/phase6_bsearch_c_parity.zig',
    'zigux/tests/fixtures/phase6_bsearch_c_harness.c',
    'zigux/tests/phase6_checksum.zig',
    'zigux/tests/phase6_checksum_perf.zig',
    'zigux/tests/fixtures/phase6_checksum_vectors.zig',
    'zigux/tests/phase6_hexdump.zig',
    'zigux/tests/phase6_hexdump_perf.zig',
    'zigux/tests/fixtures/phase6_hexdump_vectors.zig',
    'Documentation/zigux/phase6-helper-parity-catalog.md',
    'scripts/zigux/validate-phase6.py',
]

required_doc_readme_markers = [
    'Phase 6 notes',
    'Documentation/zigux/phase6-helper-parity-catalog.md',
    'Documentation/zigux/phase6-base64-slice.md',
    'Documentation/zigux/phase6-bsearch-slice.md',
    'Documentation/zigux/phase6-checksum-slice.md',
    'Documentation/zigux/phase6-hexdump-slice.md',
    'zigux/tests/phase6_build.zig',
    'make -C zigux phase6',
    'make -C zigux phase6-validate',
    'make -C zigux phase6-base64-perf',
    'python3 scripts/zigux/check-phase6-base64-c-parity.py',
    'python3 scripts/zigux/check-phase6-bsearch-c-parity.py',
    'make -C zigux phase6-hexdump-perf',
    'generated fixture flow',
    'python3 scripts/zigux/validate-phase6.py',
]

required_phase6_catalog_markers = [
    'Phase 6 Helper Parity Catalog',
    'verified head:',
    'lib/base64.zig',
    'scripts/zigux/check-phase6-base64-c-parity.py',
    'lib/bsearch.zig',
    'scripts/zigux/check-phase6-bsearch-c-parity.py',
    'lib/checksum.zig',
    'lib/hexdump.zig',
    'zigux/tests/phase6_build.zig',
    'scripts/zigux/validate-phase6.py',
    '.github/workflows/zigux-bootstrap.yml',
    'Documentation/zigux/README.md',
    'scripts/zigux/README.md',
    'zigux/tests/README.md',
]

required_phase6_build_markers = [
    '../../lib/base64.zig',
    '../../lib/bsearch.zig',
    '../../lib/checksum.zig',
    '../../lib/hexdump.zig',
    'phase6_base64.zig',
    'phase6_base64_perf.zig',
    'phase6_bsearch.zig',
    'phase6_bsearch_perf.zig',
    'phase6_checksum.zig',
    'phase6_checksum_perf.zig',
    'phase6_hexdump.zig',
    'phase6_hexdump_perf.zig',
    'Run Phase 6 leaf helper tests',
    'Run the Phase 6 base64 performance sanity harness',
    'Run the Phase 6 bsearch performance sanity harness',
    'Run the Phase 6 checksum performance sanity harness',
    'Run the Phase 6 hexdump performance sanity harness',
]

required_base64_markers = [
    'fixtures/phase6_base64_vectors.zig',
    'phase 6 base64 standard encode parity matches kernel vectors',
    'phase 6 base64 exact-fit buffers work across fixture vectors',
    'phase 6 base64 decode rejects invalid kernel-style vectors',
]

required_base64_perf_markers = [
    'phase6-base64-perf',
    '.{ .label = "64B", .size = 64, .reps = 20_000 }',
    '.{ .label = "1KB", .size = 1024, .reps = 4_000 }',
    'encode_ns_per_op',
    'decode_ns_per_op',
    'try std.testing.expectEqualSlices(u8, input[0..case.size], decoded[0..decoded_len]);',
]

required_bsearch_markers = [
    'phase 6 bsearch supports string keys against sorted records',
    'phase 6 bsearch treats duplicate keys as found-or-null without claiming stable selection',
    'phase 6 bsearch keeps representative lookup work inside a binary-search budget',
    'compareU32Counted',
]

required_bsearch_perf_markers = [
    'phase6-bsearch-perf',
    '.{ .label = "256", .len = 256, .reps = 2_000 }',
    '.{ .label = "4096", .len = 4096, .reps = 500 }',
    'avg_compare_calls',
    'std.math.log2_int_ceil',
    'try std.testing.expect(avg_compare_calls <= @as(f64, @floatFromInt(max_compare_budget)));',
]

required_checksum_perf_markers = [
    'phase6-checksum-perf',
    'fixtures.perf_cases',
    'fixtures.fillPerfPayload(payload);',
    'referencePartial',
    'ns_per_byte',
    'try std.testing.expect(elapsed > 0);',
]

required_hexdump_perf_markers = [
    'phase6-hexdump-perf',
    '.{ .label = "16B-plain", .len = 16, .rowsize = 16, .groupsize = 1, .ascii = false, .reps = 40_000 }',
    '.{ .label = "32B-ascii-g2", .len = 32, .rowsize = 32, .groupsize = 2, .ascii = true, .reps = 10_000 }',
    'fixtures.prepareExpectedLine',
    'ns_per_byte',
    'try std.testing.expect(elapsed > 0);',
]

required_hexdump_markers = [
    'phase 6 hexdump overflow contract matches truncation expectations',
    'phase 6 hexdump covers normalization and empty-buffer edge cases',
]

required_slice_markers = {
    'phase6-base64-slice.md': [
        'PHASE6_STATUS=active',
        'lib/base64.zig',
        'python3 scripts/zigux/check-phase6-base64-c-parity.py',
        'zigux/tests/phase6_base64_c_parity.zig',
        'zigux/tests/fixtures/phase6_base64_c_harness.c',
        'zigux/tests/fixtures/phase6_base64_vectors.zig',
        'zigux/tests/phase6_build.zig',
        'make -C zigux phase6-base64-perf',
    ],
    'phase6-bsearch-slice.md': [
        'PHASE6_STATUS=active',
        'lib/bsearch.zig',
        'zigux/tests/phase6_build.zig',
        'make -C zigux phase6-bsearch-perf',
        'python3 scripts/zigux/check-phase6-bsearch-c-parity.py',
        'duplicate-key found-or-null parity without claiming stable selection',
        'representative lookup work stays inside a bounded binary-search comparison budget',
        'representative external C-vs-Zig parity spot check',
        'replayable perf-sanity harness reports lookup cost and average comparator work for representative sorted slices',
    ],
    'phase6-checksum-slice.md': [
        'PHASE6_STATUS=active',
        'lib/checksum.zig',
        'zigux/tests/fixtures/phase6_checksum_vectors.zig',
        'zigux/tests/phase6_build.zig',
        'make -C zigux phase6-checksum-perf',
        'replayable perf-sanity harness reports representative checksum cost per call and per byte',
    ],
    'phase6-hexdump-slice.md': [
        'PHASE6_STATUS=active',
        'lib/hexdump.zig',
        'zigux/tests/phase6_build.zig',
        'make -C zigux phase6-hexdump-perf',
        'replayable perf-sanity harness reports representative dump cost per call and per byte',
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
for marker in required_phase6_catalog_markers:
    if marker not in phase6_catalog:
        missing_markers.append(f'phase6_catalog:{marker}')
for marker in required_phase6_build_markers:
    if marker not in phase6_build:
        missing_markers.append(f'phase6_build:{marker}')
for marker in required_base64_markers:
    if marker not in phase6_base64:
        missing_markers.append(f'phase6_base64:{marker}')
for marker in required_base64_perf_markers:
    if marker not in phase6_base64_perf:
        missing_markers.append(f'phase6_base64_perf:{marker}')
for marker in required_bsearch_markers:
    if marker not in phase6_bsearch:
        missing_markers.append(f'phase6_bsearch:{marker}')
for marker in required_bsearch_perf_markers:
    if marker not in phase6_bsearch_perf:
        missing_markers.append(f'phase6_bsearch_perf:{marker}')
phase6_checksum_perf = (ROOT / 'zigux' / 'tests' / 'phase6_checksum_perf.zig').read_text(encoding='utf-8')
for marker in required_checksum_perf_markers:
    if marker not in phase6_checksum_perf:
        missing_markers.append(f'phase6_checksum_perf:{marker}')
phase6_hexdump_perf = (ROOT / 'zigux' / 'tests' / 'phase6_hexdump_perf.zig').read_text(encoding='utf-8')
for marker in required_hexdump_perf_markers:
    if marker not in phase6_hexdump_perf:
        missing_markers.append(f'phase6_hexdump_perf:{marker}')
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
    f"{len(required_make_markers) + len(required_workflow_markers) + len(required_script_readme_markers) + len(required_tests_readme_markers) + len(required_doc_readme_markers) + len(required_phase6_catalog_markers) + len(required_phase6_build_markers) + len(required_base64_markers) + len(required_base64_perf_markers) + len(required_bsearch_markers) + len(required_bsearch_perf_markers) + len(required_checksum_perf_markers) + len(required_hexdump_perf_markers) + len(required_hexdump_markers) + sum(len(markers) for markers in required_slice_markers.values())}"
)

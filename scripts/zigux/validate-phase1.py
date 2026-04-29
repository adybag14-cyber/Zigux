#!/usr/bin/env python3
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

EXPECTED_PHASE1_FIXTURE_SHAPE = {
    'find_bit': {
        'bits_per_long',
        'first',
        'next_after_6',
        'next_after_word',
        'first_zero',
        'next_zero',
        'first_and',
        'next_and',
        'tail_clamped_first',
        'tail_clamped_next',
        'tail_zero_clamped_first',
        'tail_zero_clamped_next',
        'tail_and_clamped_first',
        'tail_and_clamped_next',
        'tail_and_mixed_first',
        'tail_and_mixed_next',
    },
    'bitmap': {
        'weight',
        'scnprintf',
        'and_result',
        'and_values',
        'andnot_result',
        'andnot_values',
        'or_values',
        'xor_values',
        'copy_nbits',
        'copy_values',
        'partial_xor_nbits',
        'partial_xor_masked_values',
        'scnprintf_empty_len',
        'scnprintf_empty_bytes',
        'alloc_nbits',
        'alloc_values',
        'zalloc_nbits',
        'zalloc_values',
        'equal',
        'intersects',
        'subset',
        'range_after_set',
        'range_after_clear',
        'full_after_fill',
        'empty_after_zero',
        'scnprintf_trunc_len',
        'scnprintf_trunc',
    },
    'string': {
        'strtobool_y',
        'strtobool_on',
        'strtobool_zero',
        'strtobool_off',
        'strtobool_invalid',
        'strlcpy_len',
        'strlcpy_buffer',
        'skip_spaces',
        'trim_spaces',
        'remove_spaces',
        'remove_spaces_nul',
        'remove_spaces_nul_bytes',
        'replace_char',
        'replace_char_end',
        'memchr_inv_index',
        'memchr_inv_none',
    },
    'rbtree': {
        'empty_root',
        'insert_order',
        'reverse_order',
        'replace_order',
        'erase_init_order',
        'postorder_count',
        'erase_init_node_empty',
        'cleared_node_empty',
    },
    'argv_split': {'argc', 'argv', 'blank_argc'},
    'cmdline': {'decimal_k', 'hex_m', 'octal_k', 'invalid'},
    'ctype': {
        'mask_A',
        'mask_a',
        'mask_space',
        'isalnum_A',
        'isalpha_z',
        'isdigit_7',
        'isspace_tab',
        'isxdigit_f',
        'ispunct_bang',
        'tolower_A',
        'toupper_z',
        'isodigit_7',
        'isodigit_8',
    },
    'hweight': {'w8', 'w16', 'w32', 'w64', 'wlong'},
    'list_sort': {'tri_sorted_keys', 'tri_sorted_ordinals', 'bool_sorted_keys', 'bool_sorted_ordinals'},
    'zalloc': {'zeroed', 'freed_is_null', 'value_zeroed', 'value_freed_is_null'},
    'str_error_r': {'enoent', 'unknown'},
    'slab': {
        'null_without_reclaim',
        'alloc_count_after_kmalloc',
        'zero_after_kmalloc',
        'alloc_count_after_kmalloc_free',
        'array_zeroed',
        'alloc_count_after_kmalloc_array',
        'alloc_count_after_kmalloc_array_free',
        'slab_is_available',
    },
    'vsprintf': {'scnprintf_text', 'scnprintf_len', 'pad_text', 'pad_len'},
}

EXPECTED_PHASE1_MANIFEST_SHAPE = {
    'phase': 'Phase 1',
    'status': 'closed',
    'helper_count': 13,
    'helpers': {
        'tools/lib/argv_split.zig',
        'tools/lib/bitmap.zig',
        'tools/lib/cmdline.zig',
        'tools/lib/ctype.zig',
        'tools/lib/find_bit.zig',
        'tools/lib/hweight.zig',
        'tools/lib/list_sort.zig',
        'tools/lib/rbtree.zig',
        'tools/lib/slab.zig',
        'tools/lib/str_error_r.zig',
        'tools/lib/string.zig',
        'tools/lib/vsprintf.zig',
        'tools/lib/zalloc.zig',
    },
    'helper_review_notes': {
        'tools/lib/bitmap.zig': {
            'fixture',
            'evidence_keys',
            'summary',
            'unit_test_anchor',
            'unit_test_contract',
        },
        'tools/lib/find_bit.zig': {
            'fixture',
            'evidence_keys',
            'summary',
            'unit_test_anchor',
            'unit_test_contract',
            'set_unit_test_anchor',
            'set_unit_test_contract',
            'and_unit_test_anchor',
            'and_unit_test_contract',
            'boundary_unit_test_anchor',
            'boundary_unit_test_contract',
        },
        'tools/lib/rbtree.zig': {
            'fixture',
            'evidence_keys',
            'summary',
            'unit_test_anchor',
            'unit_test_contract',
            'search_unit_test_anchor',
            'search_unit_test_contract',
            'cached_unit_test_anchor',
            'cached_unit_test_contract',
            'cached_duplicate_unit_test_anchor',
            'cached_duplicate_unit_test_contract',
            'iterator_unit_test_anchor',
            'iterator_unit_test_contract',
            'reverse_unit_test_anchor',
            'reverse_unit_test_contract',
        },
        'tools/lib/string.zig': {
            'fixture',
            'evidence_keys',
            'summary',
            'unit_test_anchor',
            'unit_test_contract',
            'cstring_unit_test_anchor',
            'cstring_unit_test_contract',
            'alias_unit_test_anchor',
            'alias_unit_test_contract',
            'prefix_unit_test_anchor',
            'prefix_unit_test_contract',
            'suffix_unit_test_anchor',
            'suffix_unit_test_contract',
        },
    },
}


def validate_phase1_fixture_shape(path: Path) -> list[str]:
    issues: list[str] = []
    fixture = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(fixture, dict):
        return [f'phase1_fixture:expected_object:{path.relative_to(ROOT)}']

    actual_sections = set(fixture)
    expected_sections = set(EXPECTED_PHASE1_FIXTURE_SHAPE)

    for name in sorted(expected_sections - actual_sections):
        issues.append(f'phase1_fixture:missing_top_level:{name}')
    for name in sorted(actual_sections - expected_sections):
        issues.append(f'phase1_fixture:unexpected_top_level:{name}')

    for section_name, expected_keys in EXPECTED_PHASE1_FIXTURE_SHAPE.items():
        section = fixture.get(section_name)
        if section is None:
            continue
        if not isinstance(section, dict):
            issues.append(f'phase1_fixture:{section_name}:expected_object')
            continue
        actual_keys = set(section)
        for key in sorted(expected_keys - actual_keys):
            issues.append(f'phase1_fixture:{section_name}:missing_key:{key}')
        for key in sorted(actual_keys - expected_keys):
            issues.append(f'phase1_fixture:{section_name}:unexpected_key:{key}')

    return issues


def validate_phase1_manifest_shape(path: Path) -> list[str]:
    issues: list[str] = []
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(manifest, dict):
        return [f'phase1_manifest:expected_object:{path.relative_to(ROOT)}']

    if manifest.get('phase') != EXPECTED_PHASE1_MANIFEST_SHAPE['phase']:
        issues.append('phase1_manifest:phase:mismatch')
    if manifest.get('status') != EXPECTED_PHASE1_MANIFEST_SHAPE['status']:
        issues.append('phase1_manifest:status:mismatch')
    if manifest.get('helper_count') != EXPECTED_PHASE1_MANIFEST_SHAPE['helper_count']:
        issues.append('phase1_manifest:helper_count:mismatch')

    helpers = manifest.get('helpers')
    if not isinstance(helpers, list):
        issues.append('phase1_manifest:helpers:expected_list')
    else:
        actual_helpers = set(helpers)
        expected_helpers = EXPECTED_PHASE1_MANIFEST_SHAPE['helpers']
        for helper in sorted(expected_helpers - actual_helpers):
            issues.append(f'phase1_manifest:helpers:missing:{helper}')
        for helper in sorted(actual_helpers - expected_helpers):
            issues.append(f'phase1_manifest:helpers:unexpected:{helper}')
        if len(helpers) != len(actual_helpers):
            issues.append('phase1_manifest:helpers:duplicate_entries')

    review_notes = manifest.get('helper_review_notes')
    if not isinstance(review_notes, dict):
        issues.append('phase1_manifest:helper_review_notes:expected_object')
        return issues

    expected_notes = EXPECTED_PHASE1_MANIFEST_SHAPE['helper_review_notes']
    actual_note_helpers = set(review_notes)
    for helper in sorted(set(expected_notes) - actual_note_helpers):
        issues.append(f'phase1_manifest:helper_review_notes:missing_helper:{helper}')
    for helper in sorted(actual_note_helpers - set(expected_notes)):
        issues.append(f'phase1_manifest:helper_review_notes:unexpected_helper:{helper}')

    for helper, expected_fields in expected_notes.items():
        note = review_notes.get(helper)
        if note is None:
            continue
        if not isinstance(note, dict):
            issues.append(f'phase1_manifest:{helper}:expected_object')
            continue
        actual_fields = set(note)
        for field in sorted(expected_fields - actual_fields):
            issues.append(f'phase1_manifest:{helper}:missing_field:{field}')
        for field in sorted(actual_fields - expected_fields):
            issues.append(f'phase1_manifest:{helper}:unexpected_field:{field}')

        fixture = note.get('fixture')
        if fixture != 'zigux/tests/fixtures/phase1_helpers.json':
            issues.append(f'phase1_manifest:{helper}:fixture:mismatch')

        evidence_keys = note.get('evidence_keys')
        if not isinstance(evidence_keys, list) or not evidence_keys:
            issues.append(f'phase1_manifest:{helper}:evidence_keys:expected_nonempty_list')

    return issues

required_files = [
    ROOT / 'tools' / 'lib' / 'bitmap.zig',
    ROOT / 'tools' / 'lib' / 'find_bit.zig',
    ROOT / 'tools' / 'lib' / 'string.zig',
    ROOT / 'tools' / 'lib' / 'rbtree.zig',
    ROOT / 'tools' / 'lib' / 'argv_split.zig',
    ROOT / 'tools' / 'lib' / 'cmdline.zig',
    ROOT / 'tools' / 'lib' / 'ctype.zig',
    ROOT / 'tools' / 'lib' / 'hweight.zig',
    ROOT / 'tools' / 'lib' / 'list_sort.zig',
    ROOT / 'tools' / 'lib' / 'slab.zig',
    ROOT / 'tools' / 'lib' / 'str_error_r.zig',
    ROOT / 'tools' / 'lib' / 'vsprintf.zig',
    ROOT / 'tools' / 'lib' / 'zalloc.zig',
    ROOT / 'scripts' / 'zigux' / 'artifact_diff.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase1-bench.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase1-parity.py',
    ROOT / 'zigux' / 'tests' / 'build.zig',
    ROOT / 'zigux' / 'tests' / 'bitmap_diff.zig',
    ROOT / 'zigux' / 'tests' / 'bitmap_diff_build.zig',
    ROOT / 'zigux' / 'tests' / 'phase1_bench.zig',
    ROOT / 'zigux' / 'tests' / 'phase1_helpers.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_bench_expectations.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helpers_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helpers.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helper_manifest.json',
    ROOT / 'Documentation' / 'zigux' / 'phase1-closure.md',
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print('PHASE1_VALIDATION=fail')
    print('MISSING_PHASE1_FILES_START')
    for item in missing:
        print(item)
    print('MISSING_PHASE1_FILES_END')
    sys.exit(1)

fixture_shape_issues = validate_phase1_fixture_shape(
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helpers.json'
)
if fixture_shape_issues:
    print('PHASE1_VALIDATION=fail')
    print('MISSING_PHASE1_FIXTURE_SHAPE_START')
    for item in fixture_shape_issues:
        print(item)
    print('MISSING_PHASE1_FIXTURE_SHAPE_END')
    sys.exit(1)

manifest_shape_issues = validate_phase1_manifest_shape(
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helper_manifest.json'
)
if manifest_shape_issues:
    print('PHASE1_VALIDATION=fail')
    print('MISSING_PHASE1_MANIFEST_SHAPE_START')
    for item in manifest_shape_issues:
        print(item)
    print('MISSING_PHASE1_MANIFEST_SHAPE_END')
    sys.exit(1)

ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
tests_build = (ROOT / 'zigux' / 'tests' / 'build.zig').read_text(encoding='utf-8')
bitmap_root = (ROOT / 'tools' / 'lib' / 'bitmap.zig').read_text(encoding='utf-8')
string_root = (ROOT / 'tools' / 'lib' / 'string.zig').read_text(encoding='utf-8')
rbtree_root = (ROOT / 'tools' / 'lib' / 'rbtree.zig').read_text(encoding='utf-8')
phase1_bench_root = (ROOT / 'zigux' / 'tests' / 'phase1_bench.zig').read_text(encoding='utf-8')
test_root = (ROOT / 'zigux' / 'tests' / 'phase1_helpers.zig').read_text(encoding='utf-8')
bitmap_diff_root = (ROOT / 'zigux' / 'tests' / 'bitmap_diff.zig').read_text(encoding='utf-8')
bitmap_diff_build_root = (ROOT / 'zigux' / 'tests' / 'bitmap_diff_build.zig').read_text(encoding='utf-8')
phase1_closure = (ROOT / 'Documentation' / 'zigux' / 'phase1-closure.md').read_text(encoding='utf-8')
find_bit_fixture = (ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helpers.json').read_text(encoding='utf-8')
find_bit_harness = (ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helpers_c_harness.c').read_text(encoding='utf-8')
find_bit_manifest = (ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helper_manifest.json').read_text(encoding='utf-8')
phase1_bench_expectations = (ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_bench_expectations.json').read_text(encoding='utf-8')
find_bit_root = (ROOT / 'tools' / 'lib' / 'find_bit.zig').read_text(encoding='utf-8')

required_ledger_markers = [
    'feat(tools/lib): start phase-1 helper ports',
    'test(zigux): add phase-1 helper harness and workflow gate',
    'feat(tools/lib): expand phase-1 helper batch',
    'test(zigux): add phase-1 golden parity fixtures and artifact diff gate',
    'feat(tools/lib): complete bounded phase-1 helper coverage',
]
required_workflow_markers = [
    'tools/lib/*.zig',
    'python3 scripts/zigux/validate-phase1.py',
    'python3 scripts/zigux/check-phase1-bench.py',
    'python3 scripts/zigux/check-phase1-parity.py',
    'zig build bench --build-file zigux/tests/build.zig',
    'zig build test --build-file zigux/tests/build.zig',
    'zig build test --build-file zigux/tests/bitmap_diff_build.zig --summary all',
]
required_build_markers = [
    'phase1_bench.zig',
    'const bench_step = b.step("bench", "Run Phase 1 helper benchmark smoke");',
]
required_test_markers = [
    '@import("argv_split")',
    '@import("bitmap")',
    '@import("cmdline")',
    '@import("ctype")',
    '@import("find_bit")',
    '@import("hweight")',
    '@import("list_sort")',
    '@import("slab")',
    '@import("str_error_r")',
    '@import("string")',
    '@import("vsprintf")',
    '@import("zalloc")',
    '@import("rbtree")',
    '@embedFile("fixtures/phase1_helpers.json")',
]
required_bitmap_diff_markers = [
    '@import("bitmap")',
    '@import("find_bit")',
    'bitmap.copyClearTail',
    'bitmap.scnprintf',
]
required_bitmap_diff_build_markers = [
    'b.path("bitmap_diff.zig")',
    'diff_root.addImport("bitmap", bitmap_module)',
    'diff_root.addImport("find_bit", find_bit_module)',
]
required_bitmap_helper_markers = [
    'test "bitmap scnprintf truncates and keeps a terminator slot"',
    'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    'test "bitmap allocation helpers size zero fill and reset optionals"',
]
required_bitmap_test_markers = [
    'fixture.bitmap.scnprintf_trunc_len',
    'fixture.bitmap.scnprintf_trunc',
    'fixture.bitmap.scnprintf_empty_len',
    'fixture.bitmap.scnprintf_empty_bytes',
]
required_bitmap_harness_markers = [
    'unsigned long alloc_nbits = BITS_PER_LONG + 5;',
    'size_t empty_len = bitmap_scnprintf(empty_map, 8, empty_buffer, sizeof(empty_buffer));',
    'alloc_map = bitmap_alloc(alloc_nbits, 0);',
    'zero_map = bitmap_zalloc(alloc_nbits);',
    'printf("\\\"alloc_nbits\\\":%lu,", alloc_nbits);',
    'printf("\\\"scnprintf_empty_len\\\":%zu,", empty_len);',
    'printf("\\\"scnprintf_empty_bytes\\\":"); emit_word_array(empty_bytes, 4); printf(",");',
    'printf("\\\"scnprintf_trunc_len\\\":%zu,", trunc_len);',
    'printf("\\\"scnprintf_trunc\\\":\\\"%s\\\"", trunc_buffer);',
]
required_bitmap_manifest_markers = [
    '"tools/lib/bitmap.zig"',
    '"bitmap.alloc_nbits"',
    '"bitmap.alloc_values"',
    '"bitmap.scnprintf_empty_len"',
    '"bitmap.scnprintf_empty_bytes"',
    '"bitmap.scnprintf_trunc_len"',
    '"bitmap.scnprintf_trunc"',
    '"bitmap.zalloc_nbits"',
    '"bitmap.zalloc_values"',
    '"summary": "Committed C-backed parity coverage includes allocator-backed bitmap sizing, zero-allocation state, contiguous-range rendering, the empty-bitmap buffer-preservation contract, and truncation behavior that preserves the trailing terminator slot."',
    '"unit_test_anchor": "tools/lib/bitmap.zig:test \\\"bitmap allocation helpers size zero fill and reset optionals\\\""',
    '"unit_test_contract": "Direct Zig unit coverage keeps bitmapFree() honest by proving optional bitmap handles reset to null after release while allocator-backed bitmap sizing and zero-allocation state stay aligned with the committed C-backed fixture."',
]
required_bitmap_closure_markers = [
    'tools/lib/bitmap.zig` closure includes committed C-backed parity coverage for allocator-backed bitmap sizing, zero-allocation state, contiguous-range rendering, the empty-bitmap buffer-preservation contract, and the truncation path that must preserve a trailing terminator slot.',
    'tools/lib/bitmap.zig` direct Zig unit coverage now keeps `bitmapFree()` aligned by proving optional bitmap handles reset to null after release while the shared C-backed fixture covers allocator-backed sizing and zero-allocation state.',
    'bitmap direct unit-test anchor: `tools/lib/bitmap.zig:test "bitmap allocation helpers size zero fill and reset optionals"`',
    'bitmap empty-bitmap review note: `bitmap_scnprintf` must leave a non-empty caller buffer untouched when no bits are set, matching the C helper contract',
    'bitmap allocator review note: `bitmap_alloc()` and `bitmap_zalloc()` must size partial-word bitmaps through `BITS_TO_LONGS(nbits)`, while `bitmapFree()` optional-reset behavior remains direct Zig-only coverage because the C helper frees raw pointers in place',
    'PHASE1_BITMAP_FIXTURE=zigux/tests/fixtures/phase1_helpers.json',
    'PHASE1_BITMAP_REVIEW=bitmap parity covers allocator-backed sizing, zero-allocation state, contiguous-range rendering, empty-bitmap buffer preservation, and truncation that preserves the terminator slot',
    'PHASE1_BITMAP_UNIT_REVIEW=bitmap allocation helpers keep bitmapFree optional handles null after release while shared parity covers allocator-backed sizing and zero-allocation state',
]
required_bench_markers = [
    'PHASE1_BENCH=pass',
    'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=',
    'PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM=',
    'PHASE1_BENCH_STRING_CHECKSUM=',
    'PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM=',
]
required_bench_expectation_markers = [
    '"status": "pass"',
    '"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 2260000',
    '"PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM": 17862764',
    '"PHASE1_BENCH_STRING_CHECKSUM": 2500000',
    '"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 1384000',
]
required_find_bit_test_markers = [
    'fixture.find_bit.tail_clamped_first',
    'fixture.find_bit.tail_zero_clamped_first',
    'fixture.find_bit.tail_and_mixed_first',
    'find_bit.findFirstBit(&find_tail_window, find_tail_nbits)',
    'find_bit.findNextBit(&find_tail_window, find_tail_nbits, fixture.find_bit.bits_per_long + 4)',
    'find_bit.findFirstZeroBit(&find_tail_zero_window, find_tail_nbits)',
    'find_bit.findNextZeroBit(&find_tail_zero_window, find_tail_nbits, fixture.find_bit.bits_per_long)',
]
required_find_bit_helper_markers = [
    'test "find next zero bit skips earlier matches in the same word"',
    'test "empty and boundary scans return nbits"',
]
required_find_bit_fixture_markers = [
    '"tail_clamped_first"',
    '"tail_clamped_next"',
    '"tail_zero_clamped_first"',
    '"tail_zero_clamped_next"',
    '"tail_and_clamped_first"',
    '"tail_and_clamped_next"',
    '"tail_and_mixed_first"',
    '"tail_and_mixed_next"',
]
required_find_bit_harness_markers = [
    'tail_clamped_first',
    'tail_clamped_next',
    'tail_zero_clamped_first',
    'tail_zero_clamped_next',
    'tail_and_clamped_first',
    'tail_and_clamped_next',
    'tail_and_mixed_first',
    'tail_and_mixed_next',
    'find_first_and_bit(tail_and_mixed, tail_and_mixed, tail_nbits)',
    'find_next_and_bit(tail_and_mixed, tail_and_mixed, tail_nbits, BITS_PER_LONG + 4)',
]
required_find_bit_manifest_markers = [
    '"tools/lib/find_bit.zig"',
    '"find_bit.tail_clamped_first"',
    '"find_bit.tail_clamped_next"',
    '"find_bit.tail_zero_clamped_first"',
    '"find_bit.tail_zero_clamped_next"',
    '"find_bit.tail_and_clamped_first"',
    '"find_bit.tail_and_clamped_next"',
    '"find_bit.tail_and_mixed_first"',
    '"find_bit.tail_and_mixed_next"',
    'mixed-tail case where one shared bit remains in range while another lives past nbits.',
    '"boundary_unit_test_anchor": "tools/lib/find_bit.zig:test \\\"empty and boundary scans return nbits\\\""',
    '"boundary_unit_test_contract": "Direct Zig unit coverage keeps empty and out-of-range scan boundaries aligned by returning nbits for zero-length bitmaps, start-at-nbits searches, and fully set zero-bit windows that must not report past the declared range."',
]
required_find_bit_closure_markers = [
    'tools/lib/find_bit.zig` direct Zig unit coverage also keeps empty and out-of-range scan boundaries aligned by returning `nbits` for zero-length bitmaps, start-at-`nbits` searches, and fully set zero-bit windows that must not report past the declared range.',
    'find_bit boundary unit-test anchor: `tools/lib/find_bit.zig:test "empty and boundary scans return nbits"`',
    'PHASE1_FIND_BIT_BOUNDARY_UNIT_REVIEW=find_bit empty and out-of-range scans return nbits for zero-length bitmaps, start-at-nbits searches, and fully set zero-bit windows that must not report past the declared range',
]
required_string_helper_markers = [
    'pub fn strim(buf: []u8) []u8 {',
    'pub fn strreplace(buf: []u8, old: u8, new: u8) []u8 {',
    'test "skip trim remove and replace spaces work in place"',
    'test "strlcpy stops at the first embedded NUL in the source"',
    'test "strstarts matches kernel prefix semantics"',
    'test "str_ends_with matches kernel suffix semantics"',
    'test "memchrInv scans aligned and misaligned long buffers"',
    'test "memchrInv catches prefix and trailing remainder mismatches"',
]
required_string_test_markers = [
    'test "phase 1 string replaceChar stops at embedded NUL"',
    'fixture.string.remove_spaces_nul',
    'fixture.string.remove_spaces_nul_bytes',
    "string.removeSpaces(remove_nul_buffer[0 .. remove_nul_buffer.len - 1])",
    "string.replaceChar(&replace_buffer, '-', '_')",
    "&[_]u8{ 'a', '_', 0, '-', 'z' }",
]
required_string_fixture_markers = [
    '"remove_spaces_nul"',
    '"remove_spaces_nul_bytes"',
    '[97,98,0,0,32,120]',
]
required_string_harness_markers = [
    "char remove_nul_buf[] = {'a', ' ', 'b', 0, ' ', 'x'};",
    'remove_spaces(remove_nul_buf);',
    '\\\"remove_spaces_nul\\\":',
    '\\\"remove_spaces_nul_bytes\\\":',
]
required_string_manifest_markers = [
    '"tools/lib/string.zig"',
    '"string.remove_spaces_nul"',
    '"string.remove_spaces_nul_bytes"',
    '"summary": "Committed C-backed parity coverage includes Linux-style bool parsing for true, false, and invalid forms, C-string-aware strlcpy length and truncation behavior, in-place whitespace and replacement helpers including embedded-NUL remove_spaces handling, and first-mismatch memchrInv detection."',
    '"cstring_unit_test_anchor": "tools/lib/string.zig:test \\\"strlcpy stops at the first embedded NUL in the source\\\""',
    '"cstring_unit_test_contract": "Direct Zig unit coverage keeps strlcpy aligned with C-string semantics by stopping at the first embedded NUL, preserving truncation behavior, and leaving zero-sized destinations untouched."',
    '"unit_test_anchor": "tools/lib/string.zig:test \\\"memchrInv scans aligned and misaligned long buffers\\\""',
    '"unit_test_contract": "Direct Zig unit coverage keeps memchrInv honest for both aligned and misaligned long buffers beyond the short C-backed fixture cases."',
    '"alias_unit_test_anchor": "tools/lib/string.zig:test \\\"trimSpaces and strim trim trailing whitespace before an embedded NUL\\\""',
    '"alias_unit_test_contract": "Direct Zig unit coverage keeps trimSpaces and strim aligned with C-string semantics by trimming trailing whitespace that appears before the first embedded NUL while preserving bytes beyond that terminator."',
    '"prefix_unit_test_anchor": "tools/lib/string.zig:test \\\"strstarts matches kernel prefix semantics\\\""',
    '"prefix_unit_test_contract": "Direct Zig unit coverage keeps strStarts and strstarts aligned with kernel-style prefix semantics for exact, empty-prefix, shorter-input, and case-sensitive comparisons."',
    '"suffix_unit_test_anchor": "tools/lib/string.zig:test \\\"str_ends_with matches kernel suffix semantics\\\""',
    '"suffix_unit_test_contract": "Direct Zig unit coverage keeps strEndsWith and str_ends_with aligned with kernel-style suffix semantics for exact, empty-suffix, shorter-input, and case-sensitive comparisons."',
]
required_string_closure_markers = [
    'string c-string unit-test anchor: `tools/lib/string.zig:test "strlcpy stops at the first embedded NUL in the source"`',
    'PHASE1_STRING_REVIEW=string parity covers Linux-style bool parsing for true, false, and invalid forms, C-string-aware strlcpy length and truncation behavior, whitespace cleanup including embedded-NUL remove_spaces handling, replacement, and memchrInv mismatch detection',
    'PHASE1_STRING_CSTRING_UNIT_REVIEW=string strlcpy stops at the first embedded NUL, preserves truncation behavior, and leaves zero-sized destinations untouched',
    'string direct unit-test anchor: `tools/lib/string.zig:test "memchrInv scans aligned and misaligned long buffers"`',
    'string alias unit-test anchor: `tools/lib/string.zig:test "trimSpaces and strim trim trailing whitespace before an embedded NUL"`',
    'string prefix unit-test anchor: `tools/lib/string.zig:test "strstarts matches kernel prefix semantics"`',
    'string suffix unit-test anchor: `tools/lib/string.zig:test "str_ends_with matches kernel suffix semantics"`',
    'PHASE1_STRING_UNIT_REVIEW=string memchrInv aligned and misaligned long-buffer scans stay consistent beyond the short C-backed fixture cases',
    'PHASE1_STRING_ALIAS_UNIT_REVIEW=string trimSpaces and strim trim trailing whitespace before the first embedded NUL while preserving bytes beyond that terminator',
    'PHASE1_STRING_PREFIX_UNIT_REVIEW=string strStarts and strstarts keep kernel-style prefix checks aligned for exact, empty-prefix, shorter-input, and case-sensitive comparisons',
    'PHASE1_STRING_SUFFIX_UNIT_REVIEW=string strEndsWith and str_ends_with keep kernel-style suffix checks aligned for exact, empty-suffix, shorter-input, and case-sensitive comparisons',
]
required_rbtree_helper_markers = [
    'pub fn find(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {',
    'pub fn findFirst(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {',
    'pub fn findLast(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {',
    'pub fn nextMatch(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {',
    'pub fn prevMatch(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {',
    'pub fn iterateMatches(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {',
    'pub fn iterateMatchesReverse(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ReverseMatchIterator {',
    'pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {',
    'test "rbtree nextMatch walks the duplicate range in order"',
    'test "rbtree prevMatch walks the duplicate range in reverse order"',
    'test "rbtree cached root keeps leftmost in sync across add erase and replace"',
    'test "rbtree cached root tracks duplicate minima through erase and non-leftmost replace"',
    'test "rbtree iterateMatches streams only the duplicate range"',
    'test "rbtree iterateMatchesReverse streams only the duplicate range in reverse"',
    'test "rbtree duplicate search stays aligned after erase and same-key replace"',
]
required_rbtree_manifest_markers = [
    '"tools/lib/rbtree.zig"',
    '"summary": "Committed C-backed parity coverage includes ordered forward and reverse traversal plus replaceNode, eraseInit, postorder traversal, and detached-node state checks."',
    '"unit_test_anchor": "tools/lib/rbtree.zig:test \\\"rbtree findAdd keeps the first duplicate and inserts new keys\\\""',
    '"unit_test_contract": "Direct Zig unit coverage keeps findAdd duplicate handling aligned so the first equal key stays resident while new distinct keys still link into the tree."',
    '"search_unit_test_anchor": "tools/lib/rbtree.zig:test \\\"rbtree nextMatch walks the duplicate range in order\\\""',
    '"search_unit_test_contract": "Direct Zig unit coverage keeps find(), findFirst(), and nextMatch() aligned so duplicate-key lookups start at the leftmost match and walk through the final equal node without drifting into a later key."',
    '"cached_unit_test_anchor": "tools/lib/rbtree.zig:test \\\"rbtree cached root keeps leftmost in sync across add erase and replace\\\""',
    '"cached_unit_test_contract": "Direct Zig unit coverage keeps RootCached leftmost tracking aligned so addCached(), eraseCached(), and replaceNodeCached() continue to expose the same first node as the underlying tree root."',
    '"cached_duplicate_unit_test_anchor": "tools/lib/rbtree.zig:test \\\"rbtree cached root tracks duplicate minima through erase and non-leftmost replace\\\""',
    '"cached_duplicate_unit_test_contract": "Direct Zig unit coverage keeps RootCached duplicate minima aligned so eraseCached() promotes the next equal-key minimum and replaceNodeCached() leaves the cached first node unchanged when a non-leftmost node is replaced."',
    '"iterator_unit_test_anchor": "tools/lib/rbtree.zig:test \\\"rbtree iterateMatches streams only the duplicate range\\\""',
    '"iterator_unit_test_contract": "Direct Zig unit coverage keeps iterateMatches() aligned so duplicate-key iteration yields only the equal-key range and cleanly reports no match for missing keys."',
    '"reverse_unit_test_anchor": "tools/lib/rbtree.zig:test \\\"rbtree iterateMatchesReverse streams only the duplicate range in reverse\\\""',
    '"reverse_unit_test_contract": "Direct Zig unit coverage keeps findLast(), prevMatch(), and iterateMatchesReverse() aligned so reverse duplicate-key lookups start at the rightmost match, walk back through the equal-key range, and cleanly report no match for missing keys."',
]
required_rbtree_closure_markers = [
    'tools/lib/rbtree.zig` closure includes committed C-backed parity coverage for ordered forward and reverse traversal plus `replaceNode`, `eraseInit`, postorder traversal, and detached-node state checks.',
    'tools/lib/rbtree.zig` direct Zig unit coverage keeps `findAdd` duplicate handling aligned so the first equal key stays resident while new distinct keys still link into the tree.',
    'tools/lib/rbtree.zig` direct Zig unit coverage also keeps `find()`, `findFirst()`, and `nextMatch()` aligned so duplicate-key lookups start at the leftmost match and walk through the final equal node without drifting into a later key.',
    'tools/lib/rbtree.zig` direct Zig unit coverage also keeps `RootCached` leftmost tracking aligned so cached insert, erase, and replace helpers continue to expose the same first node as the underlying tree root.',
    'tools/lib/rbtree.zig` direct Zig unit coverage also keeps `RootCached` duplicate minima aligned so erasing the first equal key promotes the next duplicate minimum while non-leftmost replacement leaves the cached first node unchanged.',
    'tools/lib/rbtree.zig` direct Zig unit coverage also keeps `iterateMatches()` aligned so duplicate-key iteration yields only the equal-key range and cleanly reports no match for missing keys.',
    'tools/lib/rbtree.zig` direct Zig unit coverage also keeps `findLast()`, `prevMatch()`, and `iterateMatchesReverse()` aligned so reverse duplicate-key lookups start at the rightmost match, walk back through the equal-key range, and cleanly report no match for missing keys.',
    'rbtree direct unit-test anchor: `tools/lib/rbtree.zig:test "rbtree findAdd keeps the first duplicate and inserts new keys"`',
    'rbtree search unit-test anchor: `tools/lib/rbtree.zig:test "rbtree nextMatch walks the duplicate range in order"`',
    'rbtree cached-root unit-test anchor: `tools/lib/rbtree.zig:test "rbtree cached root keeps leftmost in sync across add erase and replace"`',
    'rbtree cached duplicate-minima unit-test anchor: `tools/lib/rbtree.zig:test "rbtree cached root tracks duplicate minima through erase and non-leftmost replace"`',
    'rbtree iterator unit-test anchor: `tools/lib/rbtree.zig:test "rbtree iterateMatches streams only the duplicate range"`',
    'rbtree reverse unit-test anchor: `tools/lib/rbtree.zig:test "rbtree iterateMatchesReverse streams only the duplicate range in reverse"`',
    'PHASE1_RBTREE_REVIEW=rbtree parity covers ordered traversal, replaceNode, eraseInit, postorder traversal, and detached-node state',
    'PHASE1_RBTREE_UNIT_REVIEW=rbtree findAdd keeps the first equal key resident while new distinct keys still link into the tree',
    'PHASE1_RBTREE_SEARCH_UNIT_REVIEW=rbtree find, findFirst, and nextMatch keep duplicate-key lookup walks aligned from the leftmost match through the final equal node',
    'PHASE1_RBTREE_CACHED_UNIT_REVIEW=rbtree RootCached leftmost tracking stays aligned across addCached, eraseCached, and replaceNodeCached so the cached first node matches the underlying tree root',
    'PHASE1_RBTREE_CACHED_DUPLICATE_UNIT_REVIEW=rbtree RootCached duplicate minima stay aligned when eraseCached promotes the next equal-key minimum and replaceNodeCached leaves the cached first node unchanged for non-leftmost replacement',
    'PHASE1_RBTREE_ITERATE_UNIT_REVIEW=rbtree iterateMatches yields only the equal-key duplicate range and cleanly reports no match for missing keys',
    'PHASE1_RBTREE_REVERSE_UNIT_REVIEW=rbtree findLast, prevMatch, and iterateMatchesReverse keep reverse duplicate-key lookup walks aligned from the rightmost match back through the equal-key range while still reporting no match for missing keys',
]

missing_markers = []
for marker in required_ledger_markers:
    if marker not in ledger:
        missing_markers.append(f'ledger:{marker}')
for marker in required_workflow_markers:
    if marker not in workflow:
        missing_markers.append(f'workflow:{marker}')
for marker in required_build_markers:
    if marker not in tests_build:
        missing_markers.append(f'build:{marker}')
for marker in required_test_markers:
    if marker not in test_root:
        missing_markers.append(f'test:{marker}')
for marker in required_bitmap_diff_markers:
    if marker not in bitmap_diff_root:
        missing_markers.append(f'bitmap_diff:{marker}')
for marker in required_bitmap_diff_build_markers:
    if marker not in bitmap_diff_build_root:
        missing_markers.append(f'bitmap_diff_build:{marker}')
for marker in required_bitmap_helper_markers:
    if marker not in bitmap_root:
        missing_markers.append(f'bitmap_helper:{marker}')
for marker in required_bitmap_test_markers:
    if marker not in test_root:
        missing_markers.append(f'bitmap_test:{marker}')
for marker in required_bitmap_harness_markers:
    if marker not in find_bit_harness:
        missing_markers.append(f'bitmap_harness:{marker}')
for marker in required_bitmap_manifest_markers:
    if marker not in find_bit_manifest:
        missing_markers.append(f'bitmap_manifest:{marker}')
for marker in required_bitmap_closure_markers:
    if marker not in phase1_closure:
        missing_markers.append(f'bitmap_closure:{marker}')
for marker in required_bench_markers:
    if marker not in phase1_bench_root:
        missing_markers.append(f'bench:{marker}')
for marker in required_bench_expectation_markers:
    if marker not in phase1_bench_expectations:
        missing_markers.append(f'bench_expectations:{marker}')
for marker in required_find_bit_test_markers:
    if marker not in test_root:
        missing_markers.append(f'find_bit_test:{marker}')
for marker in required_find_bit_helper_markers:
    if marker not in find_bit_root:
        missing_markers.append(f'find_bit_helper:{marker}')
for marker in required_find_bit_fixture_markers:
    if marker not in find_bit_fixture:
        missing_markers.append(f'find_bit_fixture:{marker}')
for marker in required_find_bit_harness_markers:
    if marker not in find_bit_harness:
        missing_markers.append(f'find_bit_harness:{marker}')
for marker in required_find_bit_manifest_markers:
    if marker not in find_bit_manifest:
        missing_markers.append(f'find_bit_manifest:{marker}')
for marker in required_find_bit_closure_markers:
    if marker not in phase1_closure:
        missing_markers.append(f'find_bit_closure:{marker}')
for marker in required_string_helper_markers:
    if marker not in string_root:
        missing_markers.append(f'string_helper:{marker}')
for marker in required_rbtree_helper_markers:
    if marker not in rbtree_root:
        missing_markers.append(f'rbtree_helper:{marker}')
for marker in required_string_test_markers:
    if marker not in test_root:
        missing_markers.append(f'string_test:{marker}')
for marker in required_string_fixture_markers:
    if marker not in find_bit_fixture:
        missing_markers.append(f'string_fixture:{marker}')
for marker in required_string_harness_markers:
    if marker not in find_bit_harness:
        missing_markers.append(f'string_harness:{marker}')
for marker in required_string_manifest_markers:
    if marker not in find_bit_manifest:
        missing_markers.append(f'string_manifest:{marker}')
for marker in required_rbtree_manifest_markers:
    if marker not in find_bit_manifest:
        missing_markers.append(f'rbtree_manifest:{marker}')
for marker in required_string_closure_markers:
    if marker not in phase1_closure:
        missing_markers.append(f'string_closure:{marker}')
for marker in required_rbtree_closure_markers:
    if marker not in phase1_closure:
        missing_markers.append(f'rbtree_closure:{marker}')

if missing_markers:
    print('PHASE1_VALIDATION=fail')
    print('MISSING_PHASE1_MARKERS_START')
    for marker in missing_markers:
        print(marker)
    print('MISSING_PHASE1_MARKERS_END')
    sys.exit(1)

print('PHASE1_VALIDATION=pass')
print(f'PHASE1_REQUIRED_FILE_COUNT={len(required_files)}')
print(
    'PHASE1_REQUIRED_MARKER_COUNT='
    f'{len(required_ledger_markers) + len(required_workflow_markers) + len(required_build_markers) + len(required_test_markers) + len(required_bitmap_diff_markers) + len(required_bitmap_diff_build_markers) + len(required_bitmap_helper_markers) + len(required_bitmap_test_markers) + len(required_bitmap_harness_markers) + len(required_bitmap_manifest_markers) + len(required_bitmap_closure_markers) + len(required_bench_markers) + len(required_bench_expectation_markers) + len(required_find_bit_test_markers) + len(required_find_bit_helper_markers) + len(required_find_bit_fixture_markers) + len(required_find_bit_harness_markers) + len(required_find_bit_manifest_markers) + len(required_find_bit_closure_markers) + len(required_string_helper_markers) + len(required_rbtree_helper_markers) + len(required_string_test_markers) + len(required_string_fixture_markers) + len(required_string_harness_markers) + len(required_string_manifest_markers) + len(required_rbtree_manifest_markers) + len(required_string_closure_markers) + len(required_rbtree_closure_markers)}'
)

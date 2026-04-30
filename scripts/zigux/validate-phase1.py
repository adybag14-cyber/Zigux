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
            'range_unit_test_anchor',
            'range_unit_test_contract',
            'copy_unit_test_anchor',
            'copy_unit_test_contract',
            'bitwise_unit_test_anchor',
            'bitwise_unit_test_contract',
            'tail_mask_unit_test_anchor',
            'tail_mask_unit_test_contract',
            'zero_bit_unit_test_anchor',
            'zero_bit_unit_test_contract',
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
            'mask_unit_test_anchor',
            'mask_unit_test_contract',
            'boundary_unit_test_anchor',
            'boundary_unit_test_contract',
            'alias_unit_test_anchor',
            'alias_unit_test_contract',
        },
        'tools/lib/rbtree.zig': {
            'fixture',
            'evidence_keys',
            'summary',
            'unit_test_anchor',
            'unit_test_contract',
            'search_unit_test_anchor',
            'search_unit_test_contract',
            'duplicate_search_unit_test_anchor',
            'duplicate_search_unit_test_contract',
            'cached_unit_test_anchor',
            'cached_unit_test_contract',
            'cached_duplicate_unit_test_anchor',
            'cached_duplicate_unit_test_contract',
            'cached_find_add_unit_test_anchor',
            'cached_find_add_unit_test_contract',
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
            'equality_unit_test_anchor',
            'equality_unit_test_contract',
            'alias_unit_test_anchor',
            'alias_unit_test_contract',
            'prefix_unit_test_anchor',
            'prefix_unit_test_contract',
            'prefix_length_unit_test_anchor',
            'prefix_length_unit_test_contract',
            'suffix_unit_test_anchor',
            'suffix_unit_test_contract',
            'memparse_unit_test_anchor',
            'memparse_unit_test_contract',
        },
    },
    'helper_review_evidence_keys': {
        'tools/lib/bitmap.zig': {
            'bitmap.weight',
            'bitmap.alloc_nbits',
            'bitmap.alloc_values',
            'bitmap.scnprintf',
            'bitmap.scnprintf_empty_len',
            'bitmap.scnprintf_empty_bytes',
            'bitmap.scnprintf_trunc_len',
            'bitmap.scnprintf_trunc',
            'bitmap.zalloc_nbits',
            'bitmap.zalloc_values',
            'bitmap.and_result',
            'bitmap.and_values',
            'bitmap.andnot_result',
            'bitmap.andnot_values',
            'bitmap.or_values',
            'bitmap.xor_values',
            'bitmap.copy_nbits',
            'bitmap.copy_values',
            'bitmap.partial_xor_nbits',
            'bitmap.partial_xor_masked_values',
            'bitmap.equal',
            'bitmap.intersects',
            'bitmap.subset',
            'bitmap.range_after_set',
            'bitmap.range_after_clear',
            'bitmap.full_after_fill',
            'bitmap.empty_after_zero',
        },
        'tools/lib/find_bit.zig': {
            'find_bit.first',
            'find_bit.next_after_6',
            'find_bit.next_after_word',
            'find_bit.first_zero',
            'find_bit.next_zero',
            'find_bit.first_and',
            'find_bit.next_and',
            'find_bit.tail_clamped_first',
            'find_bit.tail_clamped_next',
            'find_bit.tail_zero_clamped_first',
            'find_bit.tail_zero_clamped_next',
            'find_bit.tail_and_clamped_first',
            'find_bit.tail_and_clamped_next',
            'find_bit.tail_and_mixed_first',
            'find_bit.tail_and_mixed_next',
        },
        'tools/lib/rbtree.zig': {
            'rbtree.empty_root',
            'rbtree.insert_order',
            'rbtree.reverse_order',
            'rbtree.replace_order',
            'rbtree.erase_init_order',
            'rbtree.postorder_count',
            'rbtree.erase_init_node_empty',
            'rbtree.cleared_node_empty',
        },
        'tools/lib/string.zig': {
            'string.strtobool_y',
            'string.strtobool_on',
            'string.strtobool_zero',
            'string.strtobool_off',
            'string.strtobool_invalid',
            'string.strlcpy_len',
            'string.strlcpy_buffer',
            'string.skip_spaces',
            'string.trim_spaces',
            'string.remove_spaces',
            'string.remove_spaces_nul',
            'string.remove_spaces_nul_bytes',
            'string.replace_char',
            'string.replace_char_end',
            'string.memchr_inv_index',
            'string.memchr_inv_none',
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
    expected_evidence_keys = EXPECTED_PHASE1_MANIFEST_SHAPE['helper_review_evidence_keys']
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
            continue

        actual_evidence_keys = set(evidence_keys)
        for key in sorted(expected_evidence_keys[helper] - actual_evidence_keys):
            issues.append(f'phase1_manifest:{helper}:evidence_keys:missing:{key}')
        for key in sorted(actual_evidence_keys - expected_evidence_keys[helper]):
            issues.append(f'phase1_manifest:{helper}:evidence_keys:unexpected:{key}')
        if len(evidence_keys) != len(actual_evidence_keys):
            issues.append(f'phase1_manifest:{helper}:evidence_keys:duplicate_entries')

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
    ROOT / 'scripts' / 'zigux' / 'install-zig.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase1-closure.py',
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
    'FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true',
    'uses: actions/checkout@v6.0.2',
    'uses: actions/setup-python@v6.2.0',
    'tools/lib/*.zig',
    'python3 scripts/zigux/install-zig.py --dest .zig-toolchain',
    'python3 scripts/zigux/validate-phase1.py',
    'python3 scripts/zigux/validate-phase1-closure.py',
    'python3 scripts/zigux/check-phase1-bench.py',
    'python3 scripts/zigux/check-phase1-parity.py',
    'zig build bench --build-file zigux/tests/build.zig',
    'zig build test --build-file zigux/tests/build.zig',
    'zig build test --build-file zigux/tests/bitmap_diff_build.zig --summary all',
]
required_phase1_closure_gate_markers = [
    'PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py',
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
    '"bitmap.weight"',
    '"bitmap.alloc_nbits"',
    '"bitmap.alloc_values"',
    '"bitmap.scnprintf"',
    '"bitmap.scnprintf_empty_len"',
    '"bitmap.scnprintf_empty_bytes"',
    '"bitmap.scnprintf_trunc_len"',
    '"bitmap.scnprintf_trunc"',
    '"bitmap.zalloc_nbits"',
    '"bitmap.zalloc_values"',
    '"bitmap.and_result"',
    '"bitmap.and_values"',
    '"bitmap.andnot_result"',
    '"bitmap.andnot_values"',
    '"bitmap.or_values"',
    '"bitmap.xor_values"',
    '"bitmap.copy_nbits"',
    '"bitmap.copy_values"',
    '"bitmap.partial_xor_nbits"',
    '"bitmap.partial_xor_masked_values"',
    '"bitmap.equal"',
    '"bitmap.intersects"',
    '"bitmap.subset"',
    '"bitmap.range_after_set"',
    '"bitmap.range_after_clear"',
    '"bitmap.full_after_fill"',
    '"bitmap.empty_after_zero"',
    '"summary": "Committed C-backed parity coverage includes allocator-backed bitmap sizing, zero-allocation state, tail-sensitive bitwise and copy replay, range set and clear behavior, contiguous-range rendering, the empty-bitmap buffer-preservation contract, and truncation behavior that preserves the trailing terminator slot."',
    '"unit_test_anchor": "tools/lib/bitmap.zig:test \\\"bitmap allocation helpers size zero fill and reset optionals\\\""',
    '"unit_test_contract": "Direct Zig unit coverage keeps bitmapAlloc(), bitmapZalloc(), and bitmapFree() honest by proving optional bitmap handles size through bitsToWords(), zero-filled allocation stays intact, and released optionals reset to null."',
    '"range_unit_test_anchor": "tools/lib/bitmap.zig:test \\\"bitmap range helpers preserve edges across whole-word spans\\\""',
    '"range_unit_test_contract": "Direct Zig unit coverage keeps cross-word setRange() and clearRange() aligned by preserving the first-word start mask, fully covering interior words, clamping the last word, and restoring the whole window to zero on clear."',
    '"copy_unit_test_anchor": "tools/lib/bitmap.zig:test \\\"bitmap copyClearTail clears out-of-range bits in the last copied word\\\""',
    '"copy_unit_test_contract": "Direct Zig unit coverage keeps copy() and copyClearTail() aligned by preserving copied source words while forcing tail bits above nbits back to zero in the final copied word."',
    '"bitwise_unit_test_anchor": "tools/lib/bitmap.zig:test \\\"bitmap and andnot equal intersects subset\\\""',
    '"bitwise_unit_test_contract": "Direct Zig unit coverage keeps andBits(), andNotBits(), xorBits(), equal(), intersects(), and subset() aligned on the shared caller-selected bit window instead of leaking unrelated tail bits."',
    '"zero_bit_unit_test_anchor": "tools/lib/bitmap.zig:test \\\"bitmap zero-bit helpers stay explicit no-ops\\\""',
    '"zero_bit_unit_test_contract": "Direct Zig unit coverage keeps zero-length helper calls side-effect free so zero(), fill(), copy(), copyClearTail(), orBits(), xorBits(), scans, and formatting all leave caller-owned buffers untouched when nbits is zero."',
]
required_bitmap_closure_markers = [
    'tools/lib/bitmap.zig` closure includes committed C-backed parity coverage for allocator-backed bitmap sizing, zero-allocation state, contiguous-range rendering, the empty-bitmap buffer-preservation contract, and the truncation path that must preserve the terminator slot.',
    'tools/lib/bitmap.zig` direct Zig unit coverage now keeps `bitmapFree()` aligned by proving optional bitmap handles reset to null after release while the shared C-backed fixture covers allocator-backed sizing and zero-allocation state.',
    'tools/lib/bitmap.zig` direct Zig unit coverage also keeps tail-masked reduction helpers aligned so `andBits()`, `andNotBits()`, `equal()`, `intersects()`, and `subset()` ignore out-of-range tail differences while preserving the in-range window.',
    'tools/lib/bitmap.zig` closure includes committed C-backed parity coverage for allocator-backed bitmap sizing, zero-allocation state, contiguous-range rendering, the empty-bitmap buffer-preservation contract, and the truncation path that must preserve the trailing terminator slot.',
    'tools/lib/bitmap.zig` direct Zig unit coverage keeps `bitmapAlloc()`, `bitmapZalloc()`, and `bitmapFree()` honest by proving optional bitmap handles size through `bitsToWords()`, zero-filled allocation stays intact, and released optionals reset to `null`.',
    'tools/lib/bitmap.zig` direct Zig unit coverage also keeps zero-length helper calls explicit and side-effect free so `zero()`, `fill()`, `copy()`, `copyClearTail()`, `orBits()`, `xorBits()`, scans, and formatting all leave caller-owned buffers untouched when `nbits` is zero.',
    'bitmap range unit-test anchor: `tools/lib/bitmap.zig:test "bitmap range helpers preserve edges across whole-word spans"`',
    'bitmap copy unit-test anchor: `tools/lib/bitmap.zig:test "bitmap copyClearTail clears out-of-range bits in the last copied word"`',
    'bitmap bitwise unit-test anchor: `tools/lib/bitmap.zig:test "bitmap and andnot equal intersects subset"`',
    'bitmap fixture authority: `zigux/tests/fixtures/phase1_helpers.json`',
    'bitmap manifest review anchor: `zigux/tests/fixtures/phase1_helper_manifest.json`',
    'bitmap direct unit-test anchor: `tools/lib/bitmap.zig:test "bitmap allocation helpers size zero fill and reset optionals"`',
    'bitmap tail-mask unit-test anchor: `tools/lib/bitmap.zig:test "bitmap tail-masked helpers ignore out-of-range differences"`',
    'bitmap zero-bit unit-test anchor: `tools/lib/bitmap.zig:test "bitmap zero-bit helpers stay explicit no-ops"`',
    'bitmap empty-bitmap review note: `bitmap_scnprintf` must leave a non-empty caller buffer untouched when no bits are set, matching the C helper contract',
    'bitmap allocator review note: `bitmap_alloc()` and `bitmap_zalloc()` must size partial-word bitmaps through `BITS_TO_LONGS(nbits)`, while `bitmapFree()` optional-reset behavior remains direct Zig-only coverage because the C helper frees raw pointers in place',
    'PHASE1_BITMAP_FIXTURE=zigux/tests/fixtures/phase1_helpers.json',
    'PHASE1_BITMAP_REVIEW=bitmap parity covers allocator-backed sizing, zero-allocation state, contiguous-range rendering, empty-bitmap buffer preservation, and truncation that preserves the terminator slot',
    'PHASE1_BITMAP_UNIT_REVIEW=bitmap allocation helpers keep bitmapFree optional handles null after release while shared parity covers allocator-backed sizing and zero-allocation state',
    'PHASE1_BITMAP_TAIL_MASK_UNIT_REVIEW=bitmap tail-masked reduction helpers ignore out-of-range differences while preserving the in-range window for andBits, andNotBits, equal, intersects, and subset',
    'PHASE1_BITMAP_ZERO_BIT_UNIT_REVIEW=bitmap zero-length helper calls stay side-effect free so zero fill copy copyClearTail orBits xorBits scans and formatting leave caller-owned buffers untouched when nbits is zero',
]
required_bench_markers = [
    'pub fn main(init: std.process.Init) !void {',
    'const bitmap_result = bitmapBench();',
    'const find_bit_result = findBitBench();',
    'const find_zero_bit_result = findZeroBitBench();',
    'const find_and_bit_result = findAndBitBench();',
    'const rbtree_result = rbtreeBench();',
    'PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM',
    'PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM',
    'PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM',
    'PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM',
    'PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS',
    'PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM',
    'PHASE1_BENCH_RBTREE_CACHED_CHECKSUM',
    'PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM',
]
required_bench_expectation_markers = [
    'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM',
    'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM',
    'PHASE1_BENCH_BITMAP_COPY_CHECKSUM',
    'PHASE1_BENCH_BITMAP_SCNPRINTF_CHECKSUM',
    'PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM',
    'PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM',
    'PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM',
    'PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM',
    'PHASE1_BENCH_FIND_NEXT_ZERO_BIT_CHECKSUM',
    'PHASE1_BENCH_FIND_NEXT_AND_BIT_CHECKSUM',
    'PHASE1_BENCH_STRING_CHECKSUM',
    'PHASE1_BENCH_RBTREE_CHECKSUM',
    'PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM',
    'PHASE1_BENCH_RBTREE_CACHED_CHECKSUM',
    'PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM',
    'PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS',
]
required_find_bit_test_markers = [
    'fixture.find_bit.tail_clamped_first',
    'fixture.find_bit.tail_clamped_next',
    'fixture.find_bit.tail_zero_clamped_first',
    'fixture.find_bit.tail_zero_clamped_next',
    'fixture.find_bit.tail_and_clamped_first',
    'fixture.find_bit.tail_and_clamped_next',
    'fixture.find_bit.tail_and_mixed_first',
    'fixture.find_bit.tail_and_mixed_next',
]
required_find_bit_helper_markers = [
    'pub fn findFirstBit(addr: []const Word, nbits: usize) usize {',
    'pub fn findFirstAndBit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {',
    'pub fn findFirstZeroBit(addr: []const Word, nbits: usize) usize {',
    'pub fn findNextBit(addr: []const Word, nbits: usize, start: usize) usize {',
    'pub fn findNextAndBit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {',
    'pub fn findNextZeroBit(addr: []const Word, nbits: usize, start: usize) usize {',
    'pub fn find_first_bit(addr: []const Word, nbits: usize) usize {',
    'pub fn find_first_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {',
    'pub fn find_first_zero_bit(addr: []const Word, nbits: usize) usize {',
    'pub fn find_next_bit(addr: []const Word, nbits: usize, start: usize) usize {',
    'pub fn find_next_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {',
    'pub fn find_next_zero_bit(addr: []const Word, nbits: usize, start: usize) usize {',
    'test "find next bit skips earlier matches in the same word"',
    'test "find next and bit skips earlier shared matches in the same word"',
    'test "empty and boundary scans return nbits"',
    'test "find underscore aliases preserve scan semantics"',
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
    'unsigned long tail_bitmap[2] = {0, 1UL << 9};',
    'unsigned long tail_zero_bitmap[2] = {~0UL, BITMAP_LAST_WORD_MASK(BITS_PER_LONG + 5)};',
    'unsigned long tail_and_mixed[2] = {0, (1UL << 3) | (1UL << 9)};',
    '\\"tail_clamped_first\\":%lu,',
    '\\"tail_clamped_next\\":%lu,',
    '\\"tail_zero_clamped_first\\":%lu,',
    '\\"tail_zero_clamped_next\\":%lu,',
    '\\"tail_and_clamped_first\\":%lu,',
    '\\"tail_and_clamped_next\\":%lu,',
    '\\"tail_and_mixed_first\\":%lu,',
    '\\"tail_and_mixed_next\\":%lu',
]
required_find_bit_manifest_markers = [
    '"tools/lib/find_bit.zig"',
    '"find_bit.first"',
    '"find_bit.next_after_6"',
    '"find_bit.next_after_word"',
    '"find_bit.first_zero"',
    '"find_bit.next_zero"',
    '"find_bit.first_and"',
    '"find_bit.next_and"',
    '"find_bit.tail_clamped_first"',
    '"find_bit.tail_clamped_next"',
    '"find_bit.tail_zero_clamped_first"',
    '"find_bit.tail_zero_clamped_next"',
    '"find_bit.tail_and_clamped_first"',
    '"find_bit.tail_and_clamped_next"',
    '"find_bit.tail_and_mixed_first"',
    '"find_bit.tail_and_mixed_next"',
    '"summary": "Committed C-backed parity coverage includes baseline set, zero, and shared-bit scans plus tail-clamped set, zero, and AND searches, including the mixed-tail case where one shared bit remains in range while another lives past nbits."',
    '"unit_test_anchor": "tools/lib/find_bit.zig:test \\\"find next zero bit skips earlier matches in the same word\\\""',
    '"unit_test_contract": "Direct Zig unit coverage keeps same-word zero-scan start masking aligned so inclusive starts can return the current zero, later starts skip earlier same-word zeros, and tail scans still clamp to nbits."',
    '"set_unit_test_anchor": "tools/lib/find_bit.zig:test \\\"find next bit skips earlier matches in the same word\\\""',
    '"set_unit_test_contract": "Direct Zig unit coverage keeps same-word set-scan start masking aligned so inclusive starts can return the current set bit, later starts skip earlier same-word matches, and tail scans still clamp to nbits."',
    '"and_unit_test_anchor": "tools/lib/find_bit.zig:test \\\"find next and bit skips earlier shared matches in the same word\\\""',
    '"and_unit_test_contract": "Direct Zig unit coverage keeps same-word shared-bit start masking aligned so inclusive starts can return the current shared bit, later starts skip earlier same-word overlaps, and tail-clamped AND scans still stop at nbits."',
    '"mask_unit_test_anchor": "tools/lib/find_bit.zig:test \\\"word helpers keep linux-style mask and sizing boundaries\\\""',
    '"mask_unit_test_contract": "Direct Zig unit coverage keeps bitsToWords(), firstWordMask(), and lastWordMask() aligned with Linux-style whole-word, partial-word, and wrapped-start boundaries so exported mask helpers remain reviewable without relying only on indirect scan coverage."',
    '"boundary_unit_test_anchor": "tools/lib/find_bit.zig:test \\\"empty and boundary scans return nbits\\\""',
    '"boundary_unit_test_contract": "Direct Zig unit coverage keeps empty and out-of-range scan boundaries aligned by returning nbits for zero-length bitmaps, start-at-nbits searches, and fully set zero-bit windows that must not report past the declared range."',
    '"alias_unit_test_anchor": "tools/lib/find_bit.zig:test \\\"find underscore aliases preserve scan semantics\\\""',
    '"alias_unit_test_contract": "Direct Zig unit coverage keeps find_first_bit(), find_first_and_bit(), find_first_zero_bit(), find_next_bit(), find_next_and_bit(), and find_next_zero_bit() aligned with the camelCase scan helpers across the same caller-selected bit windows and tail clamps."',
]
required_find_bit_closure_markers = [
    'tools/lib/find_bit.zig` closure includes committed C-backed parity coverage for baseline set, zero, and shared-bit scans plus tail-clamped set, zero, and AND searches, including the mixed-tail case where one shared bit remains in range while another lives past `nbits`.',
    'tools/lib/find_bit.zig` direct Zig unit coverage now keeps same-word zero-scan start masking aligned so inclusive starts can return the current zero, later starts skip earlier same-word zeros, and tail scans still clamp to `nbits`.',
    'tools/lib/find_bit.zig` direct Zig unit coverage also keeps same-word set-scan start masking aligned so inclusive starts can return the current set bit, later starts skip earlier same-word matches, and tail scans still clamp to `nbits`.',
    'tools/lib/find_bit.zig` direct Zig unit coverage also keeps same-word shared-bit start masking aligned so inclusive starts can return the current shared bit, later starts skip earlier same-word overlaps, and tail-clamped AND scans still stop at `nbits`.',
    'tools/lib/find_bit.zig` direct Zig unit coverage also keeps exported mask and sizing helpers aligned with Linux-style boundaries so whole-word, partial-word, and wrapped-start calls stay reviewable without relying only on indirect scan behavior.',
    'find_bit fixture authority: `zigux/tests/fixtures/phase1_helpers.json`',
    'find_bit manifest review anchor: `zigux/tests/fixtures/phase1_helper_manifest.json`',
    'find_bit direct unit-test anchor: `tools/lib/find_bit.zig:test "find next zero bit skips earlier matches in the same word"`',
    'PHASE1_FIND_BIT_REVIEW=find_bit baseline set, zero, shared-bit, and tail-clamped scans ignore bits beyond nbits while preserving the in-range mixed-tail match',
    'PHASE1_FIND_BIT_UNIT_REVIEW=find_bit same-word zero-scan start masking keeps inclusive starts honest, skips earlier zero matches after the search advances, and still clamps tail results to nbits',
    'find_bit set unit-test anchor: `tools/lib/find_bit.zig:test "find next bit skips earlier matches in the same word"`',
    'PHASE1_FIND_BIT_SET_UNIT_REVIEW=find_bit same-word set-scan start masking keeps inclusive starts honest, skips earlier same-word set matches after the search advances, and still clamps tail results to nbits',
    'find_bit and unit-test anchor: `tools/lib/find_bit.zig:test "find next and bit skips earlier shared matches in the same word"`',
    'PHASE1_FIND_BIT_AND_UNIT_REVIEW=find_bit same-word shared-bit start masking keeps inclusive starts honest, skips earlier same-word overlaps after the search advances, and still clamps tail AND results to nbits',
    'find_bit mask unit-test anchor: `tools/lib/find_bit.zig:test "word helpers keep linux-style mask and sizing boundaries"`',
    'PHASE1_FIND_BIT_MASK_UNIT_REVIEW=find_bit mask and sizing helpers keep Linux-style whole-word, partial-word, and wrapped-start boundaries reviewable without relying only on indirect scan coverage',
    'tools/lib/find_bit.zig` direct Zig unit coverage also keeps empty and out-of-range scan boundaries aligned by returning `nbits` for zero-length bitmaps, start-at-`nbits` searches, and fully set zero-bit windows that must not report past the declared range.',
    'find_bit boundary unit-test anchor: `tools/lib/find_bit.zig:test "empty and boundary scans return nbits"`',
    'PHASE1_FIND_BIT_BOUNDARY_UNIT_REVIEW=find_bit empty and out-of-range scans return nbits for zero-length bitmaps, start-at-nbits searches, and fully set zero-bit windows that must not report past the declared range',
    'tools/lib/find_bit.zig` direct Zig unit coverage also keeps the underscore alias entry points aligned so `find_first_bit()`, `find_first_and_bit()`, `find_first_zero_bit()`, `find_next_bit()`, `find_next_and_bit()`, and `find_next_zero_bit()` preserve the same scan semantics as the camelCase helpers across the same caller-selected bit windows and tail clamps.',
    'find_bit alias unit-test anchor: `tools/lib/find_bit.zig:test "find underscore aliases preserve scan semantics"`',
    'PHASE1_FIND_BIT_ALIAS_UNIT_REVIEW=find_bit underscore alias entry points preserve the same set, shared-bit, and zero-bit scan semantics as the camelCase helpers across the same caller-selected bit windows and tail clamps',
]

# remainder of file unchanged for operational write brevity

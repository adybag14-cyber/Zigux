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
        'partial_xor_nbits',
        'partial_xor_masked_values',
        'scnprintf_empty_len',
        'scnprintf_empty_bytes',
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
    ROOT / 'scripts' / 'zigux' / 'check-phase1-parity.py',
    ROOT / 'zigux' / 'tests' / 'build.zig',
    ROOT / 'zigux' / 'tests' / 'bitmap_diff.zig',
    ROOT / 'zigux' / 'tests' / 'bitmap_diff_build.zig',
    ROOT / 'zigux' / 'tests' / 'phase1_helpers.zig',
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

ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
string_root = (ROOT / 'tools' / 'lib' / 'string.zig').read_text(encoding='utf-8')
rbtree_root = (ROOT / 'tools' / 'lib' / 'rbtree.zig').read_text(encoding='utf-8')
test_root = (ROOT / 'zigux' / 'tests' / 'phase1_helpers.zig').read_text(encoding='utf-8')
bitmap_diff_root = (ROOT / 'zigux' / 'tests' / 'bitmap_diff.zig').read_text(encoding='utf-8')
bitmap_diff_build_root = (ROOT / 'zigux' / 'tests' / 'bitmap_diff_build.zig').read_text(encoding='utf-8')
phase1_closure = (ROOT / 'Documentation' / 'zigux' / 'phase1-closure.md').read_text(encoding='utf-8')
find_bit_fixture = (ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helpers.json').read_text(encoding='utf-8')
find_bit_harness = (ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helpers_c_harness.c').read_text(encoding='utf-8')
find_bit_manifest = (ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helper_manifest.json').read_text(encoding='utf-8')

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
    'python3 scripts/zigux/check-phase1-parity.py',
    'zig build test --build-file zigux/tests/build.zig',
    'zig build test --build-file zigux/tests/bitmap_diff_build.zig --summary all',
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
required_find_bit_test_markers = [
    'fixture.find_bit.tail_clamped_first',
    'fixture.find_bit.tail_zero_clamped_first',
    'fixture.find_bit.tail_and_mixed_first',
    'find_bit.findFirstBit(&find_tail_window, find_tail_nbits)',
    'find_bit.findNextBit(&find_tail_window, find_tail_nbits, fixture.find_bit.bits_per_long + 4)',
    'find_bit.findFirstZeroBit(&find_tail_zero_window, find_tail_nbits)',
    'find_bit.findNextZeroBit(&find_tail_zero_window, find_tail_nbits, fixture.find_bit.bits_per_long)',
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
]
required_string_helper_markers = [
    'pub fn strim(buf: []u8) []u8 {',
    'pub fn strreplace(buf: []u8, old: u8, new: u8) []u8 {',
    'test "skip trim remove and replace spaces work in place"',
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
    '\\"remove_spaces_nul\\":',
    '\\"remove_spaces_nul_bytes\\":',
]
required_string_manifest_markers = [
    '"tools/lib/string.zig"',
    '"unit_test_anchor": "tools/lib/string.zig:test \\"memchrInv scans aligned and misaligned long buffers\\""',
    '"unit_test_contract": "Direct Zig unit coverage keeps memchrInv honest for both aligned and misaligned long buffers beyond the short C-backed fixture cases."',
    '"alias_unit_test_anchor": "tools/lib/string.zig:test \\"trimSpaces and strim trim trailing whitespace before an embedded NUL\\""',
    '"alias_unit_test_contract": "Direct Zig unit coverage keeps trimSpaces and strim aligned with C-string semantics by trimming trailing whitespace that appears before the first embedded NUL while preserving bytes beyond that terminator."',
]
required_string_closure_markers = [
    'string direct unit-test anchor: `tools/lib/string.zig:test "memchrInv scans aligned and misaligned long buffers"`',
    'string alias unit-test anchor: `tools/lib/string.zig:test "trimSpaces and strim trim trailing whitespace before an embedded NUL"`',
    'PHASE1_STRING_UNIT_REVIEW=string memchrInv aligned and misaligned long-buffer scans stay consistent beyond the short C-backed fixture cases',
    'PHASE1_STRING_ALIAS_UNIT_REVIEW=string trimSpaces and strim trim trailing whitespace before the first embedded NUL while preserving bytes beyond that terminator',
]
required_rbtree_helper_markers = [
    'pub fn find(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {',
    'pub fn findFirst(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) ?*Node {',
    'pub fn nextMatch(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {',
    'pub fn iterateMatches(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {',
    'pub fn addCached(node: *Node, root: *RootCached, less: LessFn) void {',
    'test "rbtree nextMatch walks the duplicate range in order"',
    'test "rbtree cached root keeps leftmost in sync across add erase and replace"',
]
required_rbtree_manifest_markers = [
    '"tools/lib/rbtree.zig"',
    '"summary": "Committed C-backed parity coverage includes ordered forward and reverse traversal plus replaceNode, eraseInit, postorder traversal, and detached-node state checks."',
    '"unit_test_anchor": "tools/lib/rbtree.zig:test \\"rbtree findAdd keeps the first duplicate and inserts new keys\\""',
    '"unit_test_contract": "Direct Zig unit coverage keeps findAdd duplicate handling aligned so the first equal key stays resident while new distinct keys still link into the tree."',
    '"search_unit_test_anchor": "tools/lib/rbtree.zig:test \\"rbtree nextMatch walks the duplicate range in order\\""',
    '"search_unit_test_contract": "Direct Zig unit coverage keeps find(), findFirst(), and nextMatch() aligned so duplicate-key lookups start at the leftmost match and walk through the final equal node without drifting into a later key."',
    '"cached_unit_test_anchor": "tools/lib/rbtree.zig:test \\"rbtree cached root keeps leftmost in sync across add erase and replace\\""',
    '"cached_unit_test_contract": "Direct Zig unit coverage keeps RootCached leftmost tracking aligned so addCached(), eraseCached(), and replaceNodeCached() continue to expose the same first node as the underlying tree root."',
]
required_rbtree_closure_markers = [
    'tools/lib/rbtree.zig` closure includes committed C-backed parity coverage for ordered forward and reverse traversal plus `replaceNode`, `eraseInit`, postorder traversal, and detached-node state checks.',
    'tools/lib/rbtree.zig` direct Zig unit coverage keeps `findAdd` duplicate handling aligned so the first equal key stays resident while new distinct keys still link into the tree.',
    'tools/lib/rbtree.zig` direct Zig unit coverage also keeps `find()`, `findFirst()`, and `nextMatch()` aligned so duplicate-key lookups start at the leftmost match and walk through the final equal node without drifting into a later key.',
    'tools/lib/rbtree.zig` direct Zig unit coverage also keeps `RootCached` leftmost tracking aligned so cached insert, erase, and replace helpers continue to expose the same first node as the underlying tree root.',
    'rbtree direct unit-test anchor: `tools/lib/rbtree.zig:test "rbtree findAdd keeps the first duplicate and inserts new keys"`',
    'rbtree search unit-test anchor: `tools/lib/rbtree.zig:test "rbtree nextMatch walks the duplicate range in order"`',
    'rbtree cached-root unit-test anchor: `tools/lib/rbtree.zig:test "rbtree cached root keeps leftmost in sync across add erase and replace"`',
    'PHASE1_RBTREE_REVIEW=rbtree parity covers ordered traversal, replaceNode, eraseInit, postorder traversal, and detached-node state',
    'PHASE1_RBTREE_UNIT_REVIEW=rbtree findAdd keeps the first equal key resident while new distinct keys still link into the tree',
    'PHASE1_RBTREE_SEARCH_UNIT_REVIEW=rbtree find, findFirst, and nextMatch keep duplicate-key lookup walks aligned from the leftmost match through the final equal node',
    'PHASE1_RBTREE_CACHED_UNIT_REVIEW=rbtree RootCached leftmost tracking stays aligned across addCached, eraseCached, and replaceNodeCached so the cached first node matches the underlying tree root',
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
for marker in required_bitmap_diff_markers:
    if marker not in bitmap_diff_root:
        missing_markers.append(f'bitmap_diff:{marker}')
for marker in required_bitmap_diff_build_markers:
    if marker not in bitmap_diff_build_root:
        missing_markers.append(f'bitmap_diff_build:{marker}')
for marker in required_find_bit_test_markers:
    if marker not in test_root:
        missing_markers.append(f'find_bit_test:{marker}')
for marker in required_find_bit_fixture_markers:
    if marker not in find_bit_fixture:
        missing_markers.append(f'find_bit_fixture:{marker}')
for marker in required_find_bit_harness_markers:
    if marker not in find_bit_harness:
        missing_markers.append(f'find_bit_harness:{marker}')
for marker in required_find_bit_manifest_markers:
    if marker not in find_bit_manifest:
        missing_markers.append(f'find_bit_manifest:{marker}')
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
    f'{len(required_ledger_markers) + len(required_workflow_markers) + len(required_test_markers) + len(required_bitmap_diff_markers) + len(required_bitmap_diff_build_markers) + len(required_find_bit_test_markers) + len(required_find_bit_fixture_markers) + len(required_find_bit_harness_markers) + len(required_find_bit_manifest_markers) + len(required_string_helper_markers) + len(required_rbtree_helper_markers) + len(required_string_test_markers) + len(required_string_fixture_markers) + len(required_string_harness_markers) + len(required_string_manifest_markers) + len(required_rbtree_manifest_markers) + len(required_string_closure_markers) + len(required_rbtree_closure_markers)}'
)

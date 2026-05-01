#!/usr/bin/env python3
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-phase1-closure.py",
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/bitmap_diff_build.zig",
    "zigux/tests/build.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_helpers.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/phase1_helpers.zig",
]

FIXTURE_SHAPE = {
    "find_bit": {
        "bits_per_long",
        "first",
        "next_after_6",
        "next_after_word",
        "first_zero",
        "next_zero",
        "first_and",
        "next_and",
        "tail_clamped_first",
        "tail_clamped_next",
        "tail_zero_clamped_first",
        "tail_zero_clamped_next",
        "tail_and_clamped_first",
        "tail_and_clamped_next",
        "tail_and_mixed_first",
        "tail_and_mixed_next",
    },
    "bitmap": {
        "weight",
        "scnprintf",
        "and_result",
        "and_values",
        "andnot_result",
        "andnot_values",
        "or_values",
        "xor_values",
        "copy_nbits",
        "copy_values",
        "partial_xor_nbits",
        "partial_xor_masked_values",
        "scnprintf_empty_len",
        "scnprintf_empty_bytes",
        "alloc_nbits",
        "alloc_values",
        "zalloc_nbits",
        "zalloc_values",
        "equal",
        "intersects",
        "subset",
        "range_after_set",
        "range_after_clear",
        "full_after_fill",
        "empty_after_zero",
        "scnprintf_trunc_len",
        "scnprintf_trunc",
    },
    "string": {
        "strtobool_y",
        "strtobool_on",
        "strtobool_zero",
        "strtobool_off",
        "strtobool_invalid",
        "strlcpy_len",
        "strlcpy_buffer",
        "skip_spaces",
        "trim_spaces",
        "remove_spaces",
        "remove_spaces_nul",
        "remove_spaces_nul_bytes",
        "replace_char",
        "replace_char_end",
        "memchr_inv_index",
        "memchr_inv_none",
    },
    "rbtree": {
        "empty_root",
        "insert_order",
        "reverse_order",
        "replace_order",
        "erase_init_order",
        "postorder_count",
        "erase_init_node_empty",
        "cleared_node_empty",
    },
    "argv_split": {"argc", "argv", "blank_argc"},
    "cmdline": {"decimal_k", "hex_m", "octal_k", "invalid"},
    "ctype": {
        "mask_A",
        "mask_a",
        "mask_space",
        "isalnum_A",
        "isalpha_z",
        "isdigit_7",
        "isspace_tab",
        "isxdigit_f",
        "ispunct_bang",
        "tolower_A",
        "toupper_z",
        "isodigit_7",
        "isodigit_8",
    },
    "hweight": {"w8", "w16", "w32", "w64", "wlong"},
    "list_sort": {"tri_sorted_keys", "tri_sorted_ordinals", "bool_sorted_keys", "bool_sorted_ordinals"},
    "zalloc": {"zeroed", "freed_is_null", "value_zeroed", "value_freed_is_null"},
    "str_error_r": {"enoent", "unknown"},
    "slab": {
        "null_without_reclaim",
        "alloc_count_after_kmalloc",
        "zero_after_kmalloc",
        "alloc_count_after_kmalloc_free",
        "array_zeroed",
        "alloc_count_after_kmalloc_array",
        "alloc_count_after_kmalloc_array_free",
        "slab_is_available",
    },
    "vsprintf": {"scnprintf_text", "scnprintf_len", "pad_text", "pad_len"},
}

HELPERS = {
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
}

MARKER_GROUPS = {
    "ledger": (
        "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
        [
            "feat(tools/lib): start phase-1 helper ports",
            "test(zigux): add phase-1 helper harness and workflow gate",
            "feat(tools/lib): expand phase-1 helper batch",
            "test(zigux): add phase-1 golden parity fixtures and artifact diff gate",
            "feat(tools/lib): complete bounded phase-1 helper coverage",
        ],
    ),
    "workflow": (
        ".github/workflows/zigux-bootstrap.yml",
        [
            "python3 scripts/zigux/validate-phase1.py",
            "python3 scripts/zigux/validate-phase1-closure.py",
            "python3 scripts/zigux/validate-phase1-closure.py --self-test",
            "python3 scripts/zigux/check-phase1-bench.py",
            "python3 scripts/zigux/check-phase1-bench.py --self-test",
            "python3 scripts/zigux/check-phase1-parity.py",
            "python3 scripts/zigux/check-phase1-parity.py --self-test",
            "zig build bench --build-file zigux/tests/build.zig",
            "zig build test --build-file zigux/tests/build.zig",
        ],
    ),
    "build": (
        "zigux/tests/build.zig",
        [
            "phase1_bench.zig",
            'const bench_step = b.step("bench", "Run Phase 1 helper benchmark smoke");',
        ],
    ),
    "phase1_closure": (
        "Documentation/zigux/phase1-closure.md",
        [
            "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py",
            "PHASE1_CLOSURE_SELF_TEST_GATE=python3 scripts/zigux/validate-phase1-closure.py --self-test",
            "PHASE1_PARITY_SELF_TEST_GATE=python3 scripts/zigux/check-phase1-parity.py --self-test",
            "PHASE1_BITMAP_ZERO_BIT_UNIT_REVIEW=",
            "PHASE1_FIND_BIT_ALIAS_UNIT_REVIEW=",
            "PHASE1_FIND_BIT_SET_UNIT_REVIEW=find_bit same-word set-scan start masking keeps inclusive starts honest, skips earlier same-word set matches after the search advances, and still clamps tail results to nbits",
            "PHASE1_FIND_BIT_AND_UNIT_REVIEW=find_bit same-word shared-bit start masking keeps inclusive starts honest, skips earlier same-word overlaps after the search advances, and still clamps tail AND results to nbits",
            "PHASE1_FIND_BIT_MASK_UNIT_REVIEW=find_bit mask and sizing helpers keep Linux-style whole-word, partial-word, and wrapped-start boundaries reviewable without relying only on indirect scan coverage",
            "PHASE1_FIND_BIT_BOUNDARY_UNIT_REVIEW=find_bit empty and out-of-range scans return nbits for zero-length bitmaps, start-at-nbits searches, and fully set zero-bit windows that must not report past the declared range",
            "PHASE1_FIND_BIT_LOW_LEVEL_UNIT_REVIEW=find_bit low-level underscore entry points preserve same-word inclusive starts and tail-clamped set, shared-bit, and zero-bit scan behavior across the same caller-selected bit windows as the public helpers",
            'find_bit small-bitmap unit-test anchor: `tools/lib/find_bit.zig:test "single-word scans keep linux small-bitmap semantics"`',
            "PHASE1_STRING_ALIAS_UNIT_REVIEW=string trimSpaces and strim trim trailing whitespace before the first embedded NUL while preserving bytes beyond that terminator",
            "PHASE1_STRING_MEMPARSE_UNIT_REVIEW=",
            "PHASE1_RBTREE_CACHED_FINDADD_UNIT_REVIEW=",
            "PHASE1_RBTREE_BENCH_REVIEW=rbtree benchmark smoke pins ordered traversal, duplicate-range, cached-leftmost, findAdd, and postorder-safe checksum surfaces so duplicate-owner and erase-while-walking regressions cannot hide behind the broader tree checksum alone",
            "PHASE1_RBTREE_BENCH_KEYS=PHASE1_BENCH_RBTREE_CHECKSUM,PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM,PHASE1_BENCH_RBTREE_CACHED_CHECKSUM,PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM,PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
            'bitmap direct unit-test anchor: `tools/lib/bitmap.zig:test "bitmap allocation helpers size zero fill and reset optionals"`',
            "bitmap allocator review note: `bitmap_alloc()` and `bitmap_zalloc()` must size partial-word bitmaps through `BITS_TO_LONGS(nbits)`, while `bitmapFree()` optional-reset behavior remains direct Zig-only coverage because the C helper frees raw pointers in place",
        ],
    ),
    "bench": (
        "zigux/tests/phase1_bench.zig",
        [
            "pub fn main(init: std.process.Init) !void {",
            "const bitmap_result = bitmapBench();",
            "const find_bit_result = findBitBench();",
            "const find_zero_bit_result = findZeroBitBench();",
            "const find_and_bit_result = findAndBitBench();",
            "const rbtree_result = rbtreeBench();",
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
            "PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM",
            "PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM",
            "PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM",
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
        ],
    ),
    "bench_expectations": (
        "zigux/tests/fixtures/phase1_bench_expectations.json",
        [
            '"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM"',
            '"PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM"',
            '"PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM"',
            '"PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM"',
            '"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"',
            '"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM"',
            '"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM"',
        ],
    ),
    "parity_checker": (
        "scripts/zigux/check-phase1-parity.py",
        [
            "print('PHASE1_PARITY=pass')",
            "print('PHASE1_PARITY_DETERMINISM=pass')",
            "print('PHASE1_PARITY_SELF_TEST=pass')",
            "print('PHASE1_PARITY_SELF_TEST_CASE_COUNT=7')",
        ],
    ),
    "phase1_tests": (
        "zigux/tests/phase1_helpers.zig",
        [
            '@import("argv_split")',
            '@import("bitmap")',
            '@import("find_bit")',
            '@import("rbtree")',
            '@import("string")',
            '@embedFile("fixtures/phase1_helpers.json")',
            "fixture.bitmap.alloc_nbits",
            "fixture.bitmap.alloc_values",
            "fixture.bitmap.zalloc_nbits",
            "fixture.bitmap.zalloc_values",
            "fixture.find_bit.tail_clamped_first",
            "fixture.find_bit.tail_and_mixed_next",
            "fixture.string.remove_spaces_nul_bytes",
            "fixture.rbtree.insert_order",
            "fixture.rbtree.reverse_order",
            "fixture.rbtree.replace_order",
            "fixture.rbtree.erase_init_order",
            "fixture.rbtree.postorder_count",
            "fixture.rbtree.erase_init_node_empty",
            "fixture.rbtree.cleared_node_empty",
        ],
    ),
    "bitmap": (
        "tools/lib/bitmap.zig",
        [
            'test "bitmap scnprintf truncates and keeps a terminator slot"',
            'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
            'test "bitmap allocation helpers size zero fill and reset optionals"',
            'test "bitmap zero-bit helpers stay explicit no-ops"',
        ],
    ),
    "bitmap_harness": (
        "zigux/tests/fixtures/phase1_helpers_c_harness.c",
        [
            "unsigned long alloc_nbits = BITS_PER_LONG + 5;",
            'printf("\\\"alloc_nbits\\\":%lu,", alloc_nbits);',
            'printf("\\\"scnprintf_trunc\\\":\\\"%s\\\"", trunc_buffer);',
        ],
    ),
    "bitmap_manifest": (
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        [
            '"alias_unit_test_anchor"',
            "bitmap_weight(), bitmap_and(), bitmap_andnot(), bitmap_or(), bitmap_xor(), bitmap_equal(), bitmap_intersects(), bitmap_subset(), bitmap_set(), bitmap_clear(), and bitmap_scnprintf() aligned with the camelCase helpers across the same caller-selected bit window.",
            '"allocator_alias_unit_test_anchor"',
            "bitmap underscore allocator aliases preserve allocation and ownership semantics",
            '"allocator_alias_unit_test_contract"',
            "bitmap_alloc(), bitmap_zalloc(), and bitmap_free() aligned with bitmapAlloc(), bitmapZalloc(), and bitmapFree() for partial-word sizing, zero-filled allocation, and optional-handle reset semantics.",
            '"range_unit_test_anchor"',
            "bitmap range helpers preserve edges across whole-word spans",
            '"range_unit_test_contract"',
            "Direct Zig unit coverage keeps cross-word setRange() and clearRange() aligned by preserving the first-word start mask, fully covering interior words, clamping the last word, and restoring the whole window to zero on clear.",
            '"copy_unit_test_anchor"',
            "bitmap copyClearTail clears out-of-range bits in the last copied word",
            '"copy_unit_test_contract"',
            "Direct Zig unit coverage keeps copy() and copyClearTail() aligned by preserving copied source words while forcing tail bits above nbits back to zero in the final copied word.",
            '"bitwise_unit_test_anchor"',
            "bitmap and andnot equal intersects subset",
            '"bitwise_unit_test_contract"',
            "Direct Zig unit coverage keeps andBits(), andNotBits(), xorBits(), equal(), intersects(), and subset() aligned on the shared caller-selected bit window instead of leaking unrelated tail bits.",
            '"xor_unit_test_anchor"',
            "bitmap xor keeps caller-selected bit window",
            '"xor_unit_test_contract"',
            "Direct Zig unit coverage keeps xorBits() aligned with the caller-selected bit window by proving partial-word and multiword-tail replays preserve only the in-range bits that callers intentionally clamp.",
            '"tail_mask_unit_test_anchor"',
            "bitmap tail-masked helpers ignore out-of-range differences",
            '"tail_mask_unit_test_contract"',
            "Direct Zig unit coverage keeps andBits(), andNotBits(), equal(), intersects(), and subset() aligned by masking out-of-range tail differences while preserving the declared in-range window.",
            '"zero_bit_unit_test_anchor"',
            "bitmap zero-bit helpers stay explicit no-ops",
            '"zero_bit_unit_test_contract"',
            "Direct Zig unit coverage keeps zero-length helper calls explicit and side-effect free so zero(), fill(), copy(), copyClearTail(), orBits(), xorBits(), scans, and formatting all leave caller-owned buffers untouched when nbits is zero.",
        ],
    ),
    "find_bit": (
        "tools/lib/find_bit.zig",
        [
            "pub fn findFirstBit(addr: []const Word, nbits: usize) usize {",
            "pub fn find_first_bit(addr: []const Word, nbits: usize) usize {",
            'test "find next bit skips earlier matches in the same word"',
            'test "find next and bit skips earlier shared matches in the same word"',
            'test "word helpers keep linux-style mask and sizing boundaries"',
            'test "empty and boundary scans return nbits"',
            'test "find underscore aliases preserve scan semantics"',
            'test "single-word scans keep linux small-bitmap semantics"',
        ],
    ),
    "find_bit_harness": (
        "zigux/tests/fixtures/phase1_helpers_c_harness.c",
        [
            "unsigned long tail_bitmap[2] = {0, 1UL << 9};",
            "unsigned long tail_zero_bitmap[2] = {~0UL, BITMAP_LAST_WORD_MASK(BITS_PER_LONG + 5)};",
            "unsigned long tail_and_mixed[2] = {0, (1UL << 3) | (1UL << 9)};",
            '\"tail_clamped_first\":%lu,',
            '\"tail_and_mixed_next\":%lu',
        ],
    ),
    "find_bit_manifest": (
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        [
            '"find_bit.tail_clamped_first"',
            '"find_bit.tail_zero_clamped_next"',
            '"find_bit.tail_and_mixed_next"',
            '"alias_unit_test_anchor"',
            '"alias_unit_test_contract"',
            '"set_unit_test_anchor"',
            '"set_unit_test_contract"',
            '"and_unit_test_anchor"',
            '"and_unit_test_contract"',
            '"mask_unit_test_anchor"',
            '"mask_unit_test_contract"',
            '"boundary_unit_test_anchor"',
            '"boundary_unit_test_contract"',
            '"low_level_unit_test_anchor"',
            '"low_level_unit_test_contract"',
            '"small_bitmap_unit_test_anchor"',
            '"small_bitmap_unit_test_contract"',
        ],
    ),
    "string": (
        "tools/lib/string.zig",
        [
            "pub fn strim(buf: []u8) []u8 {",
            "pub fn strreplace(buf: []u8, old: u8, new: u8) []u8 {",
            'test "strlcpy stops at the first embedded NUL in the source"',
            'test "streq matches C-string equality semantics"',
            'test "trimSpaces and strim trim trailing whitespace before an embedded NUL"',
            'test "strstarts matches kernel prefix semantics"',
            'test "strHasPrefix returns the matched prefix length with C-string semantics"',
            'test "str_ends_with matches kernel suffix semantics"',
            'test "memparse forwards the header-level string helper surface"',
        ],
    ),
    "string_manifest": (
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        [
            '"string.strlcpy_buffer"',
            '"string.remove_spaces_nul"',
            '"string.remove_spaces_nul_bytes"',
            '"alias_unit_test_anchor"',
            '"alias_unit_test_contract"',
            '"cstring_unit_test_anchor"',
            '"cstring_unit_test_contract"',
            '"equality_unit_test_anchor"',
            '"equality_unit_test_contract"',
            '"prefix_unit_test_anchor"',
            '"prefix_unit_test_contract"',
            '"prefix_length_unit_test_anchor"',
            '"prefix_length_unit_test_contract"',
            '"suffix_unit_test_anchor"',
            '"suffix_unit_test_contract"',
            '"memparse_unit_test_anchor"',
            '"memparse_unit_test_contract"',
        ],
    ),
    "rbtree": (
        "tools/lib/rbtree.zig",
        [
            "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
            'test "rbtree nextMatch walks the duplicate range in order"',
            'test "rbtree cached root keeps leftmost in sync across add erase and replace"',
            'test "rbtree findAddCached preserves duplicate ownership and leftmost cache"',
            'test "rbtree iterateMatchesReverse streams only the duplicate range in reverse"',
        ],
    ),
}

WORKFLOW_EXACT_LINES = {
    "run: python3 scripts/zigux/validate-phase1.py": 1,
    "run: python3 scripts/zigux/validate-phase1-closure.py": 1,
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase1-bench.py": 1,
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase1-parity.py": 1,
    "run: python3 scripts/zigux/check-phase1-parity.py --self-test": 1,
}

PHASE1_CLOSURE_PREFIX_COUNTS = {
    "- `tools/lib/bitmap.zig` closure includes committed C-backed parity coverage": 1,
    "- `tools/lib/find_bit.zig` closure includes committed C-backed parity coverage": 1,
    "- `tools/lib/rbtree.zig` closure includes committed C-backed parity coverage": 1,
    "- `tools/lib/string.zig` closure includes committed C-backed parity coverage": 1,
}


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def fail(block: str, items: list[str]) -> None:
    print("PHASE1_VALIDATION=fail")
    print(f"{block}_START")
    for item in items:
        print(item)
    print(f"{block}_END")
    sys.exit(1)


def count_exact_line(text: str, expected: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == expected)


def count_prefixed_lines(text: str, prefix: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip().startswith(prefix))


def validate_fixture_shape() -> list[str]:
    issues: list[str] = []
    fixture = json.loads(read_text("zigux/tests/fixtures/phase1_helpers.json"))
    if not isinstance(fixture, dict):
        return ["phase1_fixture:expected_object"]
    for section, expected_keys in FIXTURE_SHAPE.items():
        value = fixture.get(section)
        if not isinstance(value, dict):
            issues.append(f"phase1_fixture:{section}:expected_object")
            continue
        actual = set(value)
        for key in sorted(expected_keys - actual):
            issues.append(f"phase1_fixture:{section}:missing_key:{key}")
        for key in sorted(actual - expected_keys):
            issues.append(f"phase1_fixture:{section}:unexpected_key:{key}")
    for section in sorted(set(fixture) - set(FIXTURE_SHAPE)):
        issues.append(f"phase1_fixture:unexpected_top_level:{section}")
    return issues


def validate_manifest_shape() -> list[str]:
    issues: list[str] = []
    manifest = json.loads(read_text("zigux/tests/fixtures/phase1_helper_manifest.json"))
    if manifest.get("phase") != "Phase 1":
        issues.append("phase1_manifest:phase:mismatch")
    if manifest.get("status") != "closed":
        issues.append("phase1_manifest:status:mismatch")
    if manifest.get("helper_count") != 13:
        issues.append("phase1_manifest:helper_count:mismatch")
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        issues.append("phase1_manifest:helpers:expected_list")
    else:
        actual_helpers = set(helpers)
        for helper in sorted(HELPERS - actual_helpers):
            issues.append(f"phase1_manifest:helpers:missing:{helper}")
        for helper in sorted(actual_helpers - HELPERS):
            issues.append(f"phase1_manifest:helpers:unexpected:{helper}")
    notes = manifest.get("helper_review_notes")
    if not isinstance(notes, dict):
        issues.append("phase1_manifest:helper_review_notes:expected_object")
    else:
        for helper in (
            "tools/lib/bitmap.zig",
            "tools/lib/find_bit.zig",
            "tools/lib/rbtree.zig",
            "tools/lib/string.zig",
        ):
            note = notes.get(helper)
            if not isinstance(note, dict):
                issues.append(f"phase1_manifest:{helper}:missing_note")
                continue
            if note.get("fixture") != "zigux/tests/fixtures/phase1_helpers.json":
                issues.append(f"phase1_manifest:{helper}:fixture:mismatch")
            evidence_keys = note.get("evidence_keys")
            if not isinstance(evidence_keys, list) or not evidence_keys:
                issues.append(f"phase1_manifest:{helper}:evidence_keys:expected_nonempty_list")
        bitmap_note = notes.get("tools/lib/bitmap.zig")
        if isinstance(bitmap_note, dict):
            if bitmap_note.get("alias_unit_test_anchor") != 'tools/lib/bitmap.zig:test "bitmap underscore aliases preserve bitmap helper semantics"':
                issues.append("phase1_manifest:tools/lib/bitmap.zig:alias_unit_test_anchor:mismatch")
            if bitmap_note.get("alias_unit_test_contract") != "Direct Zig unit coverage keeps bitmap_weight(), bitmap_and(), bitmap_andnot(), bitmap_or(), bitmap_xor(), bitmap_equal(), bitmap_intersects(), bitmap_subset(), bitmap_set(), bitmap_clear(), and bitmap_scnprintf() aligned with the camelCase helpers across the same caller-selected bit window.":
                issues.append("phase1_manifest:tools/lib/bitmap.zig:alias_unit_test_contract:mismatch")
            if bitmap_note.get("allocator_alias_unit_test_anchor") != 'tools/lib/bitmap.zig:test "bitmap underscore allocator aliases preserve allocation and ownership semantics"':
                issues.append("phase1_manifest:tools/lib/bitmap.zig:allocator_alias_unit_test_anchor:mismatch")
            if bitmap_note.get("allocator_alias_unit_test_contract") != "Direct Zig unit coverage keeps bitmap_alloc(), bitmap_zalloc(), and bitmap_free() aligned with bitmapAlloc(), bitmapZalloc(), and bitmapFree() for partial-word sizing, zero-filled allocation, and optional-handle reset semantics.":
                issues.append("phase1_manifest:tools/lib/bitmap.zig:allocator_alias_unit_test_contract:mismatch")
            if bitmap_note.get("range_unit_test_anchor") != 'tools/lib/bitmap.zig:test "bitmap range helpers preserve edges across whole-word spans"':
                issues.append("phase1_manifest:tools/lib/bitmap.zig:range_unit_test_anchor:mismatch")
            if bitmap_note.get("range_unit_test_contract") != "Direct Zig unit coverage keeps cross-word setRange() and clearRange() aligned by preserving the first-word start mask, fully covering interior words, clamping the last word, and restoring the whole window to zero on clear.":
                issues.append("phase1_manifest:tools/lib/bitmap.zig:range_unit_test_contract:mismatch")
            if bitmap_note.get("copy_unit_test_anchor") != 'tools/lib/bitmap.zig:test "bitmap copyClearTail clears out-of-range bits in the last copied word"':
                issues.append("phase1_manifest:tools/lib/bitmap.zig:copy_unit_test_anchor:mismatch")
            if bitmap_note.get("copy_unit_test_contract") != "Direct Zig unit coverage keeps copy() and copyClearTail() aligned by preserving copied source words while forcing tail bits above nbits back to zero in the final copied word.":
                issues.append("phase1_manifest:tools/lib/bitmap.zig:copy_unit_test_contract:mismatch")
            if bitmap_note.get("bitwise_unit_test_anchor") != 'tools/lib/bitmap.zig:test "bitmap and andnot equal intersects subset"':
                issues.append("phase1_manifest:tools/lib/bitmap.zig:bitwise_unit_test_anchor:mismatch")
            if bitmap_note.get("bitwise_unit_test_contract") != "Direct Zig unit coverage keeps andBits(), andNotBits(), xorBits(), equal(), intersects(), and subset() aligned on the shared caller-selected bit window instead of leaking unrelated tail bits.":
                issues.append("phase1_manifest:tools/lib/bitmap.zig:bitwise_unit_test_contract:mismatch")
            if bitmap_note.get("xor_unit_test_anchor") != 'tools/lib/bitmap.zig:test "bitmap xor keeps caller-selected bit window"':
                issues.append("phase1_manifest:tools/lib/bitmap.zig:xor_unit_test_anchor:mismatch")
            if bitmap_note.get("xor_unit_test_contract") != "Direct Zig unit coverage keeps xorBits() aligned with the caller-selected bit window by proving partial-word and multiword-tail replays preserve only the in-range bits that callers intentionally clamp.":
                issues.append("phase1_manifest:tools/lib/bitmap.zig:xor_unit_test_contract:mismatch")
            if bitmap_note.get("tail_mask_unit_test_anchor") != 'tools/lib/bitmap.zig:test "bitmap tail-masked helpers ignore out-of-range differences"':
                issues.append("phase1_manifest:tools/lib/bitmap.zig:tail_mask_unit_test_anchor:mismatch")
            if bitmap_note.get("tail_mask_unit_test_contract") != "Direct Zig unit coverage keeps andBits(), andNotBits(), equal(), intersects(), and subset() aligned by masking out-of-range tail differences while preserving the declared in-range window.":
                issues.append("phase1_manifest:tools/lib/bitmap.zig:tail_mask_unit_test_contract:mismatch")
            if bitmap_note.get("zero_bit_unit_test_anchor") != 'tools/lib/bitmap.zig:test "bitmap zero-bit helpers stay explicit no-ops"':
                issues.append("phase1_manifest:tools/lib/bitmap.zig:zero_bit_unit_test_anchor:mismatch")
            if bitmap_note.get("zero_bit_unit_test_contract") != "Direct Zig unit coverage keeps zero-length helper calls explicit and side-effect free so zero(), fill(), copy(), copyClearTail(), orBits(), xorBits(), scans, and formatting all leave caller-owned buffers untouched when nbits is zero.":
                issues.append("phase1_manifest:tools/lib/bitmap.zig:zero_bit_unit_test_contract:mismatch")
        find_bit_note = notes.get("tools/lib/find_bit.zig")
        if isinstance(find_bit_note, dict):
            if find_bit_note.get("alias_unit_test_anchor") != 'tools/lib/find_bit.zig:test "find underscore aliases preserve scan semantics"':
                issues.append("phase1_manifest:tools/lib/find_bit.zig:alias_unit_test_anchor:mismatch")
            if find_bit_note.get("alias_unit_test_contract") != "Direct Zig unit coverage keeps find_first_bit(), find_first_and_bit(), find_first_zero_bit(), find_next_bit(), find_next_and_bit(), and find_next_zero_bit() aligned with the camelCase scan helpers across the same caller-selected bit windows and tail clamps.":
                issues.append("phase1_manifest:tools/lib/find_bit.zig:alias_unit_test_contract:mismatch")
            if find_bit_note.get("set_unit_test_anchor") != 'tools/lib/find_bit.zig:test "find next bit skips earlier matches in the same word"':
                issues.append("phase1_manifest:tools/lib/find_bit.zig:set_unit_test_anchor:mismatch")
            if find_bit_note.get("set_unit_test_contract") != "Direct Zig unit coverage keeps same-word set-scan start masking aligned so inclusive starts can return the current set bit, later starts skip earlier same-word matches, and tail scans still clamp to nbits.":
                issues.append("phase1_manifest:tools/lib/find_bit.zig:set_unit_test_contract:mismatch")
            if find_bit_note.get("and_unit_test_anchor") != 'tools/lib/find_bit.zig:test "find next and bit skips earlier shared matches in the same word"':
                issues.append("phase1_manifest:tools/lib/find_bit.zig:and_unit_test_anchor:mismatch")
            if find_bit_note.get("and_unit_test_contract") != "Direct Zig unit coverage keeps same-word shared-bit start masking aligned so inclusive starts can return the current shared bit, later starts skip earlier same-word overlaps, and tail-clamped AND scans still stop at nbits.":
                issues.append("phase1_manifest:tools/lib/find_bit.zig:and_unit_test_contract:mismatch")
            if find_bit_note.get("mask_unit_test_anchor") != 'tools/lib/find_bit.zig:test "word helpers keep linux-style mask and sizing boundaries"':
                issues.append("phase1_manifest:tools/lib/find_bit.zig:mask_unit_test_anchor:mismatch")
            if find_bit_note.get("mask_unit_test_contract") != "Direct Zig unit coverage keeps bitsToWords(), firstWordMask(), and lastWordMask() aligned with Linux-style whole-word, partial-word, and wrapped-start boundaries so exported mask helpers remain reviewable without relying only on indirect scan coverage.":
                issues.append("phase1_manifest:tools/lib/find_bit.zig:mask_unit_test_contract:mismatch")
            if find_bit_note.get("boundary_unit_test_anchor") != 'tools/lib/find_bit.zig:test "empty and boundary scans return nbits"':
                issues.append("phase1_manifest:tools/lib/find_bit.zig:boundary_unit_test_anchor:mismatch")
            if find_bit_note.get("boundary_unit_test_contract") != "Direct Zig unit coverage keeps empty and out-of-range scan boundaries aligned by returning nbits for zero-length bitmaps, start-at-nbits searches, and fully set zero-bit windows that must not report past the declared range.":
                issues.append("phase1_manifest:tools/lib/find_bit.zig:boundary_unit_test_contract:mismatch")
            if find_bit_note.get("low_level_unit_test_anchor") != 'tools/lib/find_bit.zig:test "find low-level underscore entry points preserve same-word and tail-clamped scan semantics"':
                issues.append("phase1_manifest:tools/lib/find_bit.zig:low_level_unit_test_anchor:mismatch")
            if find_bit_note.get("low_level_unit_test_contract") != "Direct Zig unit coverage keeps _find_first_bit(), _find_first_and_bit(), _find_first_zero_bit(), _find_next_bit(), _find_next_and_bit(), and _find_next_zero_bit() aligned with the public scan helpers across same-word inclusive starts and tail-clamped caller-selected bit windows.":
                issues.append("phase1_manifest:tools/lib/find_bit.zig:low_level_unit_test_contract:mismatch")
            if find_bit_note.get("small_bitmap_unit_test_anchor") != 'tools/lib/find_bit.zig:test "single-word scans keep linux small-bitmap semantics"':
                issues.append("phase1_manifest:tools/lib/find_bit.zig:small_bitmap_unit_test_anchor:mismatch")
            if find_bit_note.get("small_bitmap_unit_test_contract") != "Direct Zig unit coverage keeps single-word set, zero, and shared-bit scans aligned with Linux small-bitmap semantics by masking out-of-range tail bits while preserving inclusive in-range matches inside one word.":
                issues.append("phase1_manifest:tools/lib/find_bit.zig:small_bitmap_unit_test_contract:mismatch")
        string_note = notes.get("tools/lib/string.zig")
        if isinstance(string_note, dict):
            if string_note.get("cstring_unit_test_anchor") != 'tools/lib/string.zig:test "strlcpy stops at the first embedded NUL in the source"':
                issues.append("phase1_manifest:tools/lib/string.zig:cstring_unit_test_anchor:mismatch")
            if string_note.get("cstring_unit_test_contract") != "Direct Zig unit coverage keeps strlcpy aligned with C-string semantics by stopping at the first embedded NUL, preserving truncation behavior, and leaving zero-sized destinations untouched.":
                issues.append("phase1_manifest:tools/lib/string.zig:cstring_unit_test_contract:mismatch")
            if string_note.get("alias_unit_test_anchor") != 'tools/lib/string.zig:test "trimSpaces and strim trim trailing whitespace before an embedded NUL"':
                issues.append("phase1_manifest:tools/lib/string.zig:alias_unit_test_anchor:mismatch")
            if string_note.get("alias_unit_test_contract") != "Direct Zig unit coverage keeps trimSpaces and strim aligned with C-string semantics by trimming trailing whitespace that appears before the first embedded NUL while preserving bytes beyond that terminator.":
                issues.append("phase1_manifest:tools/lib/string.zig:alias_unit_test_contract:mismatch")
            if string_note.get("equality_unit_test_anchor") != 'tools/lib/string.zig:test "streq matches C-string equality semantics"':
                issues.append("phase1_manifest:tools/lib/string.zig:equality_unit_test_anchor:mismatch")
            if string_note.get("equality_unit_test_contract") != "Direct Zig unit coverage keeps strEq() and streq() aligned with C-string equality semantics for exact, empty, length-mismatched, case-sensitive, and embedded-NUL comparisons.":
                issues.append("phase1_manifest:tools/lib/string.zig:equality_unit_test_contract:mismatch")
            if string_note.get("prefix_unit_test_anchor") != 'tools/lib/string.zig:test "strstarts matches kernel prefix semantics"':
                issues.append("phase1_manifest:tools/lib/string.zig:prefix_unit_test_anchor:mismatch")
            if string_note.get("prefix_unit_test_contract") != "Direct Zig unit coverage keeps strStarts and strstarts aligned with kernel-style prefix semantics for exact, empty-prefix, shorter-input, and case-sensitive comparisons.":
                issues.append("phase1_manifest:tools/lib/string.zig:prefix_unit_test_contract:mismatch")
            if string_note.get("prefix_length_unit_test_anchor") != 'tools/lib/string.zig:test "strHasPrefix returns the matched prefix length with C-string semantics"':
                issues.append("phase1_manifest:tools/lib/string.zig:prefix_length_unit_test_anchor:mismatch")
            if string_note.get("prefix_length_unit_test_contract") != "Direct Zig unit coverage keeps strHasPrefix and str_has_prefix aligned by returning the matched C-string prefix length for exact and embedded-NUL prefixes while rejecting mismatches and longer prefixes.":
                issues.append("phase1_manifest:tools/lib/string.zig:prefix_length_unit_test_contract:mismatch")
            if string_note.get("suffix_unit_test_anchor") != 'tools/lib/string.zig:test "str_ends_with matches kernel suffix semantics"':
                issues.append("phase1_manifest:tools/lib/string.zig:suffix_unit_test_anchor:mismatch")
            if string_note.get("suffix_unit_test_contract") != "Direct Zig unit coverage keeps strEndsWith, str_ends_with, and strends aligned with kernel-style suffix semantics for exact, empty-suffix, shorter-input, and case-sensitive comparisons.":
                issues.append("phase1_manifest:tools/lib/string.zig:suffix_unit_test_contract:mismatch")
            if string_note.get("memparse_unit_test_anchor") != 'tools/lib/string.zig:test "memparse forwards the header-level string helper surface"':
                issues.append("phase1_manifest:tools/lib/string.zig:memparse_unit_test_anchor:mismatch")
            if string_note.get("memparse_unit_test_contract") != "Direct Zig unit coverage keeps memparse aligned by forwarding decimal, hexadecimal, suffix-bearing, and invalid inputs through the shared command-line parser without changing the parsed value or rest pointer contract.":
                issues.append("phase1_manifest:tools/lib/string.zig:memparse_unit_test_contract:mismatch")
        rbtree_note = notes.get("tools/lib/rbtree.zig")
        if isinstance(rbtree_note, dict):
            if rbtree_note.get("summary") != "Committed C-backed parity coverage includes ordered forward and reverse traversal plus replaceNode, eraseInit, postorder traversal, and detached-node state checks, while Linux-style rb_* alias parity remains explicitly out of scope for this closed Phase 1 tranche.":
                issues.append("phase1_manifest:tools/lib/rbtree.zig:summary:mismatch")
            if rbtree_note.get("alias_gap_note") != "Linux-style rb_* alias surface parity is still missing for the already-ported entry points, and that remaining surface stays explicitly out of scope for the closed Phase 1 tranche until a later bounded repair lands.":
                issues.append("phase1_manifest:tools/lib/rbtree.zig:alias_gap_note:mismatch")
            if rbtree_note.get("unit_test_anchor") != 'tools/lib/rbtree.zig:test "rbtree findAdd keeps the first duplicate and inserts new keys"':
                issues.append("phase1_manifest:tools/lib/rbtree.zig:unit_test_anchor:mismatch")
            if rbtree_note.get("unit_test_contract") != "Direct Zig unit coverage keeps findAdd duplicate handling aligned so the first equal key stays resident while new distinct keys still link into the tree.":
                issues.append("phase1_manifest:tools/lib/rbtree.zig:unit_test_contract:mismatch")
            if rbtree_note.get("search_unit_test_anchor") != 'tools/lib/rbtree.zig:test "rbtree nextMatch walks the duplicate range in order"':
                issues.append("phase1_manifest:tools/lib/rbtree.zig:search_unit_test_anchor:mismatch")
            if rbtree_note.get("search_unit_test_contract") != "Direct Zig unit coverage keeps find(), findFirst(), and nextMatch() aligned so duplicate-key lookups start at the leftmost match and walk through the final equal node without drifting into a later key.":
                issues.append("phase1_manifest:tools/lib/rbtree.zig:search_unit_test_contract:mismatch")
            if rbtree_note.get("duplicate_search_unit_test_anchor") != 'tools/lib/rbtree.zig:test "rbtree duplicate search stays aligned after erase and same-key replace"':
                issues.append("phase1_manifest:tools/lib/rbtree.zig:duplicate_search_unit_test_anchor:mismatch")
            if rbtree_note.get("duplicate_search_unit_test_contract") != "Direct Zig unit coverage keeps duplicate-key search aligned after erase() and same-key replaceNode() so findFirst(), findLast(), and duplicate-range iterators continue to report the surviving equal-key window in both directions.":
                issues.append("phase1_manifest:tools/lib/rbtree.zig:duplicate_search_unit_test_contract:mismatch")
            if rbtree_note.get("cached_unit_test_anchor") != 'tools/lib/rbtree.zig:test "rbtree cached root keeps leftmost in sync across add erase and replace"':
                issues.append("phase1_manifest:tools/lib/rbtree.zig:cached_unit_test_anchor:mismatch")
            if rbtree_note.get("cached_unit_test_contract") != "Direct Zig unit coverage keeps RootCached leftmost tracking aligned so addCached(), eraseCached(), and replaceNodeCached() continue to expose the same first node as the underlying tree root.":
                issues.append("phase1_manifest:tools/lib/rbtree.zig:cached_unit_test_contract:mismatch")
            if rbtree_note.get("cached_duplicate_unit_test_anchor") != 'tools/lib/rbtree.zig:test "rbtree cached root tracks duplicate minima through erase and non-leftmost replace"':
                issues.append("phase1_manifest:tools/lib/rbtree.zig:cached_duplicate_unit_test_anchor:mismatch")
            if rbtree_note.get("cached_duplicate_unit_test_contract") != "Direct Zig unit coverage keeps RootCached duplicate minima aligned so eraseCached() promotes the next equal-key minimum and replaceNodeCached() leaves the cached first node unchanged when a non-leftmost node is replaced.":
                issues.append("phase1_manifest:tools/lib/rbtree.zig:cached_duplicate_unit_test_contract:mismatch")
            if rbtree_note.get("cached_find_add_unit_test_anchor") != 'tools/lib/rbtree.zig:test "rbtree findAddCached preserves duplicate ownership and leftmost cache"':
                issues.append("phase1_manifest:tools/lib/rbtree.zig:cached_find_add_unit_test_anchor:mismatch")
            if rbtree_note.get("cached_find_add_unit_test_contract") != "Direct Zig unit coverage keeps findAddCached() aligned so equal-key probes return the original resident node, distinct inserts still link into the cached tree, and RootCached continues to expose the same leftmost node as the underlying tree root.":
                issues.append("phase1_manifest:tools/lib/rbtree.zig:cached_find_add_unit_test_contract:mismatch")
            if rbtree_note.get("iterator_unit_test_anchor") != 'tools/lib/rbtree.zig:test "rbtree iterateMatches streams only the duplicate range"':
                issues.append("phase1_manifest:tools/lib/rbtree.zig:iterator_unit_test_anchor:mismatch")
            if rbtree_note.get("iterator_unit_test_contract") != "Direct Zig unit coverage keeps iterateMatches() aligned so duplicate-key iteration yields only the equal-key range and cleanly reports no match for missing keys.":
                issues.append("phase1_manifest:tools/lib/rbtree.zig:iterator_unit_test_contract:mismatch")
            if rbtree_note.get("reverse_unit_test_anchor") != 'tools/lib/rbtree.zig:test "rbtree iterateMatchesReverse streams only the duplicate range in reverse"':
                issues.append("phase1_manifest:tools/lib/rbtree.zig:reverse_unit_test_anchor:mismatch")
            if rbtree_note.get("reverse_unit_test_contract") != "Direct Zig unit coverage keeps findLast(), prevMatch(), and iterateMatchesReverse() aligned so reverse duplicate-key lookups start at the rightmost match, walk back through the equal-key range, and cleanly report no match for missing keys.":
                issues.append("phase1_manifest:tools/lib/rbtree.zig:reverse_unit_test_contract:mismatch")

    return issues


missing_files = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
if missing_files:
    fail("MISSING_PHASE1_FILES", missing_files)

fixture_issues = validate_fixture_shape()
if fixture_issues:
    fail("MISSING_PHASE1_FIXTURE_SHAPE", fixture_issues)

manifest_issues = validate_manifest_shape()
if manifest_issues:
    fail("MISSING_PHASE1_MANIFEST_SHAPE", manifest_issues)

texts = {name: read_text(rel) for name, (rel, _) in MARKER_GROUPS.items()}
missing_markers: list[str] = []
for name, (rel, markers) in MARKER_GROUPS.items():
    text = texts[name]
    for marker in markers:
        if marker not in text:
            missing_markers.append(f"{name}:{marker}")

if missing_markers:
    fail("MISSING_PHASE1_MARKERS", missing_markers)

workflow_text = texts["workflow"]
workflow_exact_line_issues = []
for line, expected_count in WORKFLOW_EXACT_LINES.items():
    actual_count = count_exact_line(workflow_text, line)
    if actual_count != expected_count:
        workflow_exact_line_issues.append(
            f"workflow_exact:{line}:expected_count={expected_count}:actual_count={actual_count}"
        )

if workflow_exact_line_issues:
    fail("MISSING_PHASE1_WORKFLOW_EXACT_LINES", workflow_exact_line_issues)

phase1_closure_text = texts["phase1_closure"]
phase1_closure_prefix_issues = []
for prefix, expected_count in PHASE1_CLOSURE_PREFIX_COUNTS.items():
    actual_count = count_prefixed_lines(phase1_closure_text, prefix)
    if actual_count != expected_count:
        phase1_closure_prefix_issues.append(
            f"closure_prefix:{prefix}:expected_count={expected_count}:actual_count={actual_count}"
        )

if phase1_closure_prefix_issues:
    fail("MISSING_PHASE1_CLOSURE_PREFIX_COUNTS", phase1_closure_prefix_issues)

marker_count = sum(len(markers) for _, markers in MARKER_GROUPS.values()) + len(PHASE1_CLOSURE_PREFIX_COUNTS)
print("PHASE1_VALIDATION=pass")
print(f"PHASE1_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
print(f"PHASE1_REQUIRED_MARKER_COUNT={marker_count}")

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
            "fixture.find_bit.tail_clamped_first",
            "fixture.find_bit.tail_and_mixed_next",
            "fixture.string.remove_spaces_nul_bytes",
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
            '"allocator_alias_unit_test_anchor"',
            "bitmap underscore allocator aliases preserve allocation and ownership semantics",
            '"allocator_alias_unit_test_contract"',
            "bitmap_alloc(), bitmap_zalloc(), and bitmap_free() aligned with bitmapAlloc(), bitmapZalloc(), and bitmapFree() for partial-word sizing, zero-filled allocation, and optional-handle reset semantics.",
        ],
    ),
    "find_bit": (
        "tools/lib/find_bit.zig",
        [
            "pub fn findFirstBit(addr: []const Word, nbits: usize) usize {",
            "pub fn find_first_bit(addr: []const Word, nbits: usize) usize {",
            'test "find next bit skips earlier matches in the same word"',
            'test "find next and bit skips earlier shared matches in the same word"',
            'test "empty and boundary scans return nbits"',
            'test "find underscore aliases preserve scan semantics"',
        ],
    ),
    "find_bit_harness": (
        "zigux/tests/fixtures/phase1_helpers_c_harness.c",
        [
            "unsigned long tail_bitmap[2] = {0, 1UL << 9};",
            "unsigned long tail_zero_bitmap[2] = {~0UL, BITMAP_LAST_WORD_MASK(BITS_PER_LONG + 5)};",
            "unsigned long tail_and_mixed[2] = {0, (1UL << 3) | (1UL << 9)};",
            '\\"tail_clamped_first\\":%lu,',
            '\\"tail_and_mixed_next\\":%lu',
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
            'test "memparse forwards the header-level string helper surface"',
        ],
    ),
    "string_manifest": (
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        [
            '"string.remove_spaces_nul"',
            '"string.remove_spaces_nul_bytes"',
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
            if bitmap_note.get("allocator_alias_unit_test_anchor") != 'tools/lib/bitmap.zig:test "bitmap underscore allocator aliases preserve allocation and ownership semantics"':
                issues.append("phase1_manifest:tools/lib/bitmap.zig:allocator_alias_unit_test_anchor:mismatch")
            if bitmap_note.get("allocator_alias_unit_test_contract") != "Direct Zig unit coverage keeps bitmap_alloc(), bitmap_zalloc(), and bitmap_free() aligned with bitmapAlloc(), bitmapZalloc(), and bitmapFree() for partial-word sizing, zero-filled allocation, and optional-handle reset semantics.":
                issues.append("phase1_manifest:tools/lib/bitmap.zig:allocator_alias_unit_test_contract:mismatch")
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

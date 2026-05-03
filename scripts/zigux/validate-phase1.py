#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


def repo_root() -> Path:
    override = os.environ.get("ZIGUX_PHASE1_ROOT")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[2]


ROOT = repo_root()

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

HELPERS = [
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

WORKFLOW_LINES = {
    "run: python3 scripts/zigux/validate-phase1.py": 1,
    "run: python3 scripts/zigux/validate-phase1-closure.py": 1,
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase1-bench.py": 1,
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase1-parity.py": 1,
    "run: python3 scripts/zigux/check-phase1-parity.py --self-test": 1,
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
            "PHASE1_FIND_BIT_MASK_UNIT_REVIEW=find_bit mask and sizing helpers keep Linux-style whole-word, partial-word, and wrapped-start boundaries reviewable without relying only on indirect scan coverage",
            "PHASE1_FIND_BIT_BOUNDARY_UNIT_REVIEW=find_bit empty and out-of-range scans return nbits for zero-length bitmaps, start-at-nbits searches, and fully set zero-bit windows that must not report past the declared range",
            "PHASE1_FIND_BIT_LOW_LEVEL_UNIT_REVIEW=find_bit low-level underscore entry points preserve same-word inclusive starts and tail-clamped set, shared-bit, and zero-bit scan behavior across the same caller-selected bit windows as the public helpers",
            "PHASE1_FIND_BIT_SMALL_BITMAP_UNIT_REVIEW=find_bit single-word set zero and shared-bit scans keep Linux small-bitmap semantics aligned by masking out-of-range tail bits while preserving inclusive in-range matches inside one word",
            "PHASE1_FIND_BIT_TAIL_START_UNIT_REVIEW=find_bit tail-clamped set zero and shared-bit scans keep the last in-range bit reachable from an inclusive start while later starts still return nbits instead of leaking the out-of-range tail",
            "PHASE1_FIND_BIT_ZERO_SIZED_UNIT_REVIEW=find_bit zero-length set zero and shared-bit scans return 0 even when backing words are populated so declared nbits stays authoritative over caller storage",
            "PHASE1_STRING_MEMPARSE_UNIT_REVIEW=string memparse preserves decimal, hexadecimal, suffix-bearing, and invalid inputs without changing the parsed value or rest pointer contract",
            "PHASE1_RBTREE_CACHED_FINDADD_UNIT_REVIEW=",
            "PHASE1_RBTREE_BENCH_KEYS=PHASE1_BENCH_RBTREE_CHECKSUM,PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM,PHASE1_BENCH_RBTREE_CACHED_CHECKSUM,PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM,PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
        ],
    ),
    "bench": (
        "zigux/tests/phase1_bench.zig",
        [
            "const bitmap_result = bitmapBench();",
            "const find_bit_result = findBitBench();",
            "const find_zero_bit_result = findZeroBitBench();",
            "const find_and_bit_result = findAndBitBench();",
            "const rbtree_result = rbtreeBench();",
            "PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM",
            "PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM",
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
            "PHASE1_BENCH_STRING_MEMPARSE_CHECKSUM",
        ],
    ),
    "bench_expectations": (
        "zigux/tests/fixtures/phase1_bench_expectations.json",
        [
            '"PHASE1_BENCH_STRING_BOOL_TRIM_CHECKSUM"',
            '"PHASE1_BENCH_STRING_MEMCHR_CHECKSUM"',
            '"PHASE1_BENCH_STRING_COMPARE_CHECKSUM"',
            '"PHASE1_BENCH_STRING_MEMPARSE_CHECKSUM"',
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
}

PHASE1_CLOSURE_PREFIX_COUNTS = {
    "- `tools/lib/bitmap.zig` closure includes committed C-backed parity coverage": 1,
    "- `tools/lib/find_bit.zig` closure includes committed C-backed parity coverage": 1,
    "- `tools/lib/rbtree.zig` closure includes committed C-backed parity coverage": 1,
    "- `tools/lib/string.zig` closure includes committed C-backed parity coverage": 1,
}

MANIFEST_EXPECTATIONS = {
    "tools/lib/string.zig": {
        "unit_test_anchor": 'tools/lib/string.zig:test "memchrInv scans aligned and misaligned long buffers"',
        "unit_test_contract": "Direct Zig unit coverage keeps memchrInv honest across aligned and misaligned long buffers, the short-versus-long cutoff boundary, earliest dirty-word mismatch selection, high-bit byte scans, and zero-value word-boundary scans beyond the short C-backed fixture cases.",
        "cstring_unit_test_anchor": 'tools/lib/string.zig:test "strlcpy stops at the first embedded NUL in the source"',
        "cstring_unit_test_contract": "Direct Zig unit coverage keeps strlcpy aligned with C-string semantics by stopping at the first embedded NUL, preserving truncation behavior, and leaving zero-sized destinations untouched.",
        "strscpy_unit_test_anchor": 'tools/lib/string.zig:test "strscpy mirrors bounded kernel copy semantics"',
        "strscpy_unit_test_contract": "Direct Zig unit coverage keeps strscpy aligned with bounded kernel copy semantics for exact-fit, truncation, embedded-NUL, and zero-sized destination cases.",
        "equality_unit_test_anchor": 'tools/lib/string.zig:test "streq matches C-string equality semantics"',
        "equality_unit_test_contract": "Direct Zig unit coverage keeps strEq() and streq() aligned with C-string equality semantics for exact, empty, length-mismatched, case-sensitive, and embedded-NUL comparisons.",
        "sysfs_unit_test_anchor": 'tools/lib/string.zig:test "sysfsStreq treats a trailing newline as equivalent to C-string termination"',
        "sysfs_unit_test_contract": "Direct Zig unit coverage keeps sysfsStreq() and sysfs_streq() aligned by treating a single trailing newline as equivalent to C-string termination while still rejecting non-terminal newline and content mismatches.",
        "alias_unit_test_anchor": 'tools/lib/string.zig:test "trimSpaces and strim trim trailing whitespace before an embedded NUL"',
        "alias_unit_test_contract": "Direct Zig unit coverage keeps trimSpaces and strim aligned with C-string semantics by trimming trailing whitespace that appears before the first embedded NUL while preserving bytes beyond that terminator.",
        "memparse_unit_test_anchor": 'tools/lib/string.zig:test "memparse forwards the header-level string helper surface"',
        "memparse_unit_test_contract": "Direct Zig unit coverage keeps memparse aligned by preserving decimal, hexadecimal, suffix-bearing, invalid, and binary-unit-tail inputs including optional trailing B forms without changing the parsed value or rest pointer contract.",
        "prefix_unit_test_anchor": 'tools/lib/string.zig:test "strstarts matches kernel prefix semantics"',
        "prefix_unit_test_contract": "Direct Zig unit coverage keeps strStarts and strstarts aligned with kernel-style prefix semantics for exact, empty-prefix, shorter-input, and case-sensitive comparisons.",
        "prefix_length_unit_test_anchor": 'tools/lib/string.zig:test "strHasPrefix returns the matched prefix length with C-string semantics"',
        "prefix_length_unit_test_contract": "Direct Zig unit coverage keeps strHasPrefix and str_has_prefix aligned by returning the matched C-string prefix length for exact and embedded-NUL prefixes while rejecting mismatches and longer prefixes.",
        "suffix_unit_test_anchor": 'tools/lib/string.zig:test "str_ends_with matches kernel suffix semantics"',
        "suffix_unit_test_contract": "Direct Zig unit coverage keeps strEndsWith, str_ends_with, and strends aligned with kernel-style suffix semantics for exact, empty-suffix, shorter-input, and case-sensitive comparisons.",
    },
    "tools/lib/find_bit.zig": {
        "tail_start_unit_test_anchor": 'tools/lib/find_bit.zig:test "tail scans keep the last in-range bit reachable from an inclusive start"',
        "tail_start_unit_test_contract": "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit, while later starts still return `nbits` instead of leaking the out-of-range tail.",
        "tail_word_boundary_unit_test_contract": "Direct Zig unit coverage keeps set, zero, and shared-bit tail scans aligned when the search starts exactly at the first tail-word bit index, so the first in-range tail match remains reachable without rereading an earlier full-word result.",
        "zero_sized_unit_test_anchor": 'tools/lib/find_bit.zig:test "zero-sized scans ignore populated backing words"',
        "zero_sized_unit_test_contract": "Direct Zig unit coverage keeps zero-length set, zero, and shared-bit scans aligned by returning `0` even when backing words are populated, so declared `nbits` stays authoritative over caller storage.",
    },
    "tools/lib/rbtree.zig": {
        "summary": "Committed C-backed parity coverage includes ordered forward and reverse traversal plus replaceNode, eraseInit, postorder traversal, and detached-node state checks, while Linux-style rb_* alias parity remains explicitly out of scope for this closed Phase 1 tranche.",
        "cached_find_add_unit_test_anchor": 'tools/lib/rbtree.zig:test "rbtree findAddCached preserves duplicate ownership and leftmost cache"',
        "cached_find_add_unit_test_contract": "Direct Zig unit coverage keeps findAddCached() aligned so equal-key probes return the original resident node, distinct inserts still link into the cached tree, and RootCached continues to expose the same leftmost node as the underlying tree root.",
        "postorder_safe_rebalance_unit_test_anchor": 'tools/lib/rbtree.zig:test "rbtree iteratePostorderSafe survives erase-driven rebalancing"',
    },
}


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def fail(block: str, items: list[str]) -> int:
    print("PHASE1_VALIDATION=fail")
    print(f"{block}_START")
    for item in items:
        print(item)
    print(f"{block}_END")
    return 1


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
        missing = sorted(expected_keys - actual)
        for key in missing:
            issues.append(f"phase1_fixture:{section}:{key}")
    return issues


def validate_manifest_shape() -> list[str]:
    issues: list[str] = []
    manifest = json.loads(read_text("zigux/tests/fixtures/phase1_helper_manifest.json"))
    if manifest.get("phase") != "Phase 1":
        issues.append("phase1_manifest:phase")
    if manifest.get("status") != "closed":
        issues.append("phase1_manifest:status")
    if manifest.get("helper_count") != 13:
        issues.append("phase1_manifest:helper_count")
    if manifest.get("helpers") != HELPERS:
        issues.append("phase1_manifest:helpers")

    notes = manifest.get("helper_review_notes")
    if not isinstance(notes, dict):
        return issues + ["phase1_manifest:helper_review_notes"]

    for helper, expected_fields in MANIFEST_EXPECTATIONS.items():
        helper_note = notes.get(helper)
        if not isinstance(helper_note, dict):
            issues.append(f"phase1_manifest:{helper}:expected_object")
            continue
        for key, expected in expected_fields.items():
            if helper_note.get(key) != expected:
                issues.append(f"phase1_manifest:{helper}:{key}:mismatch")
    return issues


def validate_marker_groups() -> list[str]:
    issues: list[str] = []
    texts = {name: read_text(rel) for name, (rel, _) in MARKER_GROUPS.items()}
    for name, (_, markers) in MARKER_GROUPS.items():
        text = texts[name]
        for marker in markers:
            if marker not in text:
                issues.append(f"{name}:{marker}")

    workflow_text = texts["workflow"]
    for line, expected_count in WORKFLOW_LINES.items():
        actual_count = sum(1 for raw in workflow_text.splitlines() if raw.strip() == line)
        if actual_count != expected_count:
            issues.append(
                f"workflow_exact:{line}:expected_count={expected_count}:actual_count={actual_count}"
            )

    closure_text = texts["phase1_closure"]
    for prefix, expected_count in PHASE1_CLOSURE_PREFIX_COUNTS.items():
        actual_count = sum(1 for raw in closure_text.splitlines() if raw.strip().startswith(prefix))
        if actual_count != expected_count:
            issues.append(
                f"closure_prefix:{prefix}:expected_count={expected_count}:actual_count={actual_count}"
            )
    return issues


def main() -> int:
    missing_files = [rel for rel in REQUIRED_FILES if not (ROOT / rel).exists()]
    if missing_files:
        return fail("MISSING_PHASE1_FILES", missing_files)

    fixture_issues = validate_fixture_shape()
    if fixture_issues:
        return fail("MISSING_PHASE1_FIXTURE_SHAPE", fixture_issues)

    manifest_issues = validate_manifest_shape()
    if manifest_issues:
        return fail("MISSING_PHASE1_MANIFEST_SHAPE", manifest_issues)

    marker_issues = validate_marker_groups()
    if marker_issues:
        return fail("MISSING_PHASE1_MARKERS", marker_issues)

    marker_count = sum(len(markers) for _, markers in MARKER_GROUPS.values()) + len(
        PHASE1_CLOSURE_PREFIX_COUNTS
    )
    print("PHASE1_VALIDATION=pass")
    print(f"PHASE1_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_REQUIRED_MARKER_COUNT={marker_count}")
    return 0


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-validator-") as tmp:
        root = Path(tmp)
        for rel in REQUIRED_FILES:
            path = root / rel
            if rel.endswith(".json"):
                continue
            write(path, "// marker fixture\n")

        for group_name, (rel, markers) in MARKER_GROUPS.items():
            body = "\n".join(markers) + "\n"
            if group_name == "workflow":
                body += "\n".join(WORKFLOW_LINES.keys()) + "\n"
            if group_name == "phase1_closure":
                body += "\n".join(PHASE1_CLOSURE_PREFIX_COUNTS.keys()) + "\n"
            write(root / rel, body)

        write(root / "zigux/tests/fixtures/phase1_helpers.json", json.dumps({k: {x: 1 for x in v} for k, v in FIXTURE_SHAPE.items()}, indent=2) + "\n")
        helper_notes = {k: {} for k in HELPERS}
        for helper, fields in MANIFEST_EXPECTATIONS.items():
            helper_notes[helper] = dict(fields)
        manifest = {
            "phase": "Phase 1",
            "status": "closed",
            "helper_count": 13,
            "helpers": HELPERS,
            "helper_review_notes": helper_notes,
        }
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        write(
            root / "zigux/tests/fixtures/phase1_bench_expectations.json",
            json.dumps(
                {
                    "status": "pass",
                    "iterations": {
                        "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
                    },
                    "exact_checksums": {
                        "PHASE1_BENCH_STRING_BOOL_TRIM_CHECKSUM": 500000,
                        "PHASE1_BENCH_STRING_MEMCHR_CHECKSUM": 2400000,
                        "PHASE1_BENCH_STRING_COMPARE_CHECKSUM": 360000,
                        "PHASE1_BENCH_STRING_MEMPARSE_CHECKSUM": 437855789,
                        "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 1484000,
                    },
                    "checksums": [],
                },
                indent=2,
            )
            + "\n",
        )

        env = dict(os.environ)
        env["ZIGUX_PHASE1_ROOT"] = str(root)
        code = os.spawnve(os.P_WAIT, sys.executable, [sys.executable, __file__], env)
        if code != 0:
            print("PHASE1_VALIDATOR_SELF_TEST=fail")
            return 1

        manifest["helper_review_notes"]["tools/lib/string.zig"]["memparse_unit_test_contract"] = "old wording"
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        code = os.spawnve(os.P_WAIT, sys.executable, [sys.executable, __file__], env)
        if code == 0:
            print("PHASE1_VALIDATOR_SELF_TEST=fail")
            return 1

    print("PHASE1_VALIDATOR_SELF_TEST=pass")
    print("PHASE1_VALIDATOR_SELF_TEST_CASE_COUNT=2")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(self_test())
    raise SystemExit(main())

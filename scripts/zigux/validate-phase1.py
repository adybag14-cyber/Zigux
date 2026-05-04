#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def repo_root() -> Path:
    override = os.environ.get("ZIGUX_PHASE1_ROOT")
    if override:
        return Path(override)
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


ROOT = repo_root()

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/README.md",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-bitmap-validator-anchors.py",
    "scripts/zigux/check-phase1-find-bit-validator-anchors.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/check-phase1-validation-route-inventory.py",
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
        "bits_per_long", "first", "next_after_6", "next_after_word", "first_zero", "next_zero",
        "first_and", "next_and", "tail_clamped_first", "tail_clamped_next", "tail_zero_clamped_first",
        "tail_zero_clamped_next", "tail_and_clamped_first", "tail_and_clamped_next", "tail_and_mixed_first",
        "tail_and_mixed_next",
    },
    "bitmap": {
        "weight", "scnprintf", "and_result", "and_values", "andnot_result", "andnot_values",
        "or_values", "xor_values", "copy_nbits", "copy_values", "partial_xor_nbits",
        "partial_xor_masked_values", "scnprintf_empty_len", "scnprintf_empty_bytes", "alloc_nbits",
        "alloc_values", "zalloc_nbits", "zalloc_values", "equal", "intersects", "subset",
        "range_after_set", "range_after_clear", "full_after_fill", "empty_after_zero",
        "scnprintf_trunc_len", "scnprintf_trunc",
    },
    "string": {
        "strtobool_y", "strtobool_on", "strtobool_zero", "strtobool_off", "strtobool_invalid",
        "strlcpy_len", "strlcpy_buffer", "skip_spaces", "trim_spaces", "remove_spaces",
        "remove_spaces_nul", "remove_spaces_nul_bytes", "replace_char", "replace_char_end",
        "memchr_inv_index", "memchr_inv_none",
    },
    "rbtree": {
        "empty_root", "insert_order", "reverse_order", "replace_order", "erase_init_order",
        "postorder_count", "erase_init_node_empty", "cleared_node_empty",
    },
    "argv_split": {"argc", "argv", "blank_argc"},
    "cmdline": {"decimal_k", "hex_m", "octal_k", "invalid", "kib", "mb", "gib", "lowercase_kib"},
    "ctype": {
        "mask_A", "mask_a", "mask_space", "isalnum_A", "isalpha_z", "isdigit_7", "isspace_tab",
        "isxdigit_f", "ispunct_bang", "tolower_A", "toupper_z", "isodigit_7", "isodigit_8",
    },
    "hweight": {"w8", "w16", "w32", "w64", "wlong"},
    "list_sort": {"tri_sorted_keys", "tri_sorted_ordinals", "bool_sorted_keys", "bool_sorted_ordinals"},
    "zalloc": {"zeroed", "freed_is_null", "value_zeroed", "value_freed_is_null"},
    "str_error_r": {"enoent", "unknown"},
    "slab": {
        "null_without_reclaim", "alloc_count_after_kmalloc", "zero_after_kmalloc",
        "alloc_count_after_kmalloc_free", "array_zeroed", "alloc_count_after_kmalloc_array",
        "alloc_count_after_kmalloc_array_free", "slab_is_available",
    },
    "vsprintf": {"scnprintf_text", "scnprintf_len", "pad_text", "pad_len"},
}

DOCS_ROOT_MARKERS = [
    "- `Documentation/zigux/phase1-closure.md` remains the dedicated closure packet for the bounded host-side `tools/lib/*.zig` helper tranche, and `zigux/tests/fixtures/phase1_helper_manifest.json` plus `zigux/tests/phase1_helpers.zig` keep the closed helper inventory and parity-backed replay surface explicit from the docs root.",
    "- `python3 scripts/zigux/validate-phase1.py`, `python3 scripts/zigux/validate-phase1-closure.py`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` are the current validator-first and replay entrypoints for that bounded host-side helper packet.",
]

REVIEW_CHECKLIST_MARKERS = [
    "- if the change touches the closed Phase 1 host-helper packet, do `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-bitmap-validator-anchors.py`, `scripts/zigux/check-phase1-find-bit-validator-anchors.py`, `scripts/zigux/check-phase1-route-summary-counts.py`, `scripts/zigux/check-phase1-validation-route-inventory.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/phase1_helpers.zig`, and `zigux/tests/phase1_bench.zig` still agree on the same closed helper inventory, validator-first replay path, and fail-closed checker stack?",
]

SCRIPTS_ROOT_MARKERS = [
    "- `validate-phase1.py` is the validator-first entrypoint for the closed host-helper packet around `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/string.zig`, and `tools/lib/rbtree.zig` plus the bounded supporting helpers and committed `zigux/tests/fixtures/phase1_helpers.json` corpus.",
    "- `check-phase1-bitmap-validator-anchors.py --self-test`, `check-phase1-bitmap-validator-anchors.py`, `check-phase1-find-bit-validator-anchors.py --self-test`, `check-phase1-find-bit-validator-anchors.py`, `check-phase1-route-summary-counts.py --self-test`, `check-phase1-route-summary-counts.py`, `check-phase1-validation-route-inventory.py --self-test`, `check-phase1-validation-route-inventory.py`, `check-phase1-parity.py --self-test`, `check-phase1-parity.py`, `check-phase1-bench.py --self-test`, `check-phase1-bench.py`, `validate-phase1-closure.py --self-test`, and `validate-phase1-closure.py` are the bounded fail-closed review hooks around that same closed Phase 1 helper tranche.",
]

PHASE1_CLOSURE_MARKERS = [
    "PHASE1_BITMAP_HEADER_ALIAS_UNIT_REVIEW=bitmap bitmap_zero bitmap_fill bitmap_copy bitmap_empty and bitmap_full stay aligned with zero fill copy empty and full for active-word clearing partial-tail fill masking copied-tail preservation and predicate results across the same declared bit window",
    "PHASE1_BITMAP_ALIAS_UNIT_REVIEW=bitmap underscore alias entry points preserve the same caller-selected window semantics as the camelCase helpers for weight bitwise range and formatting operations",
    "PHASE1_BITMAP_ALLOCATOR_ALIAS_UNIT_REVIEW=bitmap bitmap_alloc bitmap_zalloc and bitmap_free stay aligned with bitmapAlloc bitmapZalloc and bitmapFree for partial-word sizing zero-filled allocation and optional-handle reset semantics",
    "PHASE1_BITMAP_XOR_UNIT_REVIEW=bitmap xorBits multiword-tail coverage proves callers can clamp the last word back to the in-range bits without leaking the out-of-range tail",
    "PHASE1_BITMAP_TAIL_MASK_UNIT_REVIEW=bitmap tail-masked reduction helpers ignore out-of-range differences while preserving the in-range window for andBits, andNotBits, equal, intersects, and subset",
    "PHASE1_BITMAP_ZERO_BIT_UNIT_REVIEW=bitmap zero-length helper calls stay side-effect free so zero fill copy copyClearTail orBits xorBits scans and formatting leave caller-owned buffers untouched when nbits is zero",
    "PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap bitmap_scnprintf keeps a non-empty caller buffer untouched when no bits are set, matching the committed empty-bitmap parity fixture contract",
    "PHASE1_FIND_BIT_SMALL_BITMAP_UNIT_REVIEW=find_bit single-word set zero and shared-bit scans keep Linux small-bitmap semantics aligned by masking out-of-range tail bits while preserving inclusive in-range matches inside one word",
    "PHASE1_FIND_BIT_LOW_LEVEL_UNIT_REVIEW=find_bit low-level underscore entry points preserve same-word inclusive starts and tail-clamped set, shared-bit, and zero-bit scan behavior across the same caller-selected bit windows as the public helpers",
    "PHASE1_FIND_BIT_TAIL_START_UNIT_REVIEW=find_bit tail-clamped set zero and shared-bit scans keep the last in-range bit reachable from an inclusive start while later starts still return nbits instead of leaking the out-of-range tail",
    "PHASE1_FIND_BIT_TAIL_WORD_BOUNDARY_UNIT_REVIEW=find_bit tail-clamped set zero and shared-bit scans keep the first in-range tail-word match reachable when the search starts exactly at the tail-word boundary instead of rereading an earlier full-word result",
    "PHASE1_FIND_BIT_ZERO_SIZED_UNIT_REVIEW=find_bit zero-length set zero and shared-bit scans return 0 even when backing words are populated so declared nbits stays authoritative over caller storage",
    "PHASE1_STRING_MEMPARSE_UNIT_REVIEW=string memparse preserves decimal, hexadecimal, suffix-bearing, invalid, and binary-unit-tail inputs including optional trailing B forms without changing the parsed value or rest pointer contract",
    "PHASE1_RBTREE_CACHED_DUPLICATE_UNIT_REVIEW=rbtree RootCached duplicate minima stay aligned when eraseCached promotes the next equal-key minimum and replaceNodeCached leaves the cached first node unchanged for non-leftmost replacement",
    "PHASE1_RBTREE_CACHED_FINDADD_UNIT_REVIEW=rbtree findAddCached returns the original equal-key resident node, still links new distinct keys into the cached tree, and keeps the cached first node aligned with the underlying tree root",
    "PHASE1_RBTREE_ITERATE_UNIT_REVIEW=rbtree iterateMatches yields only the equal-key duplicate range and cleanly reports no match for missing keys",
    "PHASE1_RBTREE_REVERSE_UNIT_REVIEW=rbtree findLast, prevMatch, and iterateMatchesReverse keep reverse duplicate-key lookup walks aligned from the rightmost match back through the equal-key range while still reporting no match for missing keys",
]

WORKFLOW_LINES = {
    "run: python3 scripts/zigux/validate-phase1.py": 1,
    "run: python3 scripts/zigux/validate-phase1.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py": 1,
    "run: python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py": 1,
    "run: python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py": 1,
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase1-validation-route-inventory.py": 1,
    "run: python3 scripts/zigux/check-phase1-validation-route-inventory.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase1-parity.py": 1,
    "run: python3 scripts/zigux/check-phase1-parity.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase1-bench.py": 1,
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test": 1,
    "run: python3 scripts/zigux/validate-phase1-closure.py": 1,
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test": 1,
}

MANIFEST_EXPECTATIONS = {
    "tools/lib/bitmap.zig": {
        "header_alias_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap header-style aliases preserve zero fill copy and predicate semantics"',
        "header_alias_unit_test_contract": "Direct Zig unit coverage keeps bitmap_zero(), bitmap_fill(), bitmap_copy(), bitmap_empty(), and bitmap_full() aligned with zero(), fill(), copy(), empty(), and full() for active-word clearing, partial-tail fill masking, copied-tail preservation, and predicate results across the same declared bit window.",
        "alias_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap underscore aliases preserve bitmap helper semantics"',
        "alias_unit_test_contract": "Direct Zig unit coverage keeps bitmap_weight(), bitmap_and(), bitmap_andnot(), bitmap_or(), bitmap_xor(), bitmap_equal(), bitmap_intersects(), bitmap_subset(), bitmap_set(), bitmap_clear(), and bitmap_scnprintf() aligned with the camelCase helpers across the same caller-selected bit window.",
        "allocator_alias_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap underscore allocator aliases preserve allocation and ownership semantics"',
        "allocator_alias_unit_test_contract": "Direct Zig unit coverage keeps bitmap_alloc(), bitmap_zalloc(), and bitmap_free() aligned with bitmapAlloc(), bitmapZalloc(), and bitmapFree() for partial-word sizing, zero-filled allocation, and optional-handle reset semantics.",
        "double_underscore_alias_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap double-underscore aliases preserve core helper semantics"',
        "double_underscore_alias_unit_test_contract": "Direct Zig unit coverage keeps __bitmap_weight(), __bitmap_or(), __bitmap_and(), __bitmap_andnot(), __bitmap_xor(), __bitmap_equal(), __bitmap_intersects(), __bitmap_subset(), __bitmap_set(), and __bitmap_clear() aligned with the core helpers across the same caller-selected bit window.",
        "size_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap size helpers round up to full words in bytes"',
        "size_unit_test_contract": "Direct Zig unit coverage keeps bitmapSize() and bitmap_size() aligned by rounding zero-length, partial-word, and multiword bit counts up to the same full-word byte footprint.",
        "xor_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap xor across a multiword tail still lets callers clamp the last word"',
        "xor_unit_test_contract": "Direct Zig unit coverage keeps xorBits() aligned across a multiword tail by proving callers can clamp the last word back to the in-range bits without leaking the out-of-range tail.",
        "tail_mask_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap tail-masked helpers ignore out-of-range differences"',
        "tail_mask_unit_test_contract": "Direct Zig unit coverage keeps andBits(), andNotBits(), equal(), intersects(), and subset() aligned by masking out-of-range tail differences while preserving the declared in-range window.",
        "zero_bit_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap zero-bit helpers stay explicit no-ops"',
        "zero_bit_unit_test_contract": "Direct Zig unit coverage keeps zero-length helper calls explicit and side-effect free so zero(), fill(), copy(), copyClearTail(), orBits(), xorBits(), scans, and formatting all leave caller-owned buffers untouched when nbits is zero.",
        "empty_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
        "empty_unit_test_contract": "Direct Zig unit coverage keeps bitmap_scnprintf() from mutating a non-empty caller buffer when no bits are set, matching the committed empty-bitmap parity fixture contract.",
    },
    "tools/lib/find_bit.zig": {
        "small_bitmap_unit_test_anchor": 'tools/lib/find_bit.zig:test "single-word scans keep linux small-bitmap semantics"',
        "small_bitmap_unit_test_contract": "Direct Zig unit coverage keeps single-word set, zero, and shared-bit scans aligned with Linux small-bitmap semantics by masking out-of-range tail bits while preserving inclusive in-range matches inside one word.",
        "low_level_unit_test_anchor": 'tools/lib/find_bit.zig:test "find low-level underscore entry points preserve same-word and tail-clamped scan semantics"',
        "low_level_unit_test_contract": "Direct Zig unit coverage keeps _find_first_bit(), _find_first_and_bit(), _find_first_zero_bit(), _find_next_bit(), _find_next_and_bit(), and _find_next_zero_bit() aligned with the public scan helpers across same-word inclusive starts and tail-clamped caller-selected bit windows.",
        "tail_start_unit_test_anchor": 'tools/lib/find_bit.zig:test "tail scans keep the last in-range bit reachable from an inclusive start"',
        "tail_start_unit_test_contract": "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit, while later starts still return nbits instead of leaking the out-of-range tail.",
        "tail_word_boundary_unit_test_anchor": 'tools/lib/find_bit.zig:test "tail scans honor an exact tail-word boundary start"',
        "tail_word_boundary_unit_test_contract": "Direct Zig unit coverage keeps set, zero, and shared-bit tail scans aligned when the search starts exactly at the first tail-word bit index, so the first in-range tail match remains reachable without rereading an earlier full-word result.",
        "zero_sized_unit_test_anchor": 'tools/lib/find_bit.zig:test "zero-sized scans ignore populated backing words"',
        "zero_sized_unit_test_contract": "Direct Zig unit coverage keeps zero-length set, zero, and shared-bit scans aligned by returning 0 even when backing words are populated, so declared nbits stays authoritative over caller storage.",
    },
    "tools/lib/string.zig": {
        "memparse_unit_test_contract": "Direct Zig unit coverage keeps memparse aligned by preserving decimal, hexadecimal, suffix-bearing, invalid, and binary-unit-tail inputs including optional trailing B forms without changing the parsed value or rest pointer contract.",
        "prefix_length_unit_test_anchor": 'tools/lib/string.zig:test "strHasPrefix returns the matched prefix length with C-string semantics"',
    },
    "tools/lib/rbtree.zig": {
        "cached_duplicate_unit_test_anchor": 'tools/lib/rbtree.zig:test "rbtree cached root tracks duplicate minima through erase and non-leftmost replace"',
        "cached_duplicate_unit_test_contract": "Direct Zig unit coverage keeps RootCached duplicate minima aligned when eraseCached() promotes the next equal-key minimum and replaceNodeCached() leaves the cached first node unchanged for non-leftmost replacement.",
        "cached_findadd_unit_test_anchor": 'tools/lib/rbtree.zig:test "rbtree findAddCached preserves duplicate ownership and leftmost cache"',
        "cached_findadd_unit_test_contract": "Direct Zig unit coverage keeps findAddCached() aligned by returning the original equal-key resident node, still linking new distinct keys into the cached tree, and keeping the cached first node aligned with the underlying tree root.",
        "iterate_unit_test_anchor": 'tools/lib/rbtree.zig:test "rbtree iterateMatches streams only the duplicate range"',
        "iterate_unit_test_contract": "Direct Zig unit coverage keeps iterateMatches() yielding only the equal-key duplicate range and cleanly reporting no match for missing keys.",
        "reverse_unit_test_anchor": 'tools/lib/rbtree.zig:test "rbtree iterateMatchesReverse streams only the duplicate range in reverse"',
        "reverse_unit_test_contract": "Direct Zig unit coverage keeps findLast(), prevMatch(), and iterateMatchesReverse() aligned from the rightmost duplicate back through the equal-key range while still reporting no match for missing keys.",
    },
}


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def fail(label: str, items: list[str]) -> int:
    print("PHASE1_VALIDATION=fail")
    print(f"{label}_START")
    for item in items:
        print(item)
    print(f"{label}_END")
    return 1


def validate_fixture_shape() -> list[str]:
    issues: list[str] = []
    fixture = json.loads(read_text("zigux/tests/fixtures/phase1_helpers.json"))
    for section, keys in FIXTURE_SHAPE.items():
        data = fixture.get(section)
        if not isinstance(data, dict):
            issues.append(f"fixture:{section}:missing_object")
            continue
        missing = sorted(keys - set(data.keys()))
        for key in missing:
            issues.append(f"fixture:{section}:{key}:missing")
    return issues


def validate_manifest_shape() -> list[str]:
    issues: list[str] = []
    manifest = json.loads(read_text("zigux/tests/fixtures/phase1_helper_manifest.json"))
    if manifest.get("phase") != "Phase 1":
        issues.append("manifest:phase:mismatch")
    if manifest.get("status") != "closed":
        issues.append("manifest:status:mismatch")
    if manifest.get("helper_count") != len(HELPERS):
        issues.append("manifest:helper_count:mismatch")
    if manifest.get("helpers") != HELPERS:
        issues.append("manifest:helpers:mismatch")
    review_notes = manifest.get("helper_review_notes")
    if not isinstance(review_notes, dict):
        return issues + ["manifest:helper_review_notes:missing_object"]
    for helper, fields in MANIFEST_EXPECTATIONS.items():
        note = review_notes.get(helper)
        if not isinstance(note, dict):
            issues.append(f"manifest:{helper}:missing_object")
            continue
        for field, expected in fields.items():
            if note.get(field) != expected:
                issues.append(f"manifest:{helper}:{field}:mismatch")
    return issues


def validate_markers() -> list[str]:
    issues: list[str] = []
    docs_root = read_text("Documentation/zigux/README.md")
    for marker in DOCS_ROOT_MARKERS:
        count = sum(1 for raw in docs_root.splitlines() if raw.strip() == marker)
        if count != 1:
            issues.append(f"docs_root:{marker}:expected_count=1:actual_count={count}")
    review_checklist = read_text("Documentation/zigux/review-checklist.md")
    for marker in REVIEW_CHECKLIST_MARKERS:
        count = sum(1 for raw in review_checklist.splitlines() if raw.strip() == marker)
        if count != 1:
            issues.append(f"review_checklist:{marker}:expected_count=1:actual_count={count}")
    scripts_root = read_text("scripts/zigux/README.md")
    for marker in SCRIPTS_ROOT_MARKERS:
        count = sum(1 for raw in scripts_root.splitlines() if raw.strip() == marker)
        if count != 1:
            issues.append(f"scripts_root:{marker}:expected_count=1:actual_count={count}")
    closure = read_text("Documentation/zigux/phase1-closure.md")
    for marker in PHASE1_CLOSURE_MARKERS:
        if marker not in closure:
            issues.append(f"phase1_closure:{marker}")
    workflow = read_text(".github/workflows/zigux-bootstrap.yml")
    for line, expected_count in WORKFLOW_LINES.items():
        actual_count = sum(1 for raw in workflow.splitlines() if raw.strip() == line)
        if actual_count != expected_count:
            issues.append(f"workflow_exact:{line}:expected_count={expected_count}:actual_count={actual_count}")
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
    marker_issues = validate_markers()
    if marker_issues:
        return fail("MISSING_PHASE1_MARKERS", marker_issues)
    print("PHASE1_VALIDATION=pass")
    print(f"PHASE1_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_REQUIRED_MARKER_COUNT={len(DOCS_ROOT_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(SCRIPTS_ROOT_MARKERS) + len(PHASE1_CLOSURE_MARKERS) + len(WORKFLOW_LINES)}")
    return 0


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def expect_failure(root: Path, expected: str) -> None:
    env = dict(os.environ)
    env["ZIGUX_PHASE1_ROOT"] = str(root)
    result = subprocess.run([sys.executable, str(root / "scripts/zigux/validate-phase1.py")], env=env, capture_output=True, text=True, check=False)
    output = result.stdout + result.stderr
    if result.returncode == 0:
        raise SystemExit(f"phase1-self-test:expected_failure:{expected}")
    if expected not in output:
        raise SystemExit(f"phase1-self-test:missing_expected_output:expected={expected!r}:actual={output!r}")


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-validator-") as tmp:
        root = Path(tmp)
        for rel in REQUIRED_FILES:
            path = root / rel
            if rel.endswith(".json"):
                continue
            write(path, "// fixture\n")
        write(root / "scripts/zigux/validate-phase1.py", Path(__file__).read_text(encoding="utf-8"))
        write(root / "Documentation/zigux/README.md", "\n".join(DOCS_ROOT_MARKERS) + "\n")
        write(root / "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
        write(root / "scripts/zigux/README.md", "\n".join(SCRIPTS_ROOT_MARKERS) + "\n")
        write(root / "Documentation/zigux/phase1-closure.md", "\n".join(PHASE1_CLOSURE_MARKERS) + "\n")
        write(root / ".github/workflows/zigux-bootstrap.yml", "\n".join(WORKFLOW_LINES.keys()) + "\n")
        write(root / "zigux/tests/fixtures/phase1_helpers.json", json.dumps({k: {x: 1 for x in v} for k, v in FIXTURE_SHAPE.items()}, indent=2) + "\n")
        write(root / "zigux/tests/fixtures/phase1_bench_expectations.json", json.dumps({"status": "pass"}, indent=2) + "\n")
        helper_notes = {helper: {} for helper in HELPERS}
        for helper, fields in MANIFEST_EXPECTATIONS.items():
            helper_notes[helper] = dict(fields)
        manifest = {"phase": "Phase 1", "status": "closed", "helper_count": len(HELPERS), "helpers": HELPERS, "helper_review_notes": helper_notes}
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        env = dict(os.environ)
        env["ZIGUX_PHASE1_ROOT"] = str(root)
        code = os.spawnve(os.P_WAIT, sys.executable, [sys.executable, str(root / "scripts/zigux/validate-phase1.py")], env)
        if code != 0:
            print("PHASE1_VALIDATOR_SELF_TEST=fail")
            return 1
        docs = root / "Documentation/zigux/README.md"
        docs_text = docs.read_text(encoding="utf-8")
        docs.write_text(docs_text.replace(DOCS_ROOT_MARKERS[0] + "\n", "", 1), encoding="utf-8")
        expect_failure(root, DOCS_ROOT_MARKERS[0])
        write(docs, docs_text)
        review_checklist = root / "Documentation/zigux/review-checklist.md"
        review_checklist_text = review_checklist.read_text(encoding="utf-8")
        review_checklist.write_text(review_checklist_text.replace(REVIEW_CHECKLIST_MARKERS[0] + "\n", "", 1), encoding="utf-8")
        expect_failure(root, REVIEW_CHECKLIST_MARKERS[0])
        write(review_checklist, review_checklist_text)
        closure = root / "Documentation/zigux/phase1-closure.md"
        closure_text = closure.read_text(encoding="utf-8")
        closure.write_text(closure_text.replace(PHASE1_CLOSURE_MARKERS[0] + "\n", "", 1), encoding="utf-8")
        expect_failure(root, PHASE1_CLOSURE_MARKERS[0])
        write(closure, closure_text)
        workflow = root / ".github/workflows/zigux-bootstrap.yml"
        workflow_text = workflow.read_text(encoding="utf-8")
        workflow.write_text(workflow_text.replace("run: python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py\n", "", 1), encoding="utf-8")
        expect_failure(root, "workflow_exact:run: python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py:expected_count=1:actual_count=0")
        write(workflow, workflow_text)
        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["helper_review_notes"]["tools/lib/rbtree.zig"]["cached_duplicate_unit_test_anchor"] = 'tools/lib/rbtree.zig:test "rbtree cached root tracks duplicate minima across replace and erase"'
        write(manifest_path, json.dumps(data, indent=2) + "\n")
        expect_failure(root, "manifest:tools/lib/rbtree.zig:cached_duplicate_unit_test_anchor:mismatch")
        data["helper_review_notes"]["tools/lib/rbtree.zig"]["cached_duplicate_unit_test_anchor"] = MANIFEST_EXPECTATIONS["tools/lib/rbtree.zig"]["cached_duplicate_unit_test_anchor"]
        write(manifest_path, json.dumps(data, indent=2) + "\n")
        fixture_path = root / "zigux/tests/fixtures/phase1_helpers.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        del fixture["find_bit"]["tail_and_mixed_next"]
        write(fixture_path, json.dumps(fixture, indent=2) + "\n")
        expect_failure(root, "fixture:find_bit:tail_and_mixed_next:missing")
    print("PHASE1_VALIDATOR_SELF_TEST=pass")
    print("PHASE1_VALIDATOR_SELF_TEST_CASE_COUNT=6")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(self_test())
    raise SystemExit(main())

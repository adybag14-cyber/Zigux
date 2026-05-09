#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) >= 3 else _SELF_PATH.parent

EXPECTED_HELPERS = [
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

EXPECTED_LANE_SEQUENCING = {
    "shared_replay_parked_helpers": [
        "tools/lib/argv_split.zig",
        "tools/lib/cmdline.zig",
        "tools/lib/ctype.zig",
        "tools/lib/hweight.zig",
        "tools/lib/list_sort.zig",
        "tools/lib/slab.zig",
        "tools/lib/str_error_r.zig",
        "tools/lib/vsprintf.zig",
        "tools/lib/zalloc.zig",
    ],
    "direct_anchor_followup_helpers": [
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    ],
    "rule_summary": "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",
    "anti_overlap_rule": "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.",
}

REQUIRED_FILES = [
    *EXPECTED_HELPERS,
    "scripts/zigux/artifact_diff.py",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase1-installer-review-surfaces.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/validate-phase1-closure.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "zigux/Makefile",
    "zigux/tests/build.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
    "zigux/tests/fixtures/phase1_helpers.json",
]

DOC_MARKERS = {
    "docs_root_phase1_packet": [
        "Phase 1 notes\n- `Documentation/zigux/phase1-closure.md`\n- `scripts/zigux/README.md`\n- `scripts/zigux/install-zig.py`\n- `scripts/zigux/check-phase1-installer-review-surfaces.py`",
        "keep the closure, installer-backed workflow-viability replay, the dedicated installer-review alignment checker, bootstrap-workflow replay, and validator-first contract explicit from the docs root",
    ],
    "tests_root_phase1_packet": [
        "keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root, scripts root, and workflow replay surface",
        "`.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root",
    ],
    "review_checklist_phase1_packet": [
        "if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`",
        "`scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` still agree on the same closed helper tranche",
    ],
}

PHASE1_IMPORT_MARKERS = [
    '@import("argv_split")',
    '@import("bitmap")',
    '@import("cmdline")',
    '@import("ctype")',
    '@import("find_bit")',
    '@import("hweight")',
    '@import("list_sort")',
    '@import("rbtree")',
    '@import("slab")',
    '@import("str_error_r")',
    '@import("string")',
    '@import("vsprintf")',
    '@import("zalloc")',
    '@embedFile("fixtures/phase1_helpers.json")',
]

PHASE1_REPLAY_MARKERS = [
    "fixture.find_bit.inclusive_boundary_next",
    "fixture.find_bit.inclusive_boundary_zero",
    "fixture.find_bit.inclusive_boundary_and",
    "fixture.find_bit.past_nbits_next",
    "fixture.find_bit.past_nbits_zero",
    "fixture.find_bit.past_nbits_and",
    "fixture.find_bit.tail_clamped_first",
    "fixture.find_bit.tail_zero_clamped_next",
    "fixture.find_bit.tail_and_clamped_next",
    "fixture.find_bit.tail_clamped_last",
    "fixture.find_bit.tail_clamped_empty_last",
    "fixture.bitmap.scnprintf",
    "fixture.bitmap.truncated_scnprintf_len",
    "fixture.bitmap.truncated_scnprintf",
    "fixture.bitmap.terminator_only_scnprintf_len",
    "fixture.bitmap.terminator_only_nul",
    "fixture.bitmap.zero_length_scnprintf_len",
    "fixture.bitmap.partial_xor_nbits",
    "fixture.bitmap.partial_xor_masked_values",
    "fixture.string.replace_char",
    "fixture.string.replace_char_end",
    "fixture.string.replace_char_cstr_end",
    "fixture.string.replace_char_cstr_bytes",
    "fixture.string.memchr_inv_index",
    "fixture.string.memchr_inv_none",
    "fixture.rbtree.empty_root",
    "fixture.rbtree.insert_order",
    "fixture.rbtree.reverse_order",
    "fixture.rbtree.replace_order",
    "fixture.rbtree.erase_init_order",
    "fixture.rbtree.postorder_count",
    "fixture.rbtree.erase_init_node_empty",
    "fixture.rbtree.cleared_node_empty",
    "fixture.rbtree.find_found_key",
    "fixture.rbtree.find_missing",
    "fixture.rbtree.find_first_serial",
    "fixture.rbtree.next_match_serials",
    "fixture.rbtree.next_match_terminal_null",
]

HELPER_FOLLOWUP_TESTS = [
    'test "phase 1 string replaceChar stops at embedded NUL"',
    'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
]

SOURCE_MARKERS = {
    "find_bit_test_anchor": (
        "tools/lib/find_bit.zig",
        [
            'test "single-word next scans honor start masks"',
            'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
            'test "zero-bit windows return without reading bitmap words"',
            'test "zero-sized scans ignore populated backing words"',
            'test "next scans past nbits return without reading bitmap words"',
            'test "tail-word next set scans skip earlier in-range matches before clamping"',
            'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
            'test "low-level underscore aliases mirror the primary find helpers"',
        ],
    ),
    "bitmap_test_anchor": (
        "tools/lib/bitmap.zig",
        [
            'test "bitmap range helpers honor exact first-word boundaries"',
            'test "bitmap range helpers clamp the final partial word"',
            'test "bitmap predicates ignore out-of-range tail bits"',
            'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
            'test "bitmap scnprintf reports full length while truncating the buffer"',
            'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
            'test "bitmap copy aliases preserve tail clearing and extension semantics"',
            'test "bitmap copy alias preserves raw source words without tail clearing"',
            'test "bitmap copy and extend handles zero and aligned counts"',
            'test "bitmap zero-bit helpers stay explicit no-ops"',
            'test "bitmap Linux-style aliases mirror the primary helper surface"',
        ],
    ),
    "string_test_anchor": (
        "tools/lib/string.zig",
        [
            'test "memchr_inv mirrors memchrInv byte-search semantics"',
            'test "memchrInv follows the earliest dirty byte as long buffers change"',
            'test "memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment"',
            'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
            'test "memparse clamps explicit positive signed overflow"',
            'test "memparse applies suffixes before signed clamping"',
            'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
        ],
    ),
    "rbtree_test_anchor": (
        "tools/lib/rbtree.zig",
        [
            'test "rbtree inserts and traverses in sorted order"',
            'test "rbtree erase and replace keep traversal consistent"',
            'test "rbtree eraseInit detaches erased node"',
            'test "rbtree postorder and empty node helpers behave"',
            'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
            'test "rbtree nextMatch walks the duplicate range in order"',
            'test "rbtree matchIterator walks the duplicate range in order"',
            'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
            'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
            'test "rbtree cached root keeps the leftmost pointer in sync"',
            'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
            'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
            'test "rbtree eraseCached returns null for a singleton cached tree"',
            'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
            'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
        ],
    ),
}

EXPECTED_MANIFEST_HELPER_FIELDS = {
    "tools/lib/bitmap.zig": {
        "helper_test_anchors": [
            'test "bitmap predicates ignore out-of-range tail bits"',
            'test "bitmap range helpers clamp the final partial word"',
            'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
            'test "bitmap zero-bit binary helpers stay explicit identity operations"',
            'test "bitmap copy and extend handles zero and aligned counts"',
            'test "bitmap Linux-style aliases mirror the primary helper surface"',
        ],
        "first_word_boundary_anchor": 'test "bitmap range helpers honor exact first-word boundaries"',
        "final_partial_word_anchor": 'test "bitmap range helpers clamp the final partial word"',
        "predicate_tail_mask_anchor": 'test "bitmap predicates ignore out-of-range tail bits"',
        "parity_fixture_keys": [
            "scnprintf",
            "truncated_scnprintf_len",
            "truncated_scnprintf",
            "terminator_only_scnprintf_len",
            "terminator_only_nul",
            "zero_length_scnprintf_len",
        ],
        "partial_xor_review_fields": ["partial_xor_nbits", "partial_xor_masked_values"],
        "cross_word_scnprintf_anchor": 'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
        "scnprintf_truncation_anchor": 'test "bitmap scnprintf reports full length while truncating the buffer"',
        "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
        "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
        "copy_extend_zero_aligned_anchor": 'test "bitmap copy and extend handles zero and aligned counts"',
        "zero_bit_noop_anchor": 'test "bitmap zero-bit helpers stay explicit no-ops"',
        "zero_bit_binary_identity_anchor": 'test "bitmap zero-bit binary helpers stay explicit identity operations"',
        "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror the primary helper surface"',
    },
    "tools/lib/find_bit.zig": {
        "tail_clamp_fixture_keys": [
            "tail_clamped_first",
            "tail_clamped_next",
            "tail_zero_clamped_first",
            "tail_zero_clamped_next",
            "tail_and_clamped_first",
            "tail_and_clamped_next",
            "tail_clamped_last",
            "tail_clamped_empty_last",
        ],
    },
    "tools/lib/rbtree.zig": {
        "helper_test_anchors": [
            'test "rbtree inserts and traverses in sorted order"',
            'test "rbtree erase and replace keep traversal consistent"',
            'test "rbtree eraseInit detaches erased node"',
            'test "rbtree postorder and empty node helpers behave"',
            'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
            'test "rbtree nextMatch walks the duplicate range in order"',
            'test "rbtree matchIterator walks the duplicate range in order"',
            'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
            'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
            'test "rbtree cached root keeps the leftmost pointer in sync"',
            'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
            'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
            'test "rbtree eraseCached returns null for a singleton cached tree"',
            'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
            'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
        ],
        "parity_fixture_keys": [
            "empty_root",
            "insert_order",
            "reverse_order",
            "replace_order",
            "erase_init_order",
            "postorder_count",
            "erase_init_node_empty",
            "cleared_node_empty",
            "find_found_key",
            "find_missing",
            "find_first_serial",
            "next_match_serials",
            "next_match_terminal_null",
        ],
        "duplicate_search_anchors": [
            'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
            'test "rbtree nextMatch walks the duplicate range in order"',
            'test "rbtree matchIterator walks the duplicate range in order"',
        ],
        "cached_root_followup_anchors": [
            'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
            'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
            'test "rbtree cached root keeps the leftmost pointer in sync"',
            'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
            'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
            'test "rbtree eraseCached returns null for a singleton cached tree"',
            'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
            'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
        ],
        "review_packet_summary": "shared find, first-match, and next-match duplicate-search parity stays explicit through the Phase 1 fixture and replay, while match-iterator coverage plus cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors until master ships dedicated shared iterator or cached-root fixture keys",
    },
    "tools/lib/string.zig": {
        "helper_test_anchors": [
            'test "strtobool accepts common Linux forms"',
            'test "strlcpy copies and returns the source length"',
            'test "streq matches C-string equality semantics"',
            'test "skip trim remove and replace spaces work in place"',
            'test "strreplace mirrors replaceChar C-string semantics"',
            'test "strHasPrefix honors C-string boundaries"',
            'test "strstarts mirrors the header-level prefix helper"',
            'test "strEndsWith honors C-string boundaries"',
            'test "sysfsStreq treats trailing newline and NUL as equivalent"',
            'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
            'test "memdup and memchrInv preserve byte content"',
            'test "memchr_inv mirrors memchrInv byte-search semantics"',
            'test "memchrInv keeps long-buffer first-dirty-byte results stable"',
            'test "memchrInv follows the earliest dirty byte as long buffers change"',
            'test "memchrInv dirty-word shortcut handles zero-value scans at word boundaries"',
            'test "memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment"',
            'test "memchrInv short zero-value scans stay byte-accurate"',
            'test "memparse handles decimal hexadecimal octal and suffixes"',
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse clamps explicit positive signed overflow"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
            'test "memparse applies suffixes before signed clamping"',
            'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
        ],
        "memparse_review_anchors": [
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse clamps explicit positive signed overflow"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
            'test "memparse applies suffixes before signed clamping"',
        ],
        "prefix_suffix_review_anchors": [
            'test "strHasPrefix honors C-string boundaries"',
            'test "strstarts mirrors the header-level prefix helper"',
            'test "strEndsWith honors C-string boundaries"',
        ],
        "prefix_suffix_review_summary": "helper-local prefix and suffix boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity rather than dedicated prefix or suffix fixture fields",
        "memparse_review_summary": "helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, explicit positive and signed overflow clamps remain review-visible, signed inputs keep trailing-rest splits aligned with unsigned parsing, and suffixes are still consumed after saturation",
        "phase1_helper_replay_anchor": 'test "phase 1 string replaceChar stops at embedded NUL"',
        "shared_replace_char_cstr_review_summary": "the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, trimSpaces, removeSpaces, replaceChar, and memchrInv fixture parity, while the dedicated embedded-NUL replaceChar follow-up keeps the first-terminator stop rule explicit without widening helper-local memparse ownership",
        "parity_fixture_keys": [
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
            "replace_char",
            "replace_char_end",
            "replace_char_cstr_end",
            "replace_char_cstr_bytes",
            "memchr_inv_index",
            "memchr_inv_none",
        ],
    },
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_marker_counts(text: str, label: str, markers: list[str]) -> list[str]:
    mismatches: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            mismatches.append(f"{label}:{marker}:expected=1:actual={count}")
    return mismatches


def collect_presence_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count < 1:
            missing.append(f"{label}:{marker}:expected>=1:actual={count}")
    return missing


def extract_test_body(text: str, title: str) -> str | None:
    anchor = f'test "{title}"'
    start = text.find(anchor)
    if start == -1:
        return None
    next_start = text.find('\ntest "', start + len(anchor))
    return text[start:] if next_start == -1 else text[start:next_start]


def collect_phase1_fixture_mismatches(root: Path) -> list[str]:
    fixture = json.loads((root / "zigux" / "tests" / "fixtures" / "phase1_helpers.json").read_text(encoding="utf-8"))
    mismatches: list[str] = []
    if sorted(fixture.keys()) != sorted(["argv_split", "bitmap", "cmdline", "ctype", "find_bit", "hweight", "list_sort", "rbtree", "slab", "str_error_r", "string", "vsprintf", "zalloc"]):
        mismatches.append("phase1_fixture:helper_keys")
    find_bit = fixture.get("find_bit")
    if not isinstance(find_bit, dict):
        mismatches.append("phase1_fixture_find_bit:find_bit:expected=object:actual=missing")
    else:
        expected_find_bit = {
            "bits_per_long": 64,
            "inclusive_boundary_next": 63,
            "inclusive_boundary_zero": 63,
            "inclusive_boundary_and": 63,
            "past_nbits_next": 7,
            "past_nbits_zero": 7,
            "past_nbits_and": 7,
            "tail_clamped_first": 69,
            "tail_clamped_next": 69,
            "tail_zero_clamped_next": 69,
            "tail_and_clamped_next": 69,
            "tail_clamped_last": 67,
        }
        for field, expected in expected_find_bit.items():
            if find_bit.get(field) != expected:
                mismatches.append(
                    f"phase1_fixture_find_bit:{field}:expected={expected!r}:actual={find_bit.get(field)!r}"
                )
        tail_expected = expected_find_bit["tail_clamped_first"]
        if find_bit.get("tail_zero_clamped_first") != tail_expected:
            mismatches.append(
                f"phase1_fixture_find_bit:tail_zero_clamped_first:expected={tail_expected}:actual={find_bit.get('tail_zero_clamped_first')!r}"
            )
        if find_bit.get("tail_and_clamped_first") != tail_expected:
            mismatches.append(
                f"phase1_fixture_find_bit:tail_and_clamped_first:expected={tail_expected}:actual={find_bit.get('tail_and_clamped_first')!r}"
            )
        if find_bit.get("tail_clamped_empty_last") != tail_expected:
            mismatches.append(
                f"phase1_fixture_find_bit:tail_clamped_empty_last:expected={tail_expected}:actual={find_bit.get('tail_clamped_empty_last')!r}"
            )
    bitmap = fixture.get("bitmap")
    if not isinstance(bitmap, dict):
        mismatches.append("phase1_fixture_bitmap:bitmap:expected=object:actual=missing")
    else:
        if bitmap.get("scnprintf") != "1-3,7,10-11":
            mismatches.append(f"phase1_fixture_bitmap:scnprintf:expected='1-3,7,10-11':actual={bitmap.get('scnprintf')!r}")
        if bitmap.get("truncated_scnprintf_len") != 11:
            mismatches.append(f"phase1_fixture_bitmap:truncated_scnprintf_len:expected=11:actual={bitmap.get('truncated_scnprintf_len')!r}")
        if bitmap.get("truncated_scnprintf") != "1-3,7,1":
            mismatches.append(f"phase1_fixture_bitmap:truncated_scnprintf:expected='1-3,7,1':actual={bitmap.get('truncated_scnprintf')!r}")
        if bitmap.get("terminator_only_scnprintf_len") != 1:
            mismatches.append(f"phase1_fixture_bitmap:terminator_only_scnprintf_len:expected=1:actual={bitmap.get('terminator_only_scnprintf_len')!r}")
        if bitmap.get("terminator_only_nul") != 0:
            mismatches.append(f"phase1_fixture_bitmap:terminator_only_nul:expected=0:actual={bitmap.get('terminator_only_nul')!r}")
        if bitmap.get("zero_length_scnprintf_len") != 1:
            mismatches.append(f"phase1_fixture_bitmap:zero_length_scnprintf_len:expected=1:actual={bitmap.get('zero_length_scnprintf_len')!r}")
        if bitmap.get("partial_xor_nbits") != 4:
            mismatches.append(f"phase1_fixture_bitmap:partial_xor_nbits:expected=4:actual={bitmap.get('partial_xor_nbits')!r}")
        if bitmap.get("partial_xor_masked_values") != [14]:
            mismatches.append("phase1_fixture_bitmap:partial_xor_masked_values")
    string = fixture.get("string")
    if not isinstance(string, dict):
        mismatches.append("phase1_fixture_string:string:expected=object:actual=missing")
    else:
        expected_string = {
            "strtobool_y": True,
            "strtobool_on": True,
            "strtobool_zero": False,
            "strtobool_off": False,
            "strtobool_invalid": -22,
            "strlcpy_len": 5,
            "strlcpy_buffer": "hel",
            "skip_spaces": "hello",
            "trim_spaces": "hi",
            "remove_spaces": "abc",
            "replace_char": "a_b",
            "replace_char_end": 3,
            "replace_char_cstr_end": 2,
            "replace_char_cstr_bytes": [97, 95, 0, 45, 122],
            "memchr_inv_index": 4,
            "memchr_inv_none": True,
        }
        for field, expected in expected_string.items():
            if string.get(field) != expected:
                mismatches.append(
                    f"phase1_fixture_string:{field}:expected={expected!r}:actual={string.get(field)!r}"
                )
    rbtree = fixture.get("rbtree")
    if not isinstance(rbtree, dict):
        mismatches.append("phase1_fixture_rbtree:rbtree:expected=object:actual=missing")
    else:
        expected_rbtree = {
            "empty_root": True,
            "insert_order": [5, 10, 15, 20, 25],
            "reverse_order": [25, 20, 15, 10, 5],
            "replace_order": [5, 10, 15, 25],
            "erase_init_order": [5, 15, 25],
            "postorder_count": 3,
            "erase_init_node_empty": True,
            "cleared_node_empty": True,
            "find_found_key": 15,
            "find_missing": True,
            "find_first_serial": 0,
            "next_match_serials": [0, 2, 4],
            "next_match_terminal_null": True,
        }
        for field, expected in expected_rbtree.items():
            if rbtree.get(field) != expected:
                mismatches.append(
                    f"phase1_fixture_rbtree:{field}:expected={expected!r}:actual={rbtree.get(field)!r}"
                )
    return mismatches


def collect_phase1_manifest_lane_mismatches(manifest: dict[str, object]) -> list[str]:
    mismatches: list[str] = []
    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        return ["phase1_manifest:lane_sequencing"]
    for field, expected in EXPECTED_LANE_SEQUENCING.items():
        actual = lane_sequencing.get(field)
        if actual != expected:
            mismatches.append(f"phase1_manifest:lane_sequencing:{field}")
    return mismatches


def collect_phase1_manifest_review_mismatches(root: Path) -> list[str]:
    manifest = json.loads((root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json").read_text(encoding="utf-8"))
    mismatches: list[str] = []
    if manifest.get("phase") != "Phase 1":
        mismatches.append("phase1_manifest:phase")
    if manifest.get("status") != "closed":
        mismatches.append("phase1_manifest:status")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        mismatches.append("phase1_manifest:helpers")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        mismatches.append("phase1_manifest:helper_count")
    mismatches.extend(collect_phase1_manifest_lane_mismatches(manifest))
    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return mismatches + ["phase1_manifest:review_anchors"]
    for helper, expected_fields in EXPECTED_MANIFEST_HELPER_FIELDS.items():
        helper_review = review_anchors.get(helper)
        if not isinstance(helper_review, dict):
            mismatches.append(f"phase1_manifest_review_anchor:missing_helper={helper}")
            continue
        for field, expected in expected_fields.items():
            actual = helper_review.get(field)
            if isinstance(expected, list):
                if not isinstance(actual, list):
                    mismatches.append(f"phase1_manifest_review_anchor:value={helper}:{field}")
                    continue
                for item in expected:
                    if item not in actual:
                        mismatches.append(f"phase1_manifest_review_anchor:value={helper}:{field}:{item}")
            elif actual != expected:
                mismatches.append(f"phase1_manifest_review_anchor:value={helper}:{field}")
    return mismatches


def collect_missing_markers(root: Path) -> list[str]:
    docs_readme = (root / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
    tests_readme = (root / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
    review_checklist = (root / "Documentation" / "zigux" / "review-checklist.md").read_text(encoding="utf-8")
    phase1_helpers = (root / "zigux" / "tests" / "phase1_helpers.zig").read_text(encoding="utf-8")
    missing: list[str] = []
    for label, markers in DOC_MARKERS.items():
        text = {"docs_root_phase1_packet": docs_readme, "tests_root_phase1_packet": tests_readme, "review_checklist_phase1_packet": review_checklist}[label]
        missing.extend(collect_marker_counts(text, label, markers))
    missing.extend(collect_marker_counts(phase1_helpers, "phase1_import_marker", PHASE1_IMPORT_MARKERS))
    missing.extend(collect_marker_counts(phase1_helpers, "helper_test_anchor", HELPER_FOLLOWUP_TESTS))
    replay_body = extract_test_body(phase1_helpers, "phase 1 helper ports match committed parity fixture")
    if replay_body is None:
        missing.append('phase1_parity_test:test "phase 1 helper ports match committed parity fixture":expected=1:actual=0')
    else:
        missing.extend(collect_presence_markers(replay_body, "phase1_parity_replay_marker", PHASE1_REPLAY_MARKERS))
    for label, (path, markers) in SOURCE_MARKERS.items():
        text = (root / path).read_text(encoding="utf-8")
        missing.extend(collect_marker_counts(text, label, markers))
    missing.extend(collect_phase1_fixture_mismatches(root))
    missing.extend(collect_phase1_manifest_review_mismatches(root))
    return missing


def make_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel.endswith(".json"):
            path.write_text("{}\n", encoding="utf-8")
        else:
            path.write_text("\n", encoding="utf-8")


def run_self_test() -> None:
    replay_text = "\n".join(PHASE1_REPLAY_MARKERS)
    test_text = (
        'test "phase 1 helper ports match committed parity fixture"\n'
        f"{replay_text}\n\n"
        'test "phase 1 string replaceChar stops at embedded NUL"\n'
    )
    replay = extract_test_body(test_text, "phase 1 helper ports match committed parity fixture")
    assert replay is not None
    assert not collect_presence_markers(replay, "phase1_parity_replay_marker", PHASE1_REPLAY_MARKERS)
    assert extract_test_body(test_text, "missing") is None
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        make_fixture_root(tmp_root)
        (tmp_root / "Documentation" / "zigux" / "README.md").write_text(DOC_MARKERS["docs_root_phase1_packet"][0] + "\n" + DOC_MARKERS["docs_root_phase1_packet"][1] + "\n", encoding="utf-8")
        (tmp_root / "zigux" / "tests" / "README.md").write_text(DOC_MARKERS["tests_root_phase1_packet"][0] + "\n", encoding="utf-8")
        (tmp_root / "Documentation" / "zigux" / "review-checklist.md").write_text(DOC_MARKERS["review_checklist_phase1_packet"][0] + "\n" + DOC_MARKERS["review_checklist_phase1_packet"][1] + "\n", encoding="utf-8")
        (tmp_root / "tools" / "lib" / "bitmap.zig").write_text('\n'.join(SOURCE_MARKERS["bitmap_test_anchor"][1]) + '\n', encoding="utf-8")
        (tmp_root / "tools" / "lib" / "find_bit.zig").write_text('\n'.join(SOURCE_MARKERS["find_bit_test_anchor"][1]) + '\n', encoding="utf-8")
        (tmp_root / "tools" / "lib" / "string.zig").write_text('\n'.join(SOURCE_MARKERS["string_test_anchor"][1]) + '\n', encoding="utf-8")
        (tmp_root / "tools" / "lib" / "rbtree.zig").write_text('\n'.join(SOURCE_MARKERS["rbtree_test_anchor"][1]) + '\n', encoding="utf-8")
        (tmp_root / "zigux" / "tests" / "phase1_helpers.zig").write_text('\n'.join(PHASE1_IMPORT_MARKERS) + '\n' + 'test "phase 1 helper ports match committed parity fixture"\n' + '\n'.join(PHASE1_REPLAY_MARKERS) + '\n' + '\n'.join(HELPER_FOLLOWUP_TESTS) + '\n', encoding="utf-8")
        fixture_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase1_helpers.json"
        fixture_path.write_text(json.dumps({"argv_split": {}, "bitmap": {"scnprintf": "1-3,7,10-11", "truncated_scnprintf_len": 11, "truncated_scnprintf": "1-3,7,1", "terminator_only_scnprintf_len": 1, "terminator_only_nul": 0, "zero_length_scnprintf_len": 1, "partial_xor_nbits": 4, "partial_xor_masked_values": [14]}, "cmdline": {}, "ctype": {}, "find_bit": {"bits_per_long": 64, "inclusive_boundary_next": 63, "inclusive_boundary_zero": 63, "inclusive_boundary_and": 63, "past_nbits_next": 7, "past_nbits_zero": 7, "past_nbits_and": 7, "tail_clamped_first": 69, "tail_clamped_next": 69, "tail_zero_clamped_first": 69, "tail_zero_clamped_next": 69, "tail_and_clamped_first": 69, "tail_and_clamped_next": 69, "tail_clamped_last": 67, "tail_clamped_empty_last": 69}, "hweight": {}, "list_sort": {}, "rbtree": {"empty_root": True, "insert_order": [5, 10, 15, 20, 25], "reverse_order": [25, 20, 15, 10, 5], "replace_order": [5, 10, 15, 25], "erase_init_order": [5, 15, 25], "postorder_count": 3, "erase_init_node_empty": True, "cleared_node_empty": True, "find_found_key": 15, "find_missing": True, "find_first_serial": 0, "next_match_serials": [0, 2, 4], "next_match_terminal_null": True}, "slab": {}, "str_error_r": {}, "string": {"strtobool_y": True, "strtobool_on": True, "strtobool_zero": False, "strtobool_off": False, "strtobool_invalid": -22, "strlcpy_len": 5, "strlcpy_buffer": "hel", "skip_spaces": "hello", "trim_spaces": "hi", "remove_spaces": "abc", "replace_char": "a_b", "replace_char_end": 3, "replace_char_cstr_end": 2, "replace_char_cstr_bytes": [97, 95, 0, 45, 122], "memchr_inv_index": 4, "memchr_inv_none": True}, "vsprintf": {}, "zalloc": {}}, separators=(",", ":")), encoding="utf-8")
        (tmp_root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json").write_text(json.dumps({"phase": "Phase 1", "status": "closed", "helper_count": len(EXPECTED_HELPERS), "helpers": EXPECTED_HELPERS, "lane_sequencing": EXPECTED_LANE_SEQUENCING, "review_anchors": EXPECTED_MANIFEST_HELPER_FIELDS}, indent=2) + "\n", encoding="utf-8")
        assert not collect_missing_markers(tmp_root)

        bitmap_path = tmp_root / "tools" / "lib" / "bitmap.zig"
        bitmap_text = bitmap_path.read_text(encoding="utf-8")
        bitmap_path.write_text(
            bitmap_text.replace('test "bitmap range helpers clamp the final partial word"\n', "", 1),
            encoding="utf-8",
        )
        missing = collect_missing_markers(tmp_root)
        assert 'bitmap_test_anchor:test "bitmap range helpers clamp the final partial word":expected=1:actual=0' in missing
        bitmap_path.write_text(bitmap_text, encoding="utf-8")

        bitmap_path.write_text(
            bitmap_text.replace('test "bitmap scnprintf collapses contiguous ranges across word boundaries"\n', "", 1),
            encoding="utf-8",
        )
        missing = collect_missing_markers(tmp_root)
        assert 'bitmap_test_anchor:test "bitmap scnprintf collapses contiguous ranges across word boundaries":expected=1:actual=0' in missing
        bitmap_path.write_text(bitmap_text, encoding="utf-8")

        bitmap_path.write_text(
            bitmap_text.replace('test "bitmap Linux-style aliases mirror the primary helper surface"\n', "", 1),
            encoding="utf-8",
        )
        missing = collect_missing_markers(tmp_root)
        assert 'bitmap_test_anchor:test "bitmap Linux-style aliases mirror the primary helper surface":expected=1:actual=0' in missing
        bitmap_path.write_text(bitmap_text, encoding="utf-8")

        manifest_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json"
        pristine_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        manifest = json.loads(json.dumps(pristine_manifest))
        manifest["lane_sequencing"]["direct_anchor_followup_helpers"] = manifest["lane_sequencing"]["direct_anchor_followup_helpers"][:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "phase1_manifest:lane_sequencing:direct_anchor_followup_helpers" in missing

        manifest = json.loads(json.dumps(pristine_manifest))
        manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("final_partial_word_anchor")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "phase1_manifest_review_anchor:value=tools/lib/bitmap.zig:final_partial_word_anchor" in missing

        manifest = json.loads(json.dumps(pristine_manifest))
        manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("cross_word_scnprintf_anchor")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "phase1_manifest_review_anchor:value=tools/lib/bitmap.zig:cross_word_scnprintf_anchor" in missing

        manifest = json.loads(json.dumps(pristine_manifest))
        manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("linux_alias_anchor")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "phase1_manifest_review_anchor:value=tools/lib/bitmap.zig:linux_alias_anchor" in missing

        manifest = json.loads(json.dumps(pristine_manifest))
        manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("zero_bit_binary_identity_anchor")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "phase1_manifest_review_anchor:value=tools/lib/bitmap.zig:zero_bit_binary_identity_anchor" in missing

        manifest = json.loads(json.dumps(pristine_manifest))
        manifest["review_anchors"]["tools/lib/bitmap.zig"]["helper_test_anchors"] = [
            anchor
            for anchor in manifest["review_anchors"]["tools/lib/bitmap.zig"]["helper_test_anchors"]
            if anchor != 'test "bitmap Linux-style aliases mirror the primary helper surface"'
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert 'phase1_manifest_review_anchor:value=tools/lib/bitmap.zig:helper_test_anchors:test "bitmap Linux-style aliases mirror the primary helper surface"' in missing

        manifest = json.loads(json.dumps(pristine_manifest))
        manifest["review_anchors"]["tools/lib/bitmap.zig"]["helper_test_anchors"] = [
            anchor
            for anchor in manifest["review_anchors"]["tools/lib/bitmap.zig"]["helper_test_anchors"]
            if anchor != 'test "bitmap zero-bit binary helpers stay explicit identity operations"'
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert 'phase1_manifest_review_anchor:value=tools/lib/bitmap.zig:helper_test_anchors:test "bitmap zero-bit binary helpers stay explicit identity operations"' in missing

        manifest = json.loads(json.dumps(pristine_manifest))
        manifest["review_anchors"]["tools/lib/rbtree.zig"]["helper_test_anchors"] = [
            anchor
            for anchor in manifest["review_anchors"]["tools/lib/rbtree.zig"]["helper_test_anchors"]
            if anchor != 'test "rbtree cached-root Linux-style aliases mirror the primary helpers"'
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert 'phase1_manifest_review_anchor:value=tools/lib/rbtree.zig:helper_test_anchors:test "rbtree cached-root Linux-style aliases mirror the primary helpers"' in missing

        manifest = json.loads(json.dumps(pristine_manifest))
        manifest["review_anchors"]["tools/lib/rbtree.zig"]["cached_root_followup_anchors"] = [
            anchor
            for anchor in manifest["review_anchors"]["tools/lib/rbtree.zig"]["cached_root_followup_anchors"]
            if anchor != 'test "rbtree cached-root Linux-style aliases mirror the primary helpers"'
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert 'phase1_manifest_review_anchor:value=tools/lib/rbtree.zig:cached_root_followup_anchors:test "rbtree cached-root Linux-style aliases mirror the primary helpers"' in missing

        manifest = json.loads(json.dumps(pristine_manifest))
        manifest["review_anchors"]["tools/lib/rbtree.zig"]["review_packet_summary"] = "shared find, first-match, and next-match duplicate-search parity stays explicit through the Phase 1 fixture and replay, while match-iterator coverage plus cached-root insert-miss, replacement, detach, and reseed behavior remain owned by direct helper-local anchors until master ships dedicated shared iterator or cached-root fixture keys"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "phase1_manifest_review_anchor:value=tools/lib/rbtree.zig:review_packet_summary" in missing

        manifest = json.loads(json.dumps(pristine_manifest))
        manifest["review_anchors"]["tools/lib/string.zig"]["helper_test_anchors"] = ['test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"']
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert 'phase1_manifest_review_anchor:value=tools/lib/string.zig:helper_test_anchors:test "memparse applies suffixes before signed clamping"' in missing

        string_path = tmp_root / "tools" / "lib" / "string.zig"
        string_text = string_path.read_text(encoding="utf-8")
        string_path.write_text(
            string_text.replace('test "memparse clamps explicit positive signed overflow"\n', "", 1),
            encoding="utf-8",
        )
        missing = collect_missing_markers(tmp_root)
        assert 'string_test_anchor:test "memparse clamps explicit positive signed overflow":expected=1:actual=0' in missing
        string_path.write_text(string_text, encoding="utf-8")

        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["string"]["strtobool_y"] = False
        fixture_path.write_text(json.dumps(fixture, separators=(",", ":")), encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "phase1_fixture_string:strtobool_y:expected=True:actual=False" in missing
    print("PHASE1_VALIDATION_SELF_TEST=pass")
    print("PHASE1_VALIDATION_SELF_TEST_CASE_COUNT=20")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 1 helper packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    missing = collect_missing_files(ROOT)
    if missing:
        print("PHASE1_VALIDATION=fail")
        print("MISSING_PHASE1_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE1_FILES_END")
        return 1
    missing_markers = collect_missing_markers(ROOT)
    if missing_markers:
        print("PHASE1_VALIDATION=fail")
        print("MISSING_PHASE1_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_MARKERS_END")
        return 1
    print("PHASE1_VALIDATION=pass")
    print(f"PHASE1_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print("PHASE1_REQUIRED_MARKER_COUNT=" f"{sum(len(markers) for markers in DOC_MARKERS.values()) + len(PHASE1_IMPORT_MARKERS) + len(PHASE1_REPLAY_MARKERS) + len(HELPER_FOLLOWUP_TESTS) + sum(len(markers) for _, markers in SOURCE_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

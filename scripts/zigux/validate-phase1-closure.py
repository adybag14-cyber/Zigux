#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


_SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) >= 3 else _SELF_PATH.parent

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

EXPECTED_REVIEW_ANCHORS = {
    "tools/lib/bitmap.zig": {
        "helper_test_anchors": [
            'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
            'test "bitmap allocator helpers size zero and free their buffers"',
            'test "bitmap size aliases round bit counts to full words in bytes"',
            'test "bitmap set clear weight and empty full helpers"',
            'test "bitmap range helpers honor exact first-word boundaries"',
            'test "bitmap range helpers clamp the final partial word"',
            'test "bitmap fill clamps tail bits in partial words"',
            'test "bitmap and andnot equal intersects subset"',
            'test "bitmap and andnot clamp tail bits in partial words"',
            'test "bitmap predicates ignore out-of-range tail bits"',
            'test "bitmap xor keeps caller-selected bit window"',
            'test "bitmap scnprintf collapses contiguous ranges"',
            'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
            'test "bitmap scnprintf reports full length while truncating the buffer"',
            'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
            'test "bitmap copy alias preserves raw source words without tail clearing"',
            'test "bitmap copy aliases preserve tail clearing and extension semantics"',
            'test "bitmap copy and extend handles zero and aligned counts"',
            'test "bitmap zero-bit helpers stay explicit no-ops"',
            'test "bitmap zero-bit binary helpers stay explicit identity operations"',
            'test "bitmap Linux-style aliases mirror the primary helper surface"',
        ],
        "first_word_boundary_anchor": 'test "bitmap range helpers honor exact first-word boundaries"',
        "final_partial_word_anchor": 'test "bitmap range helpers clamp the final partial word"',
        "predicate_tail_mask_anchor": 'test "bitmap predicates ignore out-of-range tail bits"',
        "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
        "parity_fixture_keys": [
            "scnprintf",
            "truncated_scnprintf_len",
            "truncated_scnprintf",
            "terminator_only_scnprintf_len",
            "terminator_only_nul",
            "zero_length_scnprintf_len",
        ],
        "partial_xor_review_fields": [
            "partial_xor_nbits",
            "partial_xor_masked_values",
        ],
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
        "helper_test_anchors": [
            'test "single-word next scans honor start masks"',
            'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
            'test "zero-bit windows return without reading bitmap words"',
            'test "zero-sized scans ignore populated backing words"',
            'test "next scans past nbits return without reading bitmap words"',
            'test "tail-word next set scans skip earlier in-range matches before clamping"',
            'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
            'test "low-level underscore aliases mirror the primary find helpers"',
        ],
        "same_word_start_masks": 'test "single-word next scans honor start masks"',
        "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
        "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
        "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers"',
        "tail_word_skip_anchor": 'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
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
        "review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, while helper-local anchors keep same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, and underscore-alias behavior review-visible on current master",
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
        "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
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

EXPECTED_BENCH_ITERATIONS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,
    "PHASE1_BENCH_STRING_ITERATIONS": 40000,
    "PHASE1_BENCH_HWEIGHT_ITERATIONS": 100000,
    "PHASE1_BENCH_LIST_SORT_ITERATIONS": 1000,
    "PHASE1_BENCH_RBTREE_ITERATIONS": 4000,
}

EXPECTED_BENCH_CHECKSUMS = [
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    "PHASE1_BENCH_STRING_CHECKSUM",
    "PHASE1_BENCH_HWEIGHT_CHECKSUM",
    "PHASE1_BENCH_LIST_SORT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CHECKSUM",
]

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-installer-review-surfaces.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_bench.zig",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    *EXPECTED_HELPERS,
]

REQUIRED_CLOSURE_MARKERS = [
    "PHASE1_STATUS=closed",
    "PHASE1_HELPER_COUNT=13",
    "PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py",
    "PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig",
    "PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig",
    "PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py",
    "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py",
    "PHASE1_LANE_SEQUENCING_RULE=shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string reopen only for their current helper-local anchors or already-committed shared fixture keys",
    "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_REVIEW=helper-local inclusive boundary proof stays explicit through the direct find_bit test anchor so same-word next scans keep the last in-range head-word bit reachable from an inclusive start",
    "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_OWNER=the shared Phase 1 replay now consumes the committed inclusive_boundary_* fixture fields directly, while the direct helper-local inclusive-boundary test remains a review-visible same-word anchor for that path",
    "PHASE1_FIND_BIT_TAIL_WORD_SKIP_REVIEW=helper-local tail-word skip proof stays explicit through the direct find_bit test anchor and the Phase 1 helper manifest so tail-word next zero and shared scans skip earlier in-range matches before clamping to nbits",
    "PHASE1_BITMAP_FIRST_WORD_BOUNDARY_REVIEW=helper-local bitmap first-word boundary proof stays explicit through the direct bitmap test anchor so setRange and clearRange preserve exact first-word masks when a range ends on the first-word boundary",
    "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor so setRange and clearRange clamp trailing partial-word masks to the requested tail window instead of spilling work beyond it",
    "PHASE1_BITMAP_SCNPRINTF_TINY_BUFFER_REVIEW=helper-local bitmap.scnprintf tiny-buffer proof stays explicit through the direct bitmap test anchor plus the shared Phase 1 parity fixture and replay so terminator-only caller buffers stay NUL-terminated and zero-length caller views return without writing hidden bytes",
    "PHASE1_BITMAP_COPY_EXTEND_ZERO_ALIGNED_REVIEW=helper-local bitmap copy-and-extend zero-count and aligned-count proof stays explicit through the direct bitmap test anchor so zero-count copies clear the destination extension and aligned word counts preserve copied words without accidental tail masking",
    "PHASE1_BITMAP_ZERO_BIT_BINARY_IDENTITY_REVIEW=helper-local bitmap zero-bit binary identity proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so andBits, andNotBits, equal, intersects, and subset keep empty-window identity semantics without treating zero-bit windows as live data",
    "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface",
    "PHASE1_RBTREE_REVIEW_PACKET=helper-local rbtree tests plus the shared traversal, detached-node, and duplicate-search replay stay explicit so duplicate-search parity keys remain shared-replay-owned while match-iterator coverage plus cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors until master ships dedicated shared iterator or cached-root fixture keys",
    "PHASE1_STRING_MEMPARSE_REVIEW=helper-local memparse safety anchors stay explicit through the direct string tests and the Phase 1 helper manifest so sign-prefixed invalid input preserves rest, explicit positive and signed overflow clamps remain review-visible, signed inputs keep trailing-rest splits aligned with unsigned parsing, and suffixes are still consumed after saturation",
    "PHASE1_STRING_REVIEW_PACKET=helper-local string tests and the shared embedded-NUL replay stay explicit so the bounded Phase 1 string surface keeps its direct review anchors, committed C-string replacement bytes, and parity fixture keys",
    "PHASE1_ROLLBACK=keep C authoritative and remove failing Zig helper from test/build wiring",
]

DOC_MARKERS = {
    "Documentation/zigux/README.md": [
        "Phase 1 notes",
        "keep the closure, installer-backed workflow-viability replay, the dedicated installer-review alignment checker, bootstrap-workflow replay, and validator-first contract explicit from the docs root",
    ],
    "Documentation/zigux/review-checklist.md": [
        "if the change touches the closed Phase 1 host-tools packet",
        "`scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` still agree on the same closed helper tranche and validator-first replay path",
    ],
    "scripts/zigux/README.md": [
        "validate-phase1-closure.py confirms the closed Phase 1 packet still matches `Documentation/zigux/phase1-closure.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, the shared helper build wiring, and the bootstrap workflow.",
        "`tools/lib/string.zig`, `Documentation/zigux/phase1-closure.md`, and `zigux/tests/fixtures/phase1_helper_manifest.json` also keep the direct Phase 1 string review packet explicit, including the `memchr_inv()` alias replay, the zero-value prefix-alignment `memchrInv()` follow-up, and the explicit positive-overflow `memparse()` anchor, so those helper-local proofs stay reviewable without widening the shared parity fixture.",
    ],
    "zigux/tests/README.md": [
        "keep the closed Phase 1 host-tools packet explicit in the tests root too:",
        "`Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root",
    ],
}

WORKFLOW_MARKERS = [
    "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
    "python3 scripts/zigux/install-zig.py --channel master --dest .zig-toolchain",
    "run: python3 scripts/zigux/check-phase1-installer-review-surfaces.py",
    "run: python3 scripts/zigux/validate-phase1.py",
    "run: python3 scripts/zigux/check-phase1-parity.py",
    "run: zig build test --build-file zigux/tests/build.zig",
    "run: zig build bench --build-file zigux/tests/build.zig",
    "run: python3 scripts/zigux/check-phase1-bench.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
]

MAKEFILE_MARKERS = [
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1: phase1-validate phase1-test phase1-bench",
]

BUILD_MARKERS = [
    '.name = "phase1-test"',
    '.name = "phase1-bench"',
    'root_source_file = b.path("phase1_helpers.zig")',
    'root_source_file = b.path("phase1_bench.zig")',
]


def repo_root_from_arg(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else DEFAULT_ROOT


def load_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_marker_misses(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={count}")
    return missing


def collect_marker_presence(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count < 1:
            missing.append(f"{label}:{marker}:expected>=1:actual={count}")
    return missing


def collect_list_mismatches(label: str, actual: object, expected: list[object]) -> list[str]:
    if not isinstance(actual, list):
        return [f"{label}:type=list"]
    if actual != expected:
        return [f"{label}:value"]
    return []


def collect_manifest_mismatches(manifest: object, root: Path) -> list[str]:
    if not isinstance(manifest, dict):
        return ["manifest:type=dict"]

    missing: list[str] = []
    if manifest.get("phase") != "Phase 1":
        missing.append("manifest:phase")
    if manifest.get("status") != "closed":
        missing.append("manifest:status")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        missing.append("manifest:helper_count")

    helpers = manifest.get("helpers")
    missing.extend(collect_list_mismatches("manifest:helpers", helpers, EXPECTED_HELPERS))

    lane = manifest.get("lane_sequencing")
    if not isinstance(lane, dict):
        missing.append("manifest:lane_sequencing:type=dict")
    else:
        for key, expected in EXPECTED_LANE_SEQUENCING.items():
            actual = lane.get(key)
            if actual != expected:
                missing.append(f"manifest:lane_sequencing:{key}")

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        missing.append("manifest:review_anchors:type=dict")
        return missing

    for helper, expected_fields in EXPECTED_REVIEW_ANCHORS.items():
        actual_fields = review_anchors.get(helper)
        if not isinstance(actual_fields, dict):
            missing.append(f"manifest:review_anchors:missing_helper={helper}")
            continue
        for field, expected in expected_fields.items():
            actual = actual_fields.get(field)
            if actual != expected:
                missing.append(f"manifest:review_anchors:{helper}:{field}")

    for rel in EXPECTED_HELPERS:
        if not (root / rel).exists():
            missing.append(f"manifest:missing_helper_file={rel}")

    return missing


def collect_bench_expectation_mismatches(expectations: object) -> list[str]:
    if not isinstance(expectations, dict):
        return ["bench_expectations:type=dict"]

    missing: list[str] = []
    if expectations.get("status") != "pass":
        missing.append("bench_expectations:status")

    iterations = expectations.get("iterations")
    if not isinstance(iterations, dict):
        missing.append("bench_expectations:iterations:type=dict")
    else:
        if iterations != EXPECTED_BENCH_ITERATIONS:
            missing.append("bench_expectations:iterations:value")

    checksums = expectations.get("checksums")
    if not isinstance(checksums, list):
        missing.append("bench_expectations:checksums:type=list")
    else:
        if checksums != EXPECTED_BENCH_CHECKSUMS:
            missing.append("bench_expectations:checksums:value")

    return missing


def load_json(path: Path, label: str) -> tuple[object | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"{label}:missing"]
    except json.JSONDecodeError:
        return None, [f"{label}:json"]


def count_manifest_expectations() -> int:
    field_count = 0
    for fields in EXPECTED_REVIEW_ANCHORS.values():
        field_count += len(fields)
    return 4 + len(EXPECTED_LANE_SEQUENCING) + field_count


def make_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel.endswith(".json"):
            path.write_text("{}\n", encoding="utf-8")
        else:
            path.write_text("\n", encoding="utf-8")

    (root / "Documentation/zigux/phase1-closure.md").write_text(
        "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n",
        encoding="utf-8",
    )
    for rel, markers in DOC_MARKERS.items():
        (root / rel).write_text("\n".join(markers) + "\n", encoding="utf-8")
    (root / ".github/workflows/zigux-bootstrap.yml").write_text(
        "\n".join(WORKFLOW_MARKERS) + "\n",
        encoding="utf-8",
    )
    (root / "zigux/Makefile").write_text("\n".join(MAKEFILE_MARKERS) + "\n", encoding="utf-8")
    (root / "zigux/tests/build.zig").write_text("\n".join(BUILD_MARKERS) + "\n", encoding="utf-8")
    (root / "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md").write_text("phase1 closed helper tranche\n", encoding="utf-8")

    manifest = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": EXPECTED_HELPERS,
        "lane_sequencing": EXPECTED_LANE_SEQUENCING,
        "review_anchors": EXPECTED_REVIEW_ANCHORS,
    }
    (root / "zigux/tests/fixtures/phase1_helper_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    expectations = {
        "status": "pass",
        "iterations": EXPECTED_BENCH_ITERATIONS,
        "checksums": EXPECTED_BENCH_CHECKSUMS,
    }
    (root / "zigux/tests/fixtures/phase1_bench_expectations.json").write_text(
        json.dumps(expectations, indent=2) + "\n",
        encoding="utf-8",
    )


def collect_missing_markers(root: Path) -> list[str]:
    closure_text = load_text(root, "Documentation/zigux/phase1-closure.md")
    docs_root = load_text(root, "Documentation/zigux/README.md")
    review_checklist = load_text(root, "Documentation/zigux/review-checklist.md")
    scripts_readme = load_text(root, "scripts/zigux/README.md")
    tests_readme = load_text(root, "zigux/tests/README.md")
    workflow = load_text(root, ".github/workflows/zigux-bootstrap.yml")
    makefile = load_text(root, "zigux/Makefile")
    build_zig = load_text(root, "zigux/tests/build.zig")

    manifest, manifest_errors = load_json(root / "zigux/tests/fixtures/phase1_helper_manifest.json", "manifest")
    expectations, expectation_errors = load_json(
        root / "zigux/tests/fixtures/phase1_bench_expectations.json",
        "bench_expectations",
    )

    missing: list[str] = []
    missing.extend(collect_marker_misses(closure_text, "closure", REQUIRED_CLOSURE_MARKERS))
    missing.extend(collect_marker_misses(docs_root, "docs_root", DOC_MARKERS["Documentation/zigux/README.md"]))
    missing.extend(
        collect_marker_misses(
            review_checklist,
            "review_checklist",
            DOC_MARKERS["Documentation/zigux/review-checklist.md"],
        )
    )
    missing.extend(collect_marker_misses(scripts_readme, "scripts_readme", DOC_MARKERS["scripts/zigux/README.md"]))
    missing.extend(collect_marker_misses(tests_readme, "tests_readme", DOC_MARKERS["zigux/tests/README.md"]))
    missing.extend(collect_marker_misses(workflow, "workflow", WORKFLOW_MARKERS))
    missing.extend(collect_marker_misses(makefile, "makefile", MAKEFILE_MARKERS))
    missing.extend(collect_marker_misses(build_zig, "build_zig", BUILD_MARKERS))
    missing.extend(manifest_errors)
    missing.extend(expectation_errors)
    if manifest is not None:
        missing.extend(collect_manifest_mismatches(manifest, root))
    if expectations is not None:
        missing.extend(collect_bench_expectation_mismatches(expectations))
    return missing


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_closure_") as tmp_str:
        root = Path(tmp_str)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []

        closure_path = root / "Documentation/zigux/phase1-closure.md"
        original_closure = closure_path.read_text(encoding="utf-8")
        for marker in [
            "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor so setRange and clearRange clamp trailing partial-word masks to the requested tail window instead of spilling work beyond it",
            "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface",
            "PHASE1_RBTREE_REVIEW_PACKET=helper-local rbtree tests plus the shared traversal, detached-node, and duplicate-search replay stay explicit so duplicate-search parity keys remain shared-replay-owned while match-iterator coverage plus cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors until master ships dedicated shared iterator or cached-root fixture keys",
            "PHASE1_STRING_MEMPARSE_REVIEW=helper-local memparse safety anchors stay explicit through the direct string tests and the Phase 1 helper manifest so sign-prefixed invalid input preserves rest, explicit positive and signed overflow clamps remain review-visible, signed inputs keep trailing-rest splits aligned with unsigned parsing, and suffixes are still consumed after saturation",
        ]:
            closure_path.write_text(original_closure.replace(marker + "\n", "", 1), encoding="utf-8")
            missing = collect_missing_markers(root)
            assert any(item.startswith("closure:") for item in missing)
            closure_path.write_text(original_closure, encoding="utf-8")
            case_count += 1

        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        pristine_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        def assert_manifest_mutation(expected_marker: str, mutate) -> None:
            nonlocal case_count
            manifest = json.loads(json.dumps(pristine_manifest))
            mutate(manifest)
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            missing = collect_missing_markers(root)
            assert expected_marker in missing
            manifest_path.write_text(json.dumps(pristine_manifest, indent=2) + "\n", encoding="utf-8")
            case_count += 1

        assert_manifest_mutation(
            "manifest:review_anchors:tools/lib/bitmap.zig:final_partial_word_anchor",
            lambda manifest: manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("final_partial_word_anchor"),
        )
        assert_manifest_mutation(
            "manifest:review_anchors:tools/lib/bitmap.zig:cross_word_scnprintf_anchor",
            lambda manifest: manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("cross_word_scnprintf_anchor"),
        )
        assert_manifest_mutation(
            "manifest:review_anchors:tools/lib/bitmap.zig:zero_bit_binary_identity_anchor",
            lambda manifest: manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("zero_bit_binary_identity_anchor"),
        )
        assert_manifest_mutation(
            "manifest:review_anchors:tools/lib/bitmap.zig:linux_alias_anchor",
            lambda manifest: manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("linux_alias_anchor"),
        )
        assert_manifest_mutation(
            "manifest:review_anchors:tools/lib/rbtree.zig:cached_root_followup_anchors",
            lambda manifest: manifest["review_anchors"]["tools/lib/rbtree.zig"].__setitem__(
                "cached_root_followup_anchors",
                [
                    anchor
                    for anchor in manifest["review_anchors"]["tools/lib/rbtree.zig"]["cached_root_followup_anchors"]
                    if anchor != 'test "rbtree cached-root Linux-style aliases mirror the primary helpers"'
                ],
            ),
        )
        assert_manifest_mutation(
            "manifest:review_anchors:tools/lib/rbtree.zig:review_packet_summary",
            lambda manifest: manifest["review_anchors"]["tools/lib/rbtree.zig"].__setitem__(
                "review_packet_summary",
                "stale summary",
            ),
        )
        assert_manifest_mutation(
            "manifest:review_anchors:tools/lib/string.zig:memparse_review_anchors",
            lambda manifest: manifest["review_anchors"]["tools/lib/string.zig"].__setitem__(
                "memparse_review_anchors",
                [
                    anchor
                    for anchor in manifest["review_anchors"]["tools/lib/string.zig"]["memparse_review_anchors"]
                    if anchor != 'test "memparse clamps explicit positive signed overflow"'
                ],
            ),
        )
        assert_manifest_mutation(
            "manifest:review_anchors:tools/lib/string.zig:helper_test_anchors",
            lambda manifest: manifest["review_anchors"]["tools/lib/string.zig"].__setitem__(
                "helper_test_anchors",
                [
                    anchor
                    for anchor in manifest["review_anchors"]["tools/lib/string.zig"]["helper_test_anchors"]
                    if anchor != 'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"'
                ],
            ),
        )
        assert_manifest_mutation(
            "manifest:lane_sequencing:direct_anchor_followup_helpers",
            lambda manifest: manifest["lane_sequencing"].__setitem__(
                "direct_anchor_followup_helpers",
                manifest["lane_sequencing"]["direct_anchor_followup_helpers"][:-1],
            ),
        )

        bench_path = root / "zigux/tests/fixtures/phase1_bench_expectations.json"
        pristine_bench = json.loads(bench_path.read_text(encoding="utf-8"))
        bench = json.loads(json.dumps(pristine_bench))
        bench["iterations"].pop("PHASE1_BENCH_STRING_ITERATIONS")
        bench_path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "bench_expectations:iterations:value" in missing
        bench_path.write_text(json.dumps(pristine_bench, indent=2) + "\n", encoding="utf-8")
        case_count += 1

        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        pristine_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            pristine_workflow.replace("run: python3 scripts/zigux/validate-phase1-closure.py\n", "", 1),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert any(item.startswith("workflow:run: python3 scripts/zigux/validate-phase1-closure.py") for item in missing)
        workflow_path.write_text(pristine_workflow, encoding="utf-8")
        case_count += 1

        (root / "zigux/tests/phase1_helpers.zig").unlink()
        assert collect_missing_files(root) == ["zigux/tests/phase1_helpers.zig"]
        case_count += 1

    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 1 closure packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root instead of the validator script checkout root.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root_from_arg(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE1_CLOSURE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_CLOSURE_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE1_CLOSURE_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE1_CLOSURE_MARKERS_END")
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print(f"PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_CLOSURE_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_CLOSURE_MARKERS) + sum(len(markers) for markers in DOC_MARKERS.values()) + len(WORKFLOW_MARKERS) + len(MAKEFILE_MARKERS) + len(BUILD_MARKERS) + count_manifest_expectations() + 1 + len(EXPECTED_BENCH_ITERATIONS) + len(EXPECTED_BENCH_CHECKSUMS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

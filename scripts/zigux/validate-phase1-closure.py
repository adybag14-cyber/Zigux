#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile
from typing import Any


_SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) >= 3 else _SELF_PATH.parent

EXPECTED_PHASE1_MANIFEST = json.loads(
    r"""
{
  "phase": "Phase 1",
  "status": "closed",
  "helper_count": 13,
  "helpers": [
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
    "tools/lib/zalloc.zig"
  ],
  "lane_sequencing": {
    "shared_replay_parked_helpers": [
      "tools/lib/argv_split.zig",
      "tools/lib/cmdline.zig",
      "tools/lib/ctype.zig",
      "tools/lib/hweight.zig",
      "tools/lib/list_sort.zig",
      "tools/lib/slab.zig",
      "tools/lib/str_error_r.zig",
      "tools/lib/vsprintf.zig",
      "tools/lib/zalloc.zig"
    ],
    "direct_anchor_followup_helpers": [
      "tools/lib/bitmap.zig",
      "tools/lib/find_bit.zig",
      "tools/lib/rbtree.zig",
      "tools/lib/string.zig"
    ],
    "rule_summary": "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",
    "anti_overlap_rule": "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys."
  },
  "review_anchors": {
    "tools/lib/bitmap.zig": {
      "helper_test_anchors": [
        "test \"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\"",
        "test \"bitmap allocator helpers size zero and free their buffers\"",
        "test \"bitmap size aliases round bit counts to full words in bytes\"",
        "test \"bitmap set clear weight and empty full helpers\"",
        "test \"bitmap range helpers honor exact first-word boundaries\"",
        "test \"bitmap range helpers clamp the final partial word\"",
        "test \"bitmap fill clamps tail bits in partial words\"",
        "test \"bitmap and andnot equal intersects subset\"",
        "test \"bitmap and andnot clamp tail bits in partial words\"",
        "test \"bitmap predicates ignore out-of-range tail bits\"",
        "test \"bitmap xor keeps caller-selected bit window\"",
        "test \"bitmap scnprintf collapses contiguous ranges\"",
        "test \"bitmap scnprintf reports full length while truncating the buffer\"",
        "test \"bitmap scnprintf handles terminator-only and zero-length caller views\"",
        "test \"bitmap copy aliases preserve tail clearing and extension semantics\"",
        "test \"bitmap copy alias preserves raw source words without tail clearing\"",
        "test \"bitmap zero-bit helpers stay explicit no-ops\"",
        "test \"bitmap Linux-style aliases mirror the primary helper surface\""
      ],
      "first_word_boundary_anchor": "test \"bitmap range helpers honor exact first-word boundaries\"",
      "final_partial_word_anchor": "test \"bitmap range helpers clamp the final partial word\"",
      "predicate_tail_mask_anchor": "test \"bitmap predicates ignore out-of-range tail bits\"",
      "phase1_helper_replay_anchor": "test \"phase 1 helper ports match committed parity fixture\"",
      "parity_fixture_keys": [
        "scnprintf",
        "truncated_scnprintf_len",
        "truncated_scnprintf",
        "terminator_only_scnprintf_len",
        "terminator_only_nul",
        "zero_length_scnprintf_len"
      ],
      "partial_xor_review_fields": [
        "partial_xor_nbits",
        "partial_xor_masked_values"
      ],
      "scnprintf_truncation_anchor": "test \"bitmap scnprintf reports full length while truncating the buffer\"",
      "copy_alias_anchor": "test \"bitmap copy aliases preserve tail clearing and extension semantics\"",
      "copy_raw_alias_anchor": "test \"bitmap copy alias preserves raw source words without tail clearing\"",
      "zero_bit_noop_anchor": "test \"bitmap zero-bit helpers stay explicit no-ops\"",
      "linux_alias_anchor": "test \"bitmap Linux-style aliases mirror the primary helper surface\""
    },
    "tools/lib/find_bit.zig": {
      "helper_test_anchors": [
        "test \"single-word next scans honor start masks\"",
        "test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\"",
        "test \"zero-bit windows return without reading bitmap words\"",
        "test \"zero-sized scans ignore populated backing words\"",
        "test \"next scans past nbits return without reading bitmap words\"",
        "test \"tail-word next set scans skip earlier in-range matches before clamping\"",
        "test \"tail-word next zero and shared scans skip earlier in-range matches before clamping\"",
        "test \"low-level underscore aliases mirror the primary find helpers\""
      ],
      "same_word_start_masks": "test \"single-word next scans honor start masks\"",
      "inclusive_boundary_start": "test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\"",
      "zero_bit_window": "test \"zero-bit windows return without reading bitmap words\"",
      "past_nbits_short_circuit": "test \"next scans past nbits return without reading bitmap words\"",
      "underscore_alias_anchor": "test \"low-level underscore aliases mirror the primary find helpers\"",
      "tail_word_skip_anchor": "test \"tail-word next zero and shared scans skip earlier in-range matches before clamping\"",
      "tail_clamp_fixture_keys": [
        "tail_clamped_first",
        "tail_clamped_next",
        "tail_zero_clamped_first",
        "tail_zero_clamped_next",
        "tail_and_clamped_first",
        "tail_and_clamped_next",
        "tail_clamped_last",
        "tail_clamped_empty_last"
      ],
      "review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, while helper-local anchors keep same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, and underscore-alias behavior review-visible on current master"
    },
    "tools/lib/rbtree.zig": {
      "helper_test_anchors": [
        "test \"rbtree inserts and traverses in sorted order\"",
        "test \"rbtree erase and replace keep traversal consistent\"",
        "test \"rbtree eraseInit detaches erased node\"",
        "test \"rbtree postorder and empty node helpers behave\"",
        "test \"rbtree findAdd keeps the first duplicate and inserts new keys\"",
        "test \"rbtree nextMatch walks the duplicate range in order\"",
        "test \"rbtree matchIterator walks the duplicate range in order\"",
        "test \"rbtree addCached returns the inserted node only when it becomes leftmost\"",
        "test \"rbtree findAddCached keeps cached leftmost stable while inserting misses\"",
        "test \"rbtree cached root keeps the leftmost pointer in sync\"",
        "test \"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\"",
        "test \"rbtree eraseCached returns null for a singleton cached tree\"",
        "test \"rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned\"",
        "test \"rbtree eraseInitCached clears singleton cached roots before reseed\""
      ],
      "phase1_helper_replay_anchor": "test \"phase 1 helper ports match committed parity fixture\"",
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
        "next_match_terminal_null"
      ],
      "duplicate_search_anchors": [
        "test \"rbtree findAdd keeps the first duplicate and inserts new keys\"",
        "test \"rbtree nextMatch walks the duplicate range in order\"",
        "test \"rbtree matchIterator walks the duplicate range in order\""
      ],
      "cached_root_followup_anchors": [
        "test \"rbtree addCached returns the inserted node only when it becomes leftmost\"",
        "test \"rbtree findAddCached keeps cached leftmost stable while inserting misses\"",
        "test \"rbtree cached root keeps the leftmost pointer in sync\"",
        "test \"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\"",
        "test \"rbtree eraseCached returns null for a singleton cached tree\"",
        "test \"rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned\"",
        "test \"rbtree eraseInitCached clears singleton cached roots before reseed\""
      ],
      "review_packet_summary": "shared find, first-match, and next-match duplicate-search parity stays explicit through the Phase 1 fixture and replay, while match-iterator coverage plus cached-root insert-miss, replacement, detach, and reseed behavior remain owned by direct helper-local anchors until master ships dedicated shared iterator or cached-root fixture keys"
    },
    "tools/lib/string.zig": {
      "helper_test_anchors": [
        "test \"strtobool accepts common Linux forms\"",
        "test \"strlcpy copies and returns the source length\"",
        "test \"streq matches C-string equality semantics\"",
        "test \"skip trim remove and replace spaces work in place\"",
        "test \"strreplace mirrors replaceChar C-string semantics\"",
        "test \"strHasPrefix honors C-string boundaries\"",
        "test \"strstarts mirrors the header-level prefix helper\"",
        "test \"strEndsWith honors C-string boundaries\"",
        "test \"sysfsStreq treats trailing newline and NUL as equivalent\"",
        "test \"sysfs_streq mirrors sysfsStreq newline and NUL equivalence\"",
        "test \"memdup and memchrInv preserve byte content\"",
        "test \"memchrInv keeps long-buffer first-dirty-byte results stable\"",
        "test \"memchrInv follows the earliest dirty byte as long buffers change\"",
        "test \"memchrInv dirty-word shortcut handles zero-value scans at word boundaries\"",
        "test \"memchrInv short zero-value scans stay byte-accurate\"",
        "test \"memparse handles decimal hexadecimal octal and suffixes\"",
        "test \"memparse keeps original rest when sign is not followed by digits\"",
        "test \"memparse saturates signed overflow instead of trapping\"",
        "test \"memparse keeps signed values and their trailing rest aligned\"",
        "test \"memparse consumes suffix after saturation\"",
        "test \"memparse applies suffixes before signed clamping\"",
        "test \"phase 1 string trim helpers stop at embedded NUL after trailing whitespace\""
      ],
      "memparse_review_anchors": [
        "test \"memparse keeps original rest when sign is not followed by digits\"",
        "test \"memparse saturates signed overflow instead of trapping\"",
        "test \"memparse keeps signed values and their trailing rest aligned\"",
        "test \"memparse consumes suffix after saturation\"",
        "test \"memparse applies suffixes before signed clamping\""
      ],
      "prefix_suffix_review_anchors": [
        "test \"strHasPrefix honors C-string boundaries\"",
        "test \"strstarts mirrors the header-level prefix helper\"",
        "test \"strEndsWith honors C-string boundaries\""
      ],
      "prefix_suffix_review_summary": "helper-local prefix and suffix boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity rather than dedicated prefix or suffix fixture fields",
      "memparse_review_summary": "helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, signed inputs keep trailing-rest splits aligned with unsigned parsing, signed overflow saturates, and suffixes are still consumed after saturation",
      "phase1_helper_replay_anchor": "test \"phase 1 string replaceChar stops at embedded NUL\"",
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
        "memchr_inv_none"
      ]
    }
  }
}
"""
)

EXPECTED_HELPERS = EXPECTED_PHASE1_MANIFEST["helpers"]
EXPECTED_REVIEW_ANCHORS = EXPECTED_PHASE1_MANIFEST["review_anchors"]

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

WORKFLOW_INSTALL_ZIG_RE = re.compile(
    r"python3 scripts/zigux/install-zig\.py --channel \S+ --dest \.zig-toolchain"
)

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
]

REQUIRED_CLOSURE_MARKERS = [
    ("closure_status_count", "PHASE1_STATUS=closed", 1),
    ("closure_helper_count_count", "PHASE1_HELPER_COUNT=13", 1),
    ("closure_manifest_line_count", "manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`", 1),
    ("closure_parity_gate_count", "PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py", 1),
    ("closure_unit_gate_count", "PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig", 1),
    ("closure_bench_gate_count", "PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig", 1),
    ("closure_bench_check_gate_count", "PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py", 1),
    ("closure_closure_gate_count", "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py", 1),
    ("closure_rollback_count", "PHASE1_ROLLBACK=keep C authoritative and remove failing Zig helper from test/build wiring", 1),
    ("closure_shared_review_workflow_count", "- `.github/workflows/zigux-bootstrap.yml`", 1),
    (
        "closure_find_bit_single_word_review_count",
        "PHASE1_FIND_BIT_SINGLE_WORD_REVIEW=helper-local single-word next-scan proof stays explicit through the direct find_bit test anchor because the shared Phase 1 parity fixture does not isolate same-word start-mask behavior",
        1,
    ),
    (
        "closure_find_bit_inclusive_boundary_review_count",
        "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_REVIEW=helper-local inclusive boundary proof stays explicit through the direct find_bit test anchor so same-word next scans keep the last in-range head-word bit reachable from an inclusive start",
        1,
    ),
    (
        "closure_find_bit_inclusive_boundary_owner_count",
        "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_OWNER=the shared Phase 1 replay now consumes the committed inclusive_boundary_* fixture fields directly, while the direct helper-local inclusive-boundary test remains a review-visible same-word anchor for that path",
        1,
    ),
    (
        "closure_find_bit_zero_window_review_count",
        "PHASE1_FIND_BIT_ZERO_WINDOW_REVIEW=helper-local zero-bit-window proof stays explicit through the direct find_bit test anchor so first-scan entrypoints return the empty-window boundary without reading bitmap words",
        1,
    ),
    (
        "closure_find_bit_past_nbits_review_count",
        "PHASE1_FIND_BIT_PAST_NBITS_REVIEW=helper-local past-nbits short-circuit proof stays explicit through the direct find_bit test anchor so next scans starting at or beyond nbits return the boundary without reading bitmap words outside the caller-visible window",
        1,
    ),
    (
        "closure_find_bit_tail_clamp_review_count",
        "PHASE1_FIND_BIT_TAIL_CLAMP_REVIEW=tail_clamped_first, tail_clamped_next, tail_zero_clamped_first, tail_zero_clamped_next, tail_and_clamped_first, and tail_and_clamped_next stay explicit through the shared Phase 1 parity fixture and replay so last-word scans cannot silently leak masked tail bits beyond nbits",
        1,
    ),
    (
        "closure_find_bit_underscore_alias_review_count",
        "PHASE1_FIND_BIT_UNDERSCORE_ALIAS_REVIEW=helper-local underscore alias proof stays explicit through the direct find_bit test anchor so the Linux-style underscore entry points remain behaviorally locked to the primary Zig helpers",
        1,
    ),
    (
        "closure_bitmap_partial_xor_review_count",
        "PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay explicit through the shared Phase 1 parity fixture and replay so caller-selected bit windows cannot silently leak tail bits beyond nbits",
        1,
    ),
    (
        "closure_bitmap_predicate_tail_mask_review_count",
        "PHASE1_BITMAP_PREDICATE_TAIL_MASK_REVIEW=helper-local bitmap predicate tail-mask proof stays explicit through the direct bitmap test anchor so equal, intersects, and subset ignore out-of-range tail bits instead of treating tail noise as live data",
        1,
    ),
    (
        "closure_bitmap_first_word_boundary_review_count",
        "PHASE1_BITMAP_FIRST_WORD_BOUNDARY_REVIEW=helper-local bitmap first-word boundary proof stays explicit through the direct bitmap test anchor so setRange and clearRange preserve exact first-word masks when a range ends on the first-word boundary",
        1,
    ),
    (
        "closure_bitmap_final_partial_word_review_count",
        "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor so setRange and clearRange clamp trailing partial-word masks to the requested tail window instead of spilling work beyond it",
        1,
    ),
    (
        "closure_bitmap_scnprintf_truncation_review_count",
        "PHASE1_BITMAP_SCNPRINTF_TRUNCATION_REVIEW=helper-local bitmap.scnprintf truncation proof stays explicit through the direct bitmap test anchor because the shared Phase 1 parity fixture only locks the full rendered range string",
        1,
    ),
    (
        "closure_bitmap_scnprintf_tiny_buffer_review_count",
        "PHASE1_BITMAP_SCNPRINTF_TINY_BUFFER_REVIEW=helper-local bitmap.scnprintf tiny-buffer proof stays explicit through the direct bitmap test anchor plus the shared Phase 1 parity fixture and replay so terminator-only caller buffers stay NUL-terminated and zero-length caller views return without writing hidden bytes",
        1,
    ),
    (
        "closure_bitmap_copy_alias_review_count",
        "PHASE1_BITMAP_COPY_ALIAS_REVIEW=helper-local bitmap copy alias proof stays explicit through the direct bitmap test anchor so bitmap_copy_clear_tail and bitmap_copy_and_extend preserve tail masking and zero-filled extension semantics",
        1,
    ),
    (
        "closure_bitmap_raw_copy_alias_review_count",
        "PHASE1_BITMAP_RAW_COPY_ALIAS_REVIEW=helper-local raw bitmap_copy alias proof stays explicit through the direct bitmap test anchor so copy and bitmap_copy preserve unmasked source words instead of silently adopting tail-clearing semantics",
        1,
    ),
    (
        "closure_bitmap_zero_bit_noop_review_count",
        "PHASE1_BITMAP_ZERO_BIT_NOOP_REVIEW=helper-local bitmap zero-bit no-op proof stays explicit through the direct bitmap test anchor so zero-bit windows keep mutating helpers, boolean queries, and the rendered empty-window path from touching caller-visible storage or writing hidden bytes",
        1,
    ),
    (
        "closure_bitmap_linux_alias_review_count",
        "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface",
        1,
    ),
    (
        "closure_rbtree_review_packet_count",
        "PHASE1_RBTREE_REVIEW_PACKET=helper-local rbtree tests plus the shared traversal, detached-node, and duplicate-search replay stay explicit so duplicate-search parity keys remain shared-replay-owned while match-iterator coverage plus cached-root insert-miss, replacement, detach, and reseed behavior keep direct review anchors without implying a broader shared iterator or cached-root fixture packet than current master ships",
        1,
    ),
    (
        "closure_rbtree_review_owner_count",
        "PHASE1_RBTREE_REVIEW_OWNER=the shared Phase 1 replay owns the committed empty-root, insertion-order, replace-order, detached-node, and duplicate-search parity keys, while direct helper-local follow-up anchors own match-iterator coverage plus cached-root insert-miss, replacement, detach, and reseed behavior until current master ships dedicated shared iterator or cached-root fixture fields",
        1,
    ),
    (
        "closure_string_memparse_review_count",
        "PHASE1_STRING_MEMPARSE_REVIEW=helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, signed inputs keep trailing-rest splits aligned with unsigned parsing, signed overflow saturates instead of trapping, and suffixes are still consumed after saturation",
        1,
    ),
    (
        "closure_string_prefix_suffix_review_count",
        "PHASE1_STRING_PREFIX_SUFFIX_REVIEW=helper-local prefix and suffix boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity rather than dedicated prefix or suffix fixture fields",
        1,
    ),
    (
        "closure_string_replace_char_cstr_review_count",
        "PHASE1_STRING_REPLACE_CHAR_CSTR_REVIEW=the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, trimSpaces, removeSpaces, replaceChar, and memchrInv fixture parity while the dedicated embedded-NUL replaceChar follow-up keeps the first-terminator stop rule explicit without widening helper-local memparse ownership",
        1,
    ),
    (
        "closure_string_sysfs_streq_review_count",
        "PHASE1_STRING_SYSFS_STREQ_REVIEW=helper-local sysfsStreq and sysfs_streq anchors stay explicit through the direct string tests so trailing newline and trailing NUL remain equivalent without widening the shared Phase 1 replay surface",
        1,
    ),
    (
        "closure_string_memchr_inv_dirty_word_review_count",
        "PHASE1_STRING_MEMCHR_INV_DIRTY_WORD_REVIEW=helper-local memchrInv long-buffer and zero-value dirty-word anchors stay explicit through the direct string tests while the shared Phase 1 replay keeps the committed first-dirty-byte and all-clean parity keys stable",
        1,
    ),
]

REQUIRED_WORKFLOW_MARKERS = [
    ("workflow_force_node24", "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true"),
    ("workflow_phase1_validate_line", "python3 scripts/zigux/validate-phase1.py"),
    ("workflow_phase1_closure_line", "python3 scripts/zigux/validate-phase1-closure.py"),
    ("workflow_phase1_parity_line", "python3 scripts/zigux/check-phase1-parity.py"),
    ("workflow_phase1_bench_line", "python3 scripts/zigux/check-phase1-bench.py"),
]

REQUIRED_EXACT_WORKFLOW_MARKERS = [
    ("workflow_job_bootstrap", "bootstrap:"),
    ("workflow_phase1_validate_name_count", "- name: Validate Phase 1 helper files", 1),
    ("workflow_phase1_validate_count", "run: python3 scripts/zigux/validate-phase1.py", 1),
    ("workflow_phase1_closure_name_count", "- name: Validate Phase 1 closure", 1),
    ("workflow_phase1_closure_count", "run: python3 scripts/zigux/validate-phase1-closure.py", 1),
    ("workflow_phase1_parity_name_count", "- name: Check Phase 1 helper parity", 1),
    ("workflow_phase1_parity_count", "run: python3 scripts/zigux/check-phase1-parity.py", 1),
    ("workflow_phase1_bench_name_count", "- name: Check Phase 1 helper benchmark output", 1),
    ("workflow_phase1_bench_count", "run: python3 scripts/zigux/check-phase1-bench.py", 1),
]

REQUIRED_PHASE1_WORKFLOW_MARKERS = [
    ("workflow_phase1_build_test_count", "run: zig build test --build-file zigux/tests/build.zig", 1),
    ("workflow_phase1_build_bench_count", "run: zig build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe", 1),
]

REQUIRED_BUILD_MARKERS = [
    ("build_phase1_helpers_import", '@import("phase1_helpers.zig")', 1),
    ("build_phase1_bench_import", '@import("phase1_bench.zig")', 1),
    ("build_test_step_name", 'const test_step = b.step("test", "Run the Phase 1 helper tests")', 1),
    ("build_bench_step_name", 'const bench_step = b.step("bench", "Run the Phase 1 helper benchmark smoke")', 1),
]

REQUIRED_LEDGER_MARKERS = [
    ("ledger_phase1_status_count", "- Status: closed and guarded by the bootstrap workflow, `make -C zigux phase1`, and the Phase 1 closure validator.", 1),
    ("ledger_phase1_lane_guard_count", "- Lane guard: Phase 1 remains limited to the bounded host-side helper tranche while follow-up work routes through the direct helper-local anchors or parked shared replay noted in `Documentation/zigux/phase1-closure.md`.", 1),
]

REQUIRED_MAKEFILE_MARKERS = [
    ("makefile_phase1_validate", "phase1-validate:", 1),
    ("makefile_phase1_validate_cmd", "\tpython3 ../scripts/zigux/validate-phase1.py", 1),
    ("makefile_phase1_closure_cmd", "\tpython3 ../scripts/zigux/validate-phase1-closure.py", 1),
    ("makefile_phase1_test", "phase1-test:", 1),
    ("makefile_phase1_test_cmd", "\tzig build test --build-file tests/build.zig", 1),
    ("makefile_phase1_bench", "phase1-bench:", 1),
    ("makefile_phase1_bench_cmd", "\tzig build bench --build-file tests/build.zig -Doptimize=ReleaseSafe", 1),
    ("makefile_phase1_target", "phase1: phase1-validate phase1-test phase1-bench", 1),
]

REQUIRED_DOCS_ROOT_MARKERS = [
    ("docs_root_phase1_status_count", "- Phase 1 is closed as a bounded helper tranche. The shipped helper packet is `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` plus the parked shared-replay helper set listed in `Documentation/zigux/phase1-closure.md`.", 1),
    ("docs_root_phase1_gate_count", "- The closure gate is `python3 scripts/zigux/validate-phase1-closure.py`, and the release path stays `make -C zigux phase1` plus `python3 scripts/zigux/check-phase1-parity.py` and `python3 scripts/zigux/check-phase1-bench.py` before any direct-anchor or parked shared-replay follow-up lands.", 1),
    ("docs_root_phase1_review_packet_count", "- Review packet: `Documentation/zigux/phase1-closure.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`.", 1),
]

REQUIRED_SCRIPTS_README_MARKERS = [
    ("scripts_readme_phase1_status_count", "- Phase 1 is closed. Use `python3 validate-phase1.py` and `python3 validate-phase1-closure.py` to guard the bounded helper packet before running `python3 check-phase1-parity.py` and `python3 check-phase1-bench.py` or `make -C ../../zigux phase1`.", 1),
    ("scripts_readme_phase1_install_review_count", "- `check-phase1-installer-review-surfaces.py`: keeps the closed Phase 1 installer-review packet aligned across `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/install-zig.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/README.md`, and the review-checklist plus tests-root command markers.", 1),
    ("scripts_readme_phase1_companion_count", "- `check-phase1-installer-companion-checks.py`: keeps the focused companion review markers for `python3 scripts/zigux/install-zig.py --self-test` and `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test` aligned across `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` without widening the closed Phase 1 packet.", 1),
    ("scripts_readme_phase1_helper_anchor_count", "- `check-phase1-parity.py`: validates the committed parity fixture for the direct helper tranche and keeps the shared replay-only follow-up owners in `Documentation/zigux/phase1-closure.md` review-visible while Phase 1 stays closed.", 1),
    ("scripts_readme_phase1_bench_anchor_count", "- `check-phase1-bench.py`: validates the committed benchmark expectation packet before any direct helper-local follow-up updates Phase 1 benchmark checksums or iteration counts.", 1),
]

REQUIRED_TESTS_README_MARKERS = [
    ("tests_readme_phase1_status_count", "- Phase 1 is closed and limited to the bounded helper tranche listed in `Documentation/zigux/phase1-closure.md`. Keep helper-local follow-up on direct anchors for `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig`, and treat the parked shared-replay helper set as closed unless packet drift forces a validator refresh.", 1),
    ("tests_readme_phase1_gate_count", "- Phase 1 release path: `python3 ../scripts/zigux/validate-phase1.py`, `python3 ../scripts/zigux/validate-phase1-closure.py`, `python3 ../scripts/zigux/check-phase1-parity.py`, `python3 ../scripts/zigux/check-phase1-bench.py`, `zig build test --build-file build.zig`, `zig build bench --build-file build.zig -Doptimize=ReleaseSafe`, and `make -C .. phase1`.", 1),
    ("tests_readme_phase1_review_packet_count", "- Review packet: `fixtures/phase1_helper_manifest.json`, `fixtures/phase1_bench_expectations.json`, `phase1_helpers.zig`, `phase1_bench.zig`, `build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `../Documentation/zigux/phase1-closure.md`.", 1),
    ("tests_readme_phase1_installer_companion_count", "- Keep `python3 scripts/zigux/install-zig.py --self-test` and `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test` visible as focused companion checks for the closed Phase 1 installer-review surface without widening the counted tests-root packet line that `scripts/zigux/validate-phase1.py` currently enforces.", 1),
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    ("review_phase1_status_count", "* if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, `zigux/tests/README.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` still agree on the same closed helper tranche and validator-first replay path without widening Phase 1 beyond the bounded host-side helper packet?", 1),
    ("review_phase1_bitmap_review_count", "- `tools/lib/bitmap.zig`: keeps direct first-word-boundary, final-partial-word, predicate-tail-mask, scnprintf truncation or tiny-buffer, copy-alias, raw-copy, zero-bit, and Linux-style alias proofs explicit while the shared parity fixture owns the committed bitmap replay keys.", 1),
    ("review_phase1_find_bit_review_count", "- `tools/lib/find_bit.zig`: keeps direct same-word start-mask, inclusive-boundary, zero-window, past-nbits, tail-word skip, and underscore-alias proofs explicit while the shared parity fixture owns the committed tail-clamp replay keys.", 1),
    ("review_phase1_rbtree_review_count", "- `tools/lib/rbtree.zig`: keeps direct match-iterator plus cached-root insert-miss, replacement, detach, and reseed proofs explicit while the shared parity fixture owns traversal, detached-node, and duplicate-search replay keys.", 1),
    ("review_phase1_string_review_count", "- `tools/lib/string.zig`: keeps direct memparse safety and prefix or suffix boundary anchors explicit while the shared replay owns the committed embedded-NUL replacement bytes and parity fixture keys.", 1),
]

def repo_root_from_arg(root_arg: str | None) -> Path:
    if root_arg:
        return Path(root_arg).resolve()
    return DEFAULT_ROOT

def load_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")

def load_json_file(path: Path, label: str) -> tuple[object | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return None, [f"{label}:json_decode:{exc.msg}"]
def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    return missing

def collect_exact_count_markers(text: str, markers: list[tuple[str, str, int]]) -> list[str]:
    missing: list[str] = []
    for label, marker, expected in markers:
        actual = text.count(marker)
        if actual != expected:
            missing.append(f"{label}:expected={expected}:actual={actual}")
    return missing

def collect_exact_line_count_markers(
    text: str, markers: list[tuple[str, str] | tuple[str, str, int]]
) -> list[str]:
    lines = text.splitlines()
    missing: list[str] = []
    for item in markers:
        if len(item) == 2:
            label, marker = item
            expected = 1
        else:
            label, marker, expected = item
        actual = sum(1 for line in lines if line.strip() == marker)
        if actual != expected:
            missing.append(f"{label}:expected={expected}:actual={actual}")
    return missing

def collect_workflow_markers(workflow_text: str) -> list[str]:
    missing: list[str] = []
    for label, marker in REQUIRED_WORKFLOW_MARKERS:
        if marker not in workflow_text:
            missing.append(f"{label}:missing")
    if not WORKFLOW_INSTALL_ZIG_RE.search(workflow_text):
        missing.append("workflow_install_zig:missing")
    return missing

def extract_workflow_job(workflow_text: str, job_name: str) -> str:
    lines = workflow_text.splitlines()
    job_anchor = f"  {job_name}:"
    start: int | None = None
    for idx, line in enumerate(lines):
        if line == job_anchor:
            start = idx
            break
    if start is None:
        return ""
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        line = lines[idx]
        if line.startswith("  ") and not line.startswith("    "):
            end = idx
            break
    return "\n".join(lines[start:end])

def collect_manifest_review_anchor_markers(manifest: object) -> list[str]:
    if not isinstance(manifest, dict):
        return ["manifest:json_object"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["manifest:review_anchors=dict"]

    missing: list[str] = []
    expected_helpers = set(EXPECTED_REVIEW_ANCHORS)
    actual_helpers = set()
    for helper_path, anchors in review_anchors.items():
        if not isinstance(helper_path, str):
            missing.append("manifest:review_helper_key_type=str")
            continue
        actual_helpers.add(helper_path)
        expected_fields = EXPECTED_REVIEW_ANCHORS.get(helper_path)
        if expected_fields is None:
            missing.append(f"manifest:unexpected_review_helper={helper_path}")
            continue
        if not isinstance(anchors, dict):
            missing.append(f"manifest:review_helper_value=dict:{helper_path}")
            continue
        for field_name, expected_value in expected_fields.items():
            if field_name not in anchors:
                missing.append(f"manifest:missing_review_anchor_field={helper_path}:{field_name}")
                continue
            actual_value = anchors[field_name]
            if actual_value != expected_value:
                missing.append(f"manifest:review_anchor_value={helper_path}:{field_name}")
        for field_name in anchors:
            if field_name not in expected_fields:
                missing.append(f"manifest:unexpected_review_anchor_field={helper_path}:{field_name}")
    for helper_path in sorted(expected_helpers - actual_helpers):
        missing.append(f"manifest:missing_review_helper={helper_path}")
    for helper_path in sorted(actual_helpers - expected_helpers):
        missing.append(f"manifest:unexpected_review_helper={helper_path}")
    return missing

def collect_manifest_markers(manifest: object, root: Path) -> list[str]:
    if not isinstance(manifest, dict):
        return ["manifest:json_object"]

    missing: list[str] = []
    if manifest.get("phase") != "Phase 1":
        missing.append("manifest:phase=Phase 1")
    if manifest.get("status") != "closed":
        missing.append("manifest:status=closed")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        missing.append(f"manifest:helper_count={len(EXPECTED_HELPERS)}")

    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        missing.append("manifest:helpers=list")
        return missing

    if manifest.get("helper_count") != len(helpers):
        missing.append(f"manifest:helper_count={len(helpers)}")
    if len(helpers) != len(EXPECTED_HELPERS):
        missing.append(f"manifest:helpers_len={len(EXPECTED_HELPERS)}")

    seen: set[str] = set()
    duplicates: set[str] = set()
    string_helpers: list[str] = []
    for rel in helpers:
        if not isinstance(rel, str):
            missing.append("manifest:helper_path_type=str")
            continue
        string_helpers.append(rel)
        if rel in seen:
            duplicates.add(rel)
        seen.add(rel)
        if not (root / rel).exists():
            missing.append(f"manifest_file:{rel}")

    expected = set(EXPECTED_HELPERS)
    actual = set(string_helpers)
    for rel in sorted(expected - actual):
        missing.append(f"manifest:missing_helper={rel}")
    for rel in sorted(actual - expected):
        missing.append(f"manifest:unexpected_helper={rel}")
    for rel in sorted(duplicates):
        missing.append(f"manifest:duplicate_helper={rel}")
    missing.extend(collect_manifest_review_anchor_markers(manifest))
    return missing

def collect_bench_expectation_markers(expectations: object) -> list[str]:
    if not isinstance(expectations, dict):
        return ["bench_expectations:json_object"]

    missing: list[str] = []
    if expectations.get("status") != "pass":
        missing.append("bench_expectations:status=pass")

    iterations = expectations.get("iterations")
    if not isinstance(iterations, dict):
        missing.append("bench_expectations:iterations=dict")
    else:
        actual_keys: set[str] = set()
        for key, value in iterations.items():
            if not isinstance(key, str):
                missing.append("bench_expectations:iteration_key_type=str")
                continue
            actual_keys.add(key)
            expected_value = EXPECTED_BENCH_ITERATIONS.get(key)
            if expected_value is None:
                missing.append(f"bench_expectations:unexpected_iteration={key}")
            elif value != expected_value:
                missing.append(f"bench_expectations:iteration_value={key}:{expected_value}")
        for key in sorted(set(EXPECTED_BENCH_ITERATIONS) - actual_keys):
            missing.append(f"bench_expectations:missing_iteration={key}")

    checksums = expectations.get("checksums")
    if not isinstance(checksums, list):
        missing.append("bench_expectations:checksums=list")
    else:
        actual: list[str] = []
        seen: set[str] = set()
        duplicates: set[str] = set()
        for item in checksums:
            if not isinstance(item, str):
                missing.append("bench_expectations:checksum_type=str")
                continue
            actual.append(item)
            if item in seen:
                duplicates.add(item)
            seen.add(item)
        for item in sorted(duplicates):
            missing.append(f"bench_expectations:duplicate_checksum={item}")
        expected = set(EXPECTED_BENCH_CHECKSUMS)
        actual_set = set(actual)
        for item in sorted(expected - actual_set):
            missing.append(f"bench_expectations:missing_checksum={item}")
        for item in sorted(actual_set - expected):
            missing.append(f"bench_expectations:unexpected_checksum={item}")
    return missing

def count_manifest_review_anchor_expectations() -> int:
    return 1 + len(EXPECTED_REVIEW_ANCHORS) + sum(len(fields) for fields in EXPECTED_REVIEW_ANCHORS.values())

def count_manifest_metadata_expectations() -> int:
    return 4 + len(EXPECTED_HELPERS)

def count_bench_expectation_expectations() -> int:
    return 1 + len(EXPECTED_BENCH_ITERATIONS) + len(EXPECTED_BENCH_CHECKSUMS)

def render_marker_fixture(markers: list[tuple[str, str, int]]) -> str:
    return "\n".join(marker for _, marker, _ in markers) + "\n"

def make_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES + EXPECTED_HELPERS:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// fixture\n", encoding="utf-8")

    (tmp_root / "Documentation/zigux/phase1-closure.md").write_text(
        render_marker_fixture(REQUIRED_CLOSURE_MARKERS),
        encoding="utf-8",
    )
    bootstrap_lines = [item[1] for item in REQUIRED_EXACT_WORKFLOW_MARKERS[1:]] + [
        item[1] for item in REQUIRED_PHASE1_WORKFLOW_MARKERS
    ]
    workflow_text = "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true\njobs:\n  bootstrap:\n" + "".join(
        f"    {line}\n" for line in bootstrap_lines
    )
    (tmp_root / ".github/workflows/zigux-bootstrap.yml").write_text(workflow_text, encoding="utf-8")
    (tmp_root / "zigux/tests/build.zig").write_text(render_marker_fixture(REQUIRED_BUILD_MARKERS), encoding="utf-8")
    (tmp_root / "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md").write_text(render_marker_fixture(REQUIRED_LEDGER_MARKERS), encoding="utf-8")
    (tmp_root / "zigux/Makefile").write_text(render_marker_fixture(REQUIRED_MAKEFILE_MARKERS), encoding="utf-8")
    (tmp_root / "Documentation/zigux/README.md").write_text(render_marker_fixture(REQUIRED_DOCS_ROOT_MARKERS), encoding="utf-8")
    (tmp_root / "scripts/zigux/README.md").write_text(render_marker_fixture(REQUIRED_SCRIPTS_README_MARKERS), encoding="utf-8")
    (tmp_root / "zigux/tests/README.md").write_text(render_marker_fixture(REQUIRED_TESTS_README_MARKERS), encoding="utf-8")
    (tmp_root / "Documentation/zigux/review-checklist.md").write_text(render_marker_fixture(REQUIRED_REVIEW_CHECKLIST_MARKERS), encoding="utf-8")

    manifest = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": EXPECTED_HELPERS,
        "review_anchors": EXPECTED_REVIEW_ANCHORS,
    }
    (tmp_root / "zigux/tests/fixtures/phase1_helper_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    bench = {
        "status": "pass",
        "iterations": dict(EXPECTED_BENCH_ITERATIONS),
        "checksums": list(EXPECTED_BENCH_CHECKSUMS),
    }
    (tmp_root / "zigux/tests/fixtures/phase1_bench_expectations.json").write_text(
        json.dumps(bench, indent=2) + "\n",
        encoding="utf-8",
    )

def collect_missing_markers(root: Path) -> list[str]:
    closure = load_text(root, "Documentation/zigux/phase1-closure.md")
    workflow = load_text(root, ".github/workflows/zigux-bootstrap.yml")
    tests_build = load_text(root, "zigux/tests/build.zig")
    ledger = load_text(root, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")
    makefile = load_text(root, "zigux/Makefile")
    docs_root = load_text(root, "Documentation/zigux/README.md")
    scripts_readme = load_text(root, "scripts/zigux/README.md")
    tests_readme = load_text(root, "zigux/tests/README.md")
    review_checklist = load_text(root, "Documentation/zigux/review-checklist.md")
    manifest, manifest_parse_markers = load_json_file(root / "zigux/tests/fixtures/phase1_helper_manifest.json", "manifest")
    bench_expectations, bench_parse_markers = load_json_file(
        root / "zigux/tests/fixtures/phase1_bench_expectations.json",
        "bench_expectations",
    )
    bootstrap_workflow = extract_workflow_job(workflow, "bootstrap")

    missing = collect_workflow_markers(workflow)
    missing.extend(manifest_parse_markers)
    missing.extend(bench_parse_markers)
    missing.extend(collect_exact_line_count_markers(workflow, [REQUIRED_EXACT_WORKFLOW_MARKERS[0]]))
    missing.extend(collect_exact_line_count_markers(bootstrap_workflow, REQUIRED_EXACT_WORKFLOW_MARKERS[1:]))
    missing.extend(collect_exact_count_markers(closure, REQUIRED_CLOSURE_MARKERS))
    missing.extend(collect_exact_count_markers(tests_build, REQUIRED_BUILD_MARKERS))
    missing.extend(collect_exact_count_markers(ledger, REQUIRED_LEDGER_MARKERS))
    missing.extend(collect_exact_line_count_markers(bootstrap_workflow, REQUIRED_PHASE1_WORKFLOW_MARKERS))
    missing.extend(collect_exact_count_markers(makefile, REQUIRED_MAKEFILE_MARKERS))
    missing.extend(collect_exact_count_markers(docs_root, REQUIRED_DOCS_ROOT_MARKERS))
    missing.extend(collect_exact_count_markers(scripts_readme, REQUIRED_SCRIPTS_README_MARKERS))
    missing.extend(collect_exact_count_markers(tests_readme, REQUIRED_TESTS_README_MARKERS))
    missing.extend(collect_exact_count_markers(review_checklist, REQUIRED_REVIEW_CHECKLIST_MARKERS))
    if manifest is not None:
        missing.extend(collect_manifest_markers(manifest, root))
    if bench_expectations is not None:
        missing.extend(collect_bench_expectation_markers(bench_expectations))
    return missing

def assert_missing_marker_case(tmp_root: Path, mutate, expected_marker: str) -> None:
    mutate()
    missing = collect_missing_markers(tmp_root)
    assert expected_marker in missing
    make_fixture_root(tmp_root)

def run_self_test() -> None:
    self_test_case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_closure_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        make_fixture_root(tmp_root)
        assert collect_missing_files(tmp_root) == []
        assert collect_missing_markers(tmp_root) == []

        closure_path = tmp_root / "Documentation/zigux/phase1-closure.md"
        closure_text = closure_path.read_text(encoding="utf-8")

        for label, marker, _ in [
            REQUIRED_CLOSURE_MARKERS[12],
            REQUIRED_CLOSURE_MARKERS[13],
            REQUIRED_CLOSURE_MARKERS[14],
            REQUIRED_CLOSURE_MARKERS[17],
            REQUIRED_CLOSURE_MARKERS[19],
            REQUIRED_CLOSURE_MARKERS[20],
            REQUIRED_CLOSURE_MARKERS[24],
            REQUIRED_CLOSURE_MARKERS[26],
        ]:
            def mutate_closure(marker=marker):
                closure_path.write_text(closure_text.replace(marker + "\n", "", 1), encoding="utf-8")

            assert_missing_marker_case(tmp_root, mutate_closure, f"{label}:expected=1:actual=0")
            self_test_case_count += 1

        manifest_path = tmp_root / "zigux/tests/fixtures/phase1_helper_manifest.json"

        def load_manifest() -> dict[str, Any]:
            return json.loads(manifest_path.read_text(encoding="utf-8"))

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: manifest_path.write_text(
                    json.dumps({**manifest, "helpers": manifest["helpers"][:-1]}, indent=2) + "\n",
                    encoding="utf-8",
                )
            )(load_manifest()),
            "manifest:helpers_len=13",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("first_word_boundary_anchor"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:missing_review_anchor_field=tools/lib/bitmap.zig:first_word_boundary_anchor",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("final_partial_word_anchor"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:missing_review_anchor_field=tools/lib/bitmap.zig:final_partial_word_anchor",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("predicate_tail_mask_anchor"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:missing_review_anchor_field=tools/lib/bitmap.zig:predicate_tail_mask_anchor",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("linux_alias_anchor"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:missing_review_anchor_field=tools/lib/bitmap.zig:linux_alias_anchor",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/find_bit.zig"].pop("zero_bit_window"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:missing_review_anchor_field=tools/lib/find_bit.zig:zero_bit_window",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/find_bit.zig"].pop("underscore_alias_anchor"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:missing_review_anchor_field=tools/lib/find_bit.zig:underscore_alias_anchor",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/find_bit.zig"]["tail_clamp_fixture_keys"].remove("tail_clamped_last"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:review_anchor_value=tools/lib/find_bit.zig:tail_clamp_fixture_keys",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/find_bit.zig"]["helper_test_anchors"].pop(),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:review_anchor_value=tools/lib/find_bit.zig:helper_test_anchors",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/find_bit.zig"].pop("tail_word_skip_anchor"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:missing_review_anchor_field=tools/lib/find_bit.zig:tail_word_skip_anchor",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/find_bit.zig"].pop("review_packet_summary"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:missing_review_anchor_field=tools/lib/find_bit.zig:review_packet_summary",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/rbtree.zig"]["cached_root_followup_anchors"].remove(
                        'test "rbtree eraseInitCached clears singleton cached roots before reseed"'
                    ),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:review_anchor_value=tools/lib/rbtree.zig:cached_root_followup_anchors",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/string.zig"]["helper_test_anchors"].remove(
                        'test "sysfsStreq treats trailing newline and NUL as equivalent"'
                    ),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:review_anchor_value=tools/lib/string.zig:helper_test_anchors",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/string.zig"]["helper_test_anchors"].remove(
                        'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"'
                    ),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:review_anchor_value=tools/lib/string.zig:helper_test_anchors",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/string.zig"]["helper_test_anchors"].remove(
                        'test "memchrInv follows the earliest dirty byte as long buffers change"'
                    ),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:review_anchor_value=tools/lib/string.zig:helper_test_anchors",
        )
        self_test_case_count += 1

        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/string.zig"].pop("shared_replace_char_cstr_review_summary"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_manifest()),
            "manifest:missing_review_anchor_field=tools/lib/string.zig:shared_replace_char_cstr_review_summary",
        )
        self_test_case_count += 1

        bench_path = tmp_root / "zigux/tests/fixtures/phase1_bench_expectations.json"
        assert_missing_marker_case(
            tmp_root,
            lambda: (
                lambda bench: (
                    bench["iterations"].pop("PHASE1_BENCH_STRING_ITERATIONS"),
                    bench_path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8"),
                )
            )(json.loads(bench_path.read_text(encoding="utf-8"))),
            "bench_expectations:missing_iteration=PHASE1_BENCH_STRING_ITERATIONS",
        )
        self_test_case_count += 1

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        assert_missing_marker_case(
            tmp_root,
            lambda: workflow_path.write_text(
                workflow_path.read_text(encoding="utf-8").replace(
                    "run: python3 scripts/zigux/check-phase1-bench.py\n", "", 1
                ),
                encoding="utf-8",
            ),
            "workflow_phase1_bench_count:expected=1:actual=0",
        )
        self_test_case_count += 1

        makefile_path = tmp_root / "zigux/Makefile"
        assert_missing_marker_case(
            tmp_root,
            lambda: makefile_path.write_text(
                makefile_path.read_text(encoding="utf-8").replace(
                    "phase1: phase1-validate phase1-test phase1-bench\n", "", 1
                ),
                encoding="utf-8",
            ),
            "makefile_phase1_target:expected=1:actual=0",
        )
        self_test_case_count += 1

        (tmp_root / "zigux/tests/phase1_helpers.zig").unlink()
        assert collect_missing_files(tmp_root) == ["zigux/tests/phase1_helpers.zig"]
        self_test_case_count += 1
        make_fixture_root(tmp_root)

        (tmp_root / ".github/workflows/zigux-bootstrap.yml").unlink()
        assert collect_missing_files(tmp_root) == [".github/workflows/zigux-bootstrap.yml"]
        self_test_case_count += 1

    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT={self_test_case_count}")

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
        f"{len(REQUIRED_CLOSURE_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_EXACT_WORKFLOW_MARKERS) + len(REQUIRED_PHASE1_WORKFLOW_MARKERS) + len(REQUIRED_BUILD_MARKERS) + len(REQUIRED_LEDGER_MARKERS) + len(REQUIRED_MAKEFILE_MARKERS) + len(REQUIRED_DOCS_ROOT_MARKERS) + len(REQUIRED_SCRIPTS_README_MARKERS) + len(REQUIRED_TESTS_README_MARKERS) + len(REQUIRED_REVIEW_CHECKLIST_MARKERS) + count_manifest_review_anchor_expectations() + count_manifest_metadata_expectations() + count_bench_expectation_expectations()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

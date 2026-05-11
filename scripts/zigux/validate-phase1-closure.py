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
      "review_packet_summary": "shared Phase 1 fixture keys now own bitmap scnprintf output, tiny-buffer, and partial-window xor replay, while helper-local anchors keep allocator sizing and zero-fill behavior, predicate tail-mask, first-word and final-partial range boundaries, cross-word scnprintf collapse, truncation, copy alias, raw copy alias, zero-and-aligned copy-and-extend behavior, zero-bit no-op, zero-bit binary identity, and Linux-style alias behavior review-visible on current master",
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
        "test \"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\"",
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

EXPECTED_BENCH_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 2260000,
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 620000,
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 15621472,
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 23340000,
    "PHASE1_BENCH_STRING_CHECKSUM": 320000,
    "PHASE1_BENCH_RBTREE_CHECKSUM": 3380000,
}

WORKFLOW_INSTALL_ZIG = "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain"
WORKFLOW_CONCURRENCY = "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}-{2}', github.workflow, github.ref, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}"

CLOSURE_MARKERS = [
    ("closure_status", "PHASE1_STATUS=closed"),
    ("closure_helper_count", "PHASE1_HELPER_COUNT=13"),
    ("closure_parity_gate", "PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py"),
    ("closure_unit_gate", "PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig"),
    ("closure_bench_gate", "PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig"),
    ("closure_bench_check_gate", "PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py"),
    ("closure_closure_gate", "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py"),
    (
        "closure_rbtree_review_packet",
        "PHASE1_RBTREE_REVIEW_PACKET=helper-local rbtree tests plus the shared traversal, detached-node, and duplicate-search replay stay explicit so duplicate-search parity keys remain shared-replay-owned while match-iterator coverage plus cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior keep direct review anchors without implying a broader shared iterator or cached-root fixture packet than current master ships",
    ),
    (
        "closure_string_memparse_review",
        "PHASE1_STRING_MEMPARSE_REVIEW=helper-local memparse safety anchors stay explicit through the direct string tests and the Phase 1 helper manifest so sign-prefixed invalid input preserves rest, signed overflow saturates instead of trapping, and suffixes are still consumed after saturation",
    ),
    (
        "closure_string_review_packet",
        "PHASE1_STRING_REVIEW_PACKET=helper-local string tests and the shared embedded-NUL replay stay explicit so the bounded Phase 1 string surface keeps its direct review anchors, committed C-string replacement bytes, and parity fixture keys",
    ),
    ("closure_rollback", "PHASE1_ROLLBACK=keep C authoritative and remove failing Zig helper from test/build wiring"),
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
]

DOCS_ROOT_MARKERS = [
    (
        "docs_root_phase1_packet",
        "- `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep the closed host-side helper packet reviewable through the shared helper build entrypoint and the Linux-style replay route, while `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the closure, installer-backed workflow-viability replay, the dedicated installer-review alignment checker, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.",
    ),
    (
        "docs_root_phase1_owner_map_note",
        "`Documentation/zigux/phase1-host-helper-lane-sequencing.md` keeps the shared owner-map note visible beside that same docs-root packet.",
    ),
]

SCRIPTS_README_MARKERS = [
    (
        "scripts_readme_phase1_packet",
        "- `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep that same closed host-side helper packet reviewable through the docs-root closure record, the shared owner-map note, the reviewer-facing checklist, the workflow-viability installer, the dedicated installer-review alignment checker, the bootstrap workflow replay, and the Linux-style replay routes instead of leaving the Phase 1 closure stack visible only through direct script and Zig commands.",
    ),
    (
        "scripts_readme_phase1_string_packet",
        "- `tools/lib/string.zig`, `Documentation/zigux/phase1-closure.md`, and `zigux/tests/fixtures/phase1_helper_manifest.json` also keep the direct Phase 1 string review packet explicit, including the `memchr_inv()` alias replay, the zero-value prefix-alignment `memchrInv()` follow-up, and the explicit positive-overflow `memparse()` anchor, so those helper-local proofs stay reviewable without widening the shared parity fixture.",
    ),
]

TESTS_README_MARKERS = [
    (
        "tests_readme_phase1_packet",
        "  * keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root, scripts root, and workflow replay surface",
    ),
    (
        "tests_readme_phase1_companion_checks",
        "  * keep `python3 scripts/zigux/install-zig.py --self-test` and `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test` visible as focused companion checks for the closed Phase 1 installer-review surface without widening the counted tests-root packet line that `scripts/zigux/validate-phase1.py` currently enforces",
    ),
]

REVIEW_CHECKLIST_MARKERS = [
    (
        "review_checklist_phase1_packet",
        "  * if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, `zigux/tests/README.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` still agree on the same closed helper tranche and validator-first replay path without widening Phase 1 beyond the bounded host-side helper packet?",
    )
]

LEDGER_MARKERS = [
    ("ledger_phase1_docs_commit", "`docs(zigux): close bounded phase-1 helper tranche`"),
    ("ledger_phase1_tests_commit", "`test(zigux): harden phase-1 closure gates`"),
    ("ledger_phase1_ci_commit", "`ci(zigux): harden phase-1 closure workflow viability`"),
    ("ledger_phase1_build_commit", "`build(zigux): remove node-20-bound Zig action from phase-1 closure path`"),
]

MAKEFILE_MARKERS = [
    ("makefile_phase1_validate_target", "phase1-validate:"),
    ("makefile_phase1_validate", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py"),
    ("makefile_phase1_installer_selftest", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-review-surfaces.py --self-test"),
    ("makefile_phase1_companion_selftest", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py --self-test"),
    ("makefile_phase1_closure", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py"),
    ("makefile_phase1_test_target", "phase1-test:"),
    ("makefile_phase1_test", "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig"),
    ("makefile_phase1_bench_target", "phase1-bench:"),
    ("makefile_phase1_bench", "cd $(ZIGUX_ROOT) && $(ZIG) build bench --build-file zigux/tests/build.zig"),
    ("makefile_phase1_target", "phase1: phase1-validate phase1-test phase1-bench"),
]

BUILD_MARKERS = [
    ("build_phase1_helpers_source", '.root_source_file = b.path("phase1_helpers.zig")'),
    ("build_phase1_tests_name", '.name = "phase1-helper-tests"'),
    ("build_phase1_test_step", 'b.step("test", "Run Phase 1 helper tests")'),
    ("build_phase1_bench_source", '.root_source_file = b.path("phase1_bench.zig")'),
    ("build_phase1_bench_name", '.name = "phase1-bench"'),
    ("build_phase1_bench_step", 'b.step("bench", "Run Phase 1 helper benchmark smoke")'),
]

WORKFLOW_MARKERS = [
    ("workflow_concurrency", WORKFLOW_CONCURRENCY),
    ("workflow_phase1_validate", "run: python3 scripts/zigux/validate-phase1.py"),
    ("workflow_phase1_closure", "run: python3 scripts/zigux/validate-phase1-closure.py"),
    ("workflow_phase1_parity", "run: python3 scripts/zigux/check-phase1-parity.py"),
    ("workflow_phase1_bench", "run: python3 scripts/zigux/check-phase1-bench.py"),
    ("workflow_phase1_test", "run: zig build test --build-file zigux/tests/build.zig"),
    ("workflow_phase1_bench_replay", "run: zig build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe"),
]

WORKFLOW_PRESENCE_MARKERS = [
    ("workflow_checkout", "uses: actions/checkout@v6.0.2"),
    ("workflow_setup_python", "uses: actions/setup-python@v6.2.0"),
    ("workflow_install_zig", WORKFLOW_INSTALL_ZIG),
]

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-installer-companion-checks.py",
    "scripts/zigux/check-phase1-installer-review-surfaces.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/phase1_helpers.zig",
]

def repo_root_from_arg(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()

def load_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")

def load_json(root: Path, relative_path: str) -> Any:
    return json.loads((root / relative_path).read_text(encoding="utf-8"))

def collect_missing_files(root: Path) -> list[str]:
    return [path for path in REQUIRED_FILES if not (root / path).exists()]

def require_exact_counts(text: str, cases: list[tuple[str, str]]) -> list[str]:
    missing: list[str] = []
    for label, marker in cases:
        actual = text.count(marker)
        if actual != 1:
            missing.append(f"{label}:expected=1:actual={actual}")
    return missing

def require_present(text: str, cases: list[tuple[str, str]]) -> list[str]:
    missing: list[str] = []
    for label, marker in cases:
        actual = text.count(marker)
        if actual < 1:
            missing.append(f"{label}:expected>=1:actual={actual}")
    return missing

def extract_job_block(workflow: str, job_name: str) -> str:
    match = re.search(rf"^  {re.escape(job_name)}:\n(.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)", workflow, re.MULTILINE | re.DOTALL)
    if not match:
        return ""
    return match.group(0)

def collect_manifest_markers(manifest: Any) -> list[str]:
    missing: list[str] = []
    if manifest.get("phase") != "Phase 1":
        missing.append(f"manifest:phase={manifest.get('phase')!r}")
    if manifest.get("status") != "closed":
        missing.append(f"manifest:status={manifest.get('status')!r}")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        missing.append(
            f"manifest:helper_count:expected={len(EXPECTED_HELPERS)}:actual={manifest.get('helper_count')!r}"
        )
    if manifest.get("helpers") != EXPECTED_HELPERS:
        missing.append("manifest:helpers")

    lane_sequencing = manifest.get("lane_sequencing", {})
    expected_lane = EXPECTED_PHASE1_MANIFEST["lane_sequencing"]
    if lane_sequencing != expected_lane:
        missing.append("manifest:lane_sequencing")

    review_anchors = manifest.get("review_anchors", {})
    for helper, expected in EXPECTED_REVIEW_ANCHORS.items():
        actual = review_anchors.get(helper)
        if actual != expected:
            missing.append(f"manifest:review_anchor:{helper}")
    return missing

def collect_bench_markers(expectations: Any) -> list[str]:
    missing: list[str] = []
    if expectations.get("status") != "pass":
        missing.append(f"bench:status={expectations.get('status')!r}")
    iterations = expectations.get("iterations", {})
    for key, expected in EXPECTED_BENCH_ITERATIONS.items():
        if iterations.get(key) != expected:
            missing.append(f"bench:{key}:expected={expected}:actual={iterations.get(key)!r}")
    checksums = expectations.get("checksums", [])
    for key in EXPECTED_BENCH_CHECKSUMS:
        if key not in checksums:
            missing.append(f"bench:missing_checksum:{key}")
    exact = expectations.get("exact_checksums", {})
    for key, expected in EXPECTED_BENCH_EXACT_CHECKSUMS.items():
        if exact.get(key) != expected:
            missing.append(f"bench:{key}:expected={expected}:actual={exact.get(key)!r}")
    return missing

def collect_missing_markers(root: Path) -> list[str]:
    workflow = load_text(root, ".github/workflows/zigux-bootstrap.yml")
    bootstrap_job = extract_job_block(workflow, "bootstrap")
    if not bootstrap_job:
        return ["workflow:missing bootstrap job"]

    closure = load_text(root, "Documentation/zigux/phase1-closure.md")
    docs_root = load_text(root, "Documentation/zigux/README.md")
    scripts_readme = load_text(root, "scripts/zigux/README.md")
    tests_readme = load_text(root, "zigux/tests/README.md")
    review_checklist = load_text(root, "Documentation/zigux/review-checklist.md")
    ledger = load_text(root, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")
    makefile = load_text(root, "zigux/Makefile")
    build_zig = load_text(root, "zigux/tests/build.zig")
    manifest = load_json(root, "zigux/tests/fixtures/phase1_helper_manifest.json")
    bench_expectations = load_json(root, "zigux/tests/fixtures/phase1_bench_expectations.json")

    missing: list[str] = []
    missing.extend(require_exact_counts(workflow, WORKFLOW_MARKERS))
    missing.extend(require_exact_counts(bootstrap_job, WORKFLOW_PRESENCE_MARKERS))
    if re.search(r"mlugg/setup-zig@", workflow):
        missing.append("workflow:unexpected mlugg/setup-zig@ reference")
    missing.extend(require_exact_counts(closure, CLOSURE_MARKERS))
    missing.extend(require_exact_counts(docs_root, DOCS_ROOT_MARKERS))
    missing.extend(require_exact_counts(scripts_readme, SCRIPTS_README_MARKERS))
    missing.extend(require_exact_counts(tests_readme, TESTS_README_MARKERS))
    missing.extend(require_exact_counts(review_checklist, REVIEW_CHECKLIST_MARKERS))
    missing.extend(require_exact_counts(ledger, LEDGER_MARKERS))
    missing.extend(require_exact_counts(makefile, MAKEFILE_MARKERS))
    missing.extend(require_exact_counts(build_zig, BUILD_MARKERS))
    missing.extend(collect_manifest_markers(manifest))
    missing.extend(collect_bench_markers(bench_expectations))
    return missing

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def make_fixture_root(root: Path) -> None:
    for path in REQUIRED_FILES:
        write_text(root / path, "// fixture\n")

    write_text(
        root / ".github/workflows/zigux-bootstrap.yml",
        "\n".join([marker for _, marker in WORKFLOW_MARKERS]) + "\n  bootstrap:\n" + "\n".join([f"    # {label}\n    {marker}" for label, marker in WORKFLOW_PRESENCE_MARKERS]) + "\n  phase2-cross-scope:\n    steps: []\n",
    )
    write_text(
        root / "Documentation/zigux/phase1-closure.md",
        "\n".join([marker for _, marker in CLOSURE_MARKERS]) + "\n",
    )
    write_text(
        root / "Documentation/zigux/README.md",
        "\n".join([marker for _, marker in DOCS_ROOT_MARKERS]) + "\n",
    )
    write_text(
        root / "scripts/zigux/README.md",
        "\n".join([marker for _, marker in SCRIPTS_README_MARKERS]) + "\n",
    )
    write_text(
        root / "zigux/tests/README.md",
        "\n".join([marker for _, marker in TESTS_README_MARKERS]) + "\n",
    )
    write_text(
        root / "Documentation/zigux/review-checklist.md",
        "\n".join([marker for _, marker in REVIEW_CHECKLIST_MARKERS]) + "\n",
    )
    write_text(
        root / "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
        "\n".join([marker for _, marker in LEDGER_MARKERS]) + "\n",
    )
    write_text(root / "zigux/Makefile", "\n".join([marker for _, marker in MAKEFILE_MARKERS]) + "\n")
    write_text(root / "zigux/tests/build.zig", "\n".join([marker for _, marker in BUILD_MARKERS]) + "\n")
    write_text(
        root / "zigux/tests/fixtures/phase1_helper_manifest.json",
        json.dumps(EXPECTED_PHASE1_MANIFEST, indent=2) + "\n",
    )
    write_text(
        root / "zigux/tests/fixtures/phase1_bench_expectations.json",
        json.dumps(
            {
                "status": "pass",
                "iterations": EXPECTED_BENCH_ITERATIONS,
                "checksums": EXPECTED_BENCH_CHECKSUMS,
                "exact_checksums": EXPECTED_BENCH_EXACT_CHECKSUMS,
            },
            indent=2,
        )
        + "\n",
    )

def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_closure_") as tmp:
        root = Path(tmp)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 1

        lane_note_path = root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md"
        lane_note_path.unlink()
        missing_files = collect_missing_files(root)
        assert "Documentation/zigux/phase1-host-helper-lane-sequencing.md" in missing_files
        case_count += 1
        make_fixture_root(root)

        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(workflow.replace(WORKFLOW_INSTALL_ZIG + "\n", "", 1), encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "workflow_install_zig:expected=1:actual=0" in missing
        case_count += 1
        make_fixture_root(root)

        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(workflow + WORKFLOW_INSTALL_ZIG + "\n", encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "workflow_install_zig:expected=1:actual=2" in missing
        case_count += 1
        make_fixture_root(root)

        docs_root_path = root / "Documentation/zigux/README.md"
        docs_root = docs_root_path.read_text(encoding="utf-8")
        target = "`Documentation/zigux/phase1-host-helper-lane-sequencing.md` keeps the shared owner-map note visible beside that same docs-root packet.\n"
        docs_root_path.write_text(docs_root.replace(target, "", 1), encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "docs_root_phase1_owner_map_note:expected=1:actual=0" in missing
        case_count += 1
        make_fixture_root(root)

        closure_path = root / "Documentation/zigux/phase1-closure.md"
        closure = closure_path.read_text(encoding="utf-8")
        target = "PHASE1_STRING_MEMPARSE_REVIEW=helper-local memparse safety anchors stay explicit through the direct string tests and the Phase 1 helper manifest so sign-prefixed invalid input preserves rest, signed overflow saturates instead of trapping, and suffixes are still consumed after saturation\n"
        closure_path.write_text(closure.replace(target, "", 1), encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "closure_string_memparse_review:expected=1:actual=0" in missing
        case_count += 1
        make_fixture_root(root)

        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("copy_raw_alias_anchor")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "manifest:review_anchor:tools/lib/bitmap.zig" in missing
        case_count += 1
        make_fixture_root(root)

        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["lane_sequencing"]["direct_anchor_followup_helpers"].append("tools/lib/slab.zig")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "manifest:lane_sequencing" in missing
        case_count += 1
        make_fixture_root(root)

        bench_path = root / "zigux/tests/fixtures/phase1_bench_expectations.json"
        bench = json.loads(bench_path.read_text(encoding="utf-8"))
        bench["exact_checksums"]["PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM"] = 1
        bench_path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "bench:PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM:expected=620000:actual=1" in missing
        case_count += 1
        make_fixture_root(root)

        bench_path = root / "zigux/tests/fixtures/phase1_bench_expectations.json"
        bench = json.loads(bench_path.read_text(encoding="utf-8"))
        bench["checksums"] = [item for item in bench["checksums"] if item != "PHASE1_BENCH_RBTREE_CHECKSUM"]
        bench_path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "bench:missing_checksum:PHASE1_BENCH_RBTREE_CHECKSUM" in missing
        case_count += 1
        make_fixture_root(root)

        review_path = root / "Documentation/zigux/review-checklist.md"
        review = review_path.read_text(encoding="utf-8")
        review_path.write_text(review.replace("validate-phase1-closure.py", "validate-phase1-closure.py.missing", 1), encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "review_checklist_phase1_packet:expected=1:actual=0" in missing
        case_count += 1
        make_fixture_root(root)

        closure_path = root / "Documentation/zigux/phase1-closure.md"
        closure_text = closure_path.read_text(encoding="utf-8")
        marker_labels = [
            "closure_bitmap_first_word_boundary_review_count",
            "closure_bitmap_final_partial_word_review_count",
            "closure_bitmap_scnprintf_truncation_review_count",
            "closure_bitmap_zero_bit_noop_review_count",
            "closure_bitmap_linux_alias_review_count",
            "closure_rbtree_review_packet_count",
        ]
        for target_label in marker_labels:
            label, marker, _ = next(case for case in CLOSURE_MARKERS if case[0] == target_label)

            def mutate_closure(marker=marker):
                closure_path.write_text(closure_text.replace(marker + "\n", "", 1), encoding="utf-8")

            mutate_closure()
            missing = collect_missing_markers(root)
            assert f"{label}:expected=1:actual=0" in missing
            case_count += 1
            make_fixture_root(root)
            closure_text = closure_path.read_text(encoding="utf-8")

    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 1 closure packet.")
    parser.add_argument("--root")
    parser.add_argument("--self-test", action="store_true")
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
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_CLOSURE_MARKERS_END")
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print(f"PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    total_markers = (
        len(CLOSURE_MARKERS)
        + len(DOCS_ROOT_MARKERS)
        + len(SCRIPTS_README_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(REVIEW_CHECKLIST_MARKERS)
        + len(LEDGER_MARKERS)
        + len(MAKEFILE_MARKERS)
        + len(BUILD_MARKERS)
        + len(WORKFLOW_MARKERS)
        + len(WORKFLOW_PRESENCE_MARKERS)
    )
    print(f"PHASE1_CLOSURE_REQUIRED_MARKER_COUNT={total_markers}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

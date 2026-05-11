#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
from typing import Any


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
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

PHASE1_CLOSURE_MARKERS = [
    "PHASE1_STATUS=closed",
    "PHASE1_HELPER_COUNT=13",
    "PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py",
    "PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig",
    "PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig",
    "PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py",
    "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py",
    "PHASE1_FIND_BIT_SINGLE_WORD_REVIEW=helper-local single-word next-scan proof stays explicit through the direct find_bit test anchor because the shared Phase 1 parity fixture does not isolate same-word start-mask behavior",
    "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_REVIEW=helper-local inclusive boundary proof stays explicit through the direct find_bit test anchor so same-word next scans keep the last in-range head-word bit reachable from an inclusive start",
    "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_OWNER=the shared Phase 1 replay now consumes the committed inclusive_boundary_* fixture fields directly, while the direct helper-local inclusive-boundary test remains a review-visible same-word anchor for that path",
    "PHASE1_FIND_BIT_ZERO_WINDOW_REVIEW=helper-local zero-bit-window proof stays explicit through the direct find_bit test anchor so first-scan entrypoints return the empty-window boundary without reading bitmap words",
    "PHASE1_FIND_BIT_PAST_NBITS_REVIEW=helper-local past-nbits short-circuit proof stays explicit through the direct find_bit test anchor so next scans starting at or beyond nbits return the boundary without reading bitmap words outside the caller-visible window",
    "PHASE1_FIND_BIT_UNDERSCORE_ALIAS_REVIEW=helper-local underscore alias proof stays explicit through the direct find_bit test anchor so the Linux-style underscore entry points remain behaviorally locked to the primary Zig helpers",
    "PHASE1_FIND_BIT_TAIL_CLAMP_REVIEW=tail_clamped_first, tail_clamped_next, tail_zero_clamped_first, tail_zero_clamped_next, tail_and_clamped_first, and tail_and_clamped_next stay explicit through the shared Phase 1 parity fixture and replay so last-word scans cannot silently leak masked tail bits beyond nbits",
    "PHASE1_FIND_BIT_BENCH_REVIEW=the shared Phase 1 benchmark packet keeps the exact next-bit and edge-loop iteration and checksum contract explicit so the steady-state and edge-case find_bit smoke paths remain live and review-visible",
    "PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay explicit through the shared Phase 1 parity fixture and replay so caller-selected bit windows cannot silently leak tail bits beyond nbits",
    "PHASE1_BITMAP_PREDICATE_TAIL_MASK_REVIEW=helper-local bitmap predicate tail-mask proof stays explicit through the direct bitmap test anchor so equal, intersects, and subset ignore out-of-range tail bits instead of treating tail noise as live data",
    "PHASE1_BITMAP_FIRST_WORD_BOUNDARY_REVIEW=helper-local bitmap first-word boundary proof stays explicit through the direct bitmap test anchor so setRange and clearRange preserve exact first-word masks when a range ends on the first-word boundary",
    "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor so setRange and clearRange clamp trailing partial-word masks to the requested tail window instead of spilling work beyond it",
    "PHASE1_BITMAP_SCNPRINTF_TRUNCATION_REVIEW=helper-local bitmap.scnprintf truncation proof stays explicit through the direct bitmap test anchor because the shared Phase 1 parity fixture only locks the full rendered range string",
    "PHASE1_BITMAP_SCNPRINTF_TINY_BUFFER_REVIEW=helper-local bitmap.scnprintf tiny-buffer proof stays explicit through the direct bitmap test anchor plus the shared Phase 1 parity fixture and replay so terminator-only caller buffers stay NUL-terminated and zero-length caller views return without writing hidden bytes",
    "PHASE1_BITMAP_COPY_ALIAS_REVIEW=helper-local bitmap copy alias proof stays explicit through the direct bitmap test anchor so bitmap_copy_clear_tail and bitmap_copy_and_extend preserve tail masking and zero-filled extension semantics",
    "PHASE1_BITMAP_RAW_COPY_ALIAS_REVIEW=helper-local raw bitmap_copy alias proof stays explicit through the direct bitmap test anchor so copy and bitmap_copy preserve unmasked source words instead of silently adopting tail-clearing semantics",
    "PHASE1_BITMAP_ZERO_BIT_NOOP_REVIEW=helper-local bitmap zero-bit no-op proof stays explicit through the direct bitmap test anchor so zero-bit windows keep mutating helpers, boolean queries, and the rendered empty-window path from touching caller-visible storage or writing hidden bytes",
    "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface",
    "PHASE1_RBTREE_REVIEW_PACKET=helper-local rbtree tests plus the shared traversal, detached-node, and duplicate-search replay stay explicit so duplicate-search parity keys remain shared-replay-owned while match-iterator coverage plus cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior keep direct review anchors without implying a broader shared iterator or cached-root fixture packet than current master ships",
    "PHASE1_STRING_MEMPARSE_REVIEW=helper-local memparse safety anchors stay explicit through the direct string tests and the Phase 1 helper manifest so sign-prefixed invalid input preserves rest, signed overflow saturates instead of trapping, and suffixes are still consumed after saturation",
    "PHASE1_STRING_REVIEW_PACKET=helper-local string tests and the shared embedded-NUL replay stay explicit so the bounded Phase 1 string surface keeps its direct review anchors, committed C-string replacement bytes, and parity fixture keys",
    "PHASE1_ROLLBACK=keep C authoritative and remove failing Zig helper from test/build wiring",
]

DOCS_ROOT_MARKERS = [
    "Phase 1 notes - `Documentation/zigux/phase1-closure.md`",
    "`scripts/zigux/check-phase1-installer-review-surfaces.py`",
    "`zigux/tests/fixtures/phase1_helper_manifest.json`",
    "`scripts/zigux/validate-phase1-closure.py`",
]

SCRIPTS_README_MARKERS = [
    "Phase 1 flow - `validate-phase1.py` checks that the bounded host-side helper inventory under `tools/lib/*.zig`, its committed fixture set, the shared `zigux/tests/build.zig` wiring, and the bootstrap workflow markers stay aligned before the helper parity and benchmark lanes run.",
    "`validate-phase1-closure.py` confirms the closed Phase 1 packet still matches `Documentation/zigux/phase1-closure.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, the shared helper build wiring, and the bootstrap workflow.",
    "`tools/lib/string.zig`, `Documentation/zigux/phase1-closure.md`, and `zigux/tests/fixtures/phase1_helper_manifest.json` also keep the direct Phase 1 string review packet explicit, including the `memchr_inv()` alias replay, the zero-value prefix-alignment `memchrInv()` follow-up, and the explicit positive-overflow `memparse()` anchor, so those helper-local proofs stay reviewable without widening the shared parity fixture.",
]

TESTS_README_MARKERS = [
    "keep the closed Phase 1 host-tools packet explicit in the tests root too:",
    "keep `python3 scripts/zigux/install-zig.py --self-test` and `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test` visible as focused companion checks for the closed Phase 1 installer-review surface",
]

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, `zigux/tests/README.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` still agree on the same closed helper tranche and validator-first replay path without widening Phase 1 beyond the bounded host-side helper packet?",
]

LEDGER_MARKERS = [
    "`docs(zigux): close bounded phase-1 helper tranche`",
    "`test(zigux): harden phase-1 closure gates`",
    "`ci(zigux): harden phase-1 closure workflow viability`",
    "`build(zigux): remove node-20-bound Zig action from phase-1 closure path`",
]

MAKEFILE_MARKERS = [
    "phase1-validate:",
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-installer-review-surfaces.py --self-test",
    "scripts/zigux/check-phase1-installer-companion-checks.py --self-test",
    "scripts/zigux/validate-phase1-closure.py",
    "phase1-test:",
    "scripts/zigux/check-phase1-parity.py",
    "zig build test --build-file zigux/tests/build.zig",
    "phase1-bench:",
    "scripts/zigux/check-phase1-bench.py",
    "zig build bench --build-file zigux/tests/build.zig",
    "phase1: phase1-validate phase1-test phase1-bench",
]

BUILD_MARKERS = [
    '.root_source_file = b.path("phase1_helpers.zig")',
    '.name = "phase1-helper-tests"',
    'b.step("test", "Run Phase 1 helper tests")',
    '.root_source_file = b.path("phase1_bench.zig")',
    '.name = "phase1-bench"',
    'b.step("bench", "Run Phase 1 helper benchmark smoke")',
]

BENCH_EXPECTATIONS = {
    "status": "pass",
    "iterations": {
        "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
        "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS": 20000,
        "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
        "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,
        "PHASE1_BENCH_STRING_ITERATIONS": 40000,
        "PHASE1_BENCH_HWEIGHT_ITERATIONS": 100000,
        "PHASE1_BENCH_LIST_SORT_ITERATIONS": 1000,
        "PHASE1_BENCH_RBTREE_ITERATIONS": 4000,
    },
    "checksums": [
        "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
        "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
        "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
        "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
        "PHASE1_BENCH_STRING_CHECKSUM",
        "PHASE1_BENCH_HWEIGHT_CHECKSUM",
        "PHASE1_BENCH_LIST_SORT_CHECKSUM",
        "PHASE1_BENCH_RBTREE_CHECKSUM",
    ],
}

PHASE1_MANIFEST = json.loads(
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
        "test \"bitmap predicates ignore out-of-range tail bits\"",
        "test \"bitmap range helpers clamp the final partial word\"",
        "test \"bitmap scnprintf collapses contiguous ranges across word boundaries\"",
        "test \"bitmap zero-bit binary helpers stay explicit identity operations\"",
        "test \"bitmap copy and extend handles zero and aligned counts\"",
        "test \"bitmap Linux-style aliases mirror the primary helper surface\""
      ],
      "first_word_boundary_anchor": "test \"bitmap range helpers honor exact first-word boundaries\"",
      "final_partial_word_anchor": "test \"bitmap range helpers clamp the final partial word\"",
      "predicate_tail_mask_anchor": "test \"bitmap predicates ignore out-of-range tail bits\"",
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
      "phase1_helper_replay_anchor": "test \"phase 1 helper ports match committed parity fixture\"",
      "review_packet_summary": "shared Phase 1 fixture keys now own bitmap scnprintf output, tiny-buffer, and partial-window xor replay, while helper-local anchors keep allocator sizing and zero-fill behavior, predicate tail-mask, first-word and final-partial range boundaries, cross-word scnprintf collapse, truncation, copy alias, raw copy alias, zero-and-aligned copy-and-extend behavior, zero-bit no-op, zero-bit binary identity, and Linux-style alias behavior review-visible on current master",
      "cross_word_scnprintf_anchor": "test \"bitmap scnprintf collapses contiguous ranges across word boundaries\"",
      "scnprintf_truncation_anchor": "test \"bitmap scnprintf reports full length while truncating the buffer\"",
      "copy_alias_anchor": "test \"bitmap copy aliases preserve tail clearing and extension semantics\"",
      "copy_raw_alias_anchor": "test \"bitmap copy alias preserves raw source words without tail clearing\"",
      "copy_extend_zero_aligned_anchor": "test \"bitmap copy and extend handles zero and aligned counts\"",
      "zero_bit_noop_anchor": "test \"bitmap zero-bit helpers stay explicit no-ops\"",
      "zero_bit_binary_identity_anchor": "test \"bitmap zero-bit binary helpers stay explicit identity operations\"",
      "linux_alias_anchor": "test \"bitmap Linux-style aliases mirror the primary helper surface\""
    },
    "tools/lib/find_bit.zig": {
      "helper_test_anchors": [
        "test \"single-word next scans honor start masks\"",
        "test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\"",
        "test \"zero-bit windows return without reading bitmap words\"",
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
      "review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, while helper-local anchors keep same-word start-mask, inclusive-boundary, zero-window, past-nbits, tail-word set or zero or shared skip, and underscore-alias behavior review-visible on current master"
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
        "test \"rbtree cached-root Linux-style aliases mirror the primary helpers\"",
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
        "test \"rbtree cached-root Linux-style aliases mirror the primary helpers\"",
        "test \"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\"",
        "test \"rbtree eraseCached returns null for a singleton cached tree\"",
        "test \"rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned\"",
        "test \"rbtree eraseInitCached clears singleton cached roots before reseed\""
      ],
      "review_packet_summary": "shared find, first-match, and next-match duplicate-search parity stays explicit through the Phase 1 fixture and replay, while match-iterator coverage plus cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors until master ships dedicated shared iterator or cached-root fixture keys"
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
        "test \"memchr_inv mirrors memchrInv byte-search semantics\"",
        "test \"memchrInv keeps long-buffer first-dirty-byte results stable\"",
        "test \"memchrInv follows the earliest dirty byte as long buffers change\"",
        "test \"memchrInv dirty-word shortcut handles zero-value scans at word boundaries\"",
        "test \"memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment\"",
        "test \"memchrInv short zero-value scans stay byte-accurate\"",
        "test \"memparse handles decimal hexadecimal octal and suffixes\"",
        "test \"memparse keeps original rest when sign is not followed by digits\"",
        "test \"memparse saturates signed overflow instead of trapping\"",
        "test \"memparse clamps explicit positive signed overflow\"",
        "test \"memparse keeps signed values and their trailing rest aligned\"",
        "test \"memparse consumes suffix after saturation\"",
        "test \"memparse applies suffixes before signed clamping\"",
        "test \"phase 1 string trim helpers stop at embedded NUL after trailing whitespace\""
      ],
      "memparse_review_anchors": [
        "test \"memparse keeps original rest when sign is not followed by digits\"",
        "test \"memparse saturates signed overflow instead of trapping\"",
        "test \"memparse clamps explicit positive signed overflow\"",
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
      "memparse_review_summary": "helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, explicit positive and signed overflow clamps remain review-visible, signed inputs keep trailing-rest splits aligned with unsigned parsing, and suffixes are still consumed after saturation",
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
      ],
      "memchr_inv_zero_prefix_alignment_anchor": "test \"memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment\""
    }
  }
}
"""
)


def repo_root_from_arg(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: str) -> Any:
    return json.loads((root / relative_path).read_text(encoding="utf-8"))


def collect_missing_files(root: Path) -> list[str]:
    return [path for path in REQUIRED_FILES if not (root / path).exists()]


def require_markers(text: str, markers: list[str], label: str) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")
    return missing


def collect_workflow_markers(workflow: str) -> list[str]:
    missing: list[str] = []
    required = [
        'group: ${{ github.ref == \'refs/heads/master\' && format(\'{0}-{1}-{2}\', github.workflow, github.ref, github.sha) || format(\'{0}-{1}\', github.workflow, github.ref) }}',
        "- name: Validate Phase 1 closure",
        'validator_path = Path("scripts/zigux/validate-phase1-closure.py")',
        'raise SystemExit(namespace["main"]())',
        "run: make -C zigux phase7-test",
    ]
    for marker in required:
        if marker not in workflow:
            missing.append(f"workflow:{marker}")
    return missing


def collect_manifest_markers(manifest: Any) -> list[str]:
    return [] if manifest == PHASE1_MANIFEST else ["manifest:phase1_helper_manifest.json does not match current Phase 1 packet expectations"]


def collect_bench_markers(bench_expectations: Any) -> list[str]:
    return [] if bench_expectations == BENCH_EXPECTATIONS else ["bench:phase1_bench_expectations.json does not match current Phase 1 packet expectations"]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    workflow = load_text(root, ".github/workflows/zigux-bootstrap.yml")
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

    missing.extend(collect_workflow_markers(workflow))
    missing.extend(require_markers(closure, PHASE1_CLOSURE_MARKERS, "phase1-closure"))
    missing.extend(require_markers(docs_root, DOCS_ROOT_MARKERS, "docs-root"))
    missing.extend(require_markers(scripts_readme, SCRIPTS_README_MARKERS, "scripts-readme"))
    missing.extend(require_markers(tests_readme, TESTS_README_MARKERS, "tests-readme"))
    missing.extend(require_markers(review_checklist, REVIEW_CHECKLIST_MARKERS, "review-checklist"))
    missing.extend(require_markers(ledger, LEDGER_MARKERS, "ledger"))
    missing.extend(require_markers(makefile, MAKEFILE_MARKERS, "makefile"))
    missing.extend(require_markers(build_zig, BUILD_MARKERS, "build-zig"))
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
        "\n".join(
            [
                "concurrency:",
                "  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}-{2}', github.workflow, github.ref, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Validate Phase 1 closure",
                "        run: |",
                "          validator_path = Path(\"scripts/zigux/validate-phase1-closure.py\")",
                "          raise SystemExit(namespace[\"main\"]())",
                "      - name: Run Phase 7 runtime helper tests",
                "        run: make -C zigux phase7-test",
                "",
            ]
        ),
    )
    write_text(root / "Documentation/zigux/phase1-closure.md", "\n".join(PHASE1_CLOSURE_MARKERS) + "\n")
    write_text(root / "Documentation/zigux/README.md", "\n".join(DOCS_ROOT_MARKERS) + "\n")
    write_text(root / "scripts/zigux/README.md", "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root / "zigux/tests/README.md", "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root / "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root / "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", "\n".join(LEDGER_MARKERS) + "\n")
    write_text(root / "zigux/Makefile", "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(root / "zigux/tests/build.zig", "\n".join(BUILD_MARKERS) + "\n")
    write_text(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(PHASE1_MANIFEST, indent=2) + "\n")
    write_text(root / "zigux/tests/fixtures/phase1_bench_expectations.json", json.dumps(BENCH_EXPECTATIONS, indent=2) + "\n")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_closure_") as tmp:
        root = Path(tmp)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 1

        closure_path = root / "Documentation/zigux/phase1-closure.md"
        original = closure_path.read_text(encoding="utf-8")
        closure_path.write_text(original.replace(PHASE1_CLOSURE_MARKERS[-1] + "\n", "", 1), encoding="utf-8")
        missing = collect_missing_markers(root)
        assert any(item.startswith("phase1-closure:PHASE1_ROLLBACK=") for item in missing)
        case_count += 1
        make_fixture_root(root)

        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        original = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(original.replace("run: make -C zigux phase7-test\n", "", 1), encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "workflow:run: make -C zigux phase7-test" in missing
        case_count += 1
        make_fixture_root(root)

        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"].pop("memchr_inv_zero_prefix_alignment_anchor")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "manifest:phase1_helper_manifest.json does not match current Phase 1 packet expectations" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        bench_path = root / "zigux/tests/fixtures/phase1_bench_expectations.json"
        bench = json.loads(bench_path.read_text(encoding="utf-8"))
        bench["iterations"]["PHASE1_BENCH_STRING_ITERATIONS"] = 1
        bench_path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        assert "bench:phase1_bench_expectations.json does not match current Phase 1 packet expectations" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        (root / "scripts/zigux/check-phase1-bench.py").unlink()
        assert collect_missing_files(root) == ["scripts/zigux/check-phase1-bench.py"]
        case_count += 1

    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 1 closure packet.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root")
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
    print(
        "PHASE1_CLOSURE_REQUIRED_MARKER_COUNT="
        f"{len(PHASE1_CLOSURE_MARKERS) + len(DOCS_ROOT_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(LEDGER_MARKERS) + len(MAKEFILE_MARKERS) + len(BUILD_MARKERS) + 5}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

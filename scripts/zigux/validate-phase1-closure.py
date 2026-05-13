#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
VALIDATE_PHASE1_REL = Path("scripts/zigux/validate-phase1.py")
STRING_HELPER_REL = Path("tools/lib/string.zig")
FIND_BIT_HELPER_REL = Path("tools/lib/find_bit.zig")

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
    "tools/lib/string.zig",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/phase1_helpers.zig",
]

WORKFLOW_MARKERS = [
    "uses: actions/checkout@v6.0.2",
    "uses: actions/setup-python@v6.2.0",
    "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}-{2}', github.workflow, github.ref, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}",
    "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
    "run: python3 scripts/zigux/validate-phase1.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: python3 scripts/zigux/check-phase1-parity.py",
    "run: python3 scripts/zigux/check-phase1-bench.py",
    "run: zig build test --build-file zigux/tests/build.zig",
    "run: zig build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe",
]

DOCS_ROOT_MARKERS = [
    "Phase 1 notes - `Documentation/zigux/phase1-closure.md` - `scripts/zigux/README.md` - `scripts/zigux/install-zig.py` - `scripts/zigux/check-phase1-installer-review-surfaces.py` - `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "while `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the closure, installer-backed workflow-viability replay, the dedicated installer-review alignment checker, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.",
]

TESTS_README_MARKERS = [
    "keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root, scripts root, and workflow replay surface",
]

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`",
    "`scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`",
]

LEDGER_MARKERS = [
    "`docs(zigux): close bounded phase-1 helper tranche`",
    "`test(zigux): harden phase-1 closure gates`",
    "`ci(zigux): harden phase-1 closure workflow viability`",
    "`build(zigux): remove node-20-bound Zig action from phase-1 closure path`",
]

MAKEFILE_MARKERS = [
    "phase1-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-review-surfaces.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py",
    "phase1-test:",
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig",
    "phase1-bench:",
    "cd $(ZIGUX_ROOT) && $(ZIG) build bench --build-file zigux/tests/build.zig",
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

CLOSURE_MARKERS = [
    "PHASE1_STATUS=closed",
    "PHASE1_HELPER_COUNT=13",
    "PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py",
    "PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig",
    "PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig",
    "PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py",
    "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py",
    "PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay explicit through the shared Phase 1 parity fixture and replay so caller-selected bit windows cannot silently leak tail bits beyond nbits",
    "PHASE1_BITMAP_FIRST_WORD_BOUNDARY_REVIEW=helper-local bitmap first-word boundary proof stays explicit through the direct bitmap test anchor so setRange and clearRange preserve exact first-word masks when a range ends on the first-word boundary",
    "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor so setRange and clearRange clamp trailing partial-word masks to the requested tail window instead of spilling work beyond it",
    "PHASE1_BITMAP_SCNPRINTF_TRUNCATION_REVIEW=helper-local bitmap.scnprintf truncation proof stays explicit through the direct bitmap test anchor because the shared Phase 1 parity fixture only locks the full rendered range string",
    "PHASE1_BITMAP_SCNPRINTF_TINY_BUFFER_REVIEW=helper-local bitmap.scnprintf tiny-buffer proof stays explicit through the direct bitmap test anchor plus the shared Phase 1 parity fixture and replay so terminator-only caller buffers stay NUL-terminated and zero-length caller views return without writing hidden bytes",
    "PHASE1_BITMAP_COPY_ALIAS_REVIEW=helper-local bitmap copy alias proof stays explicit through the direct bitmap test anchor so bitmap_copy_clear_tail and bitmap_copy_and_extend preserve tail masking and zero-filled extension semantics",
    "PHASE1_BITMAP_RAW_COPY_ALIAS_REVIEW=helper-local raw bitmap_copy alias proof stays explicit through the direct bitmap test anchor so copy and bitmap_copy preserve unmasked source words instead of silently adopting tail-clearing semantics",
    "PHASE1_BITMAP_ZERO_BIT_NOOP_REVIEW=helper-local bitmap zero-bit no-op proof stays explicit through the direct bitmap test anchor so zero-bit windows keep mutating helpers, boolean queries, and the rendered empty-window path from touching caller-visible storage or writing hidden bytes",
    "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface",
    "PHASE1_RBTREE_REVIEW_PACKET=helper-local rbtree tests plus the shared traversal, detached-node, and duplicate-search replay stay explicit so duplicate-search parity keys remain shared-replay-owned while match-iterator coverage plus cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior keep direct review anchors without implying a broader shared iterator or cached-root fixture packet than current master ships",
    "PHASE1_STRING_MEMPARSE_REVIEW=helper-local memparse safety anchors stay explicit through the direct string tests and the Phase 1 helper manifest so sign-prefixed invalid input preserves rest, signed inputs keep trailing-rest splits aligned with unsigned parsing, implicit and explicit signed overflow clamp instead of trapping, and suffixes are still consumed after saturation",
    "PHASE1_STRING_REVIEW_PACKET=helper-local string tests and the shared embedded-NUL replay stay explicit so the bounded Phase 1 string surface keeps its direct review anchors, committed C-string replacement bytes, and parity fixture keys",
    "PHASE1_FIND_BIT_SINGLE_WORD_REVIEW=helper-local single-word next-scan proof stays explicit through the direct find_bit test anchor because the shared Phase 1 parity fixture does not isolate same-word start-mask behavior",
    "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_REVIEW=helper-local inclusive boundary proof stays explicit through the direct find_bit test anchor so same-word next scans keep the last in-range head-word bit reachable from an inclusive start",
    "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_OWNER=the shared Phase 1 replay now consumes the committed inclusive_boundary_* fixture fields directly, while the direct helper-local inclusive-boundary test remains a review-visible same-word anchor for that path",
    "PHASE1_FIND_BIT_TAIL_WORD_INCLUSIVE_BOUNDARY_REVIEW=helper-local tail-word inclusive boundary proof stays explicit through the direct find_bit test anchor so same-word next scans in the final partial tail word keep the last in-range bit reachable from an inclusive start",
    "PHASE1_FIND_BIT_TAIL_WORD_INCLUSIVE_BOUNDARY_OWNER=the shared Phase 1 replay still only consumes the committed inclusive_boundary_* head-word fields directly, so the direct helper-local tail-word inclusive-boundary test remains the owning review-visible anchor for the final partial-word boundary path",
    "PHASE1_FIND_BIT_ZERO_WINDOW_REVIEW=helper-local zero-bit-window proof stays explicit through the direct find_bit test anchor so first-scan entrypoints return the empty-window boundary without reading bitmap words",
    "PHASE1_FIND_BIT_PAST_NBITS_REVIEW=helper-local past-nbits short-circuit proof stays explicit through the direct find_bit test anchor so next scans starting at or beyond nbits return the boundary without reading bitmap words outside the caller-visible window",
    "PHASE1_FIND_BIT_UNDERSCORE_ALIAS_REVIEW=helper-local underscore alias proof stays explicit through the direct find_bit test anchor so the Linux-style underscore entry points remain behaviorally locked to the primary Zig helpers",
    "PHASE1_FIND_BIT_TAIL_CLAMP_REVIEW=tail_clamped_first, tail_clamped_next, tail_zero_clamped_first, tail_zero_clamped_next, tail_and_clamped_first, tail_and_clamped_next, tail_clamped_last, and tail_clamped_empty_last stay explicit through the shared Phase 1 parity fixture and replay so last-word scans cannot silently leak masked tail bits beyond nbits",
    "PHASE1_FIND_BIT_BENCH_REVIEW=the shared Phase 1 benchmark packet keeps the exact next-bit and edge-loop iteration and checksum contract explicit so the steady-state and edge-case find_bit smoke paths remain live and review-visible",
    "PHASE1_ROLLBACK=keep C authoritative and remove failing Zig helper from test/build wiring",
    "PHASE1_BITMAP_PREDICATE_TAIL_MASK_REVIEW=helper-local bitmap predicate tail-mask proof stays explicit through the direct bitmap test anchor so equal, intersects, and subset ignore out-of-range tail bits instead of treating tail noise as live data",
    "PHASE1_BITMAP_EMPTY_BUFFER_REVIEW=helper-local bitmap.scnprintf empty-bitmap caller-buffer preservation stays explicit through the direct bitmap test anchor so a non-empty caller buffer remains untouched when no bits are set instead of being silently zeroed or NUL-terminated",
    "PHASE1_BITMAP_COPY_ZERO_AND_ALIGNED_REVIEW=helper-local bitmap zero-sized and aligned copy proof stays explicit through the direct bitmap test anchors so zero-sized destination views remain untouched and aligned-word copies preserve raw aligned words while zero-filling only the requested extension space",
    "PHASE1_BITMAP_ZERO_BIT_BINARY_IDENTITY_REVIEW=helper-local bitmap zero-bit binary identity proof stays explicit through the direct bitmap test anchor so zero-bit windows keep binary helpers in identity or empty-result mode without touching caller-visible storage or inventing overlap, subset, or equality drift",
    "PHASE1_FIND_BIT_LINUX_ALIAS_REVIEW=helper-local Linux-style alias proof stays explicit through the direct find_bit test anchor so the public Linux-style alias entry points remain behaviorally locked to the primary Zig helpers",
]

EXPECTED_BENCH = {
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
        "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
        "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
        "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
        "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
    ],
    "exact_checksums": {
        "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 2260000,
        "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 620000,
        "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 15621472,
        "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 23340000,
        "PHASE1_BENCH_STRING_CHECKSUM": 320000,
        "PHASE1_BENCH_RBTREE_CHECKSUM": 3380000,
        "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 1308000,
        "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 56000,
        "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 1868000,
        "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 148000,
    },
}

EXPECTED_BITMAP_MANIFEST = {
    "first_word_boundary_anchor": 'test "bitmap range helpers honor exact first-word boundaries"',
    "final_partial_word_anchor": 'test "bitmap range helpers clamp the final partial word"',
    "predicate_tail_mask_anchor": 'test "bitmap predicates ignore out-of-range tail bits"',
    "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
    "review_packet_summary": "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, scnprintf output, tiny-buffer, and partial-window xor replay, while helper-local anchors keep zero-size allocator and free-null behavior, predicate tail-mask, first-word and final-partial range boundaries, cross-word scnprintf collapse, truncation, empty-bitmap caller-buffer preservation, copy alias, raw copy alias, zero-and-aligned copy-and-extend behavior, zero-bit no-op, zero-bit binary identity, and Linux-style alias behavior review-visible on current master",
    "parity_fixture_keys": [
        "alloc_words",
        "zalloc_words",
        "zalloc_values",
        "scnprintf",
        "truncated_scnprintf_len",
        "truncated_scnprintf",
        "terminator_only_scnprintf_len",
        "terminator_only_nul",
        "zero_length_scnprintf_len"
    ],
    "partial_xor_review_fields": [
        "partial_xor_nbits",
        "partial_xor_masked_values",
    ],
    "scnprintf_cross_word_anchor": 'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
    "scnprintf_truncation_anchor": 'test "bitmap scnprintf reports full length while truncating the buffer"',
    "empty_buffer_anchor": 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
    "copy_zero_and_aligned_anchors": [
        'test "bitmap copy and extend handles zero and aligned counts"',
        'test "bitmap copy helpers keep zero-sized destination views untouched"',
    ],
    "zero_bit_noop_anchor": 'test "bitmap zero-bit helpers stay explicit no-ops"',
    "zero_bit_binary_identity_anchor": 'test "bitmap zero-bit binary helpers stay explicit identity operations"',
    "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror the primary helper surface"',
}

EXPECTED_FIND_BIT_MANIFEST = {
    "helper_test_anchors": [
        'test "find first and next set bits across words"',
        'test "find zero bits respects the declared bit count"',
        'test "find and bit returns the first shared set bit"',
        'test "underscore entry points reuse the public helper behavior"',
        'test "single-word next scans honor start masks"',
        'test "single-word first scans clamp to the declared bit window"',
        'test "single-word next scans clamp partial windows before returning nbits"',
        'test "word-boundary next scans start fresh on the next word"',
        'test "zero-bit windows return without reading bitmap words"',
        'test "zero-sized scans ignore populated backing words"',
        'test "next scans past nbits return without reading bitmap words"',
        'test "tail mask ignores set bits beyond nbits"',
        'test "tail mask ignores zero bits beyond nbits"',
        'test "tail mask ignores shared bits beyond nbits"',
        'test "tail-word next set scans skip earlier in-range matches before clamping"',
        'test "clump8 scans align to the containing byte and return its value"',
        'test "clump8 scans keep tail bytes reachable from partial final words"',
        'test "clump8 scans leave the caller byte untouched when no set bit remains"',
        'test "getValue8 reads aligned bytes from bitmap words"',
        'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        'test "find last bit scans backward across words"',
        'test "find last bit ignores storage beyond an exact word boundary"',
        'test "find last bit clamps tail words to nbits"',
        'test "find last bit returns nbits when no set bits remain"',
        'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
        'test "low-level underscore aliases mirror the primary find helpers"',
        'test "Linux-style aliases mirror the primary find helpers"',
    ],
    "same_word_start_masks": 'test "single-word next scans honor start masks"',
    "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "tail_word_inclusive_boundary_contract": "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit of the final partial word, while later starts still return nbits instead of leaking the out-of-range tail.",
    "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
    "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
    "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers"',
    "linux_alias_anchor": 'test "Linux-style aliases mirror the primary find helpers"',
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
    "review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, underscore-alias, and Linux-style alias behavior review-visible on current master",
}

EXPECTED_RBTREE_MANIFEST = {
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
    "ordered_alias_anchor": 'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
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
    "review_packet_summary": "shared find, first-match, and next-match duplicate-search parity stays explicit through the Phase 1 fixture and replay, while match-iterator coverage plus cached-root leftmost-return, insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors until master ships dedicated shared iterator or cached-root leftmost-return fixture keys",
    "next_safe_step_note": "If this helper lane reopens, the smallest shared-replay expansion is a dedicated iterator or cached-root leftmost-return fixture key; until then, matchIterator coverage plus cached-root leftmost-return and singleton-erase behavior stay owned by direct helper-local anchors.",
}

EXPECTED_STRING_HELPER_TESTS = [
    'test "strtobool accepts common Linux forms"',
    'test "strlcpy copies and returns the source length"',
    'test "streq matches C-string equality semantics"',
    'test "skip trim remove and replace spaces work in place"',
    'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
    'test "strreplace mirrors replaceChar C-string semantics"',
    'test "strHasPrefix returns the matched prefix length with C-string semantics"',
    'test "strstarts mirrors the header-level prefix helper"',
    'test "strEndsWith honors C-string boundaries"',
    'test "sysfsStreq treats trailing newline and NUL as equivalent"',
    'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
    'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
    'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
    'test "matchString finds C-string matches and preserves first-match order"',
    'test "match_string mirrors matchString for empty and matched lists"',
    'test "memdup and memchrInv preserve byte content"',
    'test "memchr_inv mirrors memchrInv byte-search semantics"',
    'test "memchrInv keeps long-buffer first-dirty-byte results stable"',
    'test "memchrInv follows the earliest dirty byte as long buffers change"',
    'test "memchrInv dirty-word shortcut handles zero-value scans at word boundaries"',
    'test "memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment"',
    'test "memchrInv keeps the earliest dirty byte for long non-zero scans across alignments"',
    'test "memchrInv keeps the earliest dirty byte for long zero-value scans across alignments"',
    'test "memchrInv short zero-value scans stay byte-accurate"',
    'test "memparse handles decimal hexadecimal octal and suffixes"',
    'test "memparse keeps original rest when sign is not followed by digits"',
    'test "memparse saturates signed overflow instead of trapping"',
    'test "memparse clamps explicit positive signed overflow"',
    'test "memparse keeps signed values and their trailing rest aligned"',
    'test "memparse consumes suffix after saturation"',
    'test "memparse applies suffixes before signed clamping"',
    'test "strnchr honors count and C-string boundaries"',
]

STRING_PREFIX_SUFFIX_ANCHOR_PREFIXES = (
    'test "strHasPrefix ',
    'test "strstarts ',
    'test "strEndsWith ',
)

STRING_LOOKUP_ANCHOR_PREFIXES = (
    'test "matchString ',
    'test "match_string ',
)

def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: str) -> Any:
    return json.loads(load_text(root, relative_path))


def collect_missing_files(root: Path) -> list[str]:
    return [path for path in REQUIRED_FILES if not (root / path).exists()]


def require_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")
    return missing


def collect_bench_markers(bench: Any) -> list[str]:
    missing: list[str] = []
    if not isinstance(bench, dict):
        return ["bench:json_object"]
    if bench.get("status") != EXPECTED_BENCH["status"]:
        missing.append("bench:status")
    if bench.get("iterations") != EXPECTED_BENCH["iterations"]:
        missing.append("bench:iterations")
    if bench.get("checksums") != EXPECTED_BENCH["checksums"]:
        missing.append("bench:checksums")
    if bench.get("exact_checksums") != EXPECTED_BENCH["exact_checksums"]:
        missing.append("bench:exact_checksums")
    return missing


def run_phase1_validator(root: Path) -> list[str]:
    validator = root / VALIDATE_PHASE1_REL
    result = subprocess.run(
        [sys.executable, str(validator), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return []
    detail = (result.stdout + result.stderr).strip()
    return [f"phase1_validator_failed:{detail}"]


def collect_bitmap_manifest_markers(manifest: Any) -> list[str]:
    if not isinstance(manifest, dict):
        return ["bitmap_manifest:json_object"]
    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["bitmap_manifest:review_anchors"]
    bitmap_anchors = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_anchors, dict):
        return ["bitmap_manifest:tools/lib/bitmap.zig"]

    missing: list[str] = []
    for key, expected in EXPECTED_BITMAP_MANIFEST.items():
        if bitmap_anchors.get(key) != expected:
            missing.append(f"bitmap_manifest:{key}")
    return missing


def collect_find_bit_manifest_markers(root: Path, manifest: Any) -> list[str]:
    if not isinstance(manifest, dict):
        return ["find_bit_manifest:json_object"]
    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["find_bit_manifest:review_anchors"]
    find_bit_anchors = review_anchors.get("tools/lib/find_bit.zig")
    if not isinstance(find_bit_anchors, dict):
        return ["find_bit_manifest:tools/lib/find_bit.zig"]

    try:
        helper_tests = extract_zig_test_names(load_text(root, str(FIND_BIT_HELPER_REL)))
    except FileNotFoundError:
        return ["find_bit_manifest:helper_test_anchors"]
    if not helper_tests:
        return ["find_bit_manifest:helper_test_anchors"]

    missing: list[str] = []
    if find_bit_anchors.get("helper_test_anchors") != helper_tests:
        missing.append("find_bit_manifest:helper_test_anchors")
    for key, expected in EXPECTED_FIND_BIT_MANIFEST.items():
        if key == "helper_test_anchors":
            continue
        if find_bit_anchors.get(key) != expected:
            missing.append(f"find_bit_manifest:{key}")
    return missing


def collect_rbtree_manifest_markers(manifest: Any) -> list[str]:
    if not isinstance(manifest, dict):
        return ["rbtree_manifest:json_object"]
    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["rbtree_manifest:review_anchors"]
    rbtree_anchors = review_anchors.get("tools/lib/rbtree.zig")
    if not isinstance(rbtree_anchors, dict):
        return ["rbtree_manifest:tools/lib/rbtree.zig"]

    missing: list[str] = []
    for key, expected in EXPECTED_RBTREE_MANIFEST.items():
        if rbtree_anchors.get(key) != expected:
            missing.append(f"rbtree_manifest:{key}")
    return missing


def extract_zig_test_names(text: str) -> list[str]:
    names: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith('test "'):
            continue
        closing_quote = stripped.find('"', len('test "'))
        if closing_quote == -1:
            continue
        names.append(stripped[: closing_quote + 1])
    return names


def expected_string_memparse_review_anchors(test_names: list[str]) -> list[str]:
    return [name for name in test_names if name.startswith('test "memparse ')]


def expected_string_prefix_suffix_review_anchors(test_names: list[str]) -> list[str]:
    return [name for name in test_names if name.startswith(STRING_PREFIX_SUFFIX_ANCHOR_PREFIXES)]


def expected_string_lookup_review_anchors(test_names: list[str]) -> list[str]:
    return [name for name in test_names if name.startswith(STRING_LOOKUP_ANCHOR_PREFIXES)]


def expected_string_strnchr_review_anchor(test_names: list[str]) -> str | None:
    for name in test_names:
        if name.startswith('test "strnchr '):
            return name
    return None


def collect_string_manifest_markers(root: Path, manifest: Any) -> list[str]:
    if not isinstance(manifest, dict):
        return ["string_manifest:json_object"]
    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["string_manifest:review_anchors"]
    string_anchors = review_anchors.get("tools/lib/string.zig")
    if not isinstance(string_anchors, dict):
        return ["string_manifest:tools/lib/string.zig"]

    helper_tests = extract_zig_test_names(load_text(root, str(STRING_HELPER_REL)))
    if not helper_tests:
        return ["string_manifest:helper_test_anchors"]

    missing: list[str] = []
    if string_anchors.get("helper_test_anchors") != helper_tests:
        missing.append("string_manifest:helper_test_anchors")
    if string_anchors.get("memparse_review_anchors") != expected_string_memparse_review_anchors(helper_tests):
        missing.append("string_manifest:memparse_review_anchors")
    if string_anchors.get("prefix_suffix_review_anchors") != expected_string_prefix_suffix_review_anchors(helper_tests):
        missing.append("string_manifest:prefix_suffix_review_anchors")
    if string_anchors.get("lookup_review_anchors") != expected_string_lookup_review_anchors(helper_tests):
        missing.append("string_manifest:lookup_review_anchors")
    if string_anchors.get("strnchr_review_anchor") != expected_string_strnchr_review_anchor(helper_tests):
        missing.append("string_manifest:strnchr_review_anchor")
    return missing


def collect_missing_markers(root: Path) -> list[str]:
    workflow = load_text(root, ".github/workflows/zigux-bootstrap.yml")
    docs_root = load_text(root, "Documentation/zigux/README.md")
    tests_readme = load_text(root, "zigux/tests/README.md")
    review_checklist = load_text(root, "Documentation/zigux/review-checklist.md")
    closure = load_text(root, "Documentation/zigux/phase1-closure.md")
    ledger = load_text(root, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")
    makefile = load_text(root, "zigux/Makefile")
    build_zig = load_text(root, "zigux/tests/build.zig")
    bench = load_json(root, "zigux/tests/fixtures/phase1_bench_expectations.json")
    manifest = load_json(root, "zigux/tests/fixtures/phase1_helper_manifest.json")

    missing: list[str] = []
    missing.extend(run_phase1_validator(root))
    missing.extend(require_markers(workflow, "workflow", WORKFLOW_MARKERS))
    if "mlugg/setup-zig@" in workflow:
        missing.append("workflow:unexpected mlugg/setup-zig@ reference")
    missing.extend(require_markers(docs_root, "docs_root", DOCS_ROOT_MARKERS))
    missing.extend(require_markers(tests_readme, "tests_readme", TESTS_README_MARKERS))
    missing.extend(require_markers(review_checklist, "review_checklist", REVIEW_CHECKLIST_MARKERS))
    missing.extend(require_markers(closure, "closure", CLOSURE_MARKERS))
    missing.extend(require_markers(ledger, "ledger", LEDGER_MARKERS))
    missing.extend(require_markers(makefile, "makefile", MAKEFILE_MARKERS))
    missing.extend(require_markers(build_zig, "build", BUILD_MARKERS))
    missing.extend(collect_bench_markers(bench))
    missing.extend(collect_bitmap_manifest_markers(manifest))
    missing.extend(collect_find_bit_manifest_markers(root, manifest))
    missing.extend(collect_rbtree_manifest_markers(manifest))
    missing.extend(collect_string_manifest_markers(root, manifest))
    return missing


def write_text(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_zig_fixture_source(test_names: list[str]) -> str:
    return "\n".join(f"{name} {{}}" for name in test_names) + "\n"


def make_fixture_root(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, "{}\n" if relative_path.endswith(".json") else "// fixture\n")

    write_text(root, ".github/workflows/zigux-bootstrap.yml", "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(root, "Documentation/zigux/README.md", "\n".join(DOCS_ROOT_MARKERS) + "\n")
    write_text(root, "zigux/tests/README.md", "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root, "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root, "Documentation/zigux/phase1-closure.md", "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(root, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", "\n".join(LEDGER_MARKERS) + "\n")
    write_text(root, "zigux/Makefile", "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(root, "zigux/tests/build.zig", "\n".join(BUILD_MARKERS) + "\n")
    write_text(root, str(STRING_HELPER_REL), make_zig_fixture_source(EXPECTED_STRING_HELPER_TESTS))
    write_text(root, str(FIND_BIT_HELPER_REL), make_zig_fixture_source(EXPECTED_FIND_BIT_MANIFEST["helper_test_anchors"]))
    write_text(root, "zigux/tests/fixtures/phase1_bench_expectations.json", json.dumps(EXPECTED_BENCH, indent=2) + "\n")
    write_text(
        root,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/bitmap.zig": EXPECTED_BITMAP_MANIFEST,
                    "tools/lib/find_bit.zig": EXPECTED_FIND_BIT_MANIFEST,
                    "tools/lib/rbtree.zig": EXPECTED_RBTREE_MANIFEST,
                    "tools/lib/string.zig": {
                        "helper_test_anchors": EXPECTED_STRING_HELPER_TESTS,
                        "memparse_review_anchors": expected_string_memparse_review_anchors(EXPECTED_STRING_HELPER_TESTS),
                        "prefix_suffix_review_anchors": expected_string_prefix_suffix_review_anchors(EXPECTED_STRING_HELPER_TESTS),
                        "lookup_review_anchors": expected_string_lookup_review_anchors(EXPECTED_STRING_HELPER_TESTS),
                        "strnchr_review_anchor": expected_string_strnchr_review_anchor(EXPECTED_STRING_HELPER_TESTS),
                    },
                }
            },
            indent=2,
        ) + "\n",
    )
    write_text(root, "scripts/zigux/validate-phase1.py", "import sys\nif __name__ == '__main__':\n    print('PHASE1_VALIDATION=pass')\n    raise SystemExit(0)\n")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_closure_") as tmp:
        root = Path(tmp)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 1

        (root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md").unlink()
        assert "Documentation/zigux/phase1-host-helper-lane-sequencing.md" in collect_missing_files(root)
        case_count += 1
        make_fixture_root(root)

        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        workflow_path.write_text(workflow_path.read_text(encoding="utf-8").replace(WORKFLOW_MARKERS[0], "", 1), encoding="utf-8")
        assert any(item.startswith("workflow:") for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        closure_path = root / "Documentation/zigux/phase1-closure.md"
        closure_path.write_text(closure_path.read_text(encoding="utf-8").replace(CLOSURE_MARKERS[0], "", 1), encoding="utf-8")
        assert any(item.startswith("closure:") for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        closure_path.write_text(closure_path.read_text(encoding="utf-8").replace(CLOSURE_MARKERS[19], "", 1), encoding="utf-8")
        assert any(item == f"closure:{CLOSURE_MARKERS[19]}" for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        closure_path.write_text(closure_path.read_text(encoding="utf-8").replace(CLOSURE_MARKERS[9], "", 1), encoding="utf-8")
        assert any(item == f"closure:{CLOSURE_MARKERS[9]}" for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        closure_path.write_text(closure_path.read_text(encoding="utf-8").replace(CLOSURE_MARKERS[15], "", 1), encoding="utf-8")
        assert any(item == f"closure:{CLOSURE_MARKERS[15]}" for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        closure_path.write_text(closure_path.read_text(encoding="utf-8").replace(CLOSURE_MARKERS[31], "", 1), encoding="utf-8")
        assert any(item == f"closure:{CLOSURE_MARKERS[31]}" for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        closure_path.write_text(closure_path.read_text(encoding="utf-8").replace(CLOSURE_MARKERS[32], "", 1), encoding="utf-8")
        assert any(item == f"closure:{CLOSURE_MARKERS[32]}" for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        closure_path.write_text(closure_path.read_text(encoding="utf-8").replace(CLOSURE_MARKERS[-1], "", 1), encoding="utf-8")
        assert any(item == f"closure:{CLOSURE_MARKERS[-1]}" for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/bitmap.zig"]["predicate_tail_mask_anchor"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "bitmap_manifest:predicate_tail_mask_anchor" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/find_bit.zig"]["tail_word_inclusive_boundary_anchor"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "find_bit_manifest:tail_word_inclusive_boundary_anchor" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        find_bit_path = root / FIND_BIT_HELPER_REL
        find_bit_path.write_text(
            find_bit_path.read_text(encoding="utf-8").replace(
                f"{EXPECTED_FIND_BIT_MANIFEST['helper_test_anchors'][-1]} {{}}\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert "find_bit_manifest:helper_test_anchors" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/rbtree.zig"]["next_safe_step_note"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "rbtree_manifest:next_safe_step_note" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        string_path = root / STRING_HELPER_REL
        string_path.write_text(
            string_path.read_text(encoding="utf-8").replace(f"{EXPECTED_STRING_HELPER_TESTS[-1]} {{}}\n", "", 1),
            encoding="utf-8",
        )
        assert "string_manifest:helper_test_anchors" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["memparse_review_anchors"] = ["drift"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "string_manifest:memparse_review_anchors" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["prefix_suffix_review_anchors"] = ["drift"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "string_manifest:prefix_suffix_review_anchors" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["lookup_review_anchors"] = ["drift"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "string_manifest:lookup_review_anchors" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["strnchr_review_anchor"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "string_manifest:strnchr_review_anchor" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        bench_path = root / "zigux/tests/fixtures/phase1_bench_expectations.json"
        bench = json.loads(bench_path.read_text(encoding="utf-8"))
        bench["exact_checksums"]["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"] = 1
        bench_path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        assert "bench:exact_checksums" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        phase1_validator = root / VALIDATE_PHASE1_REL
        phase1_validator.write_text("import sys\nif __name__ == '__main__':\n    print('PHASE1_VALIDATION=fail')\n    raise SystemExit(1)\n", encoding="utf-8")
        assert any(item.startswith("phase1_validator_failed:") for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        closure_path = root / "Documentation/zigux/phase1-closure.md"
        closure_text = closure_path.read_text(encoding="utf-8")
        for marker in [
            CLOSURE_MARKERS[12],
            CLOSURE_MARKERS[13],
            CLOSURE_MARKERS[14],
            CLOSURE_MARKERS[17],
            CLOSURE_MARKERS[19],
            CLOSURE_MARKERS[20],
            CLOSURE_MARKERS[24],
            CLOSURE_MARKERS[26],
        ]:
            closure_path.write_text(closure_text.replace(marker + "\n", "", 1), encoding="utf-8")
            assert any(item == f"closure:{marker}" for item in collect_missing_markers(root))
            closure_path.write_text(closure_text, encoding="utf-8")
            case_count += 1

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

    root = repo_root(args.root)
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
        f"{len(WORKFLOW_MARKERS) + len(DOCS_ROOT_MARKERS) + len(TESTS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(CLOSURE_MARKERS) + len(LEDGER_MARKERS) + len(MAKEFILE_MARKERS) + len(BUILD_MARKERS) + len(EXPECTED_BITMAP_MANIFEST) + len(EXPECTED_FIND_BIT_MANIFEST) + len(EXPECTED_RBTREE_MANIFEST) + 5}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

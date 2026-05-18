#!/usr/bin/env python3
"""Validate the current Phase 1 closure note against the live reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
TESTS_README_REL = Path("zigux/tests/README.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")
FIND_BIT_HELPER_REL = Path("tools/lib/find_bit.zig")
RBTREE_HELPER_REL = Path("tools/lib/rbtree.zig")
STRING_HELPER_REL = Path("tools/lib/string.zig")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    PHASE1_LANE_NOTE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    BENCH_CHECKER_REL,
    TESTS_README_REL,
    TESTS_BUILD_REL,
    PHASE1_SMOKE_REL,
    MANIFEST_REL,
    BITMAP_HELPER_REL,
    FIND_BIT_HELPER_REL,
    RBTREE_HELPER_REL,
    STRING_HELPER_REL,
)

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

EXPECTED_BITMAP_HELPER_TEST_ANCHORS = [
    'test "bitmap set clear weight and empty full helpers"',
    'test "bitmap range helpers preserve edges across whole-word spans"',
    'test "bitmap copy alias preserves raw source words without tail clearing"',
    'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    'test "bitmap copy and extend handles zero and aligned counts"',
    'test "bitmap copy helpers keep zero-sized destination views untouched"',
    'test "bitmap and andnot equal intersects subset"',
    'test "bitmap tail-masked helpers ignore out-of-range differences"',
    'test "bitmap full empty and weight ignore out-of-range tail bits"',
    'test "bitmap xor keeps caller-selected bit window"',
    'test "bitmap xor across a multiword tail still lets callers clamp the last word"',
    'test "bitmap scnprintf collapses contiguous ranges"',
    'test "bitmap scnprintf truncates and keeps a terminator slot"',
    'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
    'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    'test "bitmap allocation helpers size zero fill and reset optionals"',
]

EXPECTED_BITMAP_REVIEW_FIELDS = {
    "first_word_boundary_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
    "final_partial_word_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
    "fill_tail_clamp_anchor": 'test "bitmap full empty and weight ignore out-of-range tail bits"',
    "predicate_tail_mask_anchor": 'test "bitmap tail-masked helpers ignore out-of-range differences"',
    "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
    "review_packet_summary": (
        "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, "
        "scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while current "
        "master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw "
        "copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend "
        "handling, zero-sized destination-view no-op coverage, tail-masked predicate behavior, "
        "out-of-range tail-bit full or empty or weight masking, caller-window xor clamping, "
        "terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer "
        "preservation, and allocator optional-reset coverage."
    ),
    "parity_fixture_keys": [
        "alloc_words",
        "zalloc_words",
        "zalloc_values",
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
    "scnprintf_cross_word_anchor": 'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    "scnprintf_truncation_anchor": 'test "bitmap scnprintf truncates and keeps a terminator slot"',
    "empty_buffer_anchor": 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
    "copy_zero_and_aligned_anchors": [
        'test "bitmap copy and extend handles zero and aligned counts"',
        'test "bitmap copy helpers keep zero-sized destination views untouched"',
    ],
    "zero_bit_noop_anchor": "",
    "zero_bit_binary_identity_anchor": "",
    "linux_alias_anchor": "",
    "next_safe_step_note": (
        "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new "
        "direct-anchor drift inside the current helper-local packet or committed shared replay "
        "drift in the bitmap parity fields; current master still ships direct fill-tail clamp, "
        "copy-alias, truncation, cross-word scnprintf, empty-buffer, and allocator-reset anchors "
        "here, while zero-bit and Linux-style alias follow-through no longer live in the "
        "helper-local packet, and if the separate bitmap closure-validator anchor-sync repair is "
        "still outstanding, treat that as the only other bitmap follow-through."
    ),
}

EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS = [
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
    'test "clump8 scans mask tail bits beyond nbits"',
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
]

EXPECTED_FIND_BIT_SOURCE_SYMBOLS = [
    "pub fn findFirstAndNotBit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn _find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn findNextAndNotBit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn _find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
]

EXPECTED_FIND_BIT_REVIEW_FIELDS = {
    "same_word_start_masks": 'test "single-word next scans honor start masks"',
    "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "tail_word_inclusive_boundary_contract": (
        "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned "
        "when the inclusive start lands on the last in-range bit of the final partial word, "
        "while later starts still return nbits instead of leaking the out-of-range tail."
    ),
    "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
    "zero_sized_short_circuit_anchor": 'test "zero-sized scans ignore populated backing words"',
    "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
    "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers"',
    "linux_alias_anchor": 'test "Linux-style aliases mirror the primary find helpers"',
    "tail_word_set_skip_anchor": 'test "tail-word next set scans skip earlier in-range matches before clamping"',
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
    "review_packet_summary": (
        "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, while "
        "helper-local anchors keep same-word start-mask, head-word and tail-word "
        "inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, "
        "tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), "
        "underscore-alias, and Linux-style alias behavior review-visible on current master"
    ),
    "next_safe_step_note": (
        "If this helper lane reopens, keep find_bit parked unless a fresh reread finds "
        "direct-anchor drift inside same-word start-mask, inclusive-boundary, "
        "zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), "
        "findLastBit(), underscore-alias, Linux-style alias, or tail-word skip anchors, "
        "or committed tail-clamped replay drift; do not reopen older saved validator cues "
        "or neighboring helper families."
    ),
}

EXPECTED_RBTREE_HELPER_TEST_ANCHORS = [
    'test "rbtree inserts and traverses in sorted order"',
    'test "rbtree erase and replace keep traversal consistent"',
    'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
    'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
    'test "rbtree eraseInit detaches erased node"',
    'test "rbtree eraseInit clears singleton roots before reseed"',
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
]

EXPECTED_RBTREE_REVIEW_FIELDS = {
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
        "match_iterator_serials",
        "next_match_terminal_null",
    ],
    "cached_leftmost_fixture_keys": [
        "cached_leftmost_return_serials",
    ],
    "shared_replay_summary": (
        "shared traversal, detached-node, duplicate-search, and iterator replay stay explicit "
        "through the Phase 1 fixture and replay, while current master also carries the parked "
        "`cached_leftmost_return_serials` parity-only witness in the committed shared fixture "
        "beside the direct cached-root packet"
    ),
    "traversal_replay_keys": [
        "empty_root",
        "insert_order",
        "reverse_order",
        "replace_order",
        "erase_init_order",
        "postorder_count",
        "erase_init_node_empty",
        "cleared_node_empty",
    ],
    "duplicate_search_replay_keys": [
        "find_found_key",
        "find_missing",
        "find_first_serial",
        "next_match_serials",
        "match_iterator_serials",
        "next_match_terminal_null",
    ],
    "cached_root_direct_review_summary": (
        "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, "
        "replacement, detach, and reseed behavior remain owned by direct helper-local anchors, "
        "while current master already ships and the shared Zig replay already consumes the "
        "parked `cached_leftmost_return_serials` witness as shared cached-root leftmost-return "
        "evidence"
    ),
    "ordered_alias_anchor": 'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
    "low_level_alias_anchor": 'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
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
    "cached_root_alias_anchor": 'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
    "review_packet_summary": (
        "shared find, first-match, next-match, and match-iterator duplicate-search parity stays "
        "explicit through the Phase 1 fixture and replay, and current master already consumes "
        "`cached_leftmost_return_serials` as shared cached-root leftmost-return evidence, while "
        "the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, "
        "replacement, detach, and reseed review anchors stay explicit at the helper surface for "
        "any paths the shared replay still does not cover"
    ),
    "next_safe_step_note": (
        "If this helper lane reopens, keep the already-landed shared-replay promotion for "
        "`cached_leftmost_return_serials` aligned across the committed fixture, shared replay, "
        "and direct cached-root anchors; until another committed cached-root replay field lands, "
        "insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, "
        "and reseed behavior stay owned by direct helper-local anchors."
    ),
}

EXPECTED_STRING_SOURCE_SYMBOLS = [
    "pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn sysfs_match_string(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn matchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn match_string(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {",
    "pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {",
    "pub fn strnchrnul(buf: []const u8, count: usize, needle: u8) usize {",
]

EXPECTED_STRING_PACKET = {
    "helper_test_anchors": [
        'test "strtobool accepts common Linux forms"',
        'test "strlcpy copies and returns the source length"',
        'test "strscpy keeps NUL termination and reports truncation with -E2BIG"',
        'test "strscpyPad zero-pads the tail after a short source"',
        'test "strscpyPad stops at embedded NUL and pads the remaining tail"',
        'test "strscpyPad preserves strscpy truncation semantics"',
        'test "strscpy_pad mirrors strscpyPad padding semantics"',
        'test "strscpy and strscpyPad keep one-byte destinations terminated"',
        'test "streq matches C-string equality semantics"',
        'test "skip trim remove and replace spaces work in place"',
        'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
        'test "strreplace mirrors replaceChar C-string semantics"',
        'test "strHasPrefix returns the matched prefix length with C-string semantics"',
        'test "strHasSuffix returns the matched suffix length with C-string semantics"',
        'test "strstarts mirrors the header-level prefix helper"',
        'test "strEndsWith honors C-string boundaries"',
        'test "kbasename returns the final path component with C-string semantics"',
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
        'test "memchrInv keeps the earliest dirty byte across the fast-path cutoff"',
        'test "memparse handles decimal hexadecimal octal and suffixes"',
        'test "memparse keeps original rest when sign is not followed by digits"',
        'test "memparse saturates signed overflow instead of trapping"',
        'test "memparse clamps explicit positive signed overflow"',
        'test "memparse keeps signed values and their trailing rest aligned"',
        'test "memparse consumes suffix after saturation"',
        'test "memparse applies suffixes before signed clamping"',
        'test "strnchr honors count and C-string boundaries"',
        'test "strnchrNul returns the first match, NUL, or count boundary"',
    ],
    "memparse_review_anchors": [
        'test "memparse handles decimal hexadecimal octal and suffixes"',
        'test "memparse keeps original rest when sign is not followed by digits"',
        'test "memparse saturates signed overflow instead of trapping"',
        'test "memparse clamps explicit positive signed overflow"',
        'test "memparse keeps signed values and their trailing rest aligned"',
        'test "memparse consumes suffix after saturation"',
        'test "memparse applies suffixes before signed clamping"',
    ],
    "memparse_review_summary": (
        "helper-local memparse safety anchors stay explicit through the direct string tests so "
        "sign-prefixed invalid input preserves rest, signed inputs keep their trailing-rest split "
        "aligned with unsigned parsing, implicit and explicit signed overflow clamp instead of "
        "trapping, and suffixes are still consumed after saturation"
    ),
    "prefix_suffix_review_anchors": [
        'test "strHasPrefix returns the matched prefix length with C-string semantics"',
        'test "strHasSuffix returns the matched suffix length with C-string semantics"',
        'test "strstarts mirrors the header-level prefix helper"',
        'test "strEndsWith honors C-string boundaries"',
    ],
    "prefix_suffix_review_summary": (
        "helper-local prefix and suffix boundary anchors stay explicit through the direct string "
        "tests because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity "
        "rather than dedicated prefix or suffix fixture fields, so strHasPrefix and str_has_prefix "
        "plus strHasSuffix and str_has_suffix plus strstarts plus strEndsWith and str_ends_with "
        "plus strends remain review-visible at the helper surface"
    ),
    "sysfs_review_anchors": [
        'test "sysfsStreq treats trailing newline and NUL as equivalent"',
        'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
        'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
        'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
    ],
    "sysfs_review_summary": (
        "helper-local sysfs newline-aware equality and lookup-order anchors stay explicit through "
        "the direct string tests because the shared Phase 1 replay still carries no dedicated "
        "sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and "
        "sysfs_match_string remain review-visible at the helper surface"
    ),
    "lookup_review_anchors": [
        'test "matchString finds C-string matches and preserves first-match order"',
        'test "match_string mirrors matchString for empty and matched lists"',
    ],
    "lookup_review_summary": (
        "helper-local string lookup anchors stay explicit through the direct string tests because "
        "the shared Phase 1 replay still does not carry dedicated matchString() or "
        "match_string() fixture keys, so C-string list lookup order and the Linux-style alias "
        "remain review-visible at the helper surface"
    ),
    "strscpy_review_anchors": [
        'test "strscpy keeps NUL termination and reports truncation with -E2BIG"',
        'test "strscpyPad zero-pads the tail after a short source"',
        'test "strscpyPad stops at embedded NUL and pads the remaining tail"',
        'test "strscpyPad preserves strscpy truncation semantics"',
        'test "strscpy_pad mirrors strscpyPad padding semantics"',
        'test "strscpy and strscpyPad keep one-byte destinations terminated"',
    ],
    "strscpy_review_summary": (
        "helper-local string copy-and-pad anchors stay explicit through the direct string tests "
        "because the shared Phase 1 replay still does not carry dedicated strscpy() or "
        "strscpyPad() fixture keys"
    ),
    "counted_search_review_anchors": [
        'test "strnchr honors count and C-string boundaries"',
        'test "strnchrNul returns the first match, NUL, or count boundary"',
    ],
    "strnchr_review_anchor": 'test "strnchr honors count and C-string boundaries"',
    "strnchrnul_review_anchor": 'test "strnchrNul returns the first match, NUL, or count boundary"',
    "strnchr_review_summary": (
        "the direct counted-search follow-up stays explicit because the shared Phase 1 replay "
        "still does not carry dedicated counted-search fixture keys, so strnchr() count-limited "
        "scanning and strnchrNul() or strnchrnul() match-or-NUL boundary behavior remain owned "
        "by the helper-local anchors"
    ),
    "basename_review_anchor": 'test "kbasename returns the final path component with C-string semantics"',
    "basename_review_summary": (
        "helper-local basename path-tail anchor stays explicit through the direct string tests "
        "because the shared Phase 1 replay still does not carry dedicated kbasename fixture keys, "
        "so final path-component extraction at the first C-string terminator remains review-visible "
        "at the helper surface"
    ),
    "trim_nul_review_anchor": 'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
    "trim_nul_review_summary": (
        "the direct trim follow-up stays explicit because the shared Phase 1 string fixture "
        "records the trimmed bytes but not the preserved tail bytes beyond the first embedded "
        "terminator"
    ),
    "phase1_trim_cstr_replay_anchor": 'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
    "phase1_trim_cstr_replay_summary": (
        "the shared Phase 1 string replay still only locks the plain trailing-whitespace "
        "trimSpaces bytes from the committed fixture, while the direct helper-local trim "
        "follow-up keeps embedded-NUL trimming for trimSpaces and strim plus strstrip and "
        "preserved tail-byte review explicit because the shared packet still does not exercise "
        "every trim alias or every post-NUL byte position"
    ),
    "memchr_moving_dirty_anchor": 'test "memchrInv follows the earliest dirty byte as long buffers change"',
    "memchr_moving_dirty_review_summary": (
        "the direct memchrInv follow-up stays explicit because the shared Phase 1 fixture pins "
        "one fixed dirty index and the clean case, but not the moving earliest-mismatch ownership "
        "as later dirty bytes become the next live divergence"
    ),
    "phase1_helper_replay_anchor": 'test "phase 1 string replaceChar stops at embedded NUL"',
    "shared_replace_char_cstr_review_summary": (
        "the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, "
        "trimSpaces, removeSpaces, replaceChar, and memchrInv fixture parity, while the "
        "dedicated embedded-NUL replaceChar follow-up keeps the first-terminator stop rule "
        "explicit without widening helper-local memparse ownership"
    ),
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
    "next_safe_step_note": (
        "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across "
        "the string review packet and this lane note unless dedicated shared sysfs fixture keys "
        "land; do not reopen missing closure-side validator names by default."
    ),
}

EXPECTED_MARKERS = {
    "status": "`PHASE1_STATUS=parked`",
    "restore_state": "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "helper_count": "`PHASE1_HELPER_COUNT=13`",
    "reminder_packet": (
        "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,"
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,"
        "Documentation/zigux/review-checklist.md,scripts/zigux/README.md,"
        "scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,"
        "scripts/zigux/check-phase1-bench.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,"
        "zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,zigux/tests/fixtures/phase1_helper_manifest.json`"
    ),
    "gap_packet": (
        "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,"
        "zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,"
        "zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`"
    ),
    "closure_validator": "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "shared_tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "validator_state": "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "next_step": (
        "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker "
        "against the restored closure note, the closure validator, the shared tests-root smoke "
        "route, and the helper-specific next_safe_step_note entries in the committed manifest "
        "rather than widening back into the older validator-first or replay-side closure stack.`"
    ),
}

FORBIDDEN_MARKERS = {
    "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`",
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def iter_anchor_strings(expected: object) -> list[str]:
    anchors: list[str] = []
    if isinstance(expected, str):
        if expected.startswith('test "'):
            anchors.append(expected)
    elif isinstance(expected, list):
        for item in expected:
            if isinstance(item, str) and item.startswith('test "'):
                anchors.append(item)
    return anchors


def append_helper_source_checks(
    failures: list[str],
    helper_text: str,
    helper_rel: Path,
    helper_test_anchors: list[str],
    extra_expected_fields: dict[str, object] | None = None,
    source_symbols: list[str] | None = None,
) -> None:
    seen: set[str] = set()
    for anchor in helper_test_anchors:
        if anchor not in seen:
            failures.extend(
                require_exact_occurrence(
                    helper_text,
                    f"{helper_rel.as_posix()}:helper_test_anchor",
                    anchor,
                )
            )
            seen.add(anchor)

    if extra_expected_fields:
        for key, expected in extra_expected_fields.items():
            for anchor in iter_anchor_strings(expected):
                if anchor in seen:
                    continue
                failures.extend(
                    require_exact_occurrence(
                        helper_text,
                        f"{helper_rel.as_posix()}:{key}",
                        anchor,
                    )
                )
                seen.add(anchor)

    for symbol in source_symbols or []:
        failures.extend(
            require_exact_occurrence(
                helper_text,
                f"{helper_rel.as_posix()}:source_symbol",
                symbol,
            )
        )


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    for label, marker in EXPECTED_MARKERS.items():
        failures.extend(
            require_exact_occurrence(closure_text, f"{PHASE1_CLOSURE_REL.as_posix()}:{label}", marker)
        )
    for marker in FORBIDDEN_MARKERS:
        count = closure_text.count(marker)
        if count:
            failures.append(
                f"{PHASE1_CLOSURE_REL.as_posix()}:forbidden_marker:actual_count={count}:{marker}"
            )

    manifest = json.loads(load_text(root, MANIFEST_REL))
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:phase", manifest.get("phase"), "Phase 1"))
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:status", manifest.get("status"), "closed"))
    failures.extend(
        require_exact_value(f"{MANIFEST_REL.as_posix()}:helper_count", manifest.get("helper_count"), len(EXPECTED_HELPERS))
    )
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:helpers", manifest.get("helpers"), EXPECTED_HELPERS))

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict:actual={type(review_anchors).__name__}"]

    bitmap_review = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_review, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig:expected=dict:actual={type(bitmap_review).__name__}"]
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig:helper_test_anchors",
            bitmap_review.get("helper_test_anchors"),
            EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
        )
    )
    for key, expected in EXPECTED_BITMAP_REVIEW_FIELDS.items():
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig:{key}",
                bitmap_review.get(key),
                expected,
            )
        )

    find_bit_review = review_anchors.get("tools/lib/find_bit.zig")
    if not isinstance(find_bit_review, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig:expected=dict:actual={type(find_bit_review).__name__}"]
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig:helper_test_anchors",
            find_bit_review.get("helper_test_anchors"),
            EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS,
        )
    )
    for key, expected in EXPECTED_FIND_BIT_REVIEW_FIELDS.items():
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig:{key}",
                find_bit_review.get(key),
                expected,
            )
        )

    rbtree_review = review_anchors.get("tools/lib/rbtree.zig")
    if not isinstance(rbtree_review, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig:expected=dict:actual={type(rbtree_review).__name__}"]
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig:helper_test_anchors",
            rbtree_review.get("helper_test_anchors"),
            EXPECTED_RBTREE_HELPER_TEST_ANCHORS,
        )
    )
    for key, expected in EXPECTED_RBTREE_REVIEW_FIELDS.items():
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig:{key}",
                rbtree_review.get(key),
                expected,
            )
        )

    string_review = review_anchors.get("tools/lib/string.zig")
    if not isinstance(string_review, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/string.zig:expected=dict:actual={type(string_review).__name__}"]
    for key, expected in EXPECTED_STRING_PACKET.items():
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/string.zig:{key}",
                string_review.get(key),
                expected,
            )
        )

    append_helper_source_checks(
        failures,
        load_text(root, BITMAP_HELPER_REL),
        BITMAP_HELPER_REL,
        EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
        extra_expected_fields=EXPECTED_BITMAP_REVIEW_FIELDS,
    )
    append_helper_source_checks(
        failures,
        load_text(root, FIND_BIT_HELPER_REL),
        FIND_BIT_HELPER_REL,
        EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS,
        source_symbols=EXPECTED_FIND_BIT_SOURCE_SYMBOLS,
    )
    append_helper_source_checks(
        failures,
        load_text(root, RBTREE_HELPER_REL),
        RBTREE_HELPER_REL,
        EXPECTED_RBTREE_HELPER_TEST_ANCHORS,
    )
    append_helper_source_checks(
        failures,
        load_text(root, STRING_HELPER_REL),
        STRING_HELPER_REL,
        EXPECTED_STRING_PACKET["helper_test_anchors"],
        source_symbols=EXPECTED_STRING_SOURCE_SYMBOLS,
    )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def build_helper_fixture_text(helper_test_anchors: list[str], extra_expected_fields: dict[str, object] | None = None, source_symbols: list[str] | None = None) -> str:
    lines: list[str] = []
    seen: set[str] = set()

    for symbol in source_symbols or []:
        if symbol not in seen:
            lines.append(symbol)
            seen.add(symbol)

    for anchor in helper_test_anchors:
        if anchor not in seen:
            lines.append(anchor)
            seen.add(anchor)

    for expected in (extra_expected_fields or {}).values():
        for anchor in iter_anchor_strings(expected):
            if anchor not in seen:
                lines.append(anchor)
                seen.add(anchor)

    return "\n".join(lines) + "\n"


def make_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root / relative_path, f"fixture for {relative_path.as_posix()}\n")

    write_text(
        root / PHASE1_CLOSURE_REL,
        "\n".join(
            [
                "# Phase 1 Closure",
                "",
                EXPECTED_MARKERS["status"],
                EXPECTED_MARKERS["restore_state"],
                EXPECTED_MARKERS["helper_count"],
                EXPECTED_MARKERS["reminder_packet"],
                EXPECTED_MARKERS["gap_packet"],
                EXPECTED_MARKERS["closure_validator"],
                EXPECTED_MARKERS["shared_tests_route"],
                EXPECTED_MARKERS["validator_state"],
                EXPECTED_MARKERS["next_step"],
                "",
            ]
        ),
    )

    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": len(EXPECTED_HELPERS),
                "helpers": EXPECTED_HELPERS,
                "review_anchors": {
                    "tools/lib/bitmap.zig": {
                        "helper_test_anchors": EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
                        **EXPECTED_BITMAP_REVIEW_FIELDS,
                    },
                    "tools/lib/find_bit.zig": {
                        "helper_test_anchors": EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS,
                        **EXPECTED_FIND_BIT_REVIEW_FIELDS,
                    },
                    "tools/lib/rbtree.zig": {
                        "helper_test_anchors": EXPECTED_RBTREE_HELPER_TEST_ANCHORS,
                        **EXPECTED_RBTREE_REVIEW_FIELDS,
                    },
                    "tools/lib/string.zig": EXPECTED_STRING_PACKET,
                },
            },
            indent=2,
        )
        + "\n",
    )

    write_text(
        root / BITMAP_HELPER_REL,
        build_helper_fixture_text(
            EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
            extra_expected_fields=EXPECTED_BITMAP_REVIEW_FIELDS,
        ),
    )
    write_text(
        root / FIND_BIT_HELPER_REL,
        build_helper_fixture_text(
            EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS,
            source_symbols=EXPECTED_FIND_BIT_SOURCE_SYMBOLS,
        ),
    )
    write_text(
        root / RBTREE_HELPER_REL,
        build_helper_fixture_text(EXPECTED_RBTREE_HELPER_TEST_ANCHORS),
    )
    write_text(
        root / STRING_HELPER_REL,
        build_helper_fixture_text(
            EXPECTED_STRING_PACKET["helper_test_anchors"],
            source_symbols=EXPECTED_STRING_SOURCE_SYMBOLS,
        ),
    )


def mutate_manifest_packet(root: Path, helper: str, field: str, value: object) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["review_anchors"][helper][field] = value
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = [
        ("baseline", None),
        (
            "missing_restore_state",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                replace_once(load_text(root, PHASE1_CLOSURE_REL), EXPECTED_MARKERS["restore_state"], "`PHASE1_CLOSURE_RESTORE_STATE=docs_only`"),
            ),
        ),
        (
            "old_next_step_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                replace_once(
                    load_text(root, PHASE1_CLOSURE_REL),
                    EXPECTED_MARKERS["next_step"],
                    "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface against the restored closure note and closure validator`",
                ),
            ),
        ),
        ("missing_bitmap_helper_file", lambda root: (root / BITMAP_HELPER_REL).unlink()),
        (
            "bad_bitmap_review_field",
            lambda root: mutate_manifest_packet(root, "tools/lib/bitmap.zig", "copy_raw_alias_anchor", "drift"),
        ),
        (
            "missing_bitmap_source_anchor",
            lambda root: write_text(
                root / BITMAP_HELPER_REL,
                replace_once(
                    load_text(root, BITMAP_HELPER_REL),
                    EXPECTED_BITMAP_REVIEW_FIELDS["scnprintf_cross_word_anchor"] + "\n",
                    "",
                ),
            ),
        ),
        (
            "bad_find_bit_review_field",
            lambda root: mutate_manifest_packet(root, "tools/lib/find_bit.zig", "same_word_start_masks", "drift"),
        ),
        (
            "missing_find_bit_source_symbol",
            lambda root: write_text(
                root / FIND_BIT_HELPER_REL,
                replace_once(load_text(root, FIND_BIT_HELPER_REL), EXPECTED_FIND_BIT_SOURCE_SYMBOLS[0] + "\n", ""),
            ),
        ),
        (
            "bad_rbtree_review_field",
            lambda root: mutate_manifest_packet(root, "tools/lib/rbtree.zig", "low_level_alias_anchor", "drift"),
        ),
        (
            "missing_rbtree_source_anchor",
            lambda root: write_text(
                root / RBTREE_HELPER_REL,
                replace_once(load_text(root, RBTREE_HELPER_REL), EXPECTED_RBTREE_HELPER_TEST_ANCHORS[3] + "\n", ""),
            ),
        ),
        (
            "bad_string_review_field",
            lambda root: mutate_manifest_packet(root, "tools/lib/string.zig", "basename_review_anchor", "drift"),
        ),
        (
            "missing_string_source_anchor",
            lambda root: write_text(
                root / STRING_HELPER_REL,
                replace_once(load_text(root, STRING_HELPER_REL), EXPECTED_STRING_PACKET["helper_test_anchors"][15] + "\n", ""),
            ),
        ),
        (
            "forbidden_old_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL) + "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`\n",
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-selftest-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run validator self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print("PHASE1_CLOSURE_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

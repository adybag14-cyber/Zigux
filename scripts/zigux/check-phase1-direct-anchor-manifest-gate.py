#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile


EXPECTED_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_PHASE1_HELPERS = [
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

EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

EXPECTED_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)

EXPECTED_MANIFEST_RELATIVE_PATH = "zigux/tests/fixtures/phase1_helper_manifest.json"
EXPECTED_BLOCKERS_RELATIVE_PATH = "zigux/tests/fixtures/phase1_replay_blockers.json"

EXPECTED_REVIEW_ANCHORS = {
    "tools/lib/bitmap.zig": {
        "helper_test_anchors": [
            'test "bitmap set clear weight and empty full helpers"',
            'test "bitmap range helpers preserve edges across whole-word spans"',
            'test "bitmap copy alias preserves raw source words without tail clearing"',
            'test "bitmap copy aliases preserve tail clearing and extension semantics"',
            'test "bitmap copy and extend handles zero and aligned counts"',
            'test "bitmap copy helpers keep zero-sized destination views untouched"',
            'test "bitmap zero-bit logical helpers stay explicit"',
            'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
            'test "bitmap and andnot equal intersects subset"',
            'test "bitmap tail-masked helpers ignore out-of-range differences"',
            'test "bitmap full empty and weight ignore out-of-range tail bits"',
            'test "bitmap xor keeps caller-selected bit window"',
            'test "bitmap xor across a multiword tail still lets callers clamp the last word"',
            'test "bitmap or keeps caller-selected bit window"',
            'test "bitmap or across a multiword tail still lets callers clamp the last word"',
            'test "bitmap weighted or and xor clamp counts to the declared tail window"',
            'test "bitmap weighted and andnot clamp counts to the declared tail window"',
            'test "bitmap complement clamps partial tails and leaves zero-sized caller views untouched"',
            'test "bitmap scnprintf collapses contiguous ranges"',
            'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
            'test "bitmap scnprintf truncates and keeps a terminator slot"',
            'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
            'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
            'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
            'test "bitmap Linux-style aliases mirror size state and allocation helpers"',
            'test "bitmap allocation helpers size zero fill and reset optionals"',
        ],
        "first_word_boundary_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
        "final_partial_word_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
        "fill_tail_clamp_anchor": 'test "bitmap full empty and weight ignore out-of-range tail bits"',
        "equal_fast_path_anchor": 'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
        "predicate_tail_mask_anchor": 'test "bitmap tail-masked helpers ignore out-of-range differences"',
        "or_window_anchor": 'test "bitmap or keeps caller-selected bit window"',
        "or_multiword_tail_anchor": 'test "bitmap or across a multiword tail still lets callers clamp the last word"',
        "weighted_tail_count_anchor": 'test "bitmap weighted or and xor clamp counts to the declared tail window"',
        "complement_tail_anchor": 'test "bitmap complement clamps partial tails and leaves zero-sized caller views untouched"',
        "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
        "review_packet_summary": (
            "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, "
            "scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while current "
            "master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw "
            "copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend "
            "handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit "
            "coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, "
            "out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, "
            "multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only "
            "and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, "
            "Linux-style alias mirror coverage, and allocator optional-reset coverage."
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
        "zero_bit_noop_anchor": 'test "bitmap zero-bit logical helpers stay explicit"',
        "zero_bit_binary_identity_anchor": 'test "bitmap zero-bit logical helpers stay explicit"',
        "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
        "next_safe_step_note": (
            "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor "
            "drift inside the current helper-local packet or committed shared replay drift in the bitmap "
            "parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, "
            "cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and "
            "or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical "
            "short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side "
            "or validator-route cue names by default."
        ),
    },
    "tools/lib/find_bit.zig": {
        "helper_test_anchors": [
            'test "find first and next set bits across words, with andnot gaps explicit"',
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
            'test "clump8 zero-bit and past-end windows leave the caller byte untouched"',
            'test "clump8 past-end scans return without reading bitmap words"',
            'test "getValue8 reads aligned bytes from bitmap words"',
            'test "getValue8 reads the last aligned byte of a word without folding in the next word"',
            'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
            'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
            'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start"',
            'test "find last bit scans backward across words"',
            'test "find last bit ignores storage beyond an exact word boundary"',
            'test "find last bit clamps tail words to nbits"',
            'test "find last bit returns nbits when no set bits remain"',
            'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
            'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
            'test "Linux-style aliases mirror the primary find helpers, including andnot"',
        ],
        "same_word_start_masks": 'test "single-word next scans honor start masks"',
        "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        "single_word_tail_inclusive_boundary_anchor": 'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start"',
        "tail_word_inclusive_boundary_contract": (
            "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the "
            "inclusive start lands on the last in-range bit of the final partial word, while later starts "
            "still return nbits instead of leaking the out-of-range tail."
        ),
        "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
        "zero_sized_short_circuit_anchor": 'test "zero-sized scans ignore populated backing words"',
        "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
        "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
        "linux_alias_anchor": 'test "Linux-style aliases mirror the primary find helpers, including andnot"',
        "andnot_scan_entrypoints": [
            "findFirstAndNotBit",
            "find_first_andnot_bit",
            "_find_first_andnot_bit",
            "findNextAndNotBit",
            "find_next_andnot_bit",
            "_find_next_andnot_bit",
        ],
        "andnot_scan_entrypoint_contract": (
            "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the "
            "direct find_bit packet instead of being left implicit under generic alias wording."
        ),
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
        "tail_inclusive_boundary_fixture_keys": [
            "tail_inclusive_boundary_next",
            "tail_inclusive_boundary_zero",
            "tail_inclusive_boundary_and",
        ],
        "review_packet_summary": (
            "shared Phase 1 fixture keys own the exact tail-clamped and tail-inclusive-boundary find_bit "
            "replay, while helper-local anchors keep same-word start-mask, head-word and tail-word "
            "inclusive-boundary, single-word tail inclusive-boundary, zero-window, zero-sized "
            "short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), "
            "findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master"
        ),
        "next_safe_step_note": (
            "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor "
            "drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, "
            "past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage "
            "including the shipped andnot scan entry points, or tail-word skip anchors, or committed "
            "tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues "
            "or neighboring helper families."
        ),
    },
    "tools/lib/rbtree.zig": {
        "helper_test_anchors": [
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
        ],
        "phase1_helper_replay_anchor": 'test "phase1 host-tools smoke exercises live helper behavior"',
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
            "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, and "
            "exact cached-leftmost-return witnesses for rbtree, while the current shared host-tools smoke "
            "replay now rechecks duplicate-range iteration plus the exact `cached_leftmost_return_serials` "
            "cached-root leftmost-return sequence on current master"
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
        "next_safe_step_note": (
            "If this helper lane reopens, keep rbtree parked unless a fresh reread finds direct-anchor drift "
            "inside ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, "
            "leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors, or "
            "committed shared replay drift inside duplicate-search or cached-leftmost-return fields; do not "
            "batch a second widening into the same run."
        ),
    },
    "tools/lib/string.zig": {
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
            'test "strchr mirrors full-length C-string searches"',
            'test "strrchr finds the last in-range match with C-string semantics"',
            'test "strchr and strrchr return the terminator index when searching for NUL"',
            'test "strpbrk finds the first accepted byte with C-string semantics"',
            'test "strspn counts the accepted prefix with C-string semantics"',
            'test "strcspn counts until the first rejected byte with C-string semantics"',
            'test "strnchr honors count and C-string boundaries"',
            'test "strnlen honors count and C-string boundaries"',
            'test "strnchrNul returns the first match, NUL, or count boundary"',
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
            'test "strHasPrefix returns the matched prefix length with C-string semantics"',
            'test "strHasSuffix returns the matched suffix length with C-string semantics"',
            'test "strstarts mirrors the header-level prefix helper"',
            'test "strEndsWith honors C-string boundaries"',
        ],
        "phase1_helper_replay_anchor": 'test "phase 1 string replaceChar stops at embedded NUL"',
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
        "review_summary_scalars": [
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
        ],
        "sysfs_review_anchors": [
            'test "sysfsStreq treats trailing newline and NUL as equivalent"',
            'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
            'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
            'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
        ],
        "c_string_lookup_anchors": [
            'test "matchString finds C-string matches and preserves first-match order"',
            'test "match_string mirrors matchString for empty and matched lists"',
        ],
        "counted_search_anchors": [
            'test "strpbrk finds the first accepted byte with C-string semantics"',
            'test "strspn counts the accepted prefix with C-string semantics"',
            'test "strcspn counts until the first rejected byte with C-string semantics"',
            'test "strnchr honors count and C-string boundaries"',
            'test "strnchrNul returns the first match, NUL, or count boundary"',
            'test "strnlen honors count and C-string boundaries"',
            'test "strchr mirrors full-length C-string searches"',
            'test "strrchr finds the last in-range match with C-string semantics"',
            'test "strchr and strrchr return the terminator index when searching for NUL"',
        ],
        "review_packet_summary": (
            "current master keeps the direct helper-local string packet on strscpy and strscpyPad copy and "
            "pad semantics, memparse, matched prefix and suffix length, sysfs newline-aware equality and "
            "lookup order, C-string list lookup, counted search anchors, embedded-NUL trim preservation, "
            "and moving-earliest-dirty-byte memchrInv coverage, while the committed Phase 1 fixture still "
            "owns the shared replaceChar parity bytes and string review-summary scalars"
        ),
        "next_safe_step_note": (
            "If this helper lane reopens, keep string parked unless a fresh reread finds direct-anchor drift "
            "inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix "
            "boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string "
            "list lookup, counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), "
            "strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), "
            "embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed "
            "replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned "
            "across the string review packet and the lane note unless dedicated shared sysfs fixture keys "
            "land; do not reopen missing closure-side validator names by default."
        ),
    },
}


class DuplicateKeyError(ValueError):
    def __init__(self, key: str):
        super().__init__(key)
        self.key = key


def duplicate_key_object_pairs_hook(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(key)
        result[key] = value
    return result


def repo_root_from_arg(root_arg: str | None) -> Path:
    if root_arg:
        return Path(root_arg).resolve()
    return Path(__file__).resolve().parents[1]


def load_json_packet(packet_path: Path, packet_name: str, issues: list[str]):
    if not packet_path.exists():
        issues.append(f"{packet_name}:missing_file")
        return None
    if packet_path.is_dir():
        issues.append(f"{packet_name}:path_is_directory")
        return None
    try:
        return json.loads(
            packet_path.read_text(encoding="utf-8"),
            object_pairs_hook=duplicate_key_object_pairs_hook,
        )
    except DuplicateKeyError as exc:
        issues.append(f"{packet_name}:duplicate_key={exc.key}")
    except json.JSONDecodeError:
        issues.append(f"{packet_name}:malformed_json")
    return None


def collect_manifest_issues(manifest: dict, issues: list[str]) -> None:
    if manifest.get("phase") != "Phase 1":
        issues.append("manifest:phase=Phase 1")
    if manifest.get("status") != "closed":
        issues.append("manifest:status=closed")
    if manifest.get("helper_count") != len(EXPECTED_PHASE1_HELPERS):
        issues.append("manifest:helper_count=13")
    if manifest.get("helpers") != EXPECTED_PHASE1_HELPERS:
        issues.append("manifest:helpers=expected_phase1_helper_list")

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        issues.append("manifest:lane_sequencing=dict")
    else:
        expected_lane_fields = {
            "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
            "direct_anchor_followup_helpers": EXPECTED_HELPERS,
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        }
        for field, expected_value in expected_lane_fields.items():
            if field not in lane_sequencing:
                issues.append(f"manifest:missing_lane_sequencing_field={field}")
            elif lane_sequencing[field] != expected_value:
                issues.append(f"manifest:lane_sequencing.{field}=expected_value")

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        issues.append("manifest:review_anchors=dict")
        return

    for helper in EXPECTED_HELPERS:
        actual_entry = review_anchors.get(helper)
        expected_entry = EXPECTED_REVIEW_ANCHORS[helper]
        if not isinstance(actual_entry, dict):
            issues.append(f"manifest:missing_review_anchor={helper}")
            continue
        for field, expected_value in expected_entry.items():
            if field not in actual_entry:
                issues.append(f"manifest:missing_review_anchor_field={helper}:{field}")
                continue
            if actual_entry[field] != expected_value:
                issues.append(f"manifest:review_anchor_value={helper}:{field}")


def collect_blocker_issues(blockers: dict, issues: list[str]) -> None:
    if blockers.get("status") != "parked":
        issues.append("blockers:status=parked")

    lane_sequencing = blockers.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        issues.append("blockers:lane_sequencing=dict")
        return

    expected_lane_fields = {
        "manifest": EXPECTED_MANIFEST_RELATIVE_PATH,
        "shared_replay_parked_helper_count": len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
        "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
        "direct_anchor_followup_helper_count": len(EXPECTED_HELPERS),
        "direct_anchor_followup_helpers": EXPECTED_HELPERS,
        "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
    }
    for field, expected_value in expected_lane_fields.items():
        if field not in lane_sequencing:
            issues.append(f"blockers:missing_lane_sequencing_field={field}")
        elif lane_sequencing[field] != expected_value:
            issues.append(f"blockers:lane_sequencing.{field}=expected_value")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    manifest = load_json_packet(root / EXPECTED_MANIFEST_RELATIVE_PATH, "manifest", issues)
    blockers = load_json_packet(root / EXPECTED_BLOCKERS_RELATIVE_PATH, "blockers", issues)

    if isinstance(manifest, dict):
        collect_manifest_issues(manifest, issues)
    if isinstance(blockers, dict):
        collect_blocker_issues(blockers, issues)

    return issues


def make_fixture_root(tmp_root: Path) -> None:
    manifest_path = tmp_root / EXPECTED_MANIFEST_RELATIVE_PATH
    blockers_path = tmp_root / EXPECTED_BLOCKERS_RELATIVE_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    blockers_path.parent.mkdir(parents=True, exist_ok=True)
    if manifest_path.is_dir():
        shutil.rmtree(manifest_path)
    if blockers_path.is_dir():
        shutil.rmtree(blockers_path)

    manifest = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_PHASE1_HELPERS),
        "helpers": EXPECTED_PHASE1_HELPERS,
        "lane_sequencing": {
            "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
            "direct_anchor_followup_helpers": EXPECTED_HELPERS,
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "review_anchors": EXPECTED_REVIEW_ANCHORS,
    }
    blockers = {
        "status": "parked",
        "lane_sequencing": {
            "manifest": EXPECTED_MANIFEST_RELATIVE_PATH,
            "shared_replay_parked_helper_count": len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
            "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
            "direct_anchor_followup_helper_count": len(EXPECTED_HELPERS),
            "direct_anchor_followup_helpers": EXPECTED_HELPERS,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "replay": {
            "path": "zigux/tests/phase1_helpers.zig",
            "state": "blocked",
            "blockers": [
                {
                    "id": "phase1_helpers_zig_slab_zero_after_kmalloc",
                    "kind": "fixture_mismatch",
                    "path": "tools/lib/slab.zig",
                    "field": "slab.zero_after_kmalloc",
                    "expected": True,
                    "actual": False,
                    "evidence": (
                        "Focused 2026-05-17 scratch replay of `zig build test --build-file zigux/tests/build.zig "
                        "--summary all` failed at `phase1_helpers.zig:595` because the committed fixture expects "
                        "`true` while `tools/lib/slab.zig` still produced `false`."
                    ),
                }
            ],
        },
        "c_harness": {
            "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "state": "blocked",
            "reason": (
                "The old host-side parity route still depends on helper `tools/lib/*.c` inputs that current "
                "master no longer ships beside the Phase 1 `.zig` ports."
            ),
            "helper_count": len(EXPECTED_PHASE1_HELPERS),
            "helpers": EXPECTED_PHASE1_HELPERS,
            "blocker_id": "phase1_helpers_c_harness_missing_c_sources",
        },
    }

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")


def assert_issue_case(tmp_root: Path, mutate, expected_issue: str) -> None:
    mutate()
    issues = collect_issues(tmp_root)
    assert expected_issue in issues, issues
    make_fixture_root(tmp_root)


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_direct_anchor_manifest_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        make_fixture_root(tmp_root)
        assert collect_issues(tmp_root) == []

        manifest_path = tmp_root / EXPECTED_MANIFEST_RELATIVE_PATH
        blockers_path = tmp_root / EXPECTED_BLOCKERS_RELATIVE_PATH

        def load_current(path: Path) -> dict:
            return json.loads(path.read_text(encoding="utf-8"))

        assert_issue_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("scnprintf_cross_word_anchor"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_current(manifest_path)),
            "manifest:missing_review_anchor_field=tools/lib/bitmap.zig:scnprintf_cross_word_anchor",
        )
        case_count += 1

        assert_issue_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/find_bit.zig"]["tail_clamp_fixture_keys"].remove(
                        "tail_clamped_last"
                    ),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_current(manifest_path)),
            "manifest:review_anchor_value=tools/lib/find_bit.zig:tail_clamp_fixture_keys",
        )
        case_count += 1

        assert_issue_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["lane_sequencing"]["direct_anchor_followup_helpers"].pop(),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_current(manifest_path)),
            "manifest:lane_sequencing.direct_anchor_followup_helpers=expected_value",
        )
        case_count += 1

        assert_issue_case(
            tmp_root,
            lambda: blockers_path.unlink(),
            "blockers:missing_file",
        )
        case_count += 1

        assert_issue_case(
            tmp_root,
            lambda: (
                blockers_path.unlink(),
                blockers_path.mkdir(),
            ),
            "blockers:path_is_directory",
        )
        case_count += 1

        assert_issue_case(
            tmp_root,
            lambda: (
                lambda blockers: (
                    blockers["lane_sequencing"].update({"direct_anchor_followup_helper_count": 3}),
                    blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_current(blockers_path)),
            "blockers:lane_sequencing.direct_anchor_followup_helper_count=expected_value",
        )
        case_count += 1

        assert_issue_case(
            tmp_root,
            lambda: blockers_path.write_text("{\n  \"status\": \"parked\",\n  \"status\": \"blocked\"\n}\n", encoding="utf-8"),
            "blockers:duplicate_key=status",
        )
        case_count += 1

        assert_issue_case(
            tmp_root,
            lambda: blockers_path.write_text("{ not json }\n", encoding="utf-8"),
            "blockers:malformed_json",
        )
        case_count += 1

    print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass")
    print(f"PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST_CASE_COUNT={case_count}")


def write_sample_root(sample_root: Path) -> None:
    make_fixture_root(sample_root)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the direct-anchor Phase 1 helper manifest packet for bitmap, find_bit, rbtree, and "
            "string, including the live direct-anchor lane split shared with the replay-blocker packet."
        )
    )
    parser.add_argument("--self-test", action="store_true", help="Run embedded self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux checkout root.")
    parser.add_argument("--write-sample-root", help="Write a current-like sample root to the provided path.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    issues = collect_issues(repo_root_from_arg(args.root))
    if issues:
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=fail")
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_END")
        return 1

    print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass")
    print(f"PHASE1_DIRECT_ANCHOR_MANIFEST={EXPECTED_MANIFEST_RELATIVE_PATH}")
    print(f"PHASE1_DIRECT_ANCHOR_BLOCKERS={EXPECTED_BLOCKERS_RELATIVE_PATH}")
    print(f"PHASE1_DIRECT_ANCHOR_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(
        "PHASE1_DIRECT_ANCHOR_SHARED_REPLAY_PARKED_HELPER_COUNT="
        f"{len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS)}"
    )
    print(
        "PHASE1_DIRECT_ANCHOR_REVIEW_FIELD_COUNT="
        f"{sum(len(fields) for fields in EXPECTED_REVIEW_ANCHORS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

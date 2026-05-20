#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")

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

EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers "
    "above, while bitmap, find_bit, rbtree, and string keep the only bounded "
    "direct helper-local follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)

HELPER_EXPECTATIONS = {
    "tools/lib/bitmap.zig": {
        "helper_test_anchors": [
            'test "bitmap set clear weight and empty full helpers"',
            'test "bitmap range helpers preserve edges across whole-word spans"',
            'test "bitmap copy alias preserves raw source words without tail clearing"',
            'test "bitmap copy aliases preserve tail clearing and extension semantics"',
            'test "bitmap copy and extend handles zero and aligned counts"',
            'test "bitmap copy helpers keep zero-sized destination views untouched"',
            'test "bitmap zero-bit logical helpers stay explicit"',
            'test "bitmap and andnot equal intersects subset"',
            'test "bitmap tail-masked helpers ignore out-of-range differences"',
            'test "bitmap full empty and weight ignore out-of-range tail bits"',
            'test "bitmap xor keeps caller-selected bit window"',
            'test "bitmap xor across a multiword tail still lets callers clamp the last word"',
            'test "bitmap or keeps caller-selected bit window"',
            'test "bitmap or across a multiword tail still lets callers clamp the last word"',
            'test "bitmap weighted or and xor clamp counts to the declared tail window"',
            'test "bitmap scnprintf collapses contiguous ranges"',
            'test "bitmap scnprintf truncates and keeps a terminator slot"',
            'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
            'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
            'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
            'test "bitmap Linux-style aliases mirror size state and allocation helpers"',
            'test "bitmap allocation helpers size zero fill and reset optionals"',
        ],
        "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
        "review_packet_summary": (
            "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation "
            "words, scnprintf output, truncation, tiny-buffer, and partial-window xor replay, "
            "while current master keeps the direct helper-local bitmap packet bounded to whole-word "
            "range edges, raw copy alias behavior, tail-clearing and extension semantics, zero and "
            "aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit "
            "logical short-circuit coverage, tail-masked predicate behavior, out-of-range tail-bit "
            "full or empty or weight masking, caller-window xor and or clamping, multiword-tail xor "
            "and or clamp witnesses, weighted tail-count clamping, terminator-only and zero-length "
            "caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias "
            "mirror coverage, and allocator optional-reset coverage."
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
        "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
        "next_safe_step_note": (
            "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new "
            "direct-anchor drift inside the current helper-local packet or committed shared replay "
            "drift in the bitmap parity fields; current master still ships direct fill-tail clamp, "
            "copy-alias, truncation, cross-word scnprintf, caller-window xor and or clamp, weighted "
            "tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and "
            "Linux-style alias mirror anchors here, and if the separate bitmap closure-validator "
            "anchor-sync repair is still outstanding, treat that as the only other bitmap follow-through."
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
            'test "getValue8 reads aligned bytes from bitmap words"',
            'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
            'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
            'test "find last bit scans backward across words"',
            'test "find last bit ignores storage beyond an exact word boundary"',
            'test "find last bit clamps tail words to nbits"',
            'test "find last bit returns nbits when no set bits remain"',
            'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
            'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
            'test "Linux-style aliases mirror the primary find helpers, including andnot"',
        ],
        "same_word_start_masks": 'test "single-word next scans honor start masks"',
        "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        "tail_word_inclusive_boundary_contract": (
            "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned "
            "when the inclusive start lands on the last in-range bit of the final partial word, "
            "while later starts still return nbits instead of leaking the out-of-range tail."
        ),
        "andnot_scan_entrypoints": [
            "findFirstAndNotBit",
            "find_first_andnot_bit",
            "_find_first_andnot_bit",
            "findNextAndNotBit",
            "find_next_andnot_bit",
            "_find_next_andnot_bit",
        ],
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
            "shared Phase 1 fixture keys own the exact tail-clamped and tail-inclusive-boundary "
            "find_bit replay, while helper-local anchors keep same-word start-mask, head-word and "
            "tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, "
            "tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), "
            "underscore-alias, and Linux-style alias behavior review-visible on current master"
        ),
        "next_safe_step_note": (
            "If this helper lane reopens, keep find_bit parked unless a fresh reread finds "
            "direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, "
            "zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), "
            "underscore-alias, Linux-style alias coverage including the shipped andnot scan entry "
            "points, or tail-word skip anchors, or committed tail-clamped or tail-inclusive-boundary "
            "replay drift; do not reopen older saved validator cues or neighboring helper families."
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
        "cached_leftmost_fixture_keys": ["cached_leftmost_return_serials"],
        "duplicate_search_replay_keys": [
            "find_found_key",
            "find_missing",
            "find_first_serial",
            "next_match_serials",
            "match_iterator_serials",
            "next_match_terminal_null",
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
        "review_packet_summary": (
            "the current shared host-tools smoke replay keeps duplicate-range iteration and the "
            "exact `cached_leftmost_return_serials` cached-root leftmost-return witness visible for "
            "rbtree, while the committed Phase 1 fixture still carries the exact traversal, "
            "detached-node, duplicate-search, and cached-leftmost-return witnesses; direct "
            "helper-local anchors continue to own cached-root insert-miss, leftmost-sync, "
            "cached-root alias, singleton-erase, replacement, detach, and reseed paths that the "
            "shared smoke route does not replay exactly"
        ),
        "next_safe_step_note": (
            "If this helper lane reopens, keep the already-landed shared-replay promotion for "
            "`cached_leftmost_return_serials` aligned across the committed fixture, shared replay, "
            "and direct cached-root anchors; the ordered Linux-style alias proof, dedicated "
            "`low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, "
            "cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay "
            "owned by direct helper-local anchors until another committed cached-root field lands."
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
            'test "strchr mirrors full-length C-string searches"',
            'test "strrchr finds the last in-range match with C-string semantics"',
            'test "strpbrk finds the first accepted byte with C-string semantics"',
            'test "strspn counts the accepted prefix with C-string semantics"',
            'test "strnchr honors count and C-string boundaries"',
            'test "strnlen honors count and C-string boundaries"',
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
        "prefix_suffix_review_summary": (
            "helper-local prefix and suffix boundary anchors stay explicit through the direct string "
            "tests because the shared Phase 1 replay still focuses on replaceChar and memchrInv "
            "parity rather than dedicated prefix or suffix fixture fields, so strHasPrefix and "
            "str_has_prefix plus strHasSuffix and str_has_suffix plus strstarts plus strEndsWith "
            "and str_ends_with plus strends remain review-visible at the helper surface"
        ),
        "sysfs_review_summary": (
            "helper-local sysfs newline-aware equality and lookup-order anchors stay explicit "
            "through the direct string tests because the shared Phase 1 replay still carries no "
            "dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString "
            "and sysfs_match_string remain review-visible at the helper surface"
        ),
        "strnchr_review_summary": (
            "the direct counted-search and C-string search-length follow-up stays explicit because "
            "the shared Phase 1 replay still does not carry dedicated counted-search or search-length "
            "fixture keys, so strchr() or strrchr() full-length C-string searches, strpbrk() "
            "first-accepted-byte scanning, strspn() accepted-prefix scanning, strnchr() count-limited "
            "scanning, strnlen() count-clamped length, and strnchrNul() or strnchrnul() match-or-NUL "
            "boundary behavior remain owned by the helper-local anchors"
        ),
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
        "next_safe_step_note": (
            "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across "
            "the string review packet and this lane note unless dedicated shared sysfs fixture keys "
            "land; do not reopen missing closure-side validator names by default."
        ),
    },
}


class CheckError(Exception):
    pass


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    seen: set[str] = set()
    for key, value in pairs:
        if key in seen:
            raise CheckError(f"duplicate_key:{key}")
        seen.add(key)
        result[key] = value
    return result


def read_json_file(path: Path, label: str) -> object:
    if not path.exists():
        raise CheckError(f"{label}:missing")
    if not path.is_file():
        raise CheckError(f"{label}:not_file")
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except CheckError as exc:
        raise CheckError(f"{label}:{exc}") from exc
    except json.JSONDecodeError as exc:
        raise CheckError(
            f"{label}:json_decode_error:{exc.msg}:line={exc.lineno}:column={exc.colno}"
        ) from exc


def expect(condition: bool, issues: list[str], label: str) -> None:
    if not condition:
        issues.append(label)


def check_manifest(payload: object, issues: list[str]) -> None:
    if not isinstance(payload, dict):
        issues.append("manifest:not_json_object")
        return

    expect(payload.get("phase") == "Phase 1", issues, "manifest:phase")
    expect(payload.get("status") == "closed", issues, "manifest:status")
    expect(payload.get("helper_count") == len(EXPECTED_HELPERS), issues, "manifest:helper_count")
    expect(payload.get("helpers") == EXPECTED_HELPERS, issues, "manifest:helpers")

    lane = payload.get("lane_sequencing")
    if not isinstance(lane, dict):
        issues.append("manifest:lane_sequencing")
    else:
        expect(
            lane.get("shared_replay_parked_helpers") == EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
            issues,
            "manifest:shared_replay_helpers",
        )
        expect(
            lane.get("direct_anchor_followup_helpers") == EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
            issues,
            "manifest:direct_anchor_helpers",
        )
        expect(lane.get("rule_summary") == EXPECTED_RULE_SUMMARY, issues, "manifest:rule_summary")
        expect(
            lane.get("anti_overlap_rule") == EXPECTED_ANTI_OVERLAP_RULE,
            issues,
            "manifest:anti_overlap_rule",
        )

    review_anchors = payload.get("review_anchors")
    if not isinstance(review_anchors, dict):
        issues.append("manifest:review_anchors")
        return

    for helper, expected_fields in HELPER_EXPECTATIONS.items():
        actual_entry = review_anchors.get(helper)
        if not isinstance(actual_entry, dict):
            issues.append(f"manifest:missing_review_anchor={helper}")
            continue
        for field_name, expected_value in expected_fields.items():
            expect(
                actual_entry.get(field_name) == expected_value,
                issues,
                f"manifest:{helper}:{field_name}",
            )


def check_blockers(payload: object, issues: list[str]) -> None:
    if not isinstance(payload, dict):
        issues.append("blockers:not_json_object")
        return

    expect(payload.get("status") == "parked", issues, "blockers:status")

    lane = payload.get("lane_sequencing")
    if not isinstance(lane, dict):
        issues.append("blockers:lane_sequencing")
        return

    expect(lane.get("manifest") == str(MANIFEST_REL), issues, "blockers:manifest_path")
    expect(
        lane.get("shared_replay_parked_helper_count") == len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
        issues,
        "blockers:shared_replay_helper_count",
    )
    expect(
        lane.get("shared_replay_parked_helpers") == EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
        issues,
        "blockers:shared_replay_helpers",
    )
    expect(
        lane.get("direct_anchor_followup_helper_count") == len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
        issues,
        "blockers:direct_anchor_helper_count",
    )
    expect(
        lane.get("direct_anchor_followup_helpers") == EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
        issues,
        "blockers:direct_anchor_helpers",
    )
    expect(
        lane.get("anti_overlap_rule") == EXPECTED_ANTI_OVERLAP_RULE,
        issues,
        "blockers:anti_overlap_rule",
    )


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    try:
        manifest = read_json_file(root / MANIFEST_REL, "manifest")
    except CheckError as exc:
        issues.append(str(exc))
    else:
        check_manifest(manifest, issues)

    try:
        blockers = read_json_file(root / BLOCKERS_REL, "blockers")
    except CheckError as exc:
        issues.append(str(exc))
    else:
        check_blockers(blockers, issues)

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=fail")
        for issue in issues:
            print(f"PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUE={issue}")
        return 1

    print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass")
    print(f"PHASE1_DIRECT_ANCHOR_HELPER_COUNT={len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS)}")
    print(
        "PHASE1_DIRECT_ANCHOR_REVIEW_FIELD_COUNT="
        + str(sum(len(fields) for fields in HELPER_EXPECTATIONS.values()))
    )
    print(
        "PHASE1_DIRECT_ANCHOR_MANIFEST="
        + str(MANIFEST_REL)
    )
    print(
        "PHASE1_DIRECT_ANCHOR_BLOCKERS="
        + str(BLOCKERS_REL)
    )
    return 0


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def good_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": list(EXPECTED_HELPERS),
        "lane_sequencing": {
            "shared_replay_parked_helpers": list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
            "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "review_anchors": {
            helper: dict(fields) for helper, fields in HELPER_EXPECTATIONS.items()
        },
    }


def good_blockers() -> dict[str, object]:
    return {
        "status": "parked",
        "lane_sequencing": {
            "manifest": str(MANIFEST_REL),
            "shared_replay_parked_helper_count": len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
            "shared_replay_parked_helpers": list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
            "direct_anchor_followup_helper_count": len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
            "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
    }


def build_root(root: Path) -> Path:
    write_json(root / MANIFEST_REL, good_manifest())
    write_json(root / BLOCKERS_REL, good_blockers())
    return root


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def expect_failure(root: Path, expected_prefix: str) -> bool:
    return any(issue.startswith(expected_prefix) for issue in collect_issues(root))


def run_self_test() -> int:
    failed: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_direct_anchor_manifest_gate_") as tmp_dir:
        base = Path(tmp_dir)

        good_root = build_root(base / "good")
        if run_check(good_root) != 0:
            failed.append("good")

        missing_manifest_root = build_root(base / "missing_manifest")
        (missing_manifest_root / MANIFEST_REL).unlink()
        if not expect_failure(missing_manifest_root, "manifest:missing"):
            failed.append("missing_manifest")

        manifest_not_file_root = build_root(base / "manifest_not_file")
        (manifest_not_file_root / MANIFEST_REL).unlink()
        (manifest_not_file_root / MANIFEST_REL).mkdir(parents=True)
        if not expect_failure(manifest_not_file_root, "manifest:not_file"):
            failed.append("manifest_not_file")

        manifest_bad_json_root = build_root(base / "manifest_bad_json")
        write_text(manifest_bad_json_root / MANIFEST_REL, "{\n")
        if not expect_failure(manifest_bad_json_root, "manifest:json_decode_error:"):
            failed.append("manifest_bad_json")

        manifest_dup_key_root = build_root(base / "manifest_dup_key")
        write_text(
            manifest_dup_key_root / MANIFEST_REL,
            '{\n  "phase": "Phase 1",\n  "phase": "duplicate"\n}\n',
        )
        if not expect_failure(manifest_dup_key_root, "manifest:duplicate_key:phase"):
            failed.append("manifest_dup_key")

        manifest_direct_anchor_root = build_root(base / "manifest_direct_anchor")
        payload = good_manifest()
        payload["lane_sequencing"]["direct_anchor_followup_helpers"] = ["tools/lib/bitmap.zig"]
        write_json(manifest_direct_anchor_root / MANIFEST_REL, payload)
        if not expect_failure(manifest_direct_anchor_root, "manifest:direct_anchor_helpers"):
            failed.append("manifest_direct_anchor")

        manifest_bitmap_root = build_root(base / "manifest_bitmap")
        payload = good_manifest()
        payload["review_anchors"]["tools/lib/bitmap.zig"]["review_packet_summary"] = "drift"
        write_json(manifest_bitmap_root / MANIFEST_REL, payload)
        if not expect_failure(
            manifest_bitmap_root,
            "manifest:tools/lib/bitmap.zig:review_packet_summary",
        ):
            failed.append("manifest_bitmap")

        manifest_find_bit_root = build_root(base / "manifest_find_bit")
        payload = good_manifest()
        payload["review_anchors"]["tools/lib/find_bit.zig"]["tail_inclusive_boundary_fixture_keys"] = [
            "tail_inclusive_boundary_next"
        ]
        write_json(manifest_find_bit_root / MANIFEST_REL, payload)
        if not expect_failure(
            manifest_find_bit_root,
            "manifest:tools/lib/find_bit.zig:tail_inclusive_boundary_fixture_keys",
        ):
            failed.append("manifest_find_bit")

        manifest_rbtree_root = build_root(base / "manifest_rbtree")
        payload = good_manifest()
        payload["review_anchors"]["tools/lib/rbtree.zig"]["cached_leftmost_fixture_keys"] = []
        write_json(manifest_rbtree_root / MANIFEST_REL, payload)
        if not expect_failure(
            manifest_rbtree_root,
            "manifest:tools/lib/rbtree.zig:cached_leftmost_fixture_keys",
        ):
            failed.append("manifest_rbtree")

        manifest_string_root = build_root(base / "manifest_string")
        payload = good_manifest()
        payload["review_anchors"]["tools/lib/string.zig"]["parity_fixture_keys"] = ["strtobool_y"]
        write_json(manifest_string_root / MANIFEST_REL, payload)
        if not expect_failure(
            manifest_string_root,
            "manifest:tools/lib/string.zig:parity_fixture_keys",
        ):
            failed.append("manifest_string")

        missing_blockers_root = build_root(base / "missing_blockers")
        (missing_blockers_root / BLOCKERS_REL).unlink()
        if not expect_failure(missing_blockers_root, "blockers:missing"):
            failed.append("missing_blockers")

        blockers_not_file_root = build_root(base / "blockers_not_file")
        (blockers_not_file_root / BLOCKERS_REL).unlink()
        (blockers_not_file_root / BLOCKERS_REL).mkdir(parents=True)
        if not expect_failure(blockers_not_file_root, "blockers:not_file"):
            failed.append("blockers_not_file")

        blockers_bad_json_root = build_root(base / "blockers_bad_json")
        write_text(blockers_bad_json_root / BLOCKERS_REL, "{\n")
        if not expect_failure(blockers_bad_json_root, "blockers:json_decode_error:"):
            failed.append("blockers_bad_json")

        blockers_dup_key_root = build_root(base / "blockers_dup_key")
        write_text(
            blockers_dup_key_root / BLOCKERS_REL,
            '{\n  "status": "parked",\n  "status": "duplicate"\n}\n',
        )
        if not expect_failure(blockers_dup_key_root, "blockers:duplicate_key:status"):
            failed.append("blockers_dup_key")

        blockers_direct_anchor_root = build_root(base / "blockers_direct_anchor")
        payload = good_blockers()
        payload["lane_sequencing"]["direct_anchor_followup_helpers"] = ["tools/lib/string.zig"]
        write_json(blockers_direct_anchor_root / BLOCKERS_REL, payload)
        if not expect_failure(blockers_direct_anchor_root, "blockers:direct_anchor_helpers"):
            failed.append("blockers_direct_anchor")

        blockers_overlap_rule_root = build_root(base / "blockers_overlap_rule")
        payload = good_blockers()
        payload["lane_sequencing"]["anti_overlap_rule"] = "drift"
        write_json(blockers_overlap_rule_root / BLOCKERS_REL, payload)
        if not expect_failure(blockers_overlap_rule_root, "blockers:anti_overlap_rule"):
            failed.append("blockers_overlap_rule")

    if failed:
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=fail")
        for label in failed:
            print(f"PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST_FAILED_CASE={label}")
        return 1

    print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass")
    print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST_CASE_COUNT=16")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 1 direct-anchor helper manifest packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_root(args.write_sample_root.resolve())
        return 0
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())

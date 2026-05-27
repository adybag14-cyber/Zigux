#!/usr/bin/env python3
"""Validate the current Phase 1 closure note against the live reminder packet."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
FIND_BIT_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")
RBTREE_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-rbtree-review-packet.py")
DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
DIRECT_ANCHOR_MANIFEST_GATE_REL = Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")
ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")
BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-bitmap-direct-anchors.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
TESTS_README_REL = Path("zigux/tests/README.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
PHASE1_HELPERS_REPLAY_REL = Path("zigux/tests/phase1_helpers.zig")
PHASE1_HELPERS_BUILD_REL = Path("zigux/tests/phase1_helpers_build.zig")
PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
ZIGUX_MAKEFILE_REL = Path("zigux/Makefile")
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
    STRING_REVIEW_CHECKER_REL,
    FIND_BIT_REVIEW_CHECKER_REL,
    RBTREE_REVIEW_CHECKER_REL,
    DIRECT_OWNER_CHECKER_REL,
    DIRECT_ANCHOR_MANIFEST_GATE_REL,
    ROUTE_SUMMARY_CHECKER_REL,
    BENCH_CHECKER_REL,
    FIND_BIT_BENCH_ANCHOR_CHECKER_REL,
    BITMAP_DIRECT_ANCHOR_CHECKER_REL,
    SHARED_REMINDER_CHECKER_REL,
    TESTS_README_REL,
    TESTS_BUILD_REL,
    PHASE1_HELPERS_REPLAY_REL,
    PHASE1_HELPERS_BUILD_REL,
    PHASE1_SMOKE_REL,
    WORKFLOW_REL,
    MANIFEST_REL,
    ZIGUX_MAKEFILE_REL,
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

EXPECTED_LANE_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers "
    "reopen only for their existing helper-local anchors or already-committed shared fixture keys."
)

EXPECTED_CLOSURE_MARKERS = {
    "status": "`PHASE1_STATUS=parked`",
    "restore_state": "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "helper_count": "`PHASE1_HELPER_COUNT=13`",
    "reminder_packet": "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
    "gap_packet": "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "closure_validator": "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "route_summary_guard": "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    "shared_tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "validator_state": "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "bitmap_direct_review": "`PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet because the shared Phase 1 replay still only owns allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer handling, and partial-window xor replay, so current master keeps fill-tail clamp, raw copy alias, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, complement-tail masking, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage review-visible at the helper surface`",
    "bitmap_unit_review": "`PHASE1_BITMAP_UNIT_REVIEW=bitmap multiword-tail xorBits behavior still lets callers clamp the last word without leaking out-of-range bits into the asserted view`",
    "bitmap_empty_unit_review": "`PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap_scnprintf leaves a non-empty caller buffer untouched when no bits are set, matching both the direct Zig unit test and the committed parity fixture`",
    "bitmap_final_partial_word_review": "`PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor so setRange and clearRange clamp trailing partial-word masks to the requested tail window instead of spilling work beyond it`",
    "bitmap_linux_alias_review": "`PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface`",
    "string_sysfs_review": "`PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`",
    "string_review_guard": "`PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py exact-checks helper-local string anchors plus the committed replaceChar and current string fixture packet across the helper, closure note, lane note, manifest, and fixture`",
    "string_memtostr_review": "Current `master` now also spells the helper-local `memtostr()`, `memtostrPad()`, and `memtostr_pad()` anchors directly in the shipped manifest-backed string review packet beside the `memcpyAndPad()`, `memcpy_and_pad()`, `strtomem()`, and `strtomem_pad()` byte-copy anchors. Keep those byte-copy and pad tests helper-local review evidence rather than shared-fixture or validator-owned requirements until dedicated fixture keys land.",
    "find_bit_bench_guard": "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
    "rbtree_bench_guard": "`PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",
    "find_bit_bench_anchor_guard": "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",
    "find_bit_review_guard": "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",
    "rbtree_review_guard": "`PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py exact-checks helper-local rbtree anchors plus the committed duplicate-search and cached-leftmost replay packet across the helper, closure note, lane note, manifest, fixture, and shared smoke route`",
    "direct_anchor_manifest_gate": "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",
    "next_step": "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
}

FORBIDDEN_CLOSURE_MARKERS = {
    "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`",
}

EXPECTED_MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase3-validate:",
    "phase3:",
    "phase4-validate:",
    "phase6-validate:",
    "phase8-validate:",
    "phase8-exec-cmd-test:",
    "phase8-test:",
    "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
    "phase10-validate:",
    "phase10-test:",
    "phase10: phase10-validate phase10-test",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
    "phase14-validate:",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
)

EXPECTED_FIND_BIT_REVIEW_ANCHORS = {
    "andnot_scan_entrypoint_contract": "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.",
    "review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped and tail-inclusive-boundary find_bit replay, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, single-word tail inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master",
    "next_safe_step_note": "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families.",
}

EXPECTED_RBTREE_REVIEW_ANCHORS = {
    "phase1_helper_replay_anchor": 'test "phase1 host-tools smoke exercises live helper behavior"',
    "shared_replay_summary": "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, and exact cached-leftmost-return witnesses for rbtree, while the current shared host-tools smoke replay now rechecks duplicate-range iteration plus the exact `cached_leftmost_return_serials` cached-root leftmost-return sequence on current master",
    "cached_root_direct_review_summary": "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors, while the exact `cached_leftmost_return_serials` witness now stays aligned across the helper-local tests, the shared host-tools smoke replay, and the committed fixture",
    "ordered_alias_anchor": 'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
    "low_level_alias_anchor": 'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
    "cached_root_alias_anchor": 'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
    "cached_leftmost_fixture_keys": ["cached_leftmost_return_serials"],
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
    "review_packet_summary": "the current shared host-tools smoke replay keeps duplicate-range iteration and the exact `cached_leftmost_return_serials` cached-root leftmost-return witness visible for rbtree, while the committed Phase 1 fixture still carries the exact traversal, detached-node, duplicate-search, and cached-leftmost-return witnesses; direct helper-local anchors continue to own cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed paths that the shared smoke route does not replay exactly",
    "next_safe_step_note": "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; the ordered Linux-style alias proof, dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors until another committed cached-root field lands.",
}

EXPECTED_BITMAP_REVIEW_ANCHORS = {
    "final_partial_word_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
    "equal_fast_path_anchor": 'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
    "or_window_anchor": 'test "bitmap or keeps caller-selected bit window"',
    "or_multiword_tail_anchor": 'test "bitmap or across a multiword tail still lets callers clamp the last word"',
    "weighted_tail_count_anchor": 'test "bitmap weighted or and xor clamp counts to the declared tail window"',
    "scnprintf_cross_word_anchor": 'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    "empty_buffer_anchor": 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
    "copy_zero_and_aligned_anchors": [
        'test "bitmap copy and extend handles zero and aligned counts"',
        'test "bitmap copy helpers keep zero-sized destination views untouched"',
    ],
    "zero_bit_noop_anchor": 'test "bitmap zero-bit logical helpers stay explicit"',
    "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
    "review_packet_summary": "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while current master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage.",
    "next_safe_step_note": "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side or validator-route cue names by default.",
}

EXPECTED_STRING_REVIEW_ANCHORS = {
    "sysfs_review_summary": "helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface",
    "counted_search_review_anchors": [
        'test "strchr mirrors full-length C-string searches"',
        'test "strrchr finds the last in-range match with C-string semantics"',
        'test "strpbrk finds the first accepted byte with C-string semantics"',
        'test "strspn counts the accepted prefix with C-string semantics"',
        'test "strcspn counts until the first rejected byte with C-string semantics"',
        'test "strnchr honors count and C-string boundaries"',
        'test "strnlen honors count and C-string boundaries"',
        'test "strnchrNul returns the first match, NUL, or count boundary"',
        'test "strchrNul and strchrnul return the first match or terminator boundary"',
    ],
    "strcmp_review_anchors": [
        'test "strcmp mirrors C-string lexical ordering"',
        'test "strcmp stops at embedded NULs and length mismatches"',
    ],
    "strcmp_review_summary": "helper-local lexical-compare anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strcmp() fixture keys, so lexical ordering and embedded-NUL length-mismatch behavior remain review-visible at the helper surface",
    "search_length_review_anchors": [
        'test "strchr mirrors full-length C-string searches"',
        'test "strrchr finds the last in-range match with C-string semantics"',
        'test "strchr and strrchr return the terminator index when searching for NUL"',
        'test "strlen honors C-string boundaries"',
        'test "strnlen honors count and C-string boundaries"',
        'test "strchrNul and strchrnul return the first match or terminator boundary"',
    ],
    "search_length_review_summary": "helper-local search-and-length boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated search-length fixture keys, so strchr() or strrchr() boundary scans, terminator-index searches, strchrNul() or strchrnul() match-or-terminator boundaries, and strlen() or strnlen() length boundaries remain review-visible at the helper surface",
    "strnchr_review_summary": "the direct counted-search and C-string search-length follow-up stays explicit because the shared Phase 1 replay still does not carry dedicated counted-search or search-length fixture keys, so strchr() or strrchr() full-length C-string searches, strpbrk() first-accepted-byte scanning, strspn() accepted-prefix scanning, strcspn() rejected-byte scanning, strnchr() count-limited scanning, strnlen() count-clamped length, strnchrNul() or strnchrnul() match-or-NUL boundary behavior, and strchrNul() or strchrnul() match-or-terminator boundaries remain owned by the helper-local anchors",
    "next_safe_step_note": "If this helper lane reopens, keep the helper-local strlcat, sysfs, case-insensitive compare, and match-or-terminator review anchors aligned across the string review packet and this lane note unless dedicated shared fixture keys land; do not reopen missing closure-side validator names by default.",
}

DELEGATED_CHECKERS = (
    (STRING_REVIEW_CHECKER_REL, "phase1-string-review-packet"),
    (FIND_BIT_REVIEW_CHECKER_REL, "phase1-find-bit-review-packet"),
    (RBTREE_REVIEW_CHECKER_REL, "phase1-rbtree-review-packet"),
    (DIRECT_OWNER_CHECKER_REL, "phase1-direct-owner-markers"),
    (DIRECT_ANCHOR_MANIFEST_GATE_REL, "phase1-direct-anchor-manifest-gate"),
    (ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts"),
    (BENCH_CHECKER_REL, "phase1-bench"),
    (FIND_BIT_BENCH_ANCHOR_CHECKER_REL, "phase1-find-bit-bench-anchors"),
    (BITMAP_DIRECT_ANCHOR_CHECKER_REL, "phase1-bitmap-direct-anchors"),
    (SHARED_REMINDER_CHECKER_REL, "phase1-shared-reminder-packet"),
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json_with_duplicate_tracking(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(collect_duplicate_json_key_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            paths.extend(collect_duplicate_json_key_paths(item, prefix))
    return paths


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def require_expected_mapping(prefix: str, actual: object, expected: dict[str, object]) -> list[str]:
    if not isinstance(actual, dict):
        return [f"{prefix}:expected=dict:actual={type(actual).__name__}"]
    failures: list[str] = []
    for key, expected_value in expected.items():
        failures.extend(require_exact_value(f"{prefix}.{key}", actual.get(key), expected_value))
    return failures


def run_checker(root: Path, script_rel: Path, label: str) -> list[str]:
    proc = subprocess.run(
        [sys.executable, str(root / script_rel), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return []
    output = (proc.stdout + proc.stderr).splitlines() or [f"{label}:checker_failed:returncode={proc.returncode}"]
    return [f"delegated:{label}:{line}" for line in output]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    for label, marker in EXPECTED_CLOSURE_MARKERS.items():
        failures.extend(require_exact_occurrence(closure_text, f"{PHASE1_CLOSURE_REL.as_posix()}:{label}", marker))
    for marker in FORBIDDEN_CLOSURE_MARKERS:
        count = closure_text.count(marker)
        if count:
            failures.append(f"{PHASE1_CLOSURE_REL.as_posix()}:forbidden_marker:actual_count={count}:{marker}")

    makefile_text = load_text(root, ZIGUX_MAKEFILE_REL)
    for marker in EXPECTED_MAKEFILE_MARKERS:
        failures.extend(require_exact_occurrence(makefile_text, f"{ZIGUX_MAKEFILE_REL.as_posix()}:required", marker))
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        count = makefile_text.count(marker)
        if count:
            failures.append(f"{ZIGUX_MAKEFILE_REL.as_posix()}:forbidden_marker:actual_count={count}:{marker}")

    try:
        manifest = load_json_with_duplicate_tracking(load_text(root, MANIFEST_REL))
    except json.JSONDecodeError as exc:
        return [f"{MANIFEST_REL.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    duplicate_manifest_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_manifest_paths:
        return [
            f"{MANIFEST_REL.as_posix()}:duplicate_json_key:{path}"
            for path in duplicate_manifest_paths
        ]

    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:phase", manifest.get("phase"), "Phase 1"))
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:status", manifest.get("status"), "closed"))
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:helper_count", manifest.get("helper_count"), len(EXPECTED_HELPERS)))
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:helpers", manifest.get("helpers"), EXPECTED_HELPERS))

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        return [f"{MANIFEST_REL.as_posix()}:lane_sequencing:expected=dict:actual={type(lane_sequencing).__name__}"]
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:lane_sequencing.shared_replay_parked_helpers", lane_sequencing.get("shared_replay_parked_helpers"), EXPECTED_SHARED_REPLAY_PARKED_HELPERS))
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:lane_sequencing.direct_anchor_followup_helpers", lane_sequencing.get("direct_anchor_followup_helpers"), EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS))
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:lane_sequencing.rule_summary", lane_sequencing.get("rule_summary"), EXPECTED_LANE_RULE_SUMMARY))
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:lane_sequencing.anti_overlap_rule", lane_sequencing.get("anti_overlap_rule"), EXPECTED_ANTI_OVERLAP_RULE))

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict:actual={type(review_anchors).__name__}"]
    failures.extend(require_expected_mapping(f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig", review_anchors.get("tools/lib/bitmap.zig"), EXPECTED_BITMAP_REVIEW_ANCHORS))
    failures.extend(require_expected_mapping(f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig", review_anchors.get("tools/lib/find_bit.zig"), EXPECTED_FIND_BIT_REVIEW_ANCHORS))
    failures.extend(require_expected_mapping(f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig", review_anchors.get("tools/lib/rbtree.zig"), EXPECTED_RBTREE_REVIEW_ANCHORS))
    failures.extend(require_expected_mapping(f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/string.zig", review_anchors.get("tools/lib/string.zig"), EXPECTED_STRING_REVIEW_ANCHORS))

    for script_rel, label in DELEGATED_CHECKERS:
        failures.extend(run_checker(root, script_rel, label))

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_checker_stub(path: Path, ok: bool = True) -> None:
    write_text(
        path,
        "#!/usr/bin/env python3\nimport sys\nprint('stub:ok' if %s else 'stub:failure')\nraise SystemExit(%s)\n"
        % ("True" if ok else "False", "0" if ok else "1"),
    )


def make_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root / relative_path, f"fixture for {relative_path.as_posix()}\n")

    write_text(root / PHASE1_CLOSURE_REL, "# Phase 1 Closure\n\n" + "\n".join(EXPECTED_CLOSURE_MARKERS.values()) + "\n")
    write_text(root / ZIGUX_MAKEFILE_REL, "\n".join(EXPECTED_MAKEFILE_MARKERS) + "\n")
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": len(EXPECTED_HELPERS),
                "helpers": EXPECTED_HELPERS,
                "lane_sequencing": {
                    "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
                    "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
                    "rule_summary": EXPECTED_LANE_RULE_SUMMARY,
                    "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
                },
                "review_anchors": {
                    "tools/lib/bitmap.zig": EXPECTED_BITMAP_REVIEW_ANCHORS,
                    "tools/lib/find_bit.zig": EXPECTED_FIND_BIT_REVIEW_ANCHORS,
                    "tools/lib/rbtree.zig": EXPECTED_RBTREE_REVIEW_ANCHORS,
                    "tools/lib/string.zig": EXPECTED_STRING_REVIEW_ANCHORS,
                },
            },
            indent=2,
        )
        + "\n",
    )

    for checker_rel, _ in DELEGATED_CHECKERS:
        make_checker_stub(root / checker_rel)


def mutate_remove_review_key(root: Path, helper: str, key: str) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    del manifest["review_anchors"][helper][key]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def mutate_bad_review_value(root: Path, helper: str, key: str) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["review_anchors"][helper][key] = "drifted value"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def insert_duplicate_manifest_line(root: Path, needle: str, duplicate_line: str) -> None:
    manifest_path = root / MANIFEST_REL
    text = manifest_path.read_text(encoding="utf-8")
    manifest_path.write_text(text.replace(needle, duplicate_line + "\n" + needle, 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_restore_state", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["restore_state"] + "\n", "", 1))),
        ("old_next_step_marker", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["next_step"], "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface against the restored closure note and closure validator`", 1))),
        ("forbidden_old_marker", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL) + "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`\n")),
        ("missing_find_bit_bench_guard", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["find_bit_bench_guard"] + "\n", "", 1))),
        ("missing_rbtree_bench_guard", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["rbtree_bench_guard"] + "\n", "", 1))),
        ("missing_find_bit_bench_anchor_guard", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["find_bit_bench_anchor_guard"] + "\n", "", 1))),
        ("missing_find_bit_review_guard", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["find_bit_review_guard"] + "\n", "", 1))),
        ("stale_find_bit_review_guard", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["find_bit_review_guard"], "`PHASE1_FIND_BIT_REVIEW_GUARD=drifted review guard marker`", 1))),
        ("missing_rbtree_review_guard", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["rbtree_review_guard"] + "\n", "", 1))),
        ("stale_rbtree_review_guard", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["rbtree_review_guard"], "`PHASE1_RBTREE_REVIEW_GUARD=drifted review guard marker`", 1))),
        ("missing_direct_anchor_manifest_gate_marker", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["direct_anchor_manifest_gate"] + "\n", "", 1))),
        ("stale_direct_anchor_manifest_gate_marker", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["direct_anchor_manifest_gate"], "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=drifted direct anchor manifest gate marker`", 1))),
        ("missing_route_summary_guard", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["route_summary_guard"] + "\n", "", 1))),
        ("missing_shared_tests_route", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["shared_tests_route"] + "\n", "", 1))),
        ("missing_validator_state", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["validator_state"] + "\n", "", 1))),
        ("missing_bitmap_direct_review", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["bitmap_direct_review"] + "\n", "", 1))),
        ("stale_bitmap_direct_review", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["bitmap_direct_review"], "`PHASE1_BITMAP_DIRECT_REVIEW=drifted bitmap direct review marker`", 1))),
        ("missing_bitmap_unit_review", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["bitmap_unit_review"] + "\n", "", 1))),
        ("stale_bitmap_unit_review", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["bitmap_unit_review"], "`PHASE1_BITMAP_UNIT_REVIEW=drifted bitmap unit marker`", 1))),
        ("missing_bitmap_empty_unit_review", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["bitmap_empty_unit_review"] + "\n", "", 1))),
        ("stale_bitmap_empty_unit_review", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["bitmap_empty_unit_review"], "`PHASE1_BITMAP_EMPTY_UNIT_REVIEW=drifted bitmap empty marker`", 1))),
        ("missing_bitmap_final_partial_word_review", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["bitmap_final_partial_word_review"] + "\n", "", 1))),
        ("stale_bitmap_final_partial_word_review", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["bitmap_final_partial_word_review"], "`PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=drifted bitmap final partial-word marker`", 1))),
        ("missing_bitmap_linux_alias_review", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["bitmap_linux_alias_review"] + "\n", "", 1))),
        ("stale_bitmap_linux_alias_review", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["bitmap_linux_alias_review"], "`PHASE1_BITMAP_LINUX_ALIAS_REVIEW=drifted bitmap Linux-style alias marker`", 1))),
        ("stale_string_sysfs_review", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["string_sysfs_review"], "`PHASE1_STRING_SYSFS_REVIEW=drifted string sysfs review marker`", 1))),
        ("missing_string_review_guard", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["string_review_guard"] + "\n", "", 1))),
        ("stale_string_review_guard", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["string_review_guard"], "`PHASE1_STRING_REVIEW_GUARD=drifted string review guard marker`", 1))),
        ("missing_string_memtostr_review", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["string_memtostr_review"] + "\n", "", 1))),
        ("stale_string_memtostr_review", lambda root: write_text(root / PHASE1_CLOSURE_REL, load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS["string_memtostr_review"], "Current `master` now spells a drifted memtostr reminder paragraph.", 1))),
        ("bad_helper_count", lambda root: write_text(root / MANIFEST_REL, json.dumps({**json.loads(load_text(root, MANIFEST_REL)), "helper_count": 99}, indent=2) + "\n")),
        ("stale_lane_rule_summary", lambda root: write_text(root / MANIFEST_REL, json.dumps({**json.loads(load_text(root, MANIFEST_REL)), "lane_sequencing": {**json.loads(load_text(root, MANIFEST_REL))["lane_sequencing"], "rule_summary": "drifted rule summary"}}, indent=2) + "\n")),
        ("stale_anti_overlap_rule", lambda root: write_text(root / MANIFEST_REL, json.dumps({**json.loads(load_text(root, MANIFEST_REL)), "lane_sequencing": {**json.loads(load_text(root, MANIFEST_REL))["lane_sequencing"], "anti_overlap_rule": "drifted anti-overlap rule"}}, indent=2) + "\n")),
        ("duplicate_manifest_helper_count", lambda root: insert_duplicate_manifest_line(root, '  "helper_count": 13,', '  "helper_count": 99,')),
        ("duplicate_manifest_lane_rule_summary", lambda root: insert_duplicate_manifest_line(root, f'    "rule_summary": "{EXPECTED_LANE_RULE_SUMMARY}",', '    "rule_summary": "drifted rule summary",')),
        ("missing_find_bit_andnot_contract", lambda root: mutate_remove_review_key(root, "tools/lib/find_bit.zig", "andnot_scan_entrypoint_contract")),
        ("stale_find_bit_review_summary", lambda root: mutate_bad_review_value(root, "tools/lib/find_bit.zig", "review_packet_summary")),
        ("stale_find_bit_next_safe_step_note", lambda root: mutate_bad_review_value(root, "tools/lib/find_bit.zig", "next_safe_step_note")),
        ("missing_rbtree_cached_root_alias_anchor", lambda root: mutate_remove_review_key(root, "tools/lib/rbtree.zig", "cached_root_alias_anchor")),
        ("stale_rbtree_shared_replay_summary", lambda root: mutate_bad_review_value(root, "tools/lib/rbtree.zig", "shared_replay_summary")),
        ("stale_rbtree_cached_root_direct_review_summary", lambda root: mutate_bad_review_value(root, "tools/lib/rbtree.zig", "cached_root_direct_review_summary")),
        ("missing_bitmap_or_window_anchor", lambda root: mutate_remove_review_key(root, "tools/lib/bitmap.zig", "or_window_anchor")),
        ("missing_bitmap_copy_raw_alias_anchor", lambda root: mutate_remove_review_key(root, "tools/lib/bitmap.zig", "copy_raw_alias_anchor")),
        ("missing_bitmap_final_partial_word_anchor", lambda root: mutate_remove_review_key(root, "tools/lib/bitmap.zig", "final_partial_word_anchor")),
        ("missing_bitmap_linux_alias_anchor", lambda root: mutate_remove_review_key(root, "tools/lib/bitmap.zig", "linux_alias_anchor")),
        ("stale_bitmap_empty_buffer_anchor", lambda root: mutate_bad_review_value(root, "tools/lib/bitmap.zig", "empty_buffer_anchor")),
        ("stale_bitmap_next_safe_step_note", lambda root: mutate_bad_review_value(root, "tools/lib/bitmap.zig", "next_safe_step_note")),
        ("stale_string_sysfs_review_summary", lambda root: mutate_bad_review_value(root, "tools/lib/string.zig", "sysfs_review_summary")),
        ("stale_string_strcmp_review_anchors", lambda root: mutate_bad_review_value(root, "tools/lib/string.zig", "strcmp_review_anchors")),
        ("stale_string_strcmp_review_summary", lambda root: mutate_bad_review_value(root, "tools/lib/string.zig", "strcmp_review_summary")),
        ("stale_string_search_length_review_anchors", lambda root: mutate_bad_review_value(root, "tools/lib/string.zig", "search_length_review_anchors")),
        ("stale_string_search_length_review_summary", lambda root: mutate_bad_review_value(root, "tools/lib/string.zig", "search_length_review_summary")),
        ("stale_string_counted_search_review_anchors", lambda root: mutate_bad_review_value(root, "tools/lib/string.zig", "counted_search_review_anchors")),
        ("stale_string_strnchr_review_summary", lambda root: mutate_bad_review_value(root, "tools/lib/string.zig", "strnchr_review_summary")),
        ("stale_string_next_safe_step_note", lambda root: mutate_bad_review_value(root, "tools/lib/string.zig", "next_safe_step_note")),
        ("missing_string_checker", lambda root: (root / STRING_REVIEW_CHECKER_REL).unlink()),
        ("failing_string_checker", lambda root: make_checker_stub(root / STRING_REVIEW_CHECKER_REL, ok=False)),
        ("missing_find_bit_review_checker", lambda root: (root / FIND_BIT_REVIEW_CHECKER_REL).unlink()),
        ("missing_rbtree_review_checker", lambda root: (root / RBTREE_REVIEW_CHECKER_REL).unlink()),
        ("missing_find_bit_bench_anchor_checker", lambda root: (root / FIND_BIT_BENCH_ANCHOR_CHECKER_REL).unlink()),
        ("failing_find_bit_bench_anchor_checker", lambda root: make_checker_stub(root / FIND_BIT_BENCH_ANCHOR_CHECKER_REL, ok=False)),
        ("missing_bitmap_direct_anchor_checker", lambda root: (root / BITMAP_DIRECT_ANCHOR_CHECKER_REL).unlink()),
        ("failing_bitmap_direct_anchor_checker", lambda root: make_checker_stub(root / BITMAP_DIRECT_ANCHOR_CHECKER_REL, ok=False)),
        ("missing_direct_anchor_manifest_gate_checker", lambda root: (root / DIRECT_ANCHOR_MANIFEST_GATE_REL).unlink()),
        ("failing_direct_anchor_manifest_gate_checker", lambda root: make_checker_stub(root / DIRECT_ANCHOR_MANIFEST_GATE_REL, ok=False)),
        ("failing_find_bit_review_checker", lambda root: make_checker_stub(root / FIND_BIT_REVIEW_CHECKER_REL, ok=False)),
        ("failing_rbtree_review_checker", lambda root: make_checker_stub(root / RBTREE_REVIEW_CHECKER_REL, ok=False)),
        ("failing_direct_owner_checker", lambda root: make_checker_stub(root / DIRECT_OWNER_CHECKER_REL, ok=False)),
        ("missing_makefile_marker", lambda root: write_text(root / ZIGUX_MAKEFILE_REL, load_text(root, ZIGUX_MAKEFILE_REL).replace("phase12-test:\n", "", 1))),
        ("missing_phase8_exec_cmd_route", lambda root: write_text(root / ZIGUX_MAKEFILE_REL, load_text(root, ZIGUX_MAKEFILE_REL).replace("phase8-exec-cmd-test:\n", "", 1))),
        ("forbidden_phase1_makefile_route", lambda root: write_text(root / ZIGUX_MAKEFILE_REL, load_text(root, ZIGUX_MAKEFILE_REL) + "phase1-validate:\n")),
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
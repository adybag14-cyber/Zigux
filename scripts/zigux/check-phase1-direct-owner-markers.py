#!/usr/bin/env python3
"""Guard the Phase 1 direct-owner marker packet against lane-note and helper drift."""

from __future__ import annotations

import argparse
import json
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


LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
TESTS_README_REL = Path("zigux/tests/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
PHASE1_CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")
FIND_BIT_HELPER_REL = Path("tools/lib/find_bit.zig")
RBTREE_HELPER_REL = Path("tools/lib/rbtree.zig")
STRING_HELPER_REL = Path("tools/lib/string.zig")

REQUIRED_FILES = (
    LANE_NOTE_REL,
    DOCS_ROOT_REL,
    PHASE1_CLOSURE_REL,
    REVIEW_CHECKLIST_REL,
    TESTS_README_REL,
    SCRIPTS_README_REL,
    PHASE1_CLOSURE_VALIDATOR_REL,
    SHARED_REMINDER_CHECKER_REL,
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
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)
EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers "
    "reopen only for their existing helper-local anchors or already-committed shared fixture keys."
)

EXPECTED_BITMAP_REVIEW_PACKET_SUMMARY = (
    "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, "
    "scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while current "
    "master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw "
    "copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend "
    "handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit "
    "coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, "
    "out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, "
    "multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only "
    "and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style "
    "alias mirror coverage, and allocator optional-reset coverage."
)
EXPECTED_BITMAP_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor "
    "drift inside the current helper-local packet or committed shared replay drift in the bitmap "
    "parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, "
    "cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and "
    "or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical "
    "short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side "
    "or validator-route cue names by default."
)
EXPECTED_FIND_BIT_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor "
    "drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, "
    "past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage "
    "including the shipped andnot scan entry points, or tail-word skip anchors, or committed "
    "tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues "
    "or neighboring helper families."
)
EXPECTED_FIND_BIT_ANDNOT_SCAN_ENTRYPOINTS = [
    "findFirstAndNotBit",
    "find_first_andnot_bit",
    "_find_first_andnot_bit",
    "findNextAndNotBit",
    "find_next_andnot_bit",
    "_find_next_andnot_bit",
]
EXPECTED_FIND_BIT_ANDNOT_SCAN_ENTRYPOINT_CONTRACT = (
    "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording."
)
EXPECTED_RBTREE_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep the already-landed shared-replay promotion for "
    "`cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and "
    "direct cached-root anchors; the ordered Linux-style alias proof, dedicated "
    "`low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, "
    "cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by "
    "direct helper-local anchors until another committed cached-root field lands."
)
EXPECTED_RBTREE_SHARED_REPLAY_SUMMARY = (
    "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, "
    "and exact cached-leftmost-return witnesses for rbtree, while the current shared host-tools "
    "smoke replay now rechecks duplicate-range iteration plus the exact `cached_leftmost_return_serials` "
    "cached-root leftmost-return sequence on current master"
)
EXPECTED_RBTREE_CACHED_ROOT_DIRECT_REVIEW_SUMMARY = (
    "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, "
    "detach, and reseed behavior remain owned by direct helper-local anchors, while the exact "
    "`cached_leftmost_return_serials` witness now stays aligned across the helper-local tests, "
    "the shared host-tools smoke replay, and the committed fixture"
)
EXPECTED_RBTREE_REVIEW_PACKET_SUMMARY = (
    "the current shared host-tools smoke replay keeps duplicate-range iteration and the exact "
    "`cached_leftmost_return_serials` cached-root leftmost-return witness visible for rbtree, "
    "while the committed Phase 1 fixture still carries the exact traversal, detached-node, "
    "duplicate-search, and cached-leftmost-return witnesses; direct helper-local anchors continue "
    "to own cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, "
    "replacement, detach, and reseed paths that the shared smoke route does not replay exactly"
)
EXPECTED_RBTREE_TRAVERSAL_REPLAY_KEYS = [
    "empty_root",
    "insert_order",
    "reverse_order",
    "replace_order",
    "erase_init_order",
    "postorder_count",
    "erase_init_node_empty",
    "cleared_node_empty",
]
EXPECTED_STRING_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the "
    "string review packet and this lane note unless dedicated shared sysfs fixture keys land; "
    "do not reopen missing closure-side validator names by default."
)
EXPECTED_STRING_COUNTED_SEARCH_REVIEW_SUMMARY = (
    "the direct counted-search and C-string search-length follow-up stays explicit because the "
    "shared Phase 1 replay still does not carry dedicated counted-search or search-length fixture "
    "keys, so strchr() or strrchr() full-length C-string searches, strpbrk() first-accepted-byte "
    "scanning, strspn() accepted-prefix scanning, strcspn() rejected-byte scanning, strnchr() "
    "count-limited scanning, strnlen() count-clamped length, and strnchrNul() or strnchrnul() "
    "match-or-NUL boundary behavior remain owned by the helper-local anchors"
)

REQUIRED_EXACT_LINES = {
    PHASE1_CLOSURE_REL: [
        "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.",
        "A current helper-family tie-breaker inside that packet is the `bitmap` direct-anchor route: keep `tools/lib/bitmap.zig` parked unless a fresh reread finds new direct-anchor drift inside the manifest-backed fill-tail clamp, copy-alias, cross-word `scnprintf()`, exact-word-boundary equality fast-path masking, empty-buffer, allocator-reset, zero-bit logical short-circuit, Linux-style alias mirror, caller-window or multiword-tail `xorBits()`/`orBits()` clamp witnesses, or weighted tail-count clamp, or drift in the already-committed bitmap replay fields summarized by the manifest; do not reopen older closure-side or validator-route cue names by default. Current `master` still spells those bitmap-local anchors in `tools/lib/bitmap.zig`, the committed helper manifest, and `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and the helper-local zero-bit logical test body no longer carries the one-argument `std.testing.expectEqual(...)` compile break that had briefly reopened this packet, so leave the helper parked unless one of those direct anchors or committed replay fields drifts.",
        "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors, zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped or tail-inclusive-boundary replay fields, and do not reopen older validator-first cues or neighboring helper families by default. Current `master` still keeps the helper-local byte-clump, backward-scan, alias, and shipped `find_*andnot*` entry-point packet directly in `tools/lib/find_bit.zig`, and the manifest-backed review surface together with `Documentation/zigux/phase1-host-helper-lane-sequencing.md` keep that helper-local progress review-visible beside the narrower closure validator. That direct packet now also includes the explicit `clump8 past-end scans return without reading bitmap words` no-read anchor, so the byte-clump coverage is not limited to in-range or zero-bit windows. Current `master` also now spells the lead direct anchor as `find first and next set bits across words, with andnot gaps explicit`, names the underscore and Linux-style alias anchors `including andnot`, and keeps the dedicated `single-word tail windows keep the last in-range next matches reachable from an inclusive start` proof alongside the head-word and tail-word boundary packet, so leave `find_bit` parked unless one of those direct anchors or committed replay fields drifts.",
        "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the dedicated manifest-backed `cached_root_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness. Current `master` still keeps both Linux-style alias proofs named explicitly in `zigux/tests/fixtures/phase1_helper_manifest.json`, while the shared host-tools smoke route and committed Phase 1 fixture already recheck duplicate-range iteration plus the exact cached-leftmost-return packet, so leave rbtree parked unless one of those helper-local anchors or committed replay fields drifts and do not batch a second cached-root widening into the same reopen step.",
        "A third current helper-family tie-breaker inside that packet is the `string` direct-anchor route: keep `tools/lib/string.zig` parked unless a fresh reread finds drift in the helper-local `strscpy()` or `strscpyPad()` copy-and-pad anchors, memparse safety anchors, matched-prefix-length or suffix-boundary anchors, sysfs newline-aware equality or lookup-order anchors through `sysfsStreq()`, `sysfs_streq()`, `sysfsMatchString()`, and `sysfs_match_string()`, C-string list lookup anchors through `matchString()` and `match_string()`, lexical-compare and search-or-length boundary anchors through `strcmp()`, `strlen()`, `strnlen()`, `strchr()`, `strrchr()`, `strchrNul()`, and `strchrnul()`, counted-search anchors through `strpbrk()`, `strcspn()`, `strnchr()`, `strnchrNul()` or `strnchrnul()`, and `strspn()`, embedded-NUL trim preservation, or moving-earliest-dirty-byte `memchrInv()` coverage, or unless committed `replaceChar` parity bytes or current string fixture keys drift; do not reopen missing closure-side validator names by default. Current `master` still keeps that broader string review packet explicit in `tools/lib/string.zig`, the committed manifest, `scripts/zigux/check-phase1-string-review-packet.py`, and `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, so leave string parked unless those direct string review surfaces drift, committed `replaceChar` parity bytes drift, or dedicated shared string fixture keys land.",
        "- `PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`",
    ],
    LANE_NOTE_REL: [
        "- current authenticated reads still recover `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`, so those are the trustworthy reminder surfaces for this lane on current `master`",
        "- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys it already owns; the restored phase1-closure note and validate-phase1-closure guard are live companions again, while the older validator-first and make-route names stay historical`",
        "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), and findLastBit() byte-clump and backward-scan coverage, plus the public, Linux-style, and underscore andnot coverage including the shipped findFirstAndNotBit(), findNextAndNotBit(), find_first_andnot_bit(), find_next_andnot_bit(), _find_first_andnot_bit(), and _find_next_andnot_bit() entry points, and tail-word skip anchors plus the committed tail-clamped and tail-inclusive-boundary find_bit replay fields already preserved in zigux/tests/fixtures/phase1_helpers.json`",
        "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed fixture still owns exact find(), findFirst(), nextMatch(), and matchIterator() duplicate-search fields and the shared host-tools smoke route keeps duplicate-range iteration plus the parked cached_leftmost_return_serials witness explicit`",
        "- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`",
        "- current `master` also keeps the helper-local `clump8`, `getValue8()`, and `findLastBit()` byte-clump and backward-scan proofs explicit in both `tools/lib/find_bit.zig` and the manifest's `helper_test_anchors` list, so nearby Phase 1 follow-through should keep those checks inside the same direct `find_bit` packet instead of splitting byte-clump or last-bit drift into a separate shared replay family",
        "- The counted-search owner term here also covers the current `strnchrNul()` and `strnchrnul()` match-or-NUL boundary anchor already cataloged in `zigux/tests/fixtures/phase1_helper_manifest.json`, so future string-only rereads should keep that helper-local boundary proof inside the same counted-search packet instead of treating it as an unowned follow-up beside `strnchr()`.",
        "- the same counted-search packet now also keeps the direct `strspn()` accepted-prefix anchor review-visible on current `master`, so future string-only rereads should treat accepted-byte-prefix scanning as part of that helper-local search family instead of leaving it implicit beside `strpbrk()` and `strnchr()`.",
        "- the still-open string sysfs follow-through, if it reopens, should stay on one string-only shared review-rule packet across `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `scripts/zigux/check-phase1-string-review-packet.py`; the restored `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` companions are now live broader reminder evidence on current `master`, but string should stay parked on the helper-local sysfs review anchors unless those direct string surfaces drift.",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS=the shared reminder packet now keeps scripts/zigux/check-phase1-bench.py explicit across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md, while the older installer-backed, validator-first, bench-route, and replay names stay historical packet members until they reread cleanly on current master`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`",
        "- the dedicated owner-map checker itself is now part of the live Phase 1 reminder packet beside this lane note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`, so future reminder surfaces should keep that checker explicit instead of treating the owner-map note as docs-only context",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`",
        "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`",
        "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`",
        "- the existing byte-clump and `findLastBit()` proofs belong to that same `find_bit` direct-anchor packet too, so if one of those helper-local anchors drifts, refresh the current helper-family note before widening shared replay ownership",
        "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local ordered Linux-style alias proof, dedicated low_level_alias_anchor, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach,…

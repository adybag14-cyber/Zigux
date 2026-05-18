#!/usr/bin/env python3
"""Guard the Phase 1 direct-owner marker packet against lane-note and shared-surface drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
TESTS_README_REL = Path("zigux/tests/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
PHASE1_CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    LANE_NOTE_REL,
    DOCS_ROOT_REL,
    PHASE1_CLOSURE_REL,
    REVIEW_CHECKLIST_REL,
    TESTS_README_REL,
    SCRIPTS_README_REL,
    PHASE1_CLOSURE_VALIDATOR_REL,
    MANIFEST_REL,
)

EXPECTED_PHASE = "Phase 1"
EXPECTED_STATUS = "closed"
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
    "above, while bitmap, find_bit, rbtree, and string keep the only bounded direct "
    "helper-local follow-up anchors on current master."
)
EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)
EXPECTED_BITMAP_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new "
    "direct-anchor drift inside the current helper-local packet or committed shared "
    "replay drift in the bitmap parity fields; current master still ships direct "
    "fill-tail clamp, copy-alias, truncation, cross-word scnprintf, empty-buffer, and "
    "allocator-reset anchors here, while zero-bit and Linux-style alias follow-through "
    "no longer live in the helper-local packet, and if the separate bitmap "
    "closure-validator anchor-sync repair is still outstanding, treat that as the only "
    "other bitmap follow-through."
)
EXPECTED_FIND_BIT_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep find_bit parked unless a fresh reread finds "
    "direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, "
    "zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), "
    "underscore-alias, Linux-style alias, or tail-word skip anchors, or committed "
    "tail-clamped replay drift; do not reopen older saved validator cues or "
    "neighboring helper families."
)
EXPECTED_RBTREE_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep the already-landed shared-replay promotion for "
    "`cached_leftmost_return_serials` aligned across the committed fixture, shared "
    "replay, and direct cached-root anchors; until another committed cached-root field "
    "lands, insert-miss, leftmost-sync, cached-root alias, singleton-erase, "
    "replacement, detach, and reseed behavior stay owned by direct helper-local "
    "anchors."
)
EXPECTED_STRING_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep the helper-local sysfs review anchors aligned "
    "across the string review packet and this lane note unless dedicated shared sysfs "
    "fixture keys land; do not reopen missing closure-side validator names by default."
)

REQUIRED_EXACT_LINES = {
    PHASE1_CLOSURE_REL: {
        "makefile_route_reality": "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 6, Phase 8, Phase 10, and Phase 12. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.",
    },
    LANE_NOTE_REL: {
        "missing_phase1_packet_note": "- current authenticated reads still do not recover `scripts/zigux/validate-phase1.py` on `master`, while `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1-closure.py`, and `zigux/Makefile` are back on current `master`; the returned Makefile now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate`, `phase3`, `phase8-validate`, `phase8-exec-cmd-test`, `phase8-test`, `phase8`, `phase10-validate`, `phase10-test`, and `phase10` routes, so this lane should use that restored closure-side packet as live owner-map evidence while still treating the older validator-first and Phase 1 make-route names as historical packet members",
        "bitmap_direct_owner": "- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys it already owns; the restored phase1-closure note and validate-phase1-closure guard are live companions again, while the older validator-first and make-route names stay historical`",
        "find_bit_direct_owner": "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, underscore-alias and Linux-style alias coverage including the shipped find_first_andnot_bit(), find_next_andnot_bit(), _find_first_andnot_bit(), and _find_next_andnot_bit() entry points, and tail-word skip anchors plus the committed tail-clamped find_bit replay fields already preserved in zigux/tests/fixtures/phase1_helpers.json`",
        "rbtree_direct_owner": "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed shared replay already owns duplicate-search parity through find(), findFirst(), nextMatch(), and matchIterator() plus the parked cached_leftmost_return_serials witness`",
        "string_direct_owner": "- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`",
        "find_bit_clump_packet_note": "- current `master` also keeps the helper-local `clump8`, `getValue8()`, and `findLastBit()` byte-clump and backward-scan proofs explicit in both `tools/lib/find_bit.zig` and the manifest's `helper_test_anchors` list, so nearby Phase 1 follow-through should keep those checks inside the same direct `find_bit` packet instead of splitting byte-clump or last-bit drift into a separate shared replay family",
        "string_counted_search_alias_note": "- The counted-search owner term here also covers the current `strnchrNul()` and `strnchrnul()` match-or-NUL boundary anchor already cataloged in `zigux/tests/fixtures/phase1_helper_manifest.json`, so future string-only rereads should keep that helper-local boundary proof inside the same counted-search packet instead of treating it as an unowned follow-up beside `strnchr()`.",
        "string_review_rule_note": "- the still-open string sysfs follow-through, if it reopens, should stay on one string-only shared review-rule packet across `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `scripts/zigux/check-phase1-string-review-packet.py`; the restored `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` companions are now live broader reminder evidence on current `master`, but string should stay parked on the helper-local sysfs review anchors unless those direct string surfaces drift.",
        "shared_reminder_gap_note": "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS=the shared reminder packet now keeps scripts/zigux/check-phase1-bench.py explicit across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md, while the older installer-backed, validator-first, bench-route, and replay names stay historical packet members until they reread cleanly on current master`",
        "shared_reminder_active_packet": "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py`",
        "shared_reminder_route_split": "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`",
        "owner_map_checker_packet_note": "- the dedicated owner-map checker itself is now part of the live Phase 1 reminder packet beside this lane note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`, so future reminder surfaces should keep that checker explicit instead of treating the owner-map note as docs-only context",
        "shared_reminder_next_step": "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, or scripts/zigux/check-phase1-bench.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`",
        "bitmap_next_safe_step": "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`",
        "find_bit_next_safe_step": "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped replay drift; do not reopen older saved validator cues or neighboring helper families`",
        "find_bit_clump_next_step_note": "- the existing byte-clump and `findLastBit()` proofs belong to that same `find_bit` direct-anchor packet too, so if one of those helper-local anchors drifts, refresh the current helper-family note before widening shared replay ownership",
        "rbtree_next_safe_step": "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
        "manifest_tie_breaker_note": "- `zigux/tests/fixtures/phase1_helper_manifest.json` now records helper-local `next_safe_step_note` entries for `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig`; treat those helper-specific manifest notes plus the `PHASE1_*_NEXT_SAFE_STEP` lines below as the authoritative tie-breakers instead of reopening a helper family from older saved cues or missing shared-validator paths.`",
        "string_next_safe_step": "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
    },
    DOCS_ROOT_REL: {
        "phase1_bench_checker_listed": "- `scripts/zigux/check-phase1-bench.py`",
        "phase1_historical_warning": "  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again even though its live body still exposes only the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes.",
        "phase1_direct_checks": "  * the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
        "phase1_helper_family_split": "  * keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
        "phase1_self_test_split": "  * `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
    },
    REVIEW_CHECKLIST_REL: {
        "phase1_packet_alignment": "  * if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` still agree on the same bounded current-`master` reminder packet: the thirteen-helper owner map, the parked shared-replay-versus-direct-anchor split, the restored closure note and closure validator, the live string-review and direct-owner guards, `zigux/tests/build.zig` and `zigux/tests/phase1_host_tools_smoke.zig` stay explicit as the shipped shared-smoke reminder anchors while `scripts/zigux/check-phase1-bench.py` stays explicit as the shipped bench-side checker anchor for the remaining shared reminder wording, and the repo-reality warning that older installer-backed, validator-first, make-route, bench-route, and replay paths such as `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` stay framed as historical packet members rather than direct current evidence unless a fresh reread materializes them again, while current `master` does materialize `zigux/Makefile` and that returned file should stay framed as live repo evidence whose body still exposes only the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes rather than as proof that the older Phase 1 wrapper names returned, while the Phase 1 reminder stays bounded to the host-side helper packet instead of reopening broader closure-stack churn?",
        "phase1_self_test_alignment": "  * if the change touches that same Phase 1 reminder packet, does the checklist still say clearly that `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the bounded live reminder checks and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the bounded live shared smoke route while `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `.github/workflows/zigux-bootstrap.yml` keep the shipped current-`master` Phase 1 reminder packet explicit, that the older installer-companion self-test-versus-live route wording stays historical until `scripts/zigux/check-phase1-installer-companion-checks.py` is directly readable again, and that the broader docs-root, checklist, and tests-root bench wording stays aligned with the shipped bench checker instead of treating it as missing current evidence?",
    },
    TESTS_README_REL: {
        "phase1_direct_packet": "  * current direct-readback Phase 1 reminder packet:",
        "phase1_historical_warning": "  * repo-reality warning for the broader historical Phase 1 validator-first, bench, and replay stack: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "phase1_bench_checker_present": "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "phase1_makefile_readback": "  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 8, Phase 10, and Phase 12 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
        "phase1_followthrough_alignment": "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    },
    SCRIPTS_README_REL: {
        "phase1_self_tests": "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, and `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the shipped bounded Phase 1 reminder checks",
        "phase1_live_guards": "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, and closure-validator packet explicit from the scripts root",
        "phase1_companions": "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet",
        "phase1_historical_warning": "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` reminder evidence",
        "phase1_bench_checker_present": "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
        "phase1_direct_anchor_tie_breakers": "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    },
}

MANIFEST_EXPECTATIONS = {
    ("phase",): EXPECTED_PHASE,
    ("status",): EXPECTED_STATUS,
    ("helper_count",): len(EXPECTED_HELPERS),
    ("helpers",): EXPECTED_HELPERS,
    ("lane_sequencing", "shared_replay_parked_helpers"): EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
    ("lane_sequencing", "direct_anchor_followup_helpers"): EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
    ("lane_sequencing", "rule_summary"): EXPECTED_RULE_SUMMARY,
    ("lane_sequencing", "anti_overlap_rule"): EXPECTED_ANTI_OVERLAP_RULE,
    ("review_anchors", "tools/lib/bitmap.zig", "next_safe_step_note"): EXPECTED_BITMAP_NEXT_SAFE_STEP_NOTE,
    ("review_anchors", "tools/lib/find_bit.zig", "next_safe_step_note"): EXPECTED_FIND_BIT_NEXT_SAFE_STEP_NOTE,
    ("review_anchors", "tools/lib/rbtree.zig", "next_safe_step_note"): EXPECTED_RBTREE_NEXT_SAFE_STEP_NOTE,
    ("review_anchors", "tools/lib/string.zig", "next_safe_step_note"): EXPECTED_STRING_NEXT_SAFE_STEP_NOTE,
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    expected = line.strip()
    count = sum(1 for current_line in text.splitlines() if current_line.strip() == expected)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def collect_direct_owner_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures
    for relative_path, labels in REQUIRED_EXACT_LINES.items():
        text = load_text(root, relative_path)
        for label, line in labels.items():
            failures.extend(require_exact_line(text, f"{relative_path.as_posix()}:{label}", line))
    manifest = load_json(root, MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]
    for path, expected in MANIFEST_EXPECTATIONS.items():
        failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:{'.'.join(path)}", nested_value(manifest, path), expected))
    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_text(relative_path: Path) -> str:
    labels = REQUIRED_EXACT_LINES[relative_path]
    return "# sample\n\n" + "\n".join(labels.values()) + "\n"


def sample_manifest() -> str:
    return (
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "status": EXPECTED_STATUS,
                "helper_count": len(EXPECTED_HELPERS),
                "helpers": EXPECTED_HELPERS,
                "lane_sequencing": {
                    "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
                    "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
                    "rule_summary": EXPECTED_RULE_SUMMARY,
                    "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
                },
                "review_anchors": {
                    "tools/lib/bitmap.zig": {
                        "next_safe_step_note": EXPECTED_BITMAP_NEXT_SAFE_STEP_NOTE,
                    },
                    "tools/lib/find_bit.zig": {
                        "next_safe_step_note": EXPECTED_FIND_BIT_NEXT_SAFE_STEP_NOTE,
                    },
                    "tools/lib/rbtree.zig": {
                        "next_safe_step_note": EXPECTED_RBTREE_NEXT_SAFE_STEP_NOTE,
                    },
                    "tools/lib/string.zig": {
                        "next_safe_step_note": EXPECTED_STRING_NEXT_SAFE_STEP_NOTE,
                    },
                },
            },
            indent=2,
        )
        + "\n"
    )


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path == MANIFEST_REL:
            write_file(root, relative_path, sample_manifest())
        elif relative_path in REQUIRED_EXACT_LINES:
            write_file(root, relative_path, sample_text(relative_path))
        else:
            write_file(root, relative_path, f"# sample for {relative_path.as_posix()}\n")


def mutate_manifest(root: Path, path: tuple[str, ...]) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = manifest
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[1:]
    elif isinstance(value, int):
        current[final_key] = value + 1
    else:
        current[final_key] = f"{value} drift"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, Path | None, str | tuple[str, ...] | None, str]] = [("success", None, None, "none")]
    for relative_path, labels in REQUIRED_EXACT_LINES.items():
        for label, line in labels.items():
            cases.append((f"missing_{relative_path.name}_{label}", relative_path, line, "remove"))
            cases.append((f"duplicate_{relative_path.name}_{label}", relative_path, line, "duplicate"))
    for path in MANIFEST_EXPECTATIONS:
        cases.append((f"manifest_{'_'.join(path)}", MANIFEST_REL, path, "manifest"))
    cases.extend(
        [
            ("missing_phase1_closure_file", PHASE1_CLOSURE_REL, None, "missing_file"),
            ("missing_phase1_closure_validator_file", PHASE1_CLOSURE_VALIDATOR_REL, None, "missing_file"),
        ]
    )
    for name, relative_path, needle, operation in cases:
        safe_name = name.replace("/", "_")
        with tempfile.TemporaryDirectory(prefix=f"phase1-direct-owner-{safe_name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if relative_path:
                target = root / relative_path
                if operation == "missing_file":
                    target.unlink()
                elif needle:
                    if operation in {"remove", "duplicate"}:
                        assert isinstance(needle, str)
                        text = target.read_text(encoding="utf-8")
                        if operation == "remove":
                            target.write_text(text.replace(needle + "\n", "", 1), encoding="utf-8")
                        else:
                            target.write_text(text.replace(needle, needle + "\n" + needle, 1), encoding="utf-8")
                    elif operation == "manifest":
                        assert isinstance(needle, tuple)
                        mutate_manifest(root, needle)
            failures = collect_direct_owner_failures(root)
            if name == "success":
                if failures:
                    print(f"self-test:{name}:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
                continue
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1
    print("self-test:ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_direct_owner_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("phase1-direct-owner-markers:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
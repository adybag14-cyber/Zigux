#!/usr/bin/env python3
"""Guard the Phase 1 lane-sequencing packet against owner-map and reminder drift."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")

REQUIRED_FILES = (
    LANE_NOTE_REL,
    PHASE1_CLOSURE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    MANIFEST_REL,
    DIRECT_OWNER_CHECKER_REL,
    STRING_REVIEW_CHECKER_REL,
    SHARED_REMINDER_CHECKER_REL,
)

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

EXPECTED_LANE_NOTE_MARKERS = {
    "shared_replay_parked_helpers": (
        "`PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,"
        "tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,"
        "tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`"
    ),
    "direct_anchor_followup_helpers": (
        "`PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,"
        "tools/lib/rbtree.zig,tools/lib/string.zig`"
    ),
    "lane_rule_summary": f"`PHASE1_LANE_RULE_SUMMARY={EXPECTED_RULE_SUMMARY}`",
    "lane_anti_overlap_rule": f"`PHASE1_LANE_ANTI_OVERLAP_RULE={EXPECTED_ANTI_OVERLAP_RULE}`",
    "shared_reminder_active_packet": (
        "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,"
        "Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,"
        "zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,"
        "scripts/zigux/check-phase1-string-review-packet.py,"
        "scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,"
        "scripts/zigux/check-phase1-shared-reminder-packet.py`"
    ),
    "shared_reminder_next_step": (
        "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording "
        "and shared-reminder checker packet parked unless a fresh reread finds drift across "
        "Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, "
        "scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, "
        "scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or "
        "scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller "
        "helper-specific next-safe-step markers below before reopening any shared reminder surface`"
    ),
    "bitmap_next_safe_step": (
        "`PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new "
        "direct-anchor drift or committed shared replay drift; do not reopen older closure-side "
        "or validator-route cue names by default`"
    ),
    "find_bit_next_safe_step": (
        "`PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside "
        "same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, "
        "past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias "
        "coverage including the shipped andnot scan entry points, or tail-word skip anchors, or "
        "for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older "
        "saved validator cues or neighboring helper families`"
    ),
    "rbtree_next_safe_step": (
        "`PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed "
        "cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner "
        "note, and any shared parity gates, or for drift inside the still-helper-local ordered "
        "Linux-style alias proof, dedicated low_level_alias_anchor, cached-root insert-miss, "
        "leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; "
        "do not widen cached-root follow-through beyond the existing direct packet until another "
        "committed shared replay field lands`"
    ),
    "string_next_safe_step": (
        "`PHASE1_STRING_NEXT_SAFE_STEP=string stays parked unless a fresh reread finds drift in "
        "the helper-local sysfs review packet, counted-search and search-length packet, memparse "
        "safety, matched-prefix and suffix-boundary packet, embedded-NUL trim preservation, "
        "moving-earliest-dirty-byte memchrInv coverage, or committed replaceChar parity bytes or "
        "current string fixture keys; do not reopen missing closure-side validator names by default`"
    ),
}

EXPECTED_CLOSURE_MARKERS = {
    "current_reminder_packet": (
        "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,"
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,"
        "Documentation/zigux/review-checklist.md,scripts/zigux/README.md,"
        "scripts/zigux/check-phase1-string-review-packet.py,"
        "scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,"
        "scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,"
        "zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,"
        ".github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`"
    ),
    "next_safe_step": (
        "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker "
        "against the restored closure note, the closure validator, the shared tests-root smoke route, "
        "and the helper-specific next_safe_step_note entries in the committed manifest rather than "
        "widening back into the older validator-first or replay-side closure stack.`"
    ),
    "bitmap_direct_review": (
        "`PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the "
        "closure packet because the shared Phase 1 replay still only owns allocator sizing, zero-filled "
        "allocation words, scnprintf output, truncation, tiny-buffer handling, and partial-window xor "
        "replay, so current master keeps fill-tail clamp, raw copy alias, tail-clearing and extension "
        "semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, "
        "zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, "
        "tail-masked predicate behavior, caller-window xor and or clamping, multiword-tail xor and or "
        "clamp witnesses, weighted tail-count clamping, complement-tail masking, terminator-only and "
        "zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias "
        "mirror coverage, and allocator optional-reset coverage review-visible at the helper surface`"
    ),
    "string_sysfs_review": (
        "`PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order "
        "anchors stay explicit through the direct string tests and the Phase 1 helper manifest because "
        "the shared Phase 1 replay still carries no dedicated sysfs fixture keys`"
    ),
}

EXPECTED_FIND_BIT_ANDNOT_SCAN_ENTRYPOINTS = [
    "findFirstAndNotBit",
    "find_first_andnot_bit",
    "_find_first_andnot_bit",
    "findNextAndNotBit",
    "find_next_andnot_bit",
    "_find_next_andnot_bit",
]

EXPECTED_FIND_BIT_ANDNOT_SCAN_ENTRYPOINT_CONTRACT = (
    "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct "
    "find_bit packet instead of being left implicit under generic alias wording."
)

EXPECTED_FIND_BIT_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift "
    "inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, "
    "clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped "
    "andnot scan entry points, or tail-word skip anchors, or committed tail-clamped or tail-inclusive-boundary "
    "replay drift; do not reopen older saved validator cues or neighboring helper families."
)

EXPECTED_RBTREE_SHARED_REPLAY_SUMMARY = (
    "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, and exact "
    "cached-leftmost-return witnesses for rbtree, while the current shared host-tools smoke replay now "
    "rechecks duplicate-range iteration plus the exact `cached_leftmost_return_serials` cached-root "
    "leftmost-return sequence on current master"
)

EXPECTED_RBTREE_CACHED_ROOT_DIRECT_REVIEW_SUMMARY = (
    "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, "
    "and reseed behavior remain owned by direct helper-local anchors, while the exact "
    "`cached_leftmost_return_serials` witness now stays aligned across the helper-local tests, the shared "
    "host-tools smoke replay, and the committed fixture"
)

EXPECTED_RBTREE_REVIEW_PACKET_SUMMARY = (
    "the current shared host-tools smoke replay keeps duplicate-range iteration and the exact "
    "`cached_leftmost_return_serials` cached-root leftmost-return witness visible for rbtree, while the "
    "committed Phase 1 fixture still carries the exact traversal, detached-node, duplicate-search, and "
    "cached-leftmost-return witnesses; direct helper-local anchors continue to own cached-root insert-miss, "
    "leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed paths that the "
    "shared smoke route does not replay exactly"
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

EXPECTED_STRING_COUNTED_SEARCH_REVIEW_SUMMARY = (
    "the direct counted-search and C-string search-length follow-up stays explicit because the shared "
    "Phase 1 replay still does not carry dedicated counted-search or search-length fixture keys, so "
    "strchr() or strrchr() full-length C-string searches, strpbrk() first-accepted-byte scanning, "
    "strspn() accepted-prefix scanning, strcspn() rejected-byte scanning, strnchr() count-limited scanning, "
    "strnlen() count-clamped length, and strnchrNul() or strnchrnul() match-or-NUL boundary behavior remain "
    "owned by the helper-local anchors"
)

EXPECTED_STRING_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string "
    "review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen "
    "missing closure-side validator names by default."
)

EXPECTED_DOCS_ROOT_MARKERS = (
    "keep the live owner map, the restored closure note and closure validator, the parked "
    "shared-replay-versus-direct-anchor split, the shipped bench checker, and the current "
    "Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools "
    "closure stack from older missing validator and replay surfaces.",
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
)

EXPECTED_REVIEW_CHECKLIST_MARKERS = (
    "`Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, "
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, "
    "`scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, "
    "`scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, "
    "`scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, "
    "`zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, "
    "`zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file "
    "zigux/tests/build.zig` still agree on the current closed-helper reminder packet",
)

EXPECTED_SCRIPTS_README_MARKERS = (
    "- `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, "
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, "
    "`zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `scripts/zigux/README.md` remain "
    "the current reminder-surface companions for that packet",
    "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen "
    "only inside their existing helper-local anchors or already-committed shared fixture keys, while the other "
    "nine closed helpers stay parked unless the shared replay or reminder packet drifts",
)

EXPECTED_TESTS_README_MARKERS = (
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "current direct-readback Phase 1 reminder packet:",
)

FORBIDDEN_FRAGMENTS = (
    "restore the missing phase1 closure note first",
    "sync one shared reminder surface against the restored closure note and closure validator",
    "reopen older closure-side or validator-route cue names",
)

DELEGATED_CHECKERS = (
    (DIRECT_OWNER_CHECKER_REL, "phase1-direct-owner-markers"),
    (STRING_REVIEW_CHECKER_REL, "phase1-string-review-packet"),
    (SHARED_REMINDER_CHECKER_REL, "phase1-shared-reminder-packet"),
)


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


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

    lane_note_text = load_text(root, LANE_NOTE_REL)
    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    docs_root_text = load_text(root, DOCS_ROOT_REL)
    review_checklist_text = load_text(root, REVIEW_CHECKLIST_REL)
    scripts_readme_text = load_text(root, SCRIPTS_README_REL)
    tests_readme_text = load_text(root, TESTS_README_REL)

    for label, marker in EXPECTED_LANE_NOTE_MARKERS.items():
        failures.extend(require_exact_occurrence(lane_note_text, f"{LANE_NOTE_REL.as_posix()}:{label}", marker))
    for label, marker in EXPECTED_CLOSURE_MARKERS.items():
        failures.extend(require_exact_occurrence(closure_text, f"{PHASE1_CLOSURE_REL.as_posix()}:{label}", marker))
    for marker in EXPECTED_DOCS_ROOT_MARKERS:
        failures.extend(require_exact_occurrence(docs_root_text, f"{DOCS_ROOT_REL.as_posix()}:required", marker))
    for marker in EXPECTED_REVIEW_CHECKLIST_MARKERS:
        failures.extend(require_exact_occurrence(review_checklist_text, f"{REVIEW_CHECKLIST_REL.as_posix()}:required", marker))
    for marker in EXPECTED_SCRIPTS_README_MARKERS:
        failures.extend(require_exact_occurrence(scripts_readme_text, f"{SCRIPTS_README_REL.as_posix()}:required", marker))
    for marker in EXPECTED_TESTS_README_MARKERS:
        failures.extend(require_exact_occurrence(tests_readme_text, f"{TESTS_README_REL.as_posix()}:required", marker))

    for relative_path, text in (
        (LANE_NOTE_REL, lane_note_text),
        (PHASE1_CLOSURE_REL, closure_text),
        (DOCS_ROOT_REL, docs_root_text),
        (REVIEW_CHECKLIST_REL, review_checklist_text),
        (SCRIPTS_README_REL, scripts_readme_text),
        (TESTS_README_REL, tests_readme_text),
    ):
        for fragment in FORBIDDEN_FRAGMENTS:
            count = text.count(fragment)
            if count and not (
                relative_path == LANE_NOTE_REL and fragment == "reopen older closure-side or validator-route cue names"
            ):
                failures.append(f"{relative_path.as_posix()}:forbidden_fragment:actual_count={count}:{fragment}")

    try:
        manifest = load_json_with_duplicate_tracking(load_text(root, MANIFEST_REL))
    except json.JSONDecodeError as exc:
        return [f"{MANIFEST_REL.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    duplicate_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_paths:
        return [f"{MANIFEST_REL.as_posix()}:duplicate_json_key:{path}" for path in duplicate_paths]

    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:phase", manifest.get("phase"), "Phase 1"))
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:status", manifest.get("status"), "closed"))
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:helper_count", manifest.get("helper_count"), 13))

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        return [f"{MANIFEST_REL.as_posix()}:lane_sequencing:expected=dict:actual={type(lane_sequencing).__name__}"]

    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.shared_replay_parked_helpers",
            lane_sequencing.get("shared_replay_parked_helpers"),
            EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.direct_anchor_followup_helpers",
            lane_sequencing.get("direct_anchor_followup_helpers"),
            EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.rule_summary",
            lane_sequencing.get("rule_summary"),
            EXPECTED_RULE_SUMMARY,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.anti_overlap_rule",
            lane_sequencing.get("anti_overlap_rule"),
            EXPECTED_ANTI_OVERLAP_RULE,
        )
    )

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict:actual={type(review_anchors).__name__}"]

    bitmap_review = review_anchors.get("tools/lib/bitmap.zig")
    find_bit_review = review_anchors.get("tools/lib/find_bit.zig")
    rbtree_review = review_anchors.get("tools/lib/rbtree.zig")
    string_review = review_anchors.get("tools/lib/string.zig")
    if not all(isinstance(item, dict) for item in (bitmap_review, find_bit_review, rbtree_review, string_review)):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors:expected_direct_anchor_dicts"]

    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig.review_packet_summary",
            bitmap_review.get("review_packet_summary"),
            EXPECTED_CLOSURE_MARKERS["bitmap_direct_review"].strip("`").split("=", 1)[1],
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig.next_safe_step_note",
            bitmap_review.get("next_safe_step_note"),
            "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side or validator-route cue names by default.",
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig.andnot_scan_entrypoints",
            find_bit_review.get("andnot_scan_entrypoints"),
            EXPECTED_FIND_BIT_ANDNOT_SCAN_ENTRYPOINTS,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig.andnot_scan_entrypoint_contract",
            find_bit_review.get("andnot_scan_entrypoint_contract"),
            EXPECTED_FIND_BIT_ANDNOT_SCAN_ENTRYPOINT_CONTRACT,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig.next_safe_step_note",
            find_bit_review.get("next_safe_step_note"),
            EXPECTED_FIND_BIT_NEXT_SAFE_STEP_NOTE,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig.shared_replay_summary",
            rbtree_review.get("shared_replay_summary"),
            EXPECTED_RBTREE_SHARED_REPLAY_SUMMARY,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig.cached_root_direct_review_summary",
            rbtree_review.get("cached_root_direct_review_summary"),
            EXPECTED_RBTREE_CACHED_ROOT_DIRECT_REVIEW_SUMMARY,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig.review_packet_summary",
            rbtree_review.get("review_packet_summary"),
            EXPECTED_RBTREE_REVIEW_PACKET_SUMMARY,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig.traversal_replay_keys",
            rbtree_review.get("traversal_replay_keys"),
            EXPECTED_RBTREE_TRAVERSAL_REPLAY_KEYS,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/string.zig.strnchr_review_summary",
            string_review.get("strnchr_review_summary"),
            EXPECTED_STRING_COUNTED_SEARCH_REVIEW_SUMMARY,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/string.zig.next_safe_step_note",
            string_review.get("next_safe_step_note"),
            EXPECTED_STRING_NEXT_SAFE_STEP_NOTE,
        )
    )

    for script_rel, label in DELEGATED_CHECKERS:
        failures.extend(run_checker(root, script_rel, label))

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_checker_stub(path: Path, ok: bool = True) -> None:
    write_text(
        path,
        "#!/usr/bin/env python3\n"
        "import argparse\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--root')\n"
        "parser.parse_args()\n"
        f"print('stub:{'ok' if ok else 'failure'}')\n"
        f"raise SystemExit({0 if ok else 1})\n",
    )


def make_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root / relative_path, f"fixture for {relative_path.as_posix()}\n")

    write_text(root / LANE_NOTE_REL, "# Phase 1 Host-Helper Lane Sequencing\n\n" + "\n".join(EXPECTED_LANE_NOTE_MARKERS.values()) + "\n")
    write_text(root / PHASE1_CLOSURE_REL, "# Phase 1 Closure\n\n" + "\n".join(EXPECTED_CLOSURE_MARKERS.values()) + "\n")
    write_text(root / DOCS_ROOT_REL, "\n".join(EXPECTED_DOCS_ROOT_MARKERS) + "\n")
    write_text(root / REVIEW_CHECKLIST_REL, "\n".join(EXPECTED_REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root / SCRIPTS_README_REL, "\n".join(EXPECTED_SCRIPTS_README_MARKERS) + "\n")
    write_text(root / TESTS_README_REL, "\n".join(EXPECTED_TESTS_README_MARKERS) + "\n")
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": 13,
                "lane_sequencing": {
                    "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
                    "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
                    "rule_summary": EXPECTED_RULE_SUMMARY,
                    "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
                },
                "review_anchors": {
                    "tools/lib/bitmap.zig": {
                        "review_packet_summary": EXPECTED_CLOSURE_MARKERS["bitmap_direct_review"].strip("`").split("=", 1)[1],
                        "next_safe_step_note": "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side or validator-route cue names by default.",
                    },
                    "tools/lib/find_bit.zig": {
                        "andnot_scan_entrypoints": EXPECTED_FIND_BIT_ANDNOT_SCAN_ENTRYPOINTS,
                        "andnot_scan_entrypoint_contract": EXPECTED_FIND_BIT_ANDNOT_SCAN_ENTRYPOINT_CONTRACT,
                        "next_safe_step_note": EXPECTED_FIND_BIT_NEXT_SAFE_STEP_NOTE,
                    },
                    "tools/lib/rbtree.zig": {
                        "shared_replay_summary": EXPECTED_RBTREE_SHARED_REPLAY_SUMMARY,
                        "cached_root_direct_review_summary": EXPECTED_RBTREE_CACHED_ROOT_DIRECT_REVIEW_SUMMARY,
                        "review_packet_summary": EXPECTED_RBTREE_REVIEW_PACKET_SUMMARY,
                        "traversal_replay_keys": EXPECTED_RBTREE_TRAVERSAL_REPLAY_KEYS,
                    },
                    "tools/lib/string.zig": {
                        "strnchr_review_summary": EXPECTED_STRING_COUNTED_SEARCH_REVIEW_SUMMARY,
                        "next_safe_step_note": EXPECTED_STRING_NEXT_SAFE_STEP_NOTE,
                    },
                },
            },
            indent=2,
        )
        + "\n",
    )

    for checker_rel, _label in DELEGATED_CHECKERS:
        make_checker_stub(root / checker_rel, ok=True)


def mutate_remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_manifest_field(root: Path, path: list[str], value: object) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cursor = manifest
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def insert_duplicate_manifest_line(root: Path, needle: str, duplicate_line: str) -> None:
    manifest_path = root / MANIFEST_REL
    text = manifest_path.read_text(encoding="utf-8")
    manifest_path.write_text(text.replace(needle, duplicate_line + "\n" + needle, 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_lane_rule_summary", lambda root: mutate_remove_marker(root, LANE_NOTE_REL, EXPECTED_LANE_NOTE_MARKERS["lane_rule_summary"])),
        ("missing_shared_reminder_next_step", lambda root: mutate_remove_marker(root, LANE_NOTE_REL, EXPECTED_LANE_NOTE_MARKERS["shared_reminder_next_step"])),
        ("missing_closure_next_safe_step", lambda root: mutate_remove_marker(root, PHASE1_CLOSURE_REL, EXPECTED_CLOSURE_MARKERS["next_safe_step"])),
        ("missing_docs_root_marker", lambda root: mutate_remove_marker(root, DOCS_ROOT_REL, EXPECTED_DOCS_ROOT_MARKERS[0])),
        ("stale_manifest_rule_summary", lambda root: mutate_manifest_field(root, ["lane_sequencing", "rule_summary"], "drifted rule summary")),
        ("stale_manifest_find_bit_note", lambda root: mutate_manifest_field(root, ["review_anchors", "tools/lib/find_bit.zig", "next_safe_step_note"], "drifted note")),
        ("duplicate_manifest_rule_summary", lambda root: insert_duplicate_manifest_line(root, f'    "rule_summary": "{EXPECTED_RULE_SUMMARY}",', '    "rule_summary": "drifted rule summary",')),
        ("missing_direct_owner_checker", lambda root: (root / DIRECT_OWNER_CHECKER_REL).unlink()),
        ("failing_shared_reminder_checker", lambda root: make_checker_stub(root / SHARED_REMINDER_CHECKER_REL, ok=False)),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-lane-sequencing-selftest-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-lane-sequencing-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-lane-sequencing-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_LANE_SEQUENCING_PACKET_SELF_TEST=pass")
    print(f"PHASE1_LANE_SEQUENCING_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def write_sample_root(destination: Path) -> None:
    make_fixture_tree(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument("--write-sample-root", help="write a passing sample repo root to the given directory")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_LANE_SEQUENCING_PACKET=pass")
    print("PHASE1_LANE_SEQUENCING_PACKET_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

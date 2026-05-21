#!/usr/bin/env python3
"""Guard the current Phase 1 lane-sequencing packet for Lane 17."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
DIRECT_OWNER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
CHECKER_REL = Path("scripts/zigux/check-phase1-lane-sequencing-packet.py")

REQUIRED_FILES = (
    LANE_NOTE_REL,
    CLOSURE_REL,
    DOCS_ROOT_REL,
    REVIEW_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    MANIFEST_REL,
    DIRECT_OWNER_REL,
    CHECKER_REL,
)

SHARED_REPLAY_HELPERS = (
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
)
DIRECT_ANCHOR_HELPERS = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
)
ACTIVE_PACKET = (
    "Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,"
    "Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,"
    "scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,"
    "scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,"
    "scripts/zigux/check-phase1-shared-reminder-packet.py"
)

MARKERS = {
    LANE_NOTE_REL: (
        "- `PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`",
        "- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS=the shared reminder packet now keeps scripts/zigux/check-phase1-bench.py explicit across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md, while the older installer-backed, validator-first, bench-route, and replay names stay historical packet members until they reread cleanly on current master`",
        f"- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET={ACTIVE_PACKET}`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`",
        "- the dedicated owner-map checker itself is now part of the live Phase 1 reminder packet beside this lane note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`, so future reminder surfaces should keep that checker explicit instead of treating the owner-map note as docs-only context",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`",
        "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`",
        "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`",
        "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
        "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
        "- the still-open string sysfs follow-through, if it reopens, should stay on one string-only shared review-rule packet across `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `scripts/zigux/check-phase1-string-review-packet.py`; the restored `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` companions are now live broader reminder evidence on current `master`, but string should stay parked on the helper-local sysfs review anchors unless those direct string surfaces drift.",
        "- the same counted-search packet now also keeps the direct `strspn()` accepted-prefix anchor review-visible on current `master`, so future string-only rereads should treat accepted-byte-prefix scanning as part of that helper-local search family instead of leaving it implicit beside `strpbrk()` and `strnchr()`.",
        "- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`",
    ),
    CLOSURE_REL: (
        "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness. Current `master` still keeps that low-level Linux-style alias proof named explicitly in `zigux/tests/fixtures/phase1_helper_manifest.json`, while the shared host-tools smoke route and committed Phase 1 fixture already recheck duplicate-range iteration plus the exact cached-leftmost-return packet, so leave rbtree parked unless one of those helper-local anchors or committed replay fields drifts and do not batch a second cached-root widening into the same reopen step.",
        "A third current helper-family tie-breaker inside that packet is the `string` direct-anchor route: keep `tools/lib/string.zig` parked unless a fresh reread finds drift in the helper-local sysfs newline-aware equality or lookup-order anchors through `sysfsStreq()`, `sysfs_streq()`, `sysfsMatchString()`, and `sysfs_match_string()`, or unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names or widen back into the broader helper-local string anchor family by default. Current `master` still keeps those sysfs review anchors explicit in `tools/lib/string.zig`, the committed manifest, `scripts/zigux/check-phase1-string-review-packet.py`, and `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, so leave string parked unless those direct sysfs review surfaces drift or dedicated shared sysfs fixture keys land.",
        "- `PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`",
        "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
    ),
    DOCS_ROOT_REL: (
        "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
        "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
        "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
    ),
    REVIEW_REL: (
        "* if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    ),
    SCRIPTS_README_REL: (
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet",
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    ),
    TESTS_README_REL: (
        "  * current direct-readback Phase 1 reminder packet:",
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ),
    DIRECT_OWNER_REL: (
        "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [",
        "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
        "EXPECTED_RULE_SUMMARY = (",
        "EXPECTED_ANTI_OVERLAP_RULE = (",
        "EXPECTED_RBTREE_SHARED_REPLAY_SUMMARY = (",
        "EXPECTED_RBTREE_CACHED_ROOT_DIRECT_REVIEW_SUMMARY = (",
        "EXPECTED_RBTREE_REVIEW_PACKET_SUMMARY = (",
        "EXPECTED_STRING_COUNTED_SEARCH_REVIEW_SUMMARY = (",
        "(\"lane_sequencing\", \"shared_replay_parked_helpers\"): EXPECTED_SHARED_REPLAY_PARKED_HELPERS,",
        "(\"lane_sequencing\", \"direct_anchor_followup_helpers\"): EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,",
        "(\"review_anchors\", \"tools/lib/rbtree.zig\", \"cached_leftmost_fixture_keys\"): [\"cached_leftmost_return_serials\"],",
        "(\"review_anchors\", \"tools/lib/string.zig\", \"counted_search_review_anchors\"): [",
    ),
}

MANIFEST_EXPECTATIONS = {
    ("lane_sequencing", "shared_replay_parked_helpers"): list(SHARED_REPLAY_HELPERS),
    ("lane_sequencing", "direct_anchor_followup_helpers"): list(DIRECT_ANCHOR_HELPERS),
    ("lane_sequencing", "rule_summary"): (
        "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
        "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
        "follow-up anchors on current master."
    ),
    ("lane_sequencing", "anti_overlap_rule"): (
        "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
        "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers "
        "reopen only for their existing helper-local anchors or already-committed shared fixture keys."
    ),
    ("review_anchors", "tools/lib/bitmap.zig", "next_safe_step_note"): (
        "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor "
        "drift inside the current helper-local packet or committed shared replay drift in the bitmap "
        "parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, "
        "cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and "
        "or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical "
        "short-circuit, and Linux-style alias mirror anchors here, and if the separate bitmap "
        "closure-validator anchor-sync repair is still outstanding, treat that as the only other "
        "bitmap follow-through."
    ),
    ("review_anchors", "tools/lib/find_bit.zig", "next_safe_step_note"): (
        "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor "
        "drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, "
        "past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage "
        "including the shipped andnot scan entry points, or tail-word skip anchors, or committed "
        "tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues "
        "or neighboring helper families."
    ),
    ("review_anchors", "tools/lib/rbtree.zig", "cached_leftmost_fixture_keys"): [
        "cached_leftmost_return_serials"
    ],
    ("review_anchors", "tools/lib/rbtree.zig", "shared_replay_summary"): (
        "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, "
        "and exact cached-leftmost-return witnesses for rbtree, while the current shared host-tools "
        "smoke replay now rechecks duplicate-range iteration plus the exact `cached_leftmost_return_serials` "
        "cached-root leftmost-return sequence on current master"
    ),
    ("review_anchors", "tools/lib/rbtree.zig", "cached_root_direct_review_summary"): (
        "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, "
        "detach, and reseed behavior remain owned by direct helper-local anchors, while the exact "
        "`cached_leftmost_return_serials` witness now stays aligned across the helper-local tests, "
        "the shared host-tools smoke replay, and the committed fixture"
    ),
    ("review_anchors", "tools/lib/rbtree.zig", "review_packet_summary"): (
        "the current shared host-tools smoke replay keeps duplicate-range iteration and the exact "
        "`cached_leftmost_return_serials` cached-root leftmost-return witness visible for rbtree, "
        "while the committed Phase 1 fixture still carries the exact traversal, detached-node, "
        "duplicate-search, and cached-leftmost-return witnesses; direct helper-local anchors continue "
        "to own cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, "
        "replacement, detach, and reseed paths that the shared smoke route does not replay exactly"
    ),
    ("review_anchors", "tools/lib/rbtree.zig", "next_safe_step_note"): (
        "If this helper lane reopens, keep the already-landed shared-replay promotion for "
        "`cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and "
        "direct cached-root anchors; the ordered Linux-style alias proof, dedicated "
        "`low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, "
        "cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by "
        "direct helper-local anchors until another committed cached-root field lands."
    ),
    ("review_anchors", "tools/lib/string.zig", "counted_search_review_anchors"): [
        'test "strchr mirrors full-length C-string searches"',
        'test "strrchr finds the last in-range match with C-string semantics"',
        'test "strpbrk finds the first accepted byte with C-string semantics"',
        'test "strspn counts the accepted prefix with C-string semantics"',
        'test "strcspn counts until the first rejected byte with C-string semantics"',
        'test "strnchr honors count and C-string boundaries"',
        'test "strnlen honors count and C-string boundaries"',
        'test "strnchrNul returns the first match, NUL, or count boundary"',
    ],
    ("review_anchors", "tools/lib/string.zig", "strnchr_review_summary"): (
        "the direct counted-search and C-string search-length follow-up stays explicit because the "
        "shared Phase 1 replay still does not carry dedicated counted-search or search-length fixture "
        "keys, so strchr() or strrchr() full-length C-string searches, strpbrk() first-accepted-byte "
        "scanning, strspn() accepted-prefix scanning, strcspn() rejected-byte scanning, strnchr() "
        "count-limited scanning, strnlen() count-clamped length, and strnchrNul() or strnchrnul() "
        "match-or-NUL boundary behavior remain owned by the helper-local anchors"
    ),
    ("review_anchors", "tools/lib/string.zig", "next_safe_step_note"): (
        "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the "
        "string review packet and this lane note unless dedicated shared sysfs fixture keys land; "
        "do not reopen missing closure-side validator names by default."
    ),
}


def load_text(root: Path, relative: Path) -> str:
    return (root / relative).read_text(encoding="utf-8")


def write_text(root: Path, relative: Path, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.exists():
            failures.append(f"missing_file:{relative.as_posix()}")
        elif not path.is_file():
            failures.append(f"non_file_path:{relative.as_posix()}")
    if failures:
        return failures

    for relative, markers in MARKERS.items():
        text = load_text(root, relative)
        for marker in markers:
            failures.extend(require_once(text, f"{relative.as_posix()}:{marker}", marker))

    manifest = json.loads(load_text(root, MANIFEST_REL))
    for path, expected in MANIFEST_EXPECTATIONS.items():
        actual = nested_value(manifest, path)
        if actual != expected:
            failures.append(
                f"{MANIFEST_REL.as_posix()}:{'.'.join(path)}:expected={expected!r}:actual={actual!r}"
            )

    return failures


def sample_manifest_text() -> str:
    data = {
        "lane_sequencing": {
            "shared_replay_parked_helpers": list(SHARED_REPLAY_HELPERS),
            "direct_anchor_followup_helpers": list(DIRECT_ANCHOR_HELPERS),
            "rule_summary": MANIFEST_EXPECTATIONS[("lane_sequencing", "rule_summary")],
            "anti_overlap_rule": MANIFEST_EXPECTATIONS[("lane_sequencing", "anti_overlap_rule")],
        },
        "review_anchors": {
            "tools/lib/bitmap.zig": {
                "next_safe_step_note": MANIFEST_EXPECTATIONS[
                    ("review_anchors", "tools/lib/bitmap.zig", "next_safe_step_note")
                ],
            },
            "tools/lib/find_bit.zig": {
                "next_safe_step_note": MANIFEST_EXPECTATIONS[
                    ("review_anchors", "tools/lib/find_bit.zig", "next_safe_step_note")
                ],
            },
            "tools/lib/rbtree.zig": {
                "cached_leftmost_fixture_keys": ["cached_leftmost_return_serials"],
                "shared_replay_summary": MANIFEST_EXPECTATIONS[
                    ("review_anchors", "tools/lib/rbtree.zig", "shared_replay_summary")
                ],
                "cached_root_direct_review_summary": MANIFEST_EXPECTATIONS[
                    ("review_anchors", "tools/lib/rbtree.zig", "cached_root_direct_review_summary")
                ],
                "review_packet_summary": MANIFEST_EXPECTATIONS[
                    ("review_anchors", "tools/lib/rbtree.zig", "review_packet_summary")
                ],
                "next_safe_step_note": MANIFEST_EXPECTATIONS[
                    ("review_anchors", "tools/lib/rbtree.zig", "next_safe_step_note")
                ],
            },
            "tools/lib/string.zig": {
                "counted_search_review_anchors": MANIFEST_EXPECTATIONS[
                    ("review_anchors", "tools/lib/string.zig", "counted_search_review_anchors")
                ],
                "strnchr_review_summary": MANIFEST_EXPECTATIONS[
                    ("review_anchors", "tools/lib/string.zig", "strnchr_review_summary")
                ],
                "next_safe_step_note": MANIFEST_EXPECTATIONS[
                    ("review_anchors", "tools/lib/string.zig", "next_safe_step_note")
                ],
            },
        },
    }
    return json.dumps(data, indent=2) + "\n"


def sample_text(relative: Path) -> str:
    if relative == MANIFEST_REL:
        return sample_manifest_text()
    return "\n".join(MARKERS.get(relative, ())) + "\n"


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    for relative in REQUIRED_FILES:
        write_text(root, relative, sample_text(relative))


def rewrite_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"missing sample text: {old}")
    return text.replace(old, new, 1)


def mutate_manifest(root: Path, path: tuple[str, ...]) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = manifest
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[:-1]
    else:
        current[final_key] = f"{value} drift"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-lane-sequencing-packet-") as tmpdir:
        root = Path(tmpdir)

        write_sample_root(root)
        if collect_failures(root):
            print("self-test:baseline_failed")
            return 1
        case_count += 1

        sample_root = root / "sample-root"
        write_sample_root(sample_root)
        if collect_failures(sample_root):
            print("self-test:written_sample_failed")
            return 1
        case_count += 1

        broken_root = root / "missing_checker"
        write_sample_root(broken_root)
        (broken_root / CHECKER_REL).unlink()
        failures = collect_failures(broken_root)
        if f"missing_file:{CHECKER_REL.as_posix()}" not in failures:
            print("self-test:missing_checker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_lane_note_marker"
        write_sample_root(broken_root)
        write_text(
            broken_root,
            LANE_NOTE_REL,
            rewrite_once(broken_root.joinpath(LANE_NOTE_REL).read_text(encoding="utf-8"), MARKERS[LANE_NOTE_REL][3] + "\n"),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{LANE_NOTE_REL.as_posix()}:{MARKERS[LANE_NOTE_REL][3]}") for item in failures):
            print("self-test:missing_lane_note_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "duplicate_docs_marker"
        write_sample_root(broken_root)
        docs_text = load_text(broken_root, DOCS_ROOT_REL)
        duplicated = docs_text.replace(MARKERS[DOCS_ROOT_REL][1], MARKERS[DOCS_ROOT_REL][1] + "\n" + MARKERS[DOCS_ROOT_REL][1], 1)
        write_text(broken_root, DOCS_ROOT_REL, duplicated)
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{DOCS_ROOT_REL.as_posix()}:{MARKERS[DOCS_ROOT_REL][1]}") for item in failures):
            print("self-test:duplicate_docs_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_tests_readme_marker"
        write_sample_root(broken_root)
        writeText = rewrite_once(load_text(broken_root, TESTS_README_REL), MARKERS[TESTS_README_REL][2] + "\n")
        write_text(
            broken_root,
            TESTS_README_REL,
            writeText,
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{TESTS_README_REL.as_posix()}:{MARKERS[TESTS_README_REL][2]}") for item in failures):
            print("self-test:missing_tests_readme_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "manifest_drift"
        write_sample_root(broken_root)
        mutate_manifest(broken_root, ("review_anchors", "tools/lib/string.zig", "strnchr_review_summary"))
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/string.zig.strnchr_review_summary") for item in failures):
            print("self-test:manifest_drift_not_detected")
            return 1
        case_count += 1

    print("PHASE1_LANE_SEQUENCING_PACKET_SELF_TEST=pass")
    print(f"PHASE1_LANE_SEQUENCING_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"phase1-lane-sequencing-packet:sample-root-written:{args.write_sample_root}")
        return 0

    failures = collect_failures(args.root.resolve())
    if failures:
        print("PHASE1_LANE_SEQUENCING_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_LANE_SEQUENCING_PACKET=pass")
    print(f"PHASE1_LANE_SEQUENCING_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_LANE_SEQUENCING_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

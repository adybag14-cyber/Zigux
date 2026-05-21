#!/usr/bin/env python3
"""Guard the current Phase 1 lane-sequencing packet against drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
TESTS_README_REL = Path("zigux/tests/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    LANE_NOTE_REL,
    PHASE1_CLOSURE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    TESTS_README_REL,
    SCRIPTS_README_REL,
    MANIFEST_REL,
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
    "fill-tail clamp, copy-alias, truncation, cross-word scnprintf, empty-buffer, "
    "allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror "
    "anchors here, and if the separate bitmap closure-validator anchor-sync repair is "
    "still outstanding, treat that as the only other bitmap follow-through."
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
    "replay, and direct cached-root anchors; the ordered Linux-style alias proof, "
    "dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, "
    "leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and "
    "reseed behavior stay owned by direct helper-local anchors until another committed "
    "cached-root field lands."
)
EXPECTED_STRING_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep the helper-local sysfs review anchors aligned "
    "across the string review packet and this lane note unless dedicated shared sysfs "
    "fixture keys land; do not reopen missing closure-side validator names by default."
)

REQUIRED_EXACT_LINES = {
    PHASE1_CLOSURE_REL: (
        "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
    ),
    LANE_NOTE_REL: (
        "- `PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`",
        "- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
        "- `PHASE1_LANE_RULE_SUMMARY=Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.`",
        "- `PHASE1_LANE_ANTI_OVERLAP_RULE=Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`",
        "- `zigux/tests/fixtures/phase1_helper_manifest.json` now records helper-local `next_safe_step_note` entries for `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig`; treat those helper-specific manifest notes plus the `PHASE1_*_NEXT_SAFE_STEP` lines below as the authoritative tie-breakers instead of reopening a helper family from older saved cues or missing shared-validator paths.`",
        "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`",
        "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped replay drift; do not reopen older saved validator cues or neighboring helper families`",
        "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
        "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
    ),
    DOCS_ROOT_REL: (
        "  * keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
        "  * `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
    ),
    REVIEW_CHECKLIST_REL: (
        "  * if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?`",
    ),
    TESTS_README_REL: (
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ),
    SCRIPTS_README_REL: (
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    ),
}

MANIFEST_EXPECTATIONS = {
    ("phase",): "Phase 1",
    ("status",): "closed",
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


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, markers in REQUIRED_EXACT_LINES.items():
        text = load_text(root, relative_path)
        for marker in markers:
            failures.extend(require_exact_line(text, f"{relative_path.as_posix()}:{marker}", marker))

    manifest = load_json(root, MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    for path, expected in MANIFEST_EXPECTATIONS.items():
        label = f"{MANIFEST_REL.as_posix()}:{'.'.join(path)}"
        failures.extend(require_exact_value(label, nested_value(manifest, path), expected))

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    return (
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": len(EXPECTED_HELPERS),
                "helpers": EXPECTED_HELPERS,
                "lane_sequencing": {
                    "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
                    "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
                    "rule_summary": EXPECTED_RULE_SUMMARY,
                    "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
                },
                "review_anchors": {
                    "tools/lib/bitmap.zig": {"next_safe_step_note": EXPECTED_BITMAP_NEXT_SAFE_STEP_NOTE},
                    "tools/lib/find_bit.zig": {"next_safe_step_note": EXPECTED_FIND_BIT_NEXT_SAFE_STEP_NOTE},
                    "tools/lib/rbtree.zig": {"next_safe_step_note": EXPECTED_RBTREE_NEXT_SAFE_STEP_NOTE},
                    "tools/lib/string.zig": {"next_safe_step_note": EXPECTED_STRING_NEXT_SAFE_STEP_NOTE},
                },
            },
            indent=2,
        )
        + "\n"
    )


def sample_text(relative_path: Path) -> str:
    return "# sample\n\n" + "\n".join(REQUIRED_EXACT_LINES[relative_path]) + "\n"


def build_sample_root(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_file(root, relative_path, sample_manifest() if relative_path == MANIFEST_REL else sample_text(relative_path))


def run_self_test() -> int:
    cases_run = 0

    with tempfile.TemporaryDirectory(prefix="phase1-lane-sequencing-") as tmpdir:
        root = Path(tmpdir)
        build_sample_root(root)
        if failures := collect_failures(root):
            print("PHASE1_LANE_SEQUENCING_SELF_TEST=fail")
            for failure in failures:
                print(f"baseline:{failure}")
            return 1
        cases_run += 1

    mutation_cases = (
        ("missing_lane_note", lambda root: (root / LANE_NOTE_REL).unlink()),
        ("missing_lane_rule_summary", lambda root: write_file(root, LANE_NOTE_REL, sample_text(LANE_NOTE_REL).replace(REQUIRED_EXACT_LINES[LANE_NOTE_REL][2] + "\n", "", 1))),
        ("missing_closure_next_step", lambda root: write_file(root, PHASE1_CLOSURE_REL, sample_text(PHASE1_CLOSURE_REL).replace("helper-family tie-breaker", "helper-family follow-up", 1))),
        ("missing_tests_followthrough_note", lambda root: write_file(root, TESTS_README_REL, sample_text(TESTS_README_REL).replace(REQUIRED_EXACT_LINES[TESTS_README_REL][1] + "\n", "", 1))),
        ("manifest_next_safe_step_drift", lambda root: write_file(root, MANIFEST_REL, json.dumps({**json.loads(sample_manifest()), "review_anchors": {**json.loads(sample_manifest())["review_anchors"], "tools/lib/string.zig": {"next_safe_step_note": "drift"}}}, indent=2) + "\n")),
    )

    for name, mutate in mutation_cases:
        with tempfile.TemporaryDirectory(prefix="phase1-lane-sequencing-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            mutate(root)
            if not collect_failures(root):
                print("PHASE1_LANE_SEQUENCING_SELF_TEST=fail")
                print(f"mutation_case_passed_unexpectedly:{name}")
                return 1
            cases_run += 1

    print("PHASE1_LANE_SEQUENCING_SELF_TEST=pass")
    print(f"PHASE1_LANE_SEQUENCING_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_LANE_SEQUENCING=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_LANE_SEQUENCING=pass")
    print(f"PHASE1_LANE_SEQUENCING_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_LANE_SEQUENCING_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_EXACT_LINES.values()) + len(MANIFEST_EXPECTATIONS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Guard the current Phase 1 lane-sequencing packet against closure-surface drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
TESTS_README_REL = Path("zigux/tests/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
PHASE1_CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    LANE_NOTE_REL,
    PHASE1_CLOSURE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    TESTS_README_REL,
    SCRIPTS_README_REL,
    BENCH_CHECKER_REL,
    DIRECT_OWNER_CHECKER_REL,
    PHASE1_CLOSURE_VALIDATOR_REL,
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

EXPECTED_LANE_NOTE_LINES = (
    "- `PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`",
    "- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
    "- `PHASE1_LANE_ANTI_OVERLAP_RULE=Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.`",
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py`",
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, or scripts/zigux/check-phase1-bench.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`",
    "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`",
    "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped replay drift; do not reopen older saved validator cues or neighboring helper families`",
    "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
    "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
)

EXPECTED_FILE_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    ),
    DOCS_ROOT_REL: (
        "- `scripts/zigux/check-phase1-bench.py`",
        "keep the live owner map, the restored closure note and closure validator, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
        "the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
    ),
    REVIEW_CHECKLIST_REL: (
        "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
        "`scripts/zigux/check-phase1-direct-owner-markers.py`",
        "`scripts/zigux/check-phase1-bench.py`",
    ),
    TESTS_README_REL: (
        "`Documentation/zigux/phase1-closure.md`",
        "`scripts/zigux/check-phase1-direct-owner-markers.py`",
        "`scripts/zigux/check-phase1-bench.py`",
        "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    ),
    SCRIPTS_README_REL: (
        "`python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`",
        "`scripts/zigux/check-phase1-direct-owner-markers.py`",
        "`scripts/zigux/check-phase1-bench.py`",
        "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
        "`scripts/zigux/validate-phase1-closure.py`",
    ),
    BENCH_CHECKER_REL: (
        "PHASE1_BENCH_CHECK_SELF_TEST=pass",
        "PHASE1_BENCH_CHECK=pass",
        "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
    ),
    DIRECT_OWNER_CHECKER_REL: (
        "self-test:ok",
        "phase1-direct-owner-markers:ok",
        "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
    ),
    PHASE1_CLOSURE_VALIDATOR_REL: (
        "PHASE1_CLOSURE_SELF_TEST=pass",
        "PHASE1_CLOSURE_VALIDATION=pass",
        "EXPECTED_HELPERS = [",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_fragment(text: str, label: str, marker: str) -> list[str]:
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

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    lane_note_text = load_text(root, LANE_NOTE_REL)
    for marker in EXPECTED_LANE_NOTE_LINES:
        failures.extend(require_exact_line(lane_note_text, f"{LANE_NOTE_REL.as_posix()}:{marker}", marker))

    for relative_path, markers in EXPECTED_FILE_MARKERS.items():
        text = load_text(root, relative_path)
        for marker in markers:
            failures.extend(
                require_exact_fragment(text, f"{relative_path.as_posix()}:{marker}", marker)
            )

    manifest = load_json(root, MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    expectations = {
        ("phase",): "Phase 1",
        ("status",): "closed",
        ("helper_count",): len(EXPECTED_HELPERS),
        ("helpers",): EXPECTED_HELPERS,
        ("lane_sequencing", "shared_replay_parked_helpers"): EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
        ("lane_sequencing", "direct_anchor_followup_helpers"): EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
        ("lane_sequencing", "rule_summary"): EXPECTED_RULE_SUMMARY,
        ("lane_sequencing", "anti_overlap_rule"): EXPECTED_ANTI_OVERLAP_RULE,
    }
    for path, expected in expectations.items():
        actual = nested_value(manifest, path)
        if actual != expected:
            failures.append(
                f"{MANIFEST_REL.as_posix()}:{'.'.join(path)}:expected={expected!r}:actual={actual!r}"
            )

    for helper in EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS:
        note = nested_value(manifest, ("review_anchors", helper, "next_safe_step_note"))
        if not isinstance(note, str) or not note:
            failures.append(
                f"{MANIFEST_REL.as_posix()}:review_anchors.{helper}.next_safe_step_note:missing_or_empty"
            )

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    payload = {
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
            helper: {"next_safe_step_note": f"{helper} next step"} for helper in EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def sample_file(relative_path: Path) -> str:
    parts = ["# sample", ""]
    if relative_path == LANE_NOTE_REL:
        parts.extend(EXPECTED_LANE_NOTE_LINES)
    elif relative_path in EXPECTED_FILE_MARKERS:
        parts.extend(EXPECTED_FILE_MARKERS[relative_path])
    return "\n".join(parts) + "\n"


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path == MANIFEST_REL:
            write_text(root, relative_path, sample_manifest())
        else:
            write_text(root, relative_path, sample_file(relative_path))


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    cases = [
        ("baseline", None, True),
        (
            "missing_lane_note_marker",
            lambda root: write_text(
                root,
                LANE_NOTE_REL,
                replace_once(load_text(root, LANE_NOTE_REL), EXPECTED_LANE_NOTE_LINES[0] + "\n", ""),
            ),
            False,
        ),
        (
            "duplicate_lane_note_marker",
            lambda root: write_text(
                root,
                LANE_NOTE_REL,
                replace_once(
                    load_text(root, LANE_NOTE_REL),
                    EXPECTED_LANE_NOTE_LINES[1],
                    EXPECTED_LANE_NOTE_LINES[1] + "\n" + EXPECTED_LANE_NOTE_LINES[1],
                ),
            ),
            False,
        ),
        (
            "missing_closure_marker",
            lambda root: write_text(
                root,
                PHASE1_CLOSURE_REL,
                replace_once(
                    load_text(root, PHASE1_CLOSURE_REL),
                    EXPECTED_FILE_MARKERS[PHASE1_CLOSURE_REL][0],
                    "`PHASE1_CLOSURE_VALIDATOR=missing`",
                ),
            ),
            False,
        ),
        (
            "missing_docs_marker",
            lambda root: write_text(
                root,
                DOCS_ROOT_REL,
                replace_once(
                    load_text(root, DOCS_ROOT_REL),
                    EXPECTED_FILE_MARKERS[DOCS_ROOT_REL][1] + "\n",
                    "",
                ),
            ),
            False,
        ),
        (
            "missing_tests_marker",
            lambda root: write_text(
                root,
                TESTS_README_REL,
                replace_once(
                    load_text(root, TESTS_README_REL),
                    EXPECTED_FILE_MARKERS[TESTS_README_REL][2],
                    "`scripts/zigux/check-phase1-bench-missing.py`",
                ),
            ),
            False,
        ),
        (
            "missing_manifest_helper",
            lambda root: write_text(
                root,
                MANIFEST_REL,
                json.dumps(
                    {
                        **json.loads(load_text(root, MANIFEST_REL)),
                        "helpers": EXPECTED_HELPERS[:-1],
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "missing_manifest_next_safe_step",
            lambda root: write_text(
                root,
                MANIFEST_REL,
                json.dumps(
                    {
                        **json.loads(load_text(root, MANIFEST_REL)),
                        "review_anchors": {
                            **json.loads(load_text(root, MANIFEST_REL))["review_anchors"],
                            "tools/lib/string.zig": {"next_safe_step_note": ""},
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "missing_required_file",
            lambda root: (root / DIRECT_OWNER_CHECKER_REL).unlink(),
            False,
        ),
    ]

    for name, mutate, expect_ok in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-lane-sequencing-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            ok = not failures
            if ok != expect_ok:
                print(f"phase1-lane-sequencing-self-test:{name}:unexpected={failures}")
                return 1

    print("PHASE1_LANE_SEQUENCING_SELF_TEST=pass")
    print(f"PHASE1_LANE_SEQUENCING_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    args = parse_args()

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
        f"{len(EXPECTED_LANE_NOTE_LINES) + sum(len(markers) for markers in EXPECTED_FILE_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

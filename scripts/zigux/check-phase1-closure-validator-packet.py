#!/usr/bin/env python3
"""Guard the current Phase 1 closure-validator packet against reminder drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    VALIDATOR_REL,
    CLOSURE_NOTE_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    WORKFLOW_REL,
    LANE_NOTE_REL,
    MANIFEST_REL,
)

VALIDATOR_MARKERS = (
    'PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")',
    'PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")',
    'SCRIPTS_README_REL = Path("scripts/zigux/README.md")',
    'TESTS_README_REL = Path("zigux/tests/README.md")',
    'WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")',
    'MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")',
    '(STRING_REVIEW_CHECKER_REL, "phase1-string-review-packet")',
    '(FIND_BIT_REVIEW_CHECKER_REL, "phase1-find-bit-review-packet")',
    '(RBTREE_REVIEW_CHECKER_REL, "phase1-rbtree-review-packet")',
    '(DIRECT_OWNER_CHECKER_REL, "phase1-direct-owner-markers")',
    '(DIRECT_ANCHOR_MANIFEST_GATE_REL, "phase1-direct-anchor-manifest-gate")',
    '(ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts")',
    '(BENCH_CHECKER_REL, "phase1-bench")',
    '(FIND_BIT_BENCH_ANCHOR_CHECKER_REL, "phase1-find-bit-bench-anchors")',
    '(BITMAP_DIRECT_ANCHOR_CHECKER_REL, "phase1-bitmap-direct-anchors")',
    '(SHARED_REMINDER_CHECKER_REL, "phase1-shared-reminder-packet")',
    'print("PHASE1_CLOSURE_VALIDATION=pass")',
    'print("PHASE1_CLOSURE_MODE=current-master-safe")',
    'print("PHASE1_CLOSURE_SELF_TEST=pass")',
)

CLOSURE_NOTE_MARKERS = (
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",
    "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",
    "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
)

SCRIPTS_README_MARKERS = (
    "`python3 scripts/zigux/validate-phase1-closure.py`",
    "`scripts/zigux/check-phase1-bitmap-direct-anchors.py` is directly readable on current `master`",
    "`zigux/Makefile` is current repo evidence again from the scripts root too",
)

TESTS_README_MARKERS = (
    "- `scripts/zigux/validate-phase1-closure.py`",
    "* current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "* keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest",
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
)

LANE_NOTE_MARKERS = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.",
    "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`",
)

EXPECTED_SHARED_HELPERS = [
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

EXPECTED_DIRECT_HELPERS = [
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
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def require_exact_once(text: str, rel: Path, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{rel.as_posix()}:expected_once:{marker}:actual_count={count}"]


def require_exact_line(text: str, rel: Path, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker)
    return [] if count == 1 else [f"{rel.as_posix()}:expected_line_once:{marker}:actual_count={count}"]


def require_json_value(label: str, actual: object, expected: object) -> list[str]:
    if actual == expected:
        return []
    return [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{rel.as_posix()}" for rel in REQUIRED_FILES if not (root / rel).is_file()]
    if failures:
        return failures

    validator_text = read_text(root, VALIDATOR_REL)
    closure_text = read_text(root, CLOSURE_NOTE_REL)
    scripts_text = read_text(root, SCRIPTS_README_REL)
    tests_text = read_text(root, TESTS_README_REL)
    workflow_text = read_text(root, WORKFLOW_REL)
    lane_text = read_text(root, LANE_NOTE_REL)

    for marker in VALIDATOR_MARKERS:
        failures.extend(require_exact_once(validator_text, VALIDATOR_REL, marker))
    for marker in CLOSURE_NOTE_MARKERS:
        failures.extend(require_exact_once(closure_text, CLOSURE_NOTE_REL, marker))
    for marker in SCRIPTS_README_MARKERS:
        failures.extend(require_exact_once(scripts_text, SCRIPTS_README_REL, marker))
    for marker in TESTS_README_MARKERS:
        failures.extend(require_exact_once(tests_text, TESTS_README_REL, marker))
    for marker in WORKFLOW_MARKERS:
        failures.extend(require_exact_line(workflow_text, WORKFLOW_REL, marker))
    for marker in LANE_NOTE_MARKERS:
        failures.extend(require_exact_once(lane_text, LANE_NOTE_REL, marker))

    try:
        manifest = json.loads(read_text(root, MANIFEST_REL))
    except json.JSONDecodeError as exc:
        return [f"{MANIFEST_REL.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    failures.extend(require_json_value(f"{MANIFEST_REL.as_posix()}:phase", manifest.get("phase"), "Phase 1"))
    failures.extend(require_json_value(f"{MANIFEST_REL.as_posix()}:status", manifest.get("status"), "closed"))
    failures.extend(require_json_value(f"{MANIFEST_REL.as_posix()}:helper_count", manifest.get("helper_count"), 13))

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        failures.append(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing:expected=dict:actual={type(lane_sequencing).__name__}"
        )
        return failures

    failures.extend(
        require_json_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.shared_replay_parked_helpers",
            lane_sequencing.get("shared_replay_parked_helpers"),
            EXPECTED_SHARED_HELPERS,
        )
    )
    failures.extend(
        require_json_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.direct_anchor_followup_helpers",
            lane_sequencing.get("direct_anchor_followup_helpers"),
            EXPECTED_DIRECT_HELPERS,
        )
    )
    failures.extend(
        require_json_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.rule_summary",
            lane_sequencing.get("rule_summary"),
            EXPECTED_LANE_RULE_SUMMARY,
        )
    )
    failures.extend(
        require_json_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.anti_overlap_rule",
            lane_sequencing.get("anti_overlap_rule"),
            EXPECTED_ANTI_OVERLAP_RULE,
        )
    )

    return failures


def make_fixture_tree(root: Path) -> None:
    write_text(root / VALIDATOR_REL, "\n".join(VALIDATOR_MARKERS) + "\n")
    write_text(root / CLOSURE_NOTE_REL, "\n".join(CLOSURE_NOTE_MARKERS) + "\n")
    write_text(root / SCRIPTS_README_REL, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root / TESTS_README_REL, "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root / WORKFLOW_REL, "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(root / LANE_NOTE_REL, "\n".join(LANE_NOTE_MARKERS) + "\n")
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": 13,
                "lane_sequencing": {
                    "shared_replay_parked_helpers": EXPECTED_SHARED_HELPERS,
                    "direct_anchor_followup_helpers": EXPECTED_DIRECT_HELPERS,
                    "rule_summary": EXPECTED_LANE_RULE_SUMMARY,
                    "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
                },
            },
            indent=2,
        )
        + "\n",
    )


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise ValueError(f"missing expected marker: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    cases = (
        ("baseline", None, True),
        ("missing_validator_file", lambda root: (root / VALIDATOR_REL).unlink(), False),
        (
            "missing_validator_marker",
            lambda root: write_text(root / VALIDATOR_REL, replace_once(read_text(root, VALIDATOR_REL), VALIDATOR_MARKERS[6] + "\n")),
            False,
        ),
        (
            "missing_closure_marker",
            lambda root: write_text(root / CLOSURE_NOTE_REL, replace_once(read_text(root, CLOSURE_NOTE_REL), CLOSURE_NOTE_MARKERS[2] + "\n")),
            False,
        ),
        (
            "missing_scripts_marker",
            lambda root: write_text(root / SCRIPTS_README_REL, replace_once(read_text(root, SCRIPTS_README_REL), SCRIPTS_README_MARKERS[1] + "\n")),
            False,
        ),
        (
            "missing_tests_marker",
            lambda root: write_text(root / TESTS_README_REL, replace_once(read_text(root, TESTS_README_REL), TESTS_README_MARKERS[0] + "\n")),
            False,
        ),
        (
            "missing_workflow_marker",
            lambda root: write_text(root / WORKFLOW_REL, replace_once(read_text(root, WORKFLOW_REL), WORKFLOW_MARKERS[0] + "\n")),
            False,
        ),
        (
            "drifted_lane_summary",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": "Phase 1",
                        "status": "closed",
                        "helper_count": 13,
                        "lane_sequencing": {
                            "shared_replay_parked_helpers": EXPECTED_SHARED_HELPERS,
                            "direct_anchor_followup_helpers": EXPECTED_DIRECT_HELPERS,
                            "rule_summary": "drifted summary",
                            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
    )

    checks_run = 0
    for name, mutate, should_pass in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-closure-validator-packet-{name}-") as tmpdir:
            root = Path(tmpdir)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if should_pass:
                if failures:
                    print(f"phase1-closure-validator-packet:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-validator-packet:{name}:expected_failure")
                return 1
            checks_run += 1

    print("PHASE1_CLOSURE_VALIDATOR_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", type=Path, help="write a current-like sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        make_fixture_tree(args.write_sample_root.resolve())
        print(f"PHASE1_CLOSURE_VALIDATOR_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    failures = collect_failures(args.root.resolve())
    if failures:
        print("PHASE1_CLOSURE_VALIDATOR_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATOR_PACKET=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_CLOSURE_VALIDATOR_PACKET_REQUIRED_MARKER_COUNT="
        f"{len(VALIDATOR_MARKERS) + len(CLOSURE_NOTE_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(WORKFLOW_MARKERS) + len(LANE_NOTE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

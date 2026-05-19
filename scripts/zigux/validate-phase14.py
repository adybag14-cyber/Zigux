#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/phase14-end-to-end-smoke-survey.md").exists() and (
            candidate / "zigux/Makefile"
        ).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SMOKE_SURVEY_PATH = "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
RELEASE_BOUNDARY_PATH = "Documentation/zigux/phase14-release-boundary-survey.md"
PRODUCTIZATION_GAP_PATH = "Documentation/zigux/phase14-productization-gap-survey.md"
STUDY_ONLY_ACCOUNTING_PATH = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
ROLLBACK_CHECKER_PATH = "scripts/zigux/check-phase14-rollback-threshold-sequencing.py"
TESTS_README_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"
WORKQUEUE_BRIDGE_PATH = "kernel/workqueue_bridge.zig"
WORKQUEUE_REVIEWABILITY_PATH = "zigux/tests/phase14_workqueue_reviewability.zig"
WORKQUEUE_MANIFEST_PATH = "zigux/tests/phase14_workqueue_bridge_manifest.json"
VALIDATOR_PATH = "scripts/zigux/validate-phase14.py"

REQUIRED_FILES = [
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    SMOKE_SURVEY_PATH,
    RELEASE_BOUNDARY_PATH,
    PRODUCTIZATION_GAP_PATH,
    STUDY_ONLY_ACCOUNTING_PATH,
    SCRIPTS_README_PATH,
    ROLLBACK_CHECKER_PATH,
    TESTS_README_PATH,
    MAKEFILE_PATH,
    WORKQUEUE_BRIDGE_PATH,
    WORKQUEUE_REVIEWABILITY_PATH,
    WORKQUEUE_MANIFEST_PATH,
    VALIDATOR_PATH,
]

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
        "scripts/zigux/validate-phase14.py",
        "zigux/tests/phase14_workqueue_reviewability.zig",
        "while `net/core/skbuff.c` and `kernel/rcu/tree.c` remain freeze-in-C anchors",
    ],
    REVIEW_CHECKLIST_PATH: [
        "Use this checklist before opening or merging Zigux product work.",
        "is the target phase named explicitly?",
        "does the change avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision?",
        "is there a stated rollback owner and fallback path?",
    ],
    SMOKE_SURVEY_PATH: [
        "  * rollback owner: `Repo Tooling Pod`",
        "  * status bucket: `study_only`",
        "  * rollback threshold: `0` tolerated same-packet drifts",
        "  * fallback path: keep this shared smoke lane aligned with the current gap notes",
        "  * automatic return-to-blocked triggers:",
        "    * workqueue-boundary-shard drift",
        "    * `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14`",
        "`phase14-workqueue-reviewability-tests` -> `phase14_workqueue_reviewability.zig` -> `full_bundle_only`",
    ],
    RELEASE_BOUNDARY_PATH: [
        "- current Makefile posture: `zigux/Makefile` is readable again on current `master`",
        "- current reminder-surface alignment:",
        "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
        "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
    ],
    PRODUCTIZATION_GAP_PATH: [
        "scripts/zigux/validate-phase14.py` through the current contents path",
        "zigux/tests/phase14_workqueue_reviewability.zig",
        "but no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets",
        "The higher-value same-lane task is reminder-surface truthfulness",
    ],
    STUDY_ONLY_ACCOUNTING_PATH: [
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only",
        "`kernel/workqueue.c` remains a boundary-study target first, not a rewrite target",
        "`kernel/trace/ring_buffer.c` remains a boundary-study target first, not a rewrite target",
    ],
    SCRIPTS_README_PATH: [
        "Phase 14 flow - the current scripts-root shared smoke packet stays reviewable",
        "`scripts/zigux/validate-phase14.py` and `scripts/zigux/check-phase14-release-boundary-exact-counts.py` keep the recoverable shared-smoke layer visible",
        "there are still no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets",
        "`ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14` remain the bounded packet-local rerun examples",
    ],
    ROLLBACK_CHECKER_PATH: [
        "PHASE14_CHECK_PACKET=rollback_threshold_sequencing",
        "ROLLBACK_OWNER = \"Repo Tooling Pod\"",
        "ROLLBACK_TRIGGER_MARKERS = [",
        "MAKEFILE_ABSENT_ROUTE_MARKERS = [",
        "PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=pass",
    ],
    TESTS_README_PATH: [
        "Keep the current bounded Phase 14 reminder packet explicit",
        "keep the directly readable `scripts/zigux/validate-phase14.py` plus the directly readable workqueue reviewability shard explicit",
        "`scripts/zigux/check-phase14-release-boundary-exact-counts.py` explicit as the directly readable release-boundary truthfulness guard",
        "Current `master` does materialize `zigux/Makefile`, but its live body currently exposes",
        "Documentation/zigux/phase14-release-boundary-survey.md",
    ],
    MAKEFILE_PATH: [
        "phase3-validate:",
        "phase4-validate:",
        "phase6-base64-test:",
        "phase8-validate:",
        "phase10-validate:",
        "phase12-smoke:",
    ],
    WORKQUEUE_BRIDGE_PATH: [
        'return "phase14-workqueue-scheduler-visible-worker-state-refinement";',
        "return .{",
        '.posture = "blocked_maintenance",',
        "zigux/tests/phase14_workqueue_reviewability.zig",
    ],
    WORKQUEUE_REVIEWABILITY_PATH: [
        'try std.testing.expectEqualStrings("P14-L04", manifest.lane_key);',
        '"zig test zigux/tests/phase14_workqueue_reviewability.zig"',
        '"blocked maintenance"',
        '"same study-only stay-in-C posture"',
    ],
    WORKQUEUE_MANIFEST_PATH: [
        '"lane_key": "P14-L04"',
        '"current_lane_posture": "blocked_maintenance"',
        '"zig test zigux/tests/phase14_workqueue_reviewability.zig"',
        '"phase14-workqueue-live-execution-blocker"',
    ],
    VALIDATOR_PATH: [
        "PHASE14_VALIDATION=pass",
        "PHASE14_VALIDATOR_SELF_TEST=pass",
        "REQUIRED_FILES = [",
        "FORBIDDEN_MARKERS = {",
    ],
}

FORBIDDEN_MARKERS = {
    TESTS_README_PATH: [
        "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`,"
    ],
    MAKEFILE_PATH: [
        "phase14-validate:",
        "phase14-smoke:",
        "phase14-test:",
        "phase14: phase14-validate phase14-smoke phase14-test",
    ],
}


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                failures.append(f"forbidden_marker:{rel_path}:{marker}")
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    return f"{title}\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


def fixture_text(rel_path: str) -> str:
    titles = {
        DOCS_README_PATH: "# Zigux Documentation",
        REVIEW_CHECKLIST_PATH: "# Zigux Review Checklist",
        SMOKE_SURVEY_PATH: "# Phase 14 End-to-End Smoke Survey",
        RELEASE_BOUNDARY_PATH: "# Phase 14 Release Boundary Survey",
        PRODUCTIZATION_GAP_PATH: "# Phase 14 Productization Gap Survey",
        STUDY_ONLY_ACCOUNTING_PATH: "# Phase 15 Study-Only Anchor Accounting",
        SCRIPTS_README_PATH: "# scripts/zigux",
        TESTS_README_PATH: "# zigux/tests",
    }
    if rel_path in REQUIRED_MARKERS:
        title = titles.get(rel_path)
        if title is not None:
            return marker_fixture(title, REQUIRED_MARKERS[rel_path])
        return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
    if rel_path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel_path.endswith(".zig"):
        return "// fixture\n"
    if rel_path.endswith(".json"):
        return "{}\n"
    return ""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"- {marker}\n", "", 1)
    if updated == text:
        updated = text.replace(f"{marker}\n", "", 1)
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-validator-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        missing_file_cases = [
            PRODUCTIZATION_GAP_PATH,
            SCRIPTS_README_PATH,
            ROLLBACK_CHECKER_PATH,
            MAKEFILE_PATH,
            WORKQUEUE_REVIEWABILITY_PATH,
            WORKQUEUE_MANIFEST_PATH,
        ]
        for rel_path in missing_file_cases:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (SMOKE_SURVEY_PATH, REQUIRED_MARKERS[SMOKE_SURVEY_PATH][2]),
            (RELEASE_BOUNDARY_PATH, REQUIRED_MARKERS[RELEASE_BOUNDARY_PATH][2]),
            (PRODUCTIZATION_GAP_PATH, REQUIRED_MARKERS[PRODUCTIZATION_GAP_PATH][0]),
            (SCRIPTS_README_PATH, REQUIRED_MARKERS[SCRIPTS_README_PATH][2]),
            (ROLLBACK_CHECKER_PATH, REQUIRED_MARKERS[ROLLBACK_CHECKER_PATH][0]),
            (TESTS_README_PATH, REQUIRED_MARKERS[TESTS_README_PATH][2]),
            (WORKQUEUE_MANIFEST_PATH, REQUIRED_MARKERS[WORKQUEUE_MANIFEST_PATH][1]),
            (WORKQUEUE_REVIEWABILITY_PATH, REQUIRED_MARKERS[WORKQUEUE_REVIEWABILITY_PATH][0]),
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        forbidden_cases = [
            (TESTS_README_PATH, FORBIDDEN_MARKERS[TESTS_README_PATH][0]),
            (MAKEFILE_PATH, FORBIDDEN_MARKERS[MAKEFILE_PATH][0]),
            (MAKEFILE_PATH, FORBIDDEN_MARKERS[MAKEFILE_PATH][1]),
            (MAKEFILE_PATH, FORBIDDEN_MARKERS[MAKEFILE_PATH][2]),
            (MAKEFILE_PATH, FORBIDDEN_MARKERS[MAKEFILE_PATH][3]),
        ]
        for rel_path, marker in forbidden_cases:
            write_fixture_tree(base)
            write_text(
                base / rel_path,
                (base / rel_path).read_text(encoding="utf-8") + f"{marker}\n",
            )
            expect_failure(base, f"forbidden_marker:{rel_path}:{marker}")

        case_count = len(missing_file_cases) + len(marker_cases) + len(forbidden_cases)
        print("PHASE14_VALIDATOR_SELF_TEST=pass")
        print(f"PHASE14_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current bounded Phase 14 shared smoke packet around the rollback "
            "threshold checker, mixed-source validator surface, workqueue reviewability shard, "
            "and current Makefile route reality."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE14_VALIDATION=fail")
        print("PHASE14_PACKET_DRIFT_START")
        for failure in failures:
            print(failure)
        print("PHASE14_PACKET_DRIFT_END")
        return 1

    print("PHASE14_VALIDATION=pass")
    print(f"PHASE14_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE14_REQUIRED_MARKER_COUNT={sum(len(m) for m in REQUIRED_MARKERS.values())}")
    print(f"PHASE14_FORBIDDEN_MARKER_COUNT={sum(len(m) for m in FORBIDDEN_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
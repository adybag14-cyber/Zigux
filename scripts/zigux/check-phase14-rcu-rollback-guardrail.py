#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
NOTE_PATH = "Documentation/zigux/phase14-rcu-tree-survey.md"

ROLLBACK_THRESHOLD_MARKER = (
    "- manifest-backed guardrail: `phase14-rcu-tree-rollback-threshold-guardrail` "
    "keeps this freeze-in-C packet fail-closed until the same review packet carries "
    "the required reopen evidence instead of a lighter status-review claim."
)
COMPANION_CONFIRMATION_HEADING = (
    "executable packet companions confirmed on current `master` through public GitHub fallback:"
)
COMPANION_PARTIAL_MARKER = (
    "authenticated contents-path readback still stays partial for those executable companions"
)
REQUIRED_EVIDENCE_HEADING = "- required evidence before any status review:"
REQUIRED_EVIDENCE_MARKERS = [
    "- `Architecture Council` reopen record linked from the active review packet",
    "- parity scorecard evidence and benchmark notes attached to the same review packet",
    "- validation replay command and evidence archive path recorded beside the latest blocker disposition",
]
RETURN_TO_BLOCKED_HEADING = "- automatic return-to-blocked triggers:"
RETURN_TO_BLOCKED_MARKERS = [
    "- any `kernel/rcu/tree_bridge.zig` claim or status review that lacks the `Architecture Council` reopen record",
    "- missing parity scorecard evidence, benchmark notes, or replay command in the active review packet",
    "- freeze-map, survey note, or dedicated-check drift that drops the blocked bridge disposition, the companion-readback warning, or the rollback owner",
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / NOTE_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

REQUIRED_MARKERS = [
    "`PHASE14_LANE_KEY=P14-L16`",
    "`PHASE14_STATUS_BUCKET=freeze_in_c`",
    "`PHASE14_ANCHOR=kernel/rcu/tree.c`",
    "`PHASE14_BLOCKED_GAP=phase14-rcu-tree-bridge-blocker`",
    "directly readable dedicated packet surfaces on current `master`:",
    COMPANION_CONFIRMATION_HEADING,
    "`zigux/tests/phase14_rcu_tree_manifest.json`",
    "`zigux/tests/phase14_rcu_tree_survey.zig`",
    COMPANION_PARTIAL_MARKER,
    "dedicated rollback guard surface:",
    "`scripts/zigux/check-phase14-rcu-rollback-guardrail.py`",
    "`phase14-rcu-tree-rollback-threshold-guardrail`",
    ROLLBACK_THRESHOLD_MARKER,
    "rollback owner: `Repo Tooling Pod`",
    REQUIRED_EVIDENCE_HEADING,
    *REQUIRED_EVIDENCE_MARKERS,
    RETURN_TO_BLOCKED_HEADING,
    *RETURN_TO_BLOCKED_MARKERS,
]

FORBIDDEN_MARKERS = [
    "current review packet:",
]


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    note = root / NOTE_PATH
    if not note.exists():
        return [f"missing_file:{NOTE_PATH}"]

    text = note.read_text(encoding="utf-8")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing_marker:{marker}")
    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            failures.append(f"forbidden_marker:{marker}")
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


FIXTURE_NOTE = """# Phase 14 RCU Tree Survey
This document records the current Phase 14 boundary-study packet for `kernel/rcu/tree.c` as it exists on verified `master`.
## Status
- `PHASE14_LANE_KEY=P14-L16`
- `PHASE14_STATUS_BUCKET=freeze_in_c`
- `PHASE14_ANCHOR=kernel/rcu/tree.c`
- `PHASE14_ROADMAP_DESTINATION=kernel/rcu/tree_bridge.zig`
- `PHASE14_BLOCKED_GAP=phase14-rcu-tree-bridge-blocker`
- survey provenance captured against verified `master` head `4c889233d157960514b241bcd5aff7cac5fda312`
- directly readable dedicated packet surfaces on current `master`:
  - `Documentation/zigux/phase14-rcu-tree-survey.md`
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase14-core-boundary-traceability.md`
  - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- """ + COMPANION_CONFIRMATION_HEADING + """
  - `zigux/tests/phase14_rcu_tree_manifest.json`
  - `zigux/tests/phase14_rcu_tree_survey.zig`
- authenticated contents-path readback still stays partial for those executable companions, so this note keeps the freeze-in-C blocker as the owner surface rather than claiming restored local replay or ownership
- dedicated rollback guard surface:
  - `scripts/zigux/check-phase14-rcu-rollback-guardrail.py`
## Rollback guardrail
""" + ROLLBACK_THRESHOLD_MARKER + """
- machine-check surface: `scripts/zigux/check-phase14-rcu-rollback-guardrail.py` keeps the dedicated note fail-closed on its lane key, blocked gap, companion-readback wording, rollback owner, and required reopen evidence.
- rollback owner: `Repo Tooling Pod`
""" + REQUIRED_EVIDENCE_HEADING + """
""" + "\n".join(f"  {marker}" for marker in REQUIRED_EVIDENCE_MARKERS) + """
""" + RETURN_TO_BLOCKED_HEADING + """
""" + "\n".join(f"  {marker}" for marker in RETURN_TO_BLOCKED_MARKERS) + """
"""


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-rcu-guardrail-"))
    try:
        write_text(base / NOTE_PATH, FIXTURE_NOTE)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture should pass but failed: {failures!r}")

        cases = [
            ("remove-lane-key", "`PHASE14_LANE_KEY=P14-L16`", "missing_marker:`PHASE14_LANE_KEY=P14-L16`"),
            (
                "remove-companion-heading",
                COMPANION_CONFIRMATION_HEADING,
                f"missing_marker:{COMPANION_CONFIRMATION_HEADING}",
            ),
            (
                "remove-companion-partial-marker",
                COMPANION_PARTIAL_MARKER,
                f"missing_marker:{COMPANION_PARTIAL_MARKER}",
            ),
            (
                "remove-checker",
                "- dedicated rollback guard surface:\n  - `scripts/zigux/check-phase14-rcu-rollback-guardrail.py`\n",
                "missing_marker:dedicated rollback guard surface:",
            ),
            (
                "remove-threshold-guardrail",
                ROLLBACK_THRESHOLD_MARKER,
                f"missing_marker:{ROLLBACK_THRESHOLD_MARKER}",
            ),
            (
                "remove-required-evidence-heading",
                REQUIRED_EVIDENCE_HEADING,
                f"missing_marker:{REQUIRED_EVIDENCE_HEADING}",
            ),
            (
                "remove-return-to-blocked-trigger",
                RETURN_TO_BLOCKED_MARKERS[0],
                f"missing_marker:{RETURN_TO_BLOCKED_MARKERS[0]}",
            ),
        ]
        for _, marker, expected in cases:
            write_text(base / NOTE_PATH, FIXTURE_NOTE.replace(marker, "", 1))
            failures = validate(base)
            if expected not in failures:
                raise SystemExit(f"expected {expected!r}, got {failures!r}")

        write_text(base / NOTE_PATH, FIXTURE_NOTE + "\n- current review packet:\n")
        failures = validate(base)
        if "forbidden_marker:current review packet:" not in failures:
            raise SystemExit(f"expected forbidden marker failure, got {failures!r}")

        print("PHASE14_RCU_ROLLBACK_GUARDRAIL_SELF_TEST=pass")
        print("PHASE14_RCU_ROLLBACK_GUARDRAIL_SELF_TEST_CASE_COUNT=8")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the dedicated Phase 14 RCU rollback note stays aligned with the "
            "current freeze-in-C guardrail markers and keeps companion readback wording honest."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run the fixture-backed self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE14_RCU_ROLLBACK_GUARDRAIL=fail")
        print("PHASE14_RCU_ROLLBACK_GUARDRAIL_DRIFT_START")
        for failure in failures:
            print(failure)
        print("PHASE14_RCU_ROLLBACK_GUARDRAIL_DRIFT_END")
        return 1

    print("PHASE14_RCU_ROLLBACK_GUARDRAIL=pass")
    print(f"PHASE14_RCU_ROLLBACK_GUARDRAIL_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE14_RCU_ROLLBACK_GUARDRAIL_FORBIDDEN_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
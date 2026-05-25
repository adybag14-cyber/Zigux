#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=productization_gap_roadmap_alignment

Fail-closed checker for the current Phase 14 productization-gap survey.

This guard keeps the roadmap-backed study-only posture explicit in
`Documentation/zigux/phase14-productization-gap-survey.md` while making sure
the current returned shared-smoke packet, dedicated stay-in-C and rollback
guards, machine-readable manifest, and exact-readback executable gaps stay
listed together instead of drifting back toward broader replay claims.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=productization_gap_roadmap_alignment"
NOTE_PATH = Path("Documentation/zigux/phase14-productization-gap-survey.md")

ROADMAP_MARKERS = [
    "Phase 14 in `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` is the `Core-Adjacent Bounded Internals` lane.",
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
    "- `net/core/skbuff.c`",
    "- `kernel/rcu/tree.c`",
    "Given the roadmap, the correct Phase 14 posture remains study-only and wrapper-first.",
]

RETURNED_PACKET_MARKERS = [
    "- `Documentation/zigux/phase14-release-boundary-survey.md`",
    "- `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`",
    "- `Documentation/zigux/freeze-map.md`",
    "- `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "- `scripts/zigux/check-phase14-shared-smoke-route.py` through the current contents path",
    "- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` through the current contents path",
    "- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py` through the current contents path",
    "- `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py` through the current contents path",
    "- `scripts/zigux/check-phase14-rcu-rollback-guardrail.py` through the current contents path",
    "- `scripts/zigux/validate-phase14.py` through the current contents path",
    "- `scripts/zigux/check-phase14-release-boundary-exact-counts.py` through the current contents path",
    "- `zigux/tests/phase14_end_to_end_smoke_manifest.json` through the current contents path",
    "- `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` are directly readable again as the workqueue-local reviewability shard",
    "- `zigux/tests/phase14_ring_buffer_survey.zig` now returns through the current contents path as a directly readable ring-buffer survey companion",
    "- `Documentation/zigux/phase14-rcu-tree-survey.md` is directly readable again through the current contents path",
]

MAKEFILE_AND_GAP_MARKERS = [
    "but no `phase14-smoke`, `phase14-test`, or `phase14` targets",
    "- `zigux/tests/phase14_build.zig`",
    "- `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    "- `zigux/tests/phase14_skbuff_bridge.zig`",
    "- `zigux/tests/phase14_rcu_tree_survey.zig`",
    "- `net/core/skbuff_bridge.zig`",
]

NEXT_STEP_MARKERS = [
    "The next honest follow-up is now whichever smaller shared reminder surface or executable-layer readback boundary next drifts against that recovered packet.",
    "`Documentation/zigux/phase14-release-boundary-survey.md`",
    "`Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`",
    "`Documentation/zigux/phase14-rcu-tree-survey.md`",
    "`scripts/zigux/check-phase14-rollback-threshold-sequencing.py`",
    "`scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py`",
    "`scripts/zigux/check-phase14-rcu-rollback-guardrail.py`",
    "without promoting the missing executable-layer paths or the absent `phase14-smoke`, `phase14-test`, and `phase14` wrappers.",
]


def infer_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / NOTE_PATH).exists():
            return candidate
    return here.parent


ROOT = infer_root()


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    if not path.exists():
        raise FileNotFoundError(rel.as_posix())
    return path.read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{marker}")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    note = root / NOTE_PATH
    if not note.exists():
        return [f"missing_file:{NOTE_PATH.as_posix()}"]

    text = note.read_text(encoding="utf-8")
    require_markers(errors, text, ROADMAP_MARKERS)
    require_markers(errors, text, RETURNED_PACKET_MARKERS)
    require_markers(errors, text, MAKEFILE_AND_GAP_MARKERS)
    require_markers(errors, text, NEXT_STEP_MARKERS)
    if "study-only and wrapper-first" not in text:
        errors.append("missing_guard_phrase:study_only_wrapper_first")
    if "stay-in-C guard" not in text:
        errors.append("missing_guard_phrase:stay_in_c_guard")
    return errors


FIXTURE_TEXT = """# Phase 14 Productization Gap Survey

## Roadmap Baseline

Phase 14 in `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` is the `Core-Adjacent Bounded Internals` lane.

- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- `net/core/skbuff.c`
- `kernel/rcu/tree.c`

## Current Direct-Readback Evidence

- `Documentation/zigux/phase14-release-boundary-survey.md`
- `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `scripts/zigux/check-phase14-shared-smoke-route.py` through the current contents path
- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` through the current contents path
- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py` through the current contents path
- `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py` through the current contents path
- `scripts/zigux/check-phase14-rcu-rollback-guardrail.py` through the current contents path
- `scripts/zigux/validate-phase14.py` through the current contents path
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py` through the current contents path
- `zigux/tests/phase14_end_to_end_smoke_manifest.json` through the current contents path
- `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` are directly readable again as the workqueue-local reviewability shard
- `zigux/tests/phase14_ring_buffer_survey.zig` now returns through the current contents path as a directly readable ring-buffer survey companion
- `Documentation/zigux/phase14-rcu-tree-survey.md` is directly readable again through the current contents path

## Current Readback Gaps

- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_end_to_end_smoke_survey.zig`
- `zigux/tests/phase14_skbuff_bridge.zig`
- `zigux/tests/phase14_rcu_tree_survey.zig`
- `net/core/skbuff_bridge.zig`

## Product Judgment

Given the roadmap, the correct Phase 14 posture remains study-only and wrapper-first.
The directly readable packet keeps the dedicated stay-in-C guard explicit, but no `phase14-smoke`, `phase14-test`, or `phase14` targets.

## Recommended Next Bounded Step

The next honest follow-up is now whichever smaller shared reminder surface or executable-layer readback boundary next drifts against that recovered packet.
Keep `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-rcu-tree-survey.md`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py`, and `scripts/zigux/check-phase14-rcu-rollback-guardrail.py` explicit without promoting the missing executable-layer paths or the absent `phase14-smoke`, `phase14-test`, and `phase14` wrappers.
"""


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-productization-gap-"))
    try:
        write_text(base, NOTE_PATH, FIXTURE_TEXT)
        failures = check(base)
        if failures:
            raise SystemExit(f"fixture should pass but failed: {failures!r}")

        cases = [
            (
                "remove-roadmap-lane",
                ROADMAP_MARKERS[0],
                f"missing_marker:{ROADMAP_MARKERS[0]}",
            ),
            (
                "remove-skbuff-guard",
                RETURNED_PACKET_MARKERS[7],
                f"missing_marker:{RETURNED_PACKET_MARKERS[7]}",
            ),
            (
                "remove-makefile-gap",
                MAKEFILE_AND_GAP_MARKERS[0],
                f"missing_marker:{MAKEFILE_AND_GAP_MARKERS[0]}",
            ),
            (
                "remove-next-step",
                NEXT_STEP_MARKERS[0],
                f"missing_marker:{NEXT_STEP_MARKERS[0]}",
            ),
        ]
        for _, marker, expected in cases:
            write_text(base, NOTE_PATH, FIXTURE_TEXT.replace(marker, "", 1))
            failures = check(base)
            if expected not in failures:
                raise SystemExit(f"expected {expected!r}, got {failures!r}")

        write_text(
            base,
            NOTE_PATH,
            FIXTURE_TEXT.replace("study-only and wrapper-first", "bounded and careful", 1),
        )
        failures = check(base)
        if "missing_guard_phrase:study_only_wrapper_first" not in failures:
            raise SystemExit(f"expected study-only guard failure, got {failures!r}")

        print("PHASE14_PRODUCTIZATION_GAP_ROADMAP_ALIGNMENT_SELF_TEST=pass")
        print("PHASE14_PRODUCTIZATION_GAP_ROADMAP_ALIGNMENT_SELF_TEST_CASE_COUNT=5")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 14 productization-gap survey stays aligned with "
            "the roadmap-backed study-only packet and current returned readback split."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run the fixture-backed self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = check(args.root)
    if failures:
        print("PHASE14_PRODUCTIZATION_GAP_ROADMAP_ALIGNMENT=fail")
        print("PHASE14_PRODUCTIZATION_GAP_ROADMAP_ALIGNMENT_DRIFT_START")
        for failure in failures:
            print(failure)
        print("PHASE14_PRODUCTIZATION_GAP_ROADMAP_ALIGNMENT_DRIFT_END")
        return 1

    print("PHASE14_PRODUCTIZATION_GAP_ROADMAP_ALIGNMENT=pass")
    print(
        "PHASE14_PRODUCTIZATION_GAP_ROADMAP_ALIGNMENT_MARKER_COUNT="
        f"{len(ROADMAP_MARKERS) + len(RETURNED_PACKET_MARKERS) + len(MAKEFILE_AND_GAP_MARKERS) + len(NEXT_STEP_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
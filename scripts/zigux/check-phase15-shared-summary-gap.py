#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

GAP_NOTE_REL = "Documentation/zigux/phase15-shared-summary-gap.md"
HANDOFF_NOTE_REL = "Documentation/zigux/phase15-handoff-next-steps-survey.md"

CURRENT_READBACK_MARKER = "current-master-readback-2026-05-27"
WATCHPOINTS_HEADING = "## Current shared-summary watchpoints"

STATUS_MARKERS = (
    "PHASE15_STATUS=shared_summary_gap_recorded",
    "PHASE15_LANE_KEY=P15-L02",
    "PHASE15_SLICE=materialized-governance-packet-truthfulness-refresh",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
)

MATERIALIZED_GOVERNANCE_PATHS = (
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-architecture-council-decision-index.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-deep-core-blocker-survey.md",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
)

MATERIALIZED_FOCUSED_COMPANIONS = (
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_build.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_build.zig",
    "scripts/zigux/check-phase15-architecture-council-packet.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
    "scripts/zigux/check-phase15-readiness-gate-packet.py",
    "scripts/zigux/validate-phase15.py",
)

ROUTE_GAP_MARKERS = (
    "no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
    "`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route name on current `master`",
)

SHARED_WATCHPOINT_MARKERS = (
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-index.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
    "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
    "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase15-architecture-council-packet.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
    "`scripts/zigux/check-phase15-readiness-gate-packet.py`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing.zig`",
    "`zigux/tests/phase15_readiness_gate_manifest.json`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "`zigux/tests/phase15_handoff_next_steps.zig`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "`zigux/tests/phase15_build.zig`",
    "`scripts/zigux/README.md` now keeps the directly materialized `scripts/zigux/validate-phase15.py` maintenance gate, the directly materialized `scripts/zigux/check-phase15-architecture-council-packet.py` Architecture Council packet checker, and the directly materialized `zigux/tests/phase15_build.zig` shared build companion explicit while the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes plus the shared-CI route remain the broader route-level gaps on current `master`",
    "broader wrapper-route wording around `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, and the dedicated shared-CI Phase 15 route names",
)

REQUIRED_NOTE_MARKERS = (
    f"surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`",
    "The tests-root governance reminder is now landed in `zigux/tests/README.md`",
    "The current same-lane truthfulness task is no longer to treat the dedicated shared build companion as missing.",
    "This refresh closes the shared-gap undercount that had fallen behind the current 2026-05-27 governance packet.",
    "These broader reminder surfaces still are not directly materialized as dedicated Phase 15 route bodies on current `master`, so shared-summary surfaces must keep them framed as gap-tracked route vocabulary rather than shipped evidence:",
    "The remaining Phase 15 discipline work is broad-summary truthfulness and route wording exactness, not missing-file recovery by wishful thinking:",
    "do not reintroduce stale missing-path claims for materialized governance assets",
    "do keep the landed tests-root Phase 15 reminder aligned with `scripts/zigux/check-phase15-tests-readme-alignment.py`",
    "Keep this note parked unless a fresh reread shows one of the broad Phase 15 reminder surfaces drifting away from the materialized governance packet above",
)

STALE_TEXT_MARKERS = (
    "current-master-readback-2026-05-17",
    "current-master-readback-2026-05-21",
    "current-master-readback-2026-05-23",
    "current-master-readback-2026-05-25",
    "## Still-missing focused companions on current master",
    "The current shared-summary drift is anchored to these still-missing paths:",
)

HANDOFF_REQUIRED_MARKERS = (
    "PHASE15_STATUS=handoff_next_steps_survey_landed",
    "The dedicated validator, the dedicated Architecture Council packet checker, the shared build companion, the governance-lane sequencing companions",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing.zig`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "`zigux/tests/phase15_handoff_next_steps.zig`",
    "`zigux/tests/phase15_build.zig`",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _extract_section(note: str, heading: str) -> str:
    _, marker, tail = note.partition(f"{heading}\n\n")
    if not marker:
        return ""
    section, _, _ = tail.partition("\n## ")
    return section


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    gap_note_path = root / GAP_NOTE_REL
    handoff_note_path = root / HANDOFF_NOTE_REL
    if not gap_note_path.exists():
        return [f"missing_file:{GAP_NOTE_REL}"]
    if not handoff_note_path.exists():
        return [f"missing_file:{HANDOFF_NOTE_REL}"]

    gap_note = _read(gap_note_path)
    handoff_note = _read(handoff_note_path)
    watchpoints = _extract_section(gap_note, WATCHPOINTS_HEADING)

    for marker in STATUS_MARKERS:
        if marker not in gap_note:
            failures.append(f"gap_note:missing_status:{marker}")

    for rel in MATERIALIZED_GOVERNANCE_PATHS:
        if not (root / rel).exists():
            failures.append(f"missing_materialized_path:{rel}")
        if f"`{rel}`" not in gap_note:
            failures.append(f"gap_note:missing_materialized_marker:`{rel}`")

    for rel in MATERIALIZED_FOCUSED_COMPANIONS:
        if not (root / rel).exists():
            failures.append(f"missing_focused_companion:{rel}")
        if f"`{rel}`" not in gap_note:
            failures.append(f"gap_note:missing_focused_marker:`{rel}`")

    for marker in ROUTE_GAP_MARKERS:
        if marker not in gap_note:
            failures.append(f"gap_note:missing_route_gap:{marker}")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in gap_note:
            failures.append(f"gap_note:missing_required:{marker}")

    if not watchpoints:
        failures.append(f"gap_note:missing_section:{WATCHPOINTS_HEADING}")
    else:
        for marker in SHARED_WATCHPOINT_MARKERS:
            if marker not in watchpoints:
                failures.append(f"gap_note:missing_watchpoint:{marker}")

    for marker in STALE_TEXT_MARKERS:
        if marker in gap_note:
            failures.append(f"gap_note:stale_text:{marker}")

    for marker in HANDOFF_REQUIRED_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff_note:missing:{marker}")

    return failures


def _seed(root: Path) -> None:
    governance_assets = "\n".join(f"- `{rel}`" for rel in MATERIALIZED_GOVERNANCE_PATHS)
    focused_assets = "\n".join(f"- `{rel}`" for rel in MATERIALIZED_FOCUSED_COMPANIONS)
    route_gaps = "\n".join(f"- {marker}" for marker in ROUTE_GAP_MARKERS)
    watchpoints = "\n".join(f"- {marker}" for marker in SHARED_WATCHPOINT_MARKERS)
    required = "\n".join(f"- {marker}" for marker in REQUIRED_NOTE_MARKERS)

    _write(
        root / GAP_NOTE_REL,
        f"""# Phase 15 Shared Summary Gap

This note records the current bounded Phase 15 shared-summary drift between the broad reminder surfaces and the live governance packet on `master`.

## Status

- `PHASE15_STATUS=shared_summary_gap_recorded`
- `PHASE15_LANE_KEY=P15-L02`
- `PHASE15_SLICE=materialized-governance-packet-truthfulness-refresh`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`

## Why this note exists

The tests-root governance reminder is now landed in `zigux/tests/README.md`, so the honest maintenance step is to keep that section aligned with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-architecture-council-review-process.md`, and the rest of this governance family rather than carrying the tests-root surface as still-missing drift.

The current same-lane truthfulness task is no longer to treat the dedicated shared build companion as missing. It is to keep the broad reminder surfaces aligned with the now-materialized packet while still refusing to imply Architecture Council approval, direct deep-core delivery, or blocked Phase 15 wrapper-route recovery just because more reminder companions are landed.

This refresh closes the shared-gap undercount that had fallen behind the current 2026-05-27 governance packet.

## Materialized Phase 15 governance assets

{governance_assets}

## Materialized focused companions on current master

{focused_assets}

## Still-missing broader wrapper and shared-CI route companions on current master

These broader reminder surfaces still are not directly materialized as dedicated Phase 15 route bodies on current `master`, so shared-summary surfaces must keep them framed as gap-tracked route vocabulary rather than shipped evidence:

{route_gaps}

## Current shared-summary watchpoints

The remaining Phase 15 discipline work is broad-summary truthfulness and route wording exactness, not missing-file recovery by wishful thinking:

{watchpoints}

{required}

## Recovery rule

- do not reintroduce stale missing-path claims for materialized governance assets
- do keep the landed tests-root Phase 15 reminder aligned with `scripts/zigux/check-phase15-tests-readme-alignment.py`

## Next bounded step

Keep this note parked unless a fresh reread shows one of the broad Phase 15 reminder surfaces drifting away from the materialized governance packet above
""",
    )

    _write(
        root / HANDOFF_NOTE_REL,
        """# Phase 15 Handoff Next Steps Survey

PHASE15_STATUS=handoff_next_steps_survey_landed

The dedicated validator, the dedicated Architecture Council packet checker, the shared build companion, the governance-lane sequencing companions, the Architecture Council decision index, and the directly materialized reminder-surface checkers now define the tighter same-lane boundaries.

- `zigux/tests/phase15_governance_lane_sequencing_manifest.json`
- `zigux/tests/phase15_governance_lane_sequencing.zig`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `zigux/tests/phase15_handoff_next_steps.zig`
- `zigux/tests/phase15_build.zig`
""",
    )

    for rel in MATERIALIZED_GOVERNANCE_PATHS + MATERIALIZED_FOCUSED_COMPANIONS:
        if not (root / rel).exists():
            _write(root / rel, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_shared_summary_gap_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = validate(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        stale_marker_root = root / "stale_marker"
        _seed(stale_marker_root)
        _write(
            stale_marker_root / GAP_NOTE_REL,
            _read(stale_marker_root / GAP_NOTE_REL).replace(CURRENT_READBACK_MARKER, "current-master-readback-2026-05-25", 1),
        )
        failures = validate(stale_marker_root)
        expected = ["gap_note:stale_text:current-master-readback-2026-05-25"]
        if failures != expected:
            raise AssertionError(f"unexpected stale-marker failure: {failures}")

        missing_governance_root = root / "missing_governance"
        _seed(missing_governance_root)
        (missing_governance_root / MATERIALIZED_GOVERNANCE_PATHS[0]).unlink()
        failures = validate(missing_governance_root)
        expected = [f"missing_materialized_path:{MATERIALIZED_GOVERNANCE_PATHS[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-governance failure: {failures}")

        missing_focused_root = root / "missing_focused"
        _seed(missing_focused_root)
        (missing_focused_root / MATERIALIZED_FOCUSED_COMPANIONS[0]).unlink()
        failures = validate(missing_focused_root)
        expected = [f"missing_focused_companion:{MATERIALIZED_FOCUSED_COMPANIONS[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-focused failure: {failures}")

        missing_watchpoint_root = root / "missing_watchpoint"
        _seed(missing_watchpoint_root)
        _write(
            missing_watchpoint_root / GAP_NOTE_REL,
            _read(missing_watchpoint_root / GAP_NOTE_REL).replace(
                "- broader wrapper-route wording around `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, and the dedicated shared-CI Phase 15 route names\n",
                "",
                1,
            ),
        )
        failures = validate(missing_watchpoint_root)
        expected = [
            "gap_note:missing_watchpoint:broader wrapper-route wording around `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, and the dedicated shared-CI Phase 15 route names"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-watchpoint failure: {failures}")

        missing_handoff_root = root / "missing_handoff"
        _seed(missing_handoff_root)
        _write(
            missing_handoff_root / HANDOFF_NOTE_REL,
            _read(missing_handoff_root / HANDOFF_NOTE_REL).replace(
                "- `zigux/tests/phase15_handoff_next_steps.zig`\n",
                "",
                1,
            ),
        )
        failures = validate(missing_handoff_root)
        expected = ["handoff_note:missing:`zigux/tests/phase15_handoff_next_steps.zig`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-handoff failure: {failures}")

    print("PHASE15_SHARED_SUMMARY_GAP_SELF_TEST=pass")
    print("PHASE15_SHARED_SUMMARY_GAP_SELF_TEST_CASES=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 shared-summary gap note stays aligned with the live governance packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE15_SHARED_SUMMARY_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

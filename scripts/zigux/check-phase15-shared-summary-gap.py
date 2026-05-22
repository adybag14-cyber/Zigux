#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
CURRENT_READBACK_MARKER = "current-master-readback-2026-05-22"
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
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
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
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "scripts/zigux/check-phase15-readiness-gate-packet.py",
)

STILL_MISSING_VALIDATOR_FIRST_PATHS = (
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_build.zig",
)

REQUIRED_NOTE_MARKERS = (
    f"surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
    "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
    "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
    "`scripts/zigux/check-phase15-readiness-gate-packet.py`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing.zig`",
    "`zigux/tests/phase15_readiness_gate_manifest.json`",
    "`zigux/tests/README.md`, whose dedicated Phase 15 governance reminder is now landed",
    "broader validator-first wording around `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, and the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes",
)

STALE_TEXT_MARKERS = (
    "## Still-missing focused companions on current master",
    "The current shared-summary drift is anchored to these still-missing paths:",
    "previously treated as missing",
    "current-master-readback-2026-05-17",
    "current-master-readback-2026-05-20",
    "`zigux/tests/README.md` still lacks the dedicated Phase 15 governance reminder section",
    "do not treat the still-missing tests-root Phase 15 reminder text as already landed",
)

HANDOFF_STATUS_MARKER = "PHASE15_STATUS=handoff_next_steps_survey_landed"
REQUIRED_WATCHPOINT_MARKERS = (
    "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
    "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _extract_section(note: str, heading: str) -> str:
    before, marker, tail = note.partition(f"{heading}\n\n")
    if not marker:
        return ""
    section, _, _ = tail.partition("\n## ")
    return section


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in (GAP_NOTE_PATH.as_posix(), HANDOFF_NOTE_PATH.as_posix()):
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    gap_note = _read_text(root / GAP_NOTE_PATH)
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    watchpoints_section = _extract_section(gap_note, WATCHPOINTS_HEADING)

    for marker in STATUS_MARKERS:
        if marker not in gap_note:
            failures.append(f"gap_note:missing_status:{marker}")

    for rel in MATERIALIZED_GOVERNANCE_PATHS:
        if not (root / rel).exists():
            failures.append(f"repo:missing_materialized:{rel}")
        if f"`{rel}`" not in gap_note:
            failures.append(f"gap_note:missing_materialized_marker:`{rel}`")

    for rel in MATERIALIZED_FOCUSED_COMPANIONS:
        if not (root / rel).exists():
            failures.append(f"repo:missing_focused:{rel}")
        if f"`{rel}`" not in gap_note:
            failures.append(f"gap_note:missing_focused_marker:`{rel}`")

    for rel in STILL_MISSING_VALIDATOR_FIRST_PATHS:
        if f"`{rel}`" not in gap_note:
            failures.append(f"gap_note:missing_gap_marker:`{rel}`")
        if (root / rel).exists():
            failures.append(f"repo:gap_path_returned:{rel}")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in gap_note:
            failures.append(f"gap_note:missing_required:{marker}")

    if not watchpoints_section:
        failures.append(f"gap_note:missing_section:{WATCHPOINTS_HEADING}")
    else:
        for marker in REQUIRED_WATCHPOINT_MARKERS:
            if marker not in watchpoints_section:
                failures.append(f"gap_note:missing_watchpoint:{marker}")

    for marker in STALE_TEXT_MARKERS:
        if marker in gap_note:
            failures.append(f"gap_note:stale_text:{marker}")

    if HANDOFF_STATUS_MARKER not in handoff_note:
        failures.append(f"handoff_note:missing_status:{HANDOFF_STATUS_MARKER}")

    return failures


def _sample_gap_note() -> str:
    materialized = "\n".join(f"- `{rel}`" for rel in MATERIALIZED_GOVERNANCE_PATHS)
    focused = "\n".join(f"- `{rel}`" for rel in MATERIALIZED_FOCUSED_COMPANIONS)
    missing = "\n".join(f"- `{rel}`" for rel in STILL_MISSING_VALIDATOR_FIRST_PATHS)
    return f"""# Phase 15 Shared Summary Gap

## Status

- `PHASE15_STATUS=shared_summary_gap_recorded`
- `PHASE15_LANE_KEY=P15-L02`
- `PHASE15_SLICE=materialized-governance-packet-truthfulness-refresh`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`

## Materialized Phase 15 governance assets

{materialized}

## Materialized focused companions on current master

{focused}

## Still-missing broader validator-first companions on current master

{missing}

## Current shared-summary watchpoints

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `scripts/zigux/check-phase15-docs-readme-alignment.py`
- `scripts/zigux/check-phase15-scripts-readme-alignment.py`
- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-handoff-note-alignment.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`
- `scripts/zigux/check-phase15-readiness-gate-packet.py`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `zigux/tests/phase15_governance_lane_sequencing_manifest.json`
- `zigux/tests/phase15_governance_lane_sequencing.zig`
- `zigux/tests/phase15_readiness_gate_manifest.json`
- `zigux/tests/README.md`, whose dedicated Phase 15 governance reminder is now landed and should stay aligned with `scripts/zigux/check-phase15-tests-readme-alignment.py` instead of falling back into stale missing-section wording
- broader validator-first wording around `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, and the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes
"""


def _sample_handoff_note() -> str:
    return "# Phase 15 Handoff Next Steps Survey\n\nPHASE15_STATUS=handoff_next_steps_survey_landed\n"


def _seed_repo(root: Path) -> None:
    _write_text(root / GAP_NOTE_PATH, _sample_gap_note())
    _write_text(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    for rel in MATERIALIZED_GOVERNANCE_PATHS + MATERIALIZED_FOCUSED_COMPANIONS:
        _write_text(root / rel, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_shared_summary_gap_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        stale_tests_gap_root = root / "stale_tests_gap"
        _seed_repo(stale_tests_gap_root)
        _write_text(
            stale_tests_gap_root / GAP_NOTE_PATH,
            _sample_gap_note().replace(
                "`zigux/tests/README.md`, whose dedicated Phase 15 governance reminder is now landed",
                "`zigux/tests/README.md` still lacks the dedicated Phase 15 governance reminder section",
                1,
            ),
        )
        failures = collect_failures(stale_tests_gap_root)
        expected = [
            "gap_note:missing_required:`zigux/tests/README.md`, whose dedicated Phase 15 governance reminder is now landed",
            "gap_note:stale_text:`zigux/tests/README.md` still lacks the dedicated Phase 15 governance reminder section",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-tests-gap failure: {failures}")

        stale_marker_root = root / "stale_marker"
        _seed_repo(stale_marker_root)
        _write_text(
            stale_marker_root / GAP_NOTE_PATH,
            _sample_gap_note().replace(CURRENT_READBACK_MARKER, "current-master-readback-2026-05-20", 1),
        )
        failures = collect_failures(stale_marker_root)
        expected = [
            f"gap_note:missing_required:surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`",
            "gap_note:stale_text:current-master-readback-2026-05-20",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-marker failure: {failures}")

        missing_focused_root = root / "missing_focused"
        _seed_repo(missing_focused_root)
        (missing_focused_root / "scripts/zigux/check-phase15-shared-summary-gap.py").unlink()
        failures = collect_failures(missing_focused_root)
        expected = ["repo:missing_focused:scripts/zigux/check-phase15-shared-summary-gap.py"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-focused failure: {failures}")

        returned_gap_root = root / "returned_gap"
        _seed_repo(returned_gap_root)
        _write_text(returned_gap_root / "scripts/zigux/validate-phase15.py", "present\n")
        failures = collect_failures(returned_gap_root)
        expected = ["repo:gap_path_returned:scripts/zigux/validate-phase15.py"]
        if failures != expected:
            raise AssertionError(f"unexpected returned-gap failure: {failures}")

    print("PHASE15_SHARED_SUMMARY_GAP_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 shared-summary gap note matches the materialized governance packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_SHARED_SUMMARY_GAP_SELF_TEST=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

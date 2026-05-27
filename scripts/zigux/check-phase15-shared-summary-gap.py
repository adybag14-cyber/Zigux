#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
CURRENT_READBACK_MARKER = "current-master-readback-2026-05-25"
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

VALIDATOR_WORDING_SPLIT_MARKER = (
    "`scripts/zigux/README.md` now keeps the directly materialized `scripts/zigux/validate-phase15.py` maintenance gate, the directly materialized `scripts/zigux/check-phase15-architecture-council-packet.py` Architecture Council packet checker, and the directly materialized `zigux/tests/phase15_build.zig` shared build companion explicit while the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes plus the shared-CI route remain the broader route-level gaps on current `master`"
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
    "`Documentation/zigux/phase15-architecture-council-decision-index.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-parity-scorecard-survey.md`",
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
    VALIDATOR_WORDING_SPLIT_MARKER,
    "broader wrapper-route wording around `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, and the dedicated shared-CI Phase 15 route names",
)

STALE_TEXT_MARKERS = (
    "## Still-missing focused companions on current master",
    "The current shared-summary drift is anchored to these still-missing paths:",
    "previously treated as missing",
    "current-master-readback-2026-05-17",
    "current-master-readback-2026-05-21",
    "current-master-readback-2026-05-23",
)

HANDOFF_STATUS_MARKER = "PHASE15_STATUS=handoff_next_steps_survey_landed"
REQUIRED_WATCHPOINT_MARKERS = (
    "`Documentation/zigux/phase15-architecture-council-decision-index.md`",
    "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing.zig`",
    "`zigux/tests/phase15_readiness_gate_manifest.json`",
    "`zigux/tests/phase15_build.zig`",
    "`scripts/zigux/check-phase15-readiness-gate-packet.py`",
    VALIDATOR_WORDING_SPLIT_MARKER,
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing file: {path}") from exc


def _extract_section(note: str, heading: str) -> str:
    _, marker, tail = note.partition(f"{heading}\n\n")
    if not marker:
        return ""
    section, _, _ = tail.partition("\n## ")
    return section


def collect_failures(root: Path) -> list[str]:
    gap_note = _read_text(root / GAP_NOTE_PATH)
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    failures: list[str] = []
    watchpoints_section = _extract_section(gap_note, WATCHPOINTS_HEADING)

    for marker in STATUS_MARKERS:
        if marker not in gap_note:
            failures.append(f"gap note missing status marker: {marker}")

    for rel in MATERIALIZED_GOVERNANCE_PATHS:
        if not (root / rel).exists():
            failures.append(f"expected materialized Phase 15 path missing: {rel}")
        if f"`{rel}`" not in gap_note:
            failures.append(f"gap note missing materialized path marker: `{rel}`")

    for rel in MATERIALIZED_FOCUSED_COMPANIONS:
        if not (root / rel).exists():
            failures.append(f"expected materialized focused companion missing: {rel}")
        if f"`{rel}`" not in gap_note:
            failures.append(f"gap note missing focused-companion marker: `{rel}`")

    for marker in ROUTE_GAP_MARKERS:
        if marker not in gap_note:
            failures.append(f"gap note missing route-gap marker: {marker}")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in gap_note:
            failures.append(f"gap note missing required marker: {marker}")

    if not watchpoints_section:
        failures.append(f"gap note missing section: {WATCHPOINTS_HEADING}")
    else:
        for marker in REQUIRED_WATCHPOINT_MARKERS:
            if marker not in watchpoints_section:
                failures.append(f"gap note missing watchpoint marker: {marker}")

    for marker in STALE_TEXT_MARKERS:
        if marker in gap_note:
            failures.append(f"gap note still carries stale missing-path wording: {marker}")

    if HANDOFF_STATUS_MARKER not in handoff_note:
        failures.append(f"handoff note missing landed status marker: {HANDOFF_STATUS_MARKER}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_gap_note() -> str:
    materialized = "\n".join(f"- `{rel}`" for rel in MATERIALIZED_GOVERNANCE_PATHS)
    focused = "\n".join(f"- `{rel}`" for rel in MATERIALIZED_FOCUSED_COMPANIONS)
    route_gaps = "\n".join(f"- {marker}" for marker in ROUTE_GAP_MARKERS)
    required = "\n".join(f"- {marker}" for marker in REQUIRED_NOTE_MARKERS[1:])
    status = "\n".join(f"- `{marker}`" for marker in STATUS_MARKERS)
    return f"""# Phase 15 Shared Summary Gap

{status}
- surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`

## Materialized Phase 15 governance assets

{materialized}

## Materialized focused companions on current master

{focused}

## Still-missing broader wrapper and shared-CI route companions on current master

{route_gaps}

## Current shared-summary watchpoints

{required}
"""


def _sample_handoff_note() -> str:
    return "# Phase 15 Handoff Next Steps Survey\n\nPHASE15_STATUS=handoff_next_steps_survey_landed\n"


def _seed_repo(root: Path) -> None:
    _write(root / GAP_NOTE_PATH, _sample_gap_note())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    for rel in MATERIALIZED_GOVERNANCE_PATHS + MATERIALIZED_FOCUSED_COMPANIONS:
        _write(root / rel, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_shared_gap_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_root = root / "missing"
        _seed_repo(missing_root)
        (missing_root / MATERIALIZED_GOVERNANCE_PATHS[0]).unlink()
        failures = collect_failures(missing_root)
        if failures != [f"expected materialized Phase 15 path missing: {MATERIALIZED_GOVERNANCE_PATHS[0]}"]:
            raise AssertionError(f"unexpected missing-path failure: {failures}")

        decision_template_root = root / "decision_template"
        _seed_repo(decision_template_root)
        _write(
            decision_template_root / GAP_NOTE_PATH,
            _sample_gap_note().replace(
                "- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`\n",
                "",
                2,
            ).replace(
                "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
                "",
                1,
            ),
        )
        failures = collect_failures(decision_template_root)
        expected = [
            "gap note missing materialized path marker: `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
            "gap note missing required marker: `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected decision-template failure: {failures}")

        focused_root = root / "focused"
        _seed_repo(focused_root)
        (focused_root / MATERIALIZED_FOCUSED_COMPANIONS[0]).unlink()
        failures = collect_failures(focused_root)
        expected = [f"expected materialized focused companion missing: {MATERIALIZED_FOCUSED_COMPANIONS[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected focused-companion failure: {failures}")

        build_root = root / "build"
        _seed_repo(build_root)
        (build_root / "zigux/tests/phase15_build.zig").unlink()
        failures = collect_failures(build_root)
        expected = ["expected materialized focused companion missing: zigux/tests/phase15_build.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected build-companion failure: {failures}")

        route_gap_root = root / "route_gap"
        _seed_repo(route_gap_root)
        _write(
            route_gap_root / GAP_NOTE_PATH,
            _sample_gap_note().replace(
                "- no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(route_gap_root)
        expected = [
            "gap note missing route-gap marker: no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected route-gap failure: {failures}")

        stale_root = root / "stale"
        _seed_repo(stale_root)
        _write(
            stale_root / GAP_NOTE_PATH,
            _sample_gap_note().replace(VALIDATOR_WORDING_SPLIT_MARKER, "old stale wording", 1),
        )
        failures = collect_failures(stale_root)
        expected = [
            f"gap note missing required marker: {VALIDATOR_WORDING_SPLIT_MARKER}",
            f"gap note missing watchpoint marker: {VALIDATOR_WORDING_SPLIT_MARKER}",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-wording failure: {failures}")

    print("PHASE15_SHARED_SUMMARY_GAP=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 shared-summary gap note stays aligned with current repo reality."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("PHASE15_SHARED_SUMMARY_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

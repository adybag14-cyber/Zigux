#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")

CURRENT_READBACK_MARKER = "current-master-readback-2026-05-21"
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
    "scripts/zigux/check-phase15-readiness-gate-packet.py",
)

STILL_MISSING_VALIDATOR_FIRST_PATHS = (
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_build.zig",
)

WATCHPOINT_PATHS = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "scripts/zigux/check-phase15-readiness-gate-packet.py",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
)

WATCHPOINT_BROADER_MARKER = (
    "broader validator-first wording around `scripts/zigux/validate-phase15.py`, "
    "`zigux/tests/phase15_build.zig`, and the parked `make -C zigux phase15-validate`, "
    "`make -C zigux phase15-test`, and `make -C zigux phase15` routes"
)

REQUIRED_NOTE_MARKERS = (
    f"surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`",
    "shared-summary truthfulness",
    "route wording exactness",
    "do not treat present focused companions as Architecture Council approval",
    "do not treat the still-missing broader validator-first companions as shipped evidence",
)

STALE_TEXT_MARKERS = (
    "current-master-readback-2026-05-20",
    "current-master-readback-2026-05-17",
    "previously treated as missing",
)

HANDOFF_STATUS_MARKERS = (
    "PHASE15_STATUS=handoff_next_steps_survey_landed",
    "PHASE15_LANE_KEY=P15-L12",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing.zig`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "`zigux/tests/phase15_handoff_next_steps.zig`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
    "`scripts/zigux/check-phase15-readiness-gate-packet.py`",
    "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
    "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_build.zig`",
    "`make -C zigux phase15-validate`",
    "`make -C zigux phase15-test`",
    "`make -C zigux phase15`",
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing file: {path}") from exc


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _extract_section(note: str, heading: str) -> str:
    before, marker, tail = note.partition(f"{heading}\n\n")
    if not marker:
        return ""
    section, _, _ = tail.partition("\n## ")
    return section


def collect_failures(root: Path) -> list[str]:
    gap_note = _read_text(root / GAP_NOTE_PATH)
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    failures: list[str] = []

    materialized_section = _extract_section(
        gap_note, "## Materialized Phase 15 governance assets"
    )
    focused_section = _extract_section(
        gap_note, "## Materialized focused companions on current master"
    )
    missing_section = _extract_section(
        gap_note, "## Still-missing broader validator-first companions on current master"
    )
    watchpoints_section = _extract_section(
        gap_note, "## Current shared-summary watchpoints"
    )

    for marker in STATUS_MARKERS:
        if marker not in gap_note:
            failures.append(f"gap note missing status marker: {marker}")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in gap_note:
            failures.append(f"gap note missing required marker: {marker}")

    if not materialized_section:
        failures.append("gap note missing section: ## Materialized Phase 15 governance assets")
    if not focused_section:
        failures.append(
            "gap note missing section: ## Materialized focused companions on current master"
        )
    if not missing_section:
        failures.append(
            "gap note missing section: ## Still-missing broader validator-first companions on current master"
        )
    if not watchpoints_section:
        failures.append("gap note missing section: ## Current shared-summary watchpoints")

    for rel in MATERIALIZED_GOVERNANCE_PATHS:
        marker = f"`{rel}`"
        if marker not in gap_note:
            failures.append(f"gap note missing materialized path marker: {marker}")
        if materialized_section and marker not in materialized_section:
            failures.append(f"gap note missing governance-section marker: {marker}")
        if not (root / rel).exists():
            failures.append(f"expected materialized Phase 15 path missing: {rel}")

    for rel in MATERIALIZED_FOCUSED_COMPANIONS:
        marker = f"`{rel}`"
        if marker not in gap_note:
            failures.append(f"gap note missing focused-companion marker: {marker}")
        if focused_section and marker not in focused_section:
            failures.append(f"gap note missing focused-section marker: {marker}")
        if not (root / rel).exists():
            failures.append(f"expected materialized focused companion missing: {rel}")

    for rel in STILL_MISSING_VALIDATOR_FIRST_PATHS:
        marker = f"`{rel}`"
        if marker not in gap_note:
            failures.append(f"gap note missing still-missing validator-first marker: {marker}")
        if missing_section and marker not in missing_section:
            failures.append(f"gap note missing missing-section marker: {marker}")
        if (root / rel).exists():
            failures.append(f"gap note still treats materialized path as missing: {marker}")

    for rel in WATCHPOINT_PATHS:
        marker = f"`{rel}`"
        if watchpoints_section and marker not in watchpoints_section:
            failures.append(f"gap note missing watchpoint marker: {marker}")

    if watchpoints_section and WATCHPOINT_BROADER_MARKER not in watchpoints_section:
        failures.append("gap note missing watchpoint marker: broader validator-first wording")

    for marker in STALE_TEXT_MARKERS:
        if marker in gap_note:
            failures.append(f"gap note still carries stale wording: {marker}")

    for marker in HANDOFF_STATUS_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff note missing required marker: {marker}")

    return failures


def _sample_gap_note() -> str:
    materialized = "\n".join(f"- `{rel}`" for rel in MATERIALIZED_GOVERNANCE_PATHS)
    focused = "\n".join(f"- `{rel}`" for rel in MATERIALIZED_FOCUSED_COMPANIONS)
    missing = "\n".join(f"- `{rel}`" for rel in STILL_MISSING_VALIDATOR_FIRST_PATHS)
    watchpoints = "\n".join(f"- `{rel}`" for rel in WATCHPOINT_PATHS)
    status = "\n".join(f"- `{marker}`" for marker in STATUS_MARKERS)
    return f"""# Phase 15 Shared Summary Gap

This note records the current bounded Phase 15 shared-summary drift between the broad reminder surfaces and the live governance packet on `master`.

## Status

{status}
- surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`
- role: keep the current Phase 15 governance packet honest now that shared-summary truthfulness and route wording exactness are the remaining tasks

## Materialized Phase 15 governance assets

{materialized}

## Materialized focused companions on current master

{focused}

## Still-missing broader validator-first companions on current master

{missing}

## Current shared-summary watchpoints

{watchpoints}
- {WATCHPOINT_BROADER_MARKER}

## Recovery rule

- do not treat present focused companions as Architecture Council approval
- do not treat the still-missing broader validator-first companions as shipped evidence
"""


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

## Status

- `PHASE15_STATUS=handoff_next_steps_survey_landed`
- `PHASE15_LANE_KEY=P15-L12`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`

## Current handed-off packet on current master

- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
- `zigux/tests/phase15_governance_lane_sequencing_manifest.json`
- `zigux/tests/phase15_governance_lane_sequencing.zig`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `zigux/tests/phase15_handoff_next_steps.zig`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
- `scripts/zigux/check-phase15-readiness-gate-packet.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`
- `scripts/zigux/check-phase15-handoff-note-alignment.py`

## Roadmap-backed open handoff gaps

- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
- `make -C zigux phase15-validate`
- `make -C zigux phase15-test`
- `make -C zigux phase15`
"""


def _seed_repo(root: Path) -> None:
    _write(root / GAP_NOTE_PATH, _sample_gap_note())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    for rel in MATERIALIZED_GOVERNANCE_PATHS + MATERIALIZED_FOCUSED_COMPANIONS + WATCHPOINT_PATHS:
        path = root / rel
        if path.exists():
            continue
        _write(path, "present\n")


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ", ".join(actual) if actual else "none"
        want = ", ".join(expected) if expected else "none"
        raise AssertionError(f"{label}: got [{got}] want [{want}]")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_shared_gap_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)
        _assert_only(collect_failures(root), [], "baseline")
        case_count += 1

        stale_marker_root = root / "stale_marker"
        _seed_repo(stale_marker_root)
        _write(
            stale_marker_root / GAP_NOTE_PATH,
            _sample_gap_note().replace(CURRENT_READBACK_MARKER, "current-master-readback-2026-05-20"),
        )
        _assert_only(
            collect_failures(stale_marker_root),
            [
                f"gap note missing required marker: surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`",
                "gap note still carries stale wording: current-master-readback-2026-05-20",
            ],
            "stale_marker",
        )
        case_count += 1

        missing_governance_section_root = root / "missing_governance_section"
        _seed_repo(missing_governance_section_root)
        _write(
            missing_governance_section_root / GAP_NOTE_PATH,
            _sample_gap_note().replace(
                "- `zigux/tests/phase15_parity_scorecard.json`\n", "", 1
            ),
        )
        _assert_only(
            collect_failures(missing_governance_section_root),
            [
                "gap note missing materialized path marker: `zigux/tests/phase15_parity_scorecard.json`",
                "gap note missing governance-section marker: `zigux/tests/phase15_parity_scorecard.json`",
            ],
            "missing_governance_section",
        )
        case_count += 1

        missing_watchpoint_root = root / "missing_watchpoint"
        _seed_repo(missing_watchpoint_root)
        watchpoint_text = _sample_gap_note()
        watchpoint_line = "- `zigux/tests/phase15_governance_lane_sequencing_manifest.json`\n"
        watchpoint_index = watchpoint_text.rfind(watchpoint_line)
        _write(
            missing_watchpoint_root / GAP_NOTE_PATH,
            watchpoint_text[:watchpoint_index]
            + watchpoint_text[watchpoint_index + len(watchpoint_line) :],
        )
        _assert_only(
            collect_failures(missing_watchpoint_root),
            [
                "gap note missing watchpoint marker: `zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
            ],
            "missing_watchpoint",
        )
        case_count += 1

        materialized_missing_root = root / "materialized_missing"
        _seed_repo(materialized_missing_root)
        (materialized_missing_root / "zigux/tests/phase15_handoff_next_steps.zig").unlink()
        _assert_only(
            collect_failures(materialized_missing_root),
            ["expected materialized focused companion missing: zigux/tests/phase15_handoff_next_steps.zig"],
            "materialized_missing",
        )
        case_count += 1

        broader_materialized_root = root / "broader_materialized"
        _seed_repo(broader_materialized_root)
        _write(broader_materialized_root / "scripts/zigux/validate-phase15.py", "present\n")
        _assert_only(
            collect_failures(broader_materialized_root),
            ["gap note still treats materialized path as missing: `scripts/zigux/validate-phase15.py`"],
            "broader_materialized",
        )
        case_count += 1

        missing_handoff_marker_root = root / "missing_handoff_marker"
        _seed_repo(missing_handoff_marker_root)
        _write(
            missing_handoff_marker_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- `scripts/zigux/check-phase15-shared-summary-gap.py`\n", "", 1
            ),
        )
        _assert_only(
            collect_failures(missing_handoff_marker_root),
            ["handoff note missing required marker: `scripts/zigux/check-phase15-shared-summary-gap.py`"],
            "missing_handoff_marker",
        )
        case_count += 1

        missing_broader_watchpoint_root = root / "missing_broader_watchpoint"
        _seed_repo(missing_broader_watchpoint_root)
        _write(
            missing_broader_watchpoint_root / GAP_NOTE_PATH,
            _sample_gap_note().replace(f"- {WATCHPOINT_BROADER_MARKER}\n", "", 1),
        )
        _assert_only(
            collect_failures(missing_broader_watchpoint_root),
            ["gap note missing watchpoint marker: broader validator-first wording"],
            "missing_broader_watchpoint",
        )
        case_count += 1

    print("PHASE15_SHARED_SUMMARY_GAP_SELF_TEST=pass")
    print(f"PHASE15_SHARED_SUMMARY_GAP_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 shared-summary gap note matches the current materialized governance packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux, scripts/zigux, and zigux/tests",
    )
    parser.add_argument("--self-test", action="store_true", help="run the built-in synthetic self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        failures = collect_failures(args.root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 shared-summary gap check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

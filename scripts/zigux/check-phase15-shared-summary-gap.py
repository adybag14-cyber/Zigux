#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
CURRENT_READBACK_MARKER = "current-master-readback-2026-05-18"

MATERIALIZED_GOVERNANCE_PATHS = (
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
)

MATERIALIZED_FOCUSED_COMPANIONS = (
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_build.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
)

STILL_MISSING_VALIDATOR_FIRST_PATHS = (
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
)

REQUIRED_NOTE_MARKERS = (
    f"surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`zigux/tests/phase15_readiness_gate_manifest.json`",
    "broader validator-first wording around `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, and the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes",
)

STALE_TEXT_MARKERS = (
    "## Still-missing focused companions on current master",
    "The current shared-summary drift is anchored to these still-missing paths:",
    "previously treated as missing",
    "current-master-readback-2026-05-17",
)

HANDOFF_STATUS_MARKER = "PHASE15_STATUS=handoff_next_steps_survey_landed"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing file: {path}") from exc


def collect_failures(root: Path) -> list[str]:
    gap_note = _read_text(root / GAP_NOTE_PATH)
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    failures: list[str] = []

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

    for rel in STILL_MISSING_VALIDATOR_FIRST_PATHS:
        if f"`{rel}`" not in gap_note:
            failures.append(f"gap note missing still-missing validator-first marker: `{rel}`")
        if (root / rel).exists():
            failures.append(f"gap note still treats materialized path as missing: `{rel}`")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in gap_note:
            failures.append(f"gap note missing required marker: {marker}")

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
    missing = "\n".join(f"- `{rel}`" for rel in STILL_MISSING_VALIDATOR_FIRST_PATHS)
    required = "\n".join(f"- {marker}" for marker in REQUIRED_NOTE_MARKERS[1:])
    return f"""# Phase 15 Shared Summary Gap

- surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`

## Materialized Phase 15 governance assets

{materialized}

## Materialized focused companions on current master

{focused}

## Still-missing broader validator-first companions on current master

{missing}

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

        focused_root = root / "focused"
        _seed_repo(focused_root)
        (focused_root / MATERIALIZED_FOCUSED_COMPANIONS[0]).unlink()
        failures = collect_failures(focused_root)
        expected = [f"expected materialized focused companion missing: {MATERIALIZED_FOCUSED_COMPANIONS[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected focused-companion failure: {failures}")

        focused_checker_root = root / "focused_checker"
        _seed_repo(focused_checker_root)
        (focused_checker_root / MATERIALIZED_FOCUSED_COMPANIONS[-1]).unlink()
        failures = collect_failures(focused_checker_root)
        expected = [f"expected materialized focused companion missing: {MATERIALIZED_FOCUSED_COMPANIONS[-1]}"]
        if failures != expected:
            raise AssertionError(f"unexpected focused-checker failure: {failures}")

        rematerialized_root = root / "rematerialized"
        _seed_repo(rematerialized_root)
        _write(rematerialized_root / STILL_MISSING_VALIDATOR_FIRST_PATHS[0], "present\n")
        failures = collect_failures(rematerialized_root)
        expected = [
            f"gap note still treats materialized path as missing: `{STILL_MISSING_VALIDATOR_FIRST_PATHS[0]}`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected rematerialized-path failure: {failures}")

        stale_root = root / "stale"
        _seed_repo(stale_root)
        _write(stale_root / GAP_NOTE_PATH, _sample_gap_note() + "\n## Still-missing focused companions on current master\n")
        failures = collect_failures(stale_root)
        expected = [
            "gap note still carries stale missing-path wording: ## Still-missing focused companions on current master"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-wording failure: {failures}")

        stale_marker_root = root / "stale_marker"
        _seed_repo(stale_marker_root)
        _write(
            stale_marker_root / GAP_NOTE_PATH,
            _sample_gap_note().replace(CURRENT_READBACK_MARKER, "current-master-readback-2026-05-17"),
        )
        failures = collect_failures(stale_marker_root)
        expected = [
            f"gap note missing required marker: surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`",
            "gap note still carries stale missing-path wording: current-master-readback-2026-05-17",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-marker failure: {failures}")

        handoff_root = root / "handoff"
        _seed_repo(handoff_root)
        _write(handoff_root / HANDOFF_NOTE_PATH, "# Phase 15 Handoff Next Steps Survey\n")
        failures = collect_failures(handoff_root)
        expected = [f"handoff note missing landed status marker: {HANDOFF_STATUS_MARKER}"]
        if failures != expected:
            raise AssertionError(f"unexpected handoff failure: {failures}")

    print("PHASE15_SHARED_SUMMARY_GAP_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 shared-summary gap note matches the materialized governance packet."
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

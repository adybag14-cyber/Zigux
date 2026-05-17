#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")

MATERIALIZED_PATHS = (
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
)

REQUIRED_NOTE_MARKERS = (
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`zigux/tests/phase15_readiness_gate_manifest.json`",
    "`scripts/zigux/validate-phase15.py`",
)

STALE_TEXT_MARKERS = (
    "The current shared-summary drift is anchored to these still-missing paths:",
    "previously treated as missing",
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

    for rel in MATERIALIZED_PATHS:
        if not (root / rel).exists():
            failures.append(f"expected materialized Phase 15 path missing: {rel}")
        if f"`{rel}`" not in gap_note:
            failures.append(f"gap note missing materialized path marker: `{rel}`")

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
    materialized = "\n".join(f"- `{rel}`" for rel in MATERIALIZED_PATHS)
    required = "\n".join(f"- {marker}" for marker in REQUIRED_NOTE_MARKERS)
    return f"""# Phase 15 Shared Summary Gap

## Materialized Phase 15 governance assets

{materialized}

## Current shared-summary watchpoints

{required}
"""


def _sample_handoff_note() -> str:
    return "# Phase 15 Handoff Next Steps Survey\n\nPHASE15_STATUS=handoff_next_steps_survey_landed\n"


def _seed_repo(root: Path) -> None:
    _write(root / GAP_NOTE_PATH, _sample_gap_note())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    for rel in MATERIALIZED_PATHS:
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
        (missing_root / MATERIALIZED_PATHS[0]).unlink()
        failures = collect_failures(missing_root)
        if failures != [f"expected materialized Phase 15 path missing: {MATERIALIZED_PATHS[0]}"]:
            raise AssertionError(f"unexpected missing-path failure: {failures}")

        note_root = root / "note"
        _seed_repo(note_root)
        _write(
            note_root / GAP_NOTE_PATH,
            _sample_gap_note().replace(f"- `{MATERIALIZED_PATHS[1]}`\n", "", 1),
        )
        failures = collect_failures(note_root)
        expected = [f"gap note missing materialized path marker: `{MATERIALIZED_PATHS[1]}`"]
        if failures != expected:
            raise AssertionError(f"unexpected note-marker failure: {failures}")

        stale_root = root / "stale"
        _seed_repo(stale_root)
        _write(stale_root / GAP_NOTE_PATH, _sample_gap_note() + "\nThe current shared-summary drift is anchored to these still-missing paths:\n")
        failures = collect_failures(stale_root)
        expected = [
            "gap note still carries stale missing-path wording: The current shared-summary drift is anchored to these still-missing paths:"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-wording failure: {failures}")

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

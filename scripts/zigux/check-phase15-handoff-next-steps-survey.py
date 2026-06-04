#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")

DIRECT_PACKET_PATHS = (
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "Documentation/zigux/README.md",
    "zigux/tests/README.md",
)

MISSING_HANDOFF_COMPANIONS = ()

REQUIRED_MARKERS = (
    "PHASE15_STATUS=handoff_next_steps_survey_landed",
    "PHASE15_LANE_KEY=P15-L12",
    "PHASE15_SLICE=existing_governance_packet_handoff_inventory",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "surveyed against dated current-master readback marker `current-master-readback-2026-05-29`",
    "The dedicated validator, the dedicated Architecture Council packet checker, the shared build companion, the readiness gap matrix, the governance-lane sequencing companions, the Architecture Council decision index, the directly materialized reminder-surface checkers, and the blocked-route recovery checker now define the tighter same-lane boundaries",
    "The dedicated governance-lane sequencing manifest `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, the focused governance-lane sequencing Zig replay `zigux/tests/phase15_governance_lane_sequencing.zig`, the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json`, and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`.",
    "keep the four freeze-in-C anchors parked",
    "keep the two roadmap study-only anchors parked",
    "do not treat any direct Zig deep-core bridge as a next-phase commitment while the current blocker posture remains unchanged",
    "if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts",
    "This note does not claim:",
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing file: {path}") from exc


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    failures: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff_note:missing_marker:{marker}")

    for rel in DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in handoff_note:
            failures.append(f"handoff_note:missing_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_path:{rel}")

    for rel in MISSING_HANDOFF_COMPANIONS:
        if f"`{rel}`" not in handoff_note:
            failures.append(f"handoff_note:missing_gap_path:`{rel}`")
        if (root / rel).exists():
            failures.append(f"repo:gap_path_returned:{rel}")

    return failures


def _sample_handoff_note() -> str:
    direct_paths = "\n".join(f"- `{rel}`" for rel in DIRECT_PACKET_PATHS[:-2])
    return f"""# Phase 15 Handoff Next Steps Survey

## Status

- `PHASE15_STATUS=handoff_next_steps_survey_landed`
- `PHASE15_LANE_KEY=P15-L12`
- `PHASE15_SLICE=existing_governance_packet_handoff_inventory`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-29`

## Why this note exists

The dedicated validator, the dedicated Architecture Council packet checker, the shared build companion, the readiness gap matrix, the governance-lane sequencing companions, the Architecture Council decision index, the directly materialized reminder-surface checkers, and the blocked-route recovery checker now define the tighter same-lane boundaries.
The dedicated governance-lane sequencing manifest `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, the focused governance-lane sequencing Zig replay `zigux/tests/phase15_governance_lane_sequencing.zig`, the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json`, and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`.

## Current handed-off packet on current master

{direct_paths}
- `Documentation/zigux/README.md`, which should be treated as a shared-summary gap source only when fresh Phase 15 wording actually appears there
- the broad `zigux/tests/README.md` reminder surface, which should be reread with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the dedicated Phase 15 governance packet instead of being carried here as an unlanded future target by default
- the dedicated handoff-specific manifest and Zig replay are directly materialized on current `master`, so treat this note plus those companions as the handoff-specific source of truth

## Current governance posture to preserve

- keep the four freeze-in-C anchors parked
- keep the two roadmap study-only anchors parked
- do not treat any direct Zig deep-core bridge as a next-phase commitment while the current blocker posture remains unchanged

## Handoff rules

- if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts, refresh this handoff note so it points to the current direct surfaces, the focused tests-readme checker, and the checker-backed shared-gap packet instead of carrying stale future-target language

## Non-goals

This note does not claim:

- that the dedicated handoff-specific manifest or Zig replay by itself lands broader Phase 15 wrapper routes
- that the broader Phase 15 validator-first route or dedicated Phase 15 Zig build routes are already shipped on current `master`

"""


def _seed_repo(root: Path) -> None:
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    for rel in DIRECT_PACKET_PATHS:
        _write(root / rel, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_handoff_next_steps_") as tmpdir:
        root = Path(tmpdir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_marker_root = root / "missing_marker"
        _seed_repo(missing_marker_root)
        _write(
            missing_marker_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "The dedicated validator, the dedicated Architecture Council packet checker, the shared build companion, the readiness gap matrix, the governance-lane sequencing companions, the Architecture Council decision index, the directly materialized reminder-surface checkers, and the blocked-route recovery checker now define the tighter same-lane boundaries.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_marker_root)
        expected = [
            "handoff_note:missing_marker:The dedicated validator, the dedicated Architecture Council packet checker, the shared build companion, the readiness gap matrix, the governance-lane sequencing companions, the Architecture Council decision index, the directly materialized reminder-surface checkers, and the blocked-route recovery checker now define the tighter same-lane boundaries"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")

        missing_direct_root = root / "missing_direct"
        _seed_repo(missing_direct_root)
        (missing_direct_root / "Documentation/zigux/phase15-governance-lane-sequencing.md").unlink()
        failures = collect_failures(missing_direct_root)
        expected = ["repo:missing_direct_path:Documentation/zigux/phase15-governance-lane-sequencing.md"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-direct failure: {failures}")

        missing_path_marker_root = root / "missing_path_marker"
        _seed_repo(missing_path_marker_root)
        _write(
            missing_path_marker_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- `scripts/zigux/check-phase15-shared-summary-gap.py`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_path_marker_root)
        expected = [
            "handoff_note:missing_path:`scripts/zigux/check-phase15-shared-summary-gap.py`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-path-marker failure: {failures}")

    print("PHASE15_HANDOFF_NEXT_STEPS_SURVEY_SELF_TEST=pass")
    print("PHASE15_HANDOFF_NEXT_STEPS_SURVEY_SELF_TEST_CASES=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 handoff-next-steps note stays aligned with the current governance packet."
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

    print("PHASE15_HANDOFF_NEXT_STEPS_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

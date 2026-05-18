#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")

PRESENT_PATHS = [
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
    "zigux/tests/phase15_architecture_council_review_process_build.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
]

MISSING_PATHS = [
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
]

REQUIRED_MARKERS = [
    "PHASE15_STATUS=handoff_next_steps_survey_landed",
    "PHASE15_LANE_KEY=P15-L08",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "no dedicated handoff-specific manifest is directly materialized on current `master`",
    "no dedicated handoff-specific Zig replay is directly materialized on current `master`",
    "treat this note as the handoff-specific source of truth until those companions actually land",
    "an Architecture Council approval workflow implementation",
    "a direct port-readiness decision for any Phase 15 anchor",
]

PRESENT_GROUP_MARKERS = [
    "one focused review-process checker",
    "one focused tests-readme checker",
    "the shared-summary gap checker",
    "the focused handoff-note checker",
]

HISTORY_RULE_MARKERS = [
    "if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts",
    "if dedicated handoff-specific companions are published later, reread this note together with those new direct paths before presenting them as current evidence here",
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    failures: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing required marker: {marker}")

    for marker in PRESENT_GROUP_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing checker-group marker: {marker}")

    for marker in HISTORY_RULE_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing handoff-rule marker: {marker}")

    for repo_path in PRESENT_PATHS:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing present-path marker: {marker}")
        if not (root / repo_path).exists():
            failures.append(f"handoff note claims present path missing from repo: {marker}")

    for repo_path in MISSING_PATHS:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing gap-path marker: {marker}")
        if (root / repo_path).exists():
            failures.append(f"handoff note still frames shipped path as missing gap: {marker}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_handoff_note() -> str:
    present_lines = "\n".join(f"- `{path}`" for path in PRESENT_PATHS[:15])
    checker_lines = "\n".join(f"- `{path}`" for path in PRESENT_PATHS[15:18])
    gap_lines = "\n".join(f"- `{path}`" for path in MISSING_PATHS)
    return f"""# Phase 15 Handoff Next Steps Survey

- `PHASE15_STATUS=handoff_next_steps_survey_landed`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- no dedicated handoff-specific manifest is directly materialized on current `master`
- no dedicated handoff-specific Zig replay is directly materialized on current `master`
- treat this note as the handoff-specific source of truth until those companions actually land

## Current handed-off packet on current master

{present_lines}
{checker_lines}
- `scripts/zigux/check-phase15-handoff-note-alignment.py`, which together keep one focused review-process checker, one focused tests-readme checker, the shared-summary gap checker, and the focused handoff-note checker materialized on current `master`

## Roadmap-backed open handoff gaps

{gap_lines}

## Handoff rules

- if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts, refresh this handoff note so it points to the current direct surfaces, the focused tests-readme checker, the checker-backed shared-gap packet, and the focused handoff-note checker instead of carrying stale future-target language
- if dedicated handoff-specific companions are published later, reread this note together with those new direct paths before presenting them as current evidence here

## Non-goals

- an Architecture Council approval workflow implementation
- a direct port-readiness decision for any Phase 15 anchor
"""


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_handoff_note_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())

        for repo_path in PRESENT_PATHS:
            _write(root / repo_path, "# fixture\n")

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        _write(
            root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "the focused handoff-note checker",
                "the parked handoff inventory",
                1,
            ).replace(
                "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
                "`scripts/zigux/check-phase15-handoff-note-check.py`",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "handoff note is missing present-path marker: `scripts/zigux/check-phase15-handoff-note-alignment.py`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected focused-checker failure: {failures}")

        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(
            root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- `zigux/tests/phase15_readiness_gate_manifest.json`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "handoff note is missing present-path marker: `zigux/tests/phase15_readiness_gate_manifest.json`"
        ]:
            raise AssertionError(f"unexpected readiness-manifest failure: {failures}")

        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(
            root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- `zigux/tests/phase15_handoff_next_steps_manifest.json`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "handoff note is missing gap-path marker: `zigux/tests/phase15_handoff_next_steps_manifest.json`"
        ]:
            raise AssertionError(f"unexpected gap-path failure: {failures}")

        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(root / "zigux/tests/phase15_build.zig", "// fixture\n")
        failures = collect_failures(root)
        if failures != [
            "handoff note still frames shipped path as missing gap: `zigux/tests/phase15_build.zig`"
        ]:
            raise AssertionError(f"unexpected shipped-gap failure: {failures}")

    print("PHASE15_HANDOFF_NOTE_ALIGNMENT_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 handoff note stays aligned with the current governance packet and still-missing companions."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux, scripts/zigux, and zigux/tests",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic repo fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 handoff-note alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

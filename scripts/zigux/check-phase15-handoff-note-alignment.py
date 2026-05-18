#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_handoff_next_steps_manifest.json")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_failures(root: Path) -> list[str]:
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)
    failures: list[str] = []

    if manifest["surveyed_commit"] not in handoff_note:
        failures.append("handoff note is missing the manifest surveyed_commit marker")

    if f"`{manifest['checker']}`" not in handoff_note:
        failures.append("handoff note is missing the focused handoff-note checker path")

    for marker in manifest["required_markers"]:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing required marker: {marker}")

    for marker in manifest["checker_group_markers"]:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing checker-group marker: {marker}")

    for marker in manifest["handoff_rule_markers"]:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing handoff-rule marker: {marker}")

    for repo_path in manifest["present_paths"]:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing present-path marker: {marker}")
        if not (root / repo_path).exists():
            failures.append(f"handoff note claims present path missing from repo: {marker}")

    for repo_path in manifest["still_missing_paths"]:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing gap-path marker: {marker}")
        if (root / repo_path).exists():
            failures.append(f"handoff note still frames shipped path as missing gap: {marker}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P15-L08",
            "phase": "Phase 15",
            "surveyed_commit": "current-master-readback-2026-05-18",
            "handoff_note": "Documentation/zigux/phase15-handoff-next-steps-survey.md",
            "checker": "scripts/zigux/check-phase15-handoff-note-alignment.py",
            "present_paths": [
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
                "zigux/tests/phase15_handoff_next_steps_manifest.json",
                "scripts/zigux/check-phase15-review-process-handoff.py",
                "scripts/zigux/check-phase15-tests-readme-alignment.py",
                "scripts/zigux/check-phase15-shared-summary-gap.py",
                "scripts/zigux/check-phase15-handoff-note-alignment.py"
            ],
            "still_missing_paths": [
                "zigux/tests/phase15_handoff_next_steps.zig",
                "scripts/zigux/validate-phase15.py",
                "zigux/tests/phase15_build.zig",
                "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig"
            ],
            "required_markers": [
                "PHASE15_STATUS=handoff_next_steps_survey_landed",
                "PHASE15_LANE_KEY=P15-L08",
                "PHASE15_PROVENANCE_MODE=dated_master_readback",
                "the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json` is directly materialized on current `master`",
                "no dedicated handoff-specific Zig replay is directly materialized on current `master`",
                "treat this note together with `zigux/tests/phase15_handoff_next_steps_manifest.json` as the handoff-specific source of truth until that replay lands",
                "an Architecture Council approval workflow implementation",
                "a direct port-readiness decision for any Phase 15 anchor"
            ],
            "checker_group_markers": [
                "one focused review-process checker",
                "one focused tests-readme checker",
                "the shared-summary gap checker",
                "the focused handoff-note checker"
            ],
            "handoff_rule_markers": [
                "if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts",
                "if dedicated handoff-specific companions are published later, reread this note together with those new direct paths before presenting them as current evidence here"
            ]
        },
        indent=2,
    ) + "\n"


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `PHASE15_STATUS=handoff_next_steps_survey_landed`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-18`
- the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json` is directly materialized on current `master`
- no dedicated handoff-specific Zig replay is directly materialized on current `master`
- treat this note together with `zigux/tests/phase15_handoff_next_steps_manifest.json` as the handoff-specific source of truth until that replay lands

## Current handed-off packet on current master

- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-parity-scorecard-survey.md`
- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `zigux/tests/phase15_architecture_council_review_process_build.zig`
- `zigux/tests/phase15_readiness_gate_manifest.json`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`
- `scripts/zigux/check-phase15-handoff-note-alignment.py`, which together keep one focused review-process checker, one focused tests-readme checker, the shared-summary gap checker, and the focused handoff-note checker materialized on current `master`

## Roadmap-backed open handoff gaps

- `zigux/tests/phase15_handoff_next_steps.zig`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`

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
        _write(root / MANIFEST_PATH, _sample_manifest())

        manifest = _read_manifest(root / MANIFEST_PATH)
        for repo_path in manifest["present_paths"]:
            if repo_path == MANIFEST_PATH.as_posix():
                continue
            _write(root / repo_path, "# fixture\n")

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_present_root = root / "missing_present"
        _write(missing_present_root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(missing_present_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(missing_present_root / MANIFEST_PATH)
        for repo_path in manifest["present_paths"]:
            if repo_path == MANIFEST_PATH.as_posix():
                continue
            _write(missing_present_root / repo_path, "# fixture\n")
        (missing_present_root / "zigux/tests/phase15_readiness_gate_manifest.json").unlink()
        failures = collect_failures(missing_present_root)
        expected = [
            "handoff note claims present path missing from repo: `zigux/tests/phase15_readiness_gate_manifest.json`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-present failure: {failures}")

        missing_gap_marker_root = root / "missing_gap_marker"
        _write(missing_gap_marker_root / HANDOFF_NOTE_PATH, _sample_handoff_note().replace(
            "- `zigux/tests/phase15_handoff_next_steps.zig`\n",
            "",
            1,
        ))
        _write(missing_gap_marker_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(missing_gap_marker_root / MANIFEST_PATH)
        for repo_path in manifest["present_paths"]:
            if repo_path == MANIFEST_PATH.as_posix():
                continue
            _write(missing_gap_marker_root / repo_path, "# fixture\n")
        failures = collect_failures(missing_gap_marker_root)
        expected = [
            "handoff note is missing gap-path marker: `zigux/tests/phase15_handoff_next_steps.zig`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-gap-marker failure: {failures}")

        returned_gap_root = root / "returned_gap"
        _write(returned_gap_root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(returned_gap_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(returned_gap_root / MANIFEST_PATH)
        for repo_path in manifest["present_paths"]:
            if repo_path == MANIFEST_PATH.as_posix():
                continue
            _write(returned_gap_root / repo_path, "# fixture\n")
        for repo_path in manifest["still_missing_paths"]:
            if repo_path != "zigux/tests/phase15_handoff_next_steps.zig":
                continue
            _write(returned_gap_root / repo_path, "// fixture\n")
        failures = collect_failures(returned_gap_root)
        expected = [
            "handoff note still frames shipped path as missing gap: `zigux/tests/phase15_handoff_next_steps.zig`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected returned-gap failure: {failures}")

    print("PHASE15_HANDOFF_NOTE_ALIGNMENT_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 handoff note stays aligned with the current governance packet and dedicated handoff manifest."
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

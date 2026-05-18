#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SEQUENCING_NOTE_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
MANIFEST_PATH = Path("zigux/tests/phase15_governance_lane_sequencing_manifest.json")
READINESS_NOTE_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
SHARED_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=governance_lane_sequencing_packet_landed",
    "PHASE15_LANE_KEY=arch-council",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "Phase 15 is a governance tranche, not a hidden deep-core delivery lane.",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig`",
    "The shared reminder surfaces must not say that:",
    "a deep-core status change has been approved",
    "a freeze-in-C anchor is ready for a direct Zigux bridge",
    "a missing focused replay, handoff-manifest, dedicated build file, or other absent companion is already landed on current `master`",
    "python3 scripts/zigux/check-phase15-tests-readme-alignment.py",
    "zig test zigux/tests/phase15_governance_lane_sequencing.zig",
)

REQUIRED_READINESS_MARKERS = (
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing.zig`",
)

EXPECTED_MAINTENANCE_REPLAY_COMMANDS = (
    "python3 scripts/zigux/check-phase15-docs-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-tests-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-review-process-handoff.py",
    "python3 scripts/zigux/check-phase15-shared-summary-gap.py",
    "zig test zigux/tests/phase15_governance_lane_sequencing.zig",
)

EXPECTED_MISSING_BROADER_PATHS = (
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
)

EXPECTED_DIRECT_PACKET_PATHS = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_failures(root: Path) -> list[str]:
    sequencing_note = _read_text(root / SEQUENCING_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)
    readiness_note = _read_text(root / READINESS_NOTE_PATH)
    shared_gap_note = _read_text(root / SHARED_GAP_NOTE_PATH)
    makefile = _read_text(root / MAKEFILE_PATH)

    failures: list[str] = []

    if manifest["lane_key"] != "arch-council":
        failures.append("manifest lane_key drifted from arch-council")
    if manifest["phase"] != "Phase 15":
        failures.append("manifest phase drifted from Phase 15")
    if manifest["sequencing_note"] != str(SEQUENCING_NOTE_PATH):
        failures.append("manifest sequencing_note path drifted from the sequencing note")
    if manifest["readiness_manifest"] != "zigux/tests/phase15_readiness_gate_manifest.json":
        failures.append("manifest readiness_manifest path drifted from the landed readiness manifest")
    if manifest["shared_summary_gap_note"] != str(SHARED_GAP_NOTE_PATH):
        failures.append("manifest shared_summary_gap_note path drifted from the shared gap note")
    if manifest["direct_packet_paths"] != list(EXPECTED_DIRECT_PACKET_PATHS):
        failures.append("manifest direct_packet_paths drifted from the current governance packet inventory")
    if manifest["still_missing_broader_paths"] != list(EXPECTED_MISSING_BROADER_PATHS):
        failures.append("manifest still_missing_broader_paths drifted from the current blocked broader-path inventory")
    if manifest["maintenance_replay_commands"] != list(EXPECTED_MAINTENANCE_REPLAY_COMMANDS):
        failures.append("manifest maintenance_replay_commands drifted from the current maintenance replay packet")

    if manifest["surveyed_commit"] not in sequencing_note:
        failures.append("sequencing note is missing the manifest surveyed_commit marker")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in sequencing_note:
            failures.append(f"sequencing note is missing required marker: {marker}")

    for marker in REQUIRED_READINESS_MARKERS:
        if marker not in readiness_note:
            failures.append(f"readiness note is missing governance-lane marker: {marker}")

    for rel in EXPECTED_DIRECT_PACKET_PATHS:
        if not (root / rel).exists():
            failures.append(f"repo is missing direct governance packet path: {rel}")

    for rel in EXPECTED_MISSING_BROADER_PATHS:
        if rel not in sequencing_note:
            failures.append(f"sequencing note is missing broader-gap marker: {rel}")
        if rel not in readiness_note:
            failures.append(f"readiness note is missing broader-gap marker: {rel}")
        if rel not in shared_gap_note:
            failures.append(f"shared-summary gap note is missing broader-gap marker: {rel}")
        if (root / rel).exists():
            failures.append(f"blocked broader path returned unexpectedly: {rel}")

    for marker in ("phase15-validate:", "phase15-test:", "phase15:", ".PHONY: phase15"):
        if marker in makefile:
            failures.append(f"makefile unexpectedly advertises blocked Phase 15 route: {marker}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_sequencing_note() -> str:
    direct_paths = "\n".join(f"- `{rel}`" for rel in EXPECTED_DIRECT_PACKET_PATHS[:10])
    missing_paths = "\n".join(f"- `{rel}`" for rel in EXPECTED_MISSING_BROADER_PATHS)
    replay_commands = "\n".join(f"  - `{cmd}`" for cmd in EXPECTED_MAINTENANCE_REPLAY_COMMANDS)
    return f"""# Phase 15 Governance Lane Sequencing

## Status

- `PHASE15_STATUS=governance_lane_sequencing_packet_landed`
- `PHASE15_LANE_KEY=arch-council`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-18`

## Purpose

Phase 15 is a governance tranche, not a hidden deep-core delivery lane.

## Lane inventory

{direct_paths}
- `zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig`

## Shared-surface boundaries

The shared reminder surfaces must not say that:

- a deep-core status change has been approved
- a freeze-in-C anchor is ready for a direct Zigux bridge
- a missing focused replay, handoff-manifest, dedicated build file, or other absent companion is already landed on current `master`

## Current repo-reality gaps

Current `master` still returns missing for several broader Phase 15 companions that reminder surfaces may still mention:

{missing_paths}

## Maintenance-mode handoff

{replay_commands}
"""


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "arch-council",
            "phase": "Phase 15",
            "surveyed_commit": "current-master-readback-2026-05-18",
            "sequencing_note": str(SEQUENCING_NOTE_PATH),
            "readiness_manifest": "zigux/tests/phase15_readiness_gate_manifest.json",
            "shared_summary_gap_note": str(SHARED_GAP_NOTE_PATH),
            "direct_packet_paths": list(EXPECTED_DIRECT_PACKET_PATHS),
            "still_missing_broader_paths": list(EXPECTED_MISSING_BROADER_PATHS),
            "maintenance_replay_commands": list(EXPECTED_MAINTENANCE_REPLAY_COMMANDS),
        },
        indent=2,
    ) + "\n"


def _sample_readiness_note() -> str:
    return """# Phase 15 Readiness Gate Survey

- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `zigux/tests/phase15_governance_lane_sequencing_manifest.json`
- `zigux/tests/phase15_governance_lane_sequencing.zig`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `zigux/tests/phase15_build.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
"""


def _sample_shared_gap_note() -> str:
    return """# Phase 15 Shared Summary Gap

- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `zigux/tests/phase15_build.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
"""


def _seed_repo(root: Path) -> None:
    _write(root / SEQUENCING_NOTE_PATH, _sample_sequencing_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / READINESS_NOTE_PATH, _sample_readiness_note())
    _write(root / SHARED_GAP_NOTE_PATH, _sample_shared_gap_note())
    _write(
        root / MAKEFILE_PATH,
        "PYTHON ?= python3\n.PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2 phase3-validate phase3 phase10-validate phase10-test phase10\n",
    )
    for rel in EXPECTED_DIRECT_PACKET_PATHS:
        if rel in {
            str(SEQUENCING_NOTE_PATH),
            str(MANIFEST_PATH),
            str(READINESS_NOTE_PATH),
            str(SHARED_GAP_NOTE_PATH),
        }:
            continue
        _write(root / rel, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_governance_lane_checker_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_marker_root = root / "missing_marker"
        _seed_repo(missing_marker_root)
        _write(
            missing_marker_root / SEQUENCING_NOTE_PATH,
            _sample_sequencing_note().replace(
                "a deep-core status change has been approved\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_marker_root)
        expected = [
            "sequencing note is missing required marker: a deep-core status change has been approved"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")

        missing_direct_root = root / "missing_direct"
        _seed_repo(missing_direct_root)
        (missing_direct_root / "Documentation/zigux/phase15-parity-scorecard.md").unlink()
        failures = collect_failures(missing_direct_root)
        expected = [
            "repo is missing direct governance packet path: Documentation/zigux/phase15-parity-scorecard.md"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-direct failure: {failures}")

        returned_gap_root = root / "returned_gap"
        _seed_repo(returned_gap_root)
        _write(returned_gap_root / "scripts/zigux/validate-phase15.py", "present\n")
        failures = collect_failures(returned_gap_root)
        expected = ["blocked broader path returned unexpectedly: scripts/zigux/validate-phase15.py"]
        if failures != expected:
            raise AssertionError(f"unexpected returned-gap failure: {failures}")

        makefile_root = root / "makefile_route"
        _seed_repo(makefile_root)
        _write(
            makefile_root / MAKEFILE_PATH,
            "PYTHON ?= python3\nphase15-validate:\n\t@true\n",
        )
        failures = collect_failures(makefile_root)
        expected = ["makefile unexpectedly advertises blocked Phase 15 route: phase15-validate:"]
        if failures != expected:
            raise AssertionError(f"unexpected makefile-route failure: {failures}")

    print("PHASE15_GOVERNANCE_LANE_SEQUENCING_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 governance-lane sequencing packet stays aligned with the current Architecture Council boundaries."
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

    print("PHASE15_GOVERNANCE_LANE_SEQUENCING=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

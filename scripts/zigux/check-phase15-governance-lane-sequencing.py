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
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
MAKEFILE_PATH = Path("zigux/Makefile")

EXPECTED_LANE_KEY = "arch-council"
EXPECTED_PHASE = "Phase 15"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-20"
EXPECTED_READINESS_MANIFEST = "zigux/tests/phase15_readiness_gate_manifest.json"
EXPECTED_SHARED_GAP_NOTE = "Documentation/zigux/phase15-shared-summary-gap.md"

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
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
)

EXPECTED_STILL_MISSING_BROADER_PATHS = (
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_build.zig",
)

EXPECTED_MAINTENANCE_REPLAY_COMMANDS = (
    "python3 scripts/zigux/check-phase15-docs-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "python3 scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-tests-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-review-process-handoff.py",
    "python3 scripts/zigux/check-phase15-handoff-note-alignment.py",
    "python3 scripts/zigux/check-phase15-shared-summary-gap.py",
    "zig test zigux/tests/phase15_governance_lane_sequencing.zig",
)

REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=governance_lane_sequencing_packet_landed",
    "PHASE15_LANE_KEY=arch-council",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "current repo reality: the core Phase 15 governance notes are landed, the dedicated review-process manifest is landed, the dedicated governance-lane sequencing manifest plus focused replay are landed, the dedicated handoff manifest plus focused handoff-specific replay plus focused handoff-note checker are landed, the focused indefinite-C lane-owner companion is landed, the focused review-checklist study-only alignment checker is landed, and the shared reminder surfaces already point at this sequencing note, but the broader validator-first and dedicated-build companions still remain repo-reality gaps on current `master`",
    "which remaining missing validator-first or dedicated-build companions must remain named as gaps instead of being implied as shipped evidence",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory that stays outside the freeze-in-C scorecard and blocked status-change rows",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `scripts/zigux/check-phase15-handoff-note-alignment.py` keep the handoff-specific inventory, focused handoff-specific replay, and focused handoff-note alignment explicit without turning the sequencing packet into the owner of the handoff packet itself",
    "a missing focused replay, dedicated build file, or other absent broader companion is already landed on current `master`",
    "broader validator-first and dedicated-build companions",
)

REQUIRED_READINESS_MARKERS = (
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing.zig`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "`zigux/tests/phase15_handoff_next_steps.zig`",
)

REQUIRED_SHARED_GAP_MARKERS = (
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing.zig`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "`zigux/tests/phase15_handoff_next_steps.zig`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
)

REQUIRED_HANDOFF_MARKERS = (
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing.zig`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "`zigux/tests/phase15_handoff_next_steps.zig`",
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
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    makefile = _read_text(root / MAKEFILE_PATH)

    failures: list[str] = []

    if manifest["lane_key"] != EXPECTED_LANE_KEY:
        failures.append(f"manifest lane_key drifted from {EXPECTED_LANE_KEY}: {manifest['lane_key']}")
    if manifest["phase"] != EXPECTED_PHASE:
        failures.append(f"manifest phase drifted from {EXPECTED_PHASE}: {manifest['phase']}")
    if manifest["surveyed_commit"] != EXPECTED_SURVEYED_COMMIT:
        failures.append(
            f"manifest surveyed_commit drifted from {EXPECTED_SURVEYED_COMMIT}: {manifest['surveyed_commit']}"
        )
    if manifest["sequencing_note"] != SEQUENCING_NOTE_PATH.as_posix():
        failures.append(
            f"manifest sequencing_note drifted from {SEQUENCING_NOTE_PATH.as_posix()}: {manifest['sequencing_note']}"
        )
    if manifest["readiness_manifest"] != EXPECTED_READINESS_MANIFEST:
        failures.append(
            f"manifest readiness_manifest drifted from {EXPECTED_READINESS_MANIFEST}: {manifest['readiness_manifest']}"
        )
    if manifest["shared_summary_gap_note"] != EXPECTED_SHARED_GAP_NOTE:
        failures.append(
            f"manifest shared_summary_gap_note drifted from {EXPECTED_SHARED_GAP_NOTE}: {manifest['shared_summary_gap_note']}"
        )
    if manifest["direct_packet_paths"] != list(EXPECTED_DIRECT_PACKET_PATHS):
        failures.append("manifest direct_packet_paths drifted from the current governance packet inventory")
    if manifest["still_missing_broader_paths"] != list(EXPECTED_STILL_MISSING_BROADER_PATHS):
        failures.append("manifest still_missing_broader_paths drifted from the current broader-gap inventory")
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

    for marker in REQUIRED_SHARED_GAP_MARKERS:
        if marker not in shared_gap_note:
            failures.append(f"shared-summary gap note is missing governance-lane marker: {marker}")

    for marker in REQUIRED_HANDOFF_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing governance-lane marker: {marker}")

    for rel in EXPECTED_DIRECT_PACKET_PATHS:
        if not (root / rel).exists():
            failures.append(f"repo is missing direct governance packet path: {rel}")

    for rel in EXPECTED_STILL_MISSING_BROADER_PATHS:
        marker = f"`{rel}`"
        if marker not in sequencing_note:
            failures.append(f"sequencing note is missing broader-gap marker: {rel}")
        if marker not in readiness_note:
            failures.append(f"readiness note is missing broader-gap marker: {rel}")
        if marker not in shared_gap_note:
            failures.append(f"shared-summary gap note is missing broader-gap marker: {rel}")
        if marker not in handoff_note:
            failures.append(f"handoff note is missing broader-gap marker: {rel}")
        if (root / rel).exists():
            failures.append(f"blocked broader path returned unexpectedly: {rel}")

    if "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`" not in readiness_note:
        failures.append("readiness note is missing the landed lane-owner replay marker")
    if "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`" not in shared_gap_note:
        failures.append("shared-summary gap note is missing the landed lane-owner replay marker")
    if "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`" not in handoff_note:
        failures.append("handoff note is missing the landed lane-owner replay marker")

    for marker in ("phase15-validate:", "phase15-test:", "phase15:", ".PHONY: phase15"):
        if marker in makefile:
            failures.append(f"makefile unexpectedly advertises blocked Phase 15 route: {marker}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_sequencing_note() -> str:
    direct_paths = "\n".join(f"- `{rel}`" for rel in EXPECTED_DIRECT_PACKET_PATHS)
    replay_commands = "\n".join(f"  - `{cmd}`" for cmd in EXPECTED_MAINTENANCE_REPLAY_COMMANDS)
    broader_gaps = "\n".join(f"- `{rel}`" for rel in EXPECTED_STILL_MISSING_BROADER_PATHS)
    return f"""# Phase 15 Governance Lane Sequencing

## Status

- `PHASE15_STATUS=governance_lane_sequencing_packet_landed`
- `PHASE15_LANE_KEY=arch-council`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{EXPECTED_SURVEYED_COMMIT}`
- current repo reality: the core Phase 15 governance notes are landed, the dedicated review-process manifest is landed, the dedicated governance-lane sequencing manifest plus focused replay are landed, the dedicated handoff manifest plus focused handoff-specific replay plus focused handoff-note checker are landed, the focused indefinite-C lane-owner companion is landed, the focused review-checklist study-only alignment checker is landed, and the shared reminder surfaces already point at this sequencing note, but the broader validator-first and dedicated-build companions still remain repo-reality gaps on current `master`

## Purpose

Phase 15 is a governance tranche, not a hidden deep-core delivery lane.

## Lane inventory

{direct_paths}
- `Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory that stays outside the freeze-in-C scorecard and blocked status-change rows
- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves
- `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `scripts/zigux/check-phase15-handoff-note-alignment.py` keep the handoff-specific inventory, focused handoff-specific replay, and focused handoff-note alignment explicit without turning the sequencing packet into the owner of the handoff packet itself

## Shared-surface boundaries

The shared reminder surfaces must not say that:

- a deep-core status change has been approved
- a freeze-in-C anchor is ready for a direct Zigux bridge
- a missing focused replay, dedicated build file, or other absent broader companion is already landed on current `master`

## Current repo-reality gaps

This note exists so the docs-root, checklist-specific, and scripts-side alignment checks can name a real sequencing companion instead of pointing at a stale governance snapshot, and so which remaining missing validator-first or dedicated-build companions must remain named as gaps instead of being implied as shipped evidence stays explicit:

{broader_gaps}

## Maintenance-mode handoff

{replay_commands}
"""


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": EXPECTED_LANE_KEY,
            "phase": EXPECTED_PHASE,
            "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
            "sequencing_note": SEQUENCING_NOTE_PATH.as_posix(),
            "readiness_manifest": EXPECTED_READINESS_MANIFEST,
            "shared_summary_gap_note": EXPECTED_SHARED_GAP_NOTE,
            "direct_packet_paths": list(EXPECTED_DIRECT_PACKET_PATHS),
            "still_missing_broader_paths": list(EXPECTED_STILL_MISSING_BROADER_PATHS),
            "maintenance_replay_commands": list(EXPECTED_MAINTENANCE_REPLAY_COMMANDS),
        },
        indent=2,
    ) + "\n"


def _sample_readiness_note() -> str:
    direct = "\n".join(f"- `{rel}`" for rel in REQUIRED_READINESS_MARKERS)
    broader = "\n".join(f"- `{rel}`" for rel in EXPECTED_STILL_MISSING_BROADER_PATHS)
    return f"""# Phase 15 Readiness Gate Survey

{direct}
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
{broader}
"""


def _sample_shared_gap_note() -> str:
    direct = "\n".join(f"- `{rel}`" for rel in REQUIRED_SHARED_GAP_MARKERS)
    broader = "\n".join(f"- `{rel}`" for rel in EXPECTED_STILL_MISSING_BROADER_PATHS)
    return f"""# Phase 15 Shared Summary Gap

{direct}
{broader}
"""


def _sample_handoff_note() -> str:
    direct = "\n".join(f"- `{rel}`" for rel in REQUIRED_HANDOFF_MARKERS)
    broader = "\n".join(f"- `{rel}`" for rel in EXPECTED_STILL_MISSING_BROADER_PATHS)
    return f"""# Phase 15 Handoff Next Steps Survey

{direct}
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
{broader}
"""


def write_sample_root(root: Path) -> None:
    _write(root / SEQUENCING_NOTE_PATH, _sample_sequencing_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / READINESS_NOTE_PATH, _sample_readiness_note())
    _write(root / SHARED_GAP_NOTE_PATH, _sample_shared_gap_note())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    _write(
        root / MAKEFILE_PATH,
        "PYTHON ?= python3\n.PHONY: phase2 phase2-validate phase3 phase10 phase14\n",
    )
    for rel in EXPECTED_DIRECT_PACKET_PATHS:
        if rel in {
            SEQUENCING_NOTE_PATH.as_posix(),
            MANIFEST_PATH.as_posix(),
            READINESS_NOTE_PATH.as_posix(),
            SHARED_GAP_NOTE_PATH.as_posix(),
            HANDOFF_NOTE_PATH.as_posix(),
            MAKEFILE_PATH.as_posix(),
        }:
            continue
        _write(root / rel, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_governance_lane_checker_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_marker_root = root / "missing_marker"
        write_sample_root(missing_marker_root)
        _write(
            missing_marker_root / SEQUENCING_NOTE_PATH,
            _sample_sequencing_note().replace(
                "broader validator-first and dedicated-build companions",
                "broader validator-first wording removed",
                1,
            ),
        )
        failures = collect_failures(missing_marker_root)
        expected = [
            "sequencing note is missing required marker: current repo reality: the core Phase 15 governance notes are landed, the dedicated review-process manifest is landed, the dedicated governance-lane sequencing manifest plus focused replay are landed, the dedicated handoff manifest plus focused handoff-specific replay plus focused handoff-note checker are landed, the focused indefinite-C lane-owner companion is landed, the focused review-checklist study-only alignment checker is landed, and the shared reminder surfaces already point at this sequencing note, but the broader validator-first and dedicated-build companions still remain repo-reality gaps on current `master`",
            "sequencing note is missing required marker: broader validator-first and dedicated-build companions"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")

        missing_direct_root = root / "missing_direct"
        write_sample_root(missing_direct_root)
        (missing_direct_root / "zigux/tests/phase15_handoff_next_steps.zig").unlink()
        failures = collect_failures(missing_direct_root)
        expected = ["repo is missing direct governance packet path: zigux/tests/phase15_handoff_next_steps.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-direct failure: {failures}")

        returned_gap_root = root / "returned_gap"
        write_sample_root(returned_gap_root)
        _write(returned_gap_root / "scripts/zigux/validate-phase15.py", "present\n")
        failures = collect_failures(returned_gap_root)
        expected = ["blocked broader path returned unexpectedly: scripts/zigux/validate-phase15.py"]
        if failures != expected:
            raise AssertionError(f"unexpected returned-gap failure: {failures}")

        missing_lane_owner_root = root / "missing_lane_owner"
        write_sample_root(missing_lane_owner_root)
        _write(
            missing_lane_owner_root / SHARED_GAP_NOTE_PATH,
            _sample_shared_gap_note().replace(
                "- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_lane_owner_root)
        expected = [
            "shared-summary gap note is missing governance-lane marker: `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
            "shared-summary gap note is missing the landed lane-owner replay marker",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-lane-owner failure: {failures}")

        stale_manifest_root = root / "stale_manifest"
        write_sample_root(stale_manifest_root)
        _write(
            stale_manifest_root / MANIFEST_PATH,
            _sample_manifest().replace(
                '"surveyed_commit": "current-master-readback-2026-05-20"',
                '"surveyed_commit": "current-master-readback-2026-05-19"',
                1,
            ),
        )
        failures = collect_failures(stale_manifest_root)
        expected = [
            "manifest surveyed_commit drifted from current-master-readback-2026-05-20: current-master-readback-2026-05-19",
            "sequencing note is missing the manifest surveyed_commit marker",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-manifest failure: {failures}")

        makefile_root = root / "makefile_route"
        write_sample_root(makefile_root)
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
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE15_GOVERNANCE_LANE_SEQUENCING_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_GOVERNANCE_LANE_SEQUENCING=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

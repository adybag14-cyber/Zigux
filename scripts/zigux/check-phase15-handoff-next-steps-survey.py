#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_handoff_next_steps_manifest.json")

EXPECTED_MANIFEST = {
    "lane_key": "P15-L12",
    "phase": "Phase 15",
    "surveyed_commit": "current-master-readback-2026-05-27",
    "handoff_note": "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "checker": "scripts/zigux/check-phase15-handoff-note-alignment.py",
    "present_paths": [
        "Documentation/zigux/freeze-map.md",
        "Documentation/zigux/review-checklist.md",
        "Documentation/zigux/phase15-freeze-map-governance.md",
        "Documentation/zigux/phase15-deep-core-blocker-survey.md",
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
        "Documentation/zigux/phase15-architecture-council-decision-index.md",
        "Documentation/zigux/phase15-indefinite-c-policy.md",
        "Documentation/zigux/phase15-parity-scorecard.md",
        "Documentation/zigux/phase15-parity-scorecard-survey.md",
        "Documentation/zigux/phase15-readiness-gate-survey.md",
        "Documentation/zigux/phase15-governance-lane-sequencing.md",
        "Documentation/zigux/phase15-study-only-anchor-accounting.md",
        "Documentation/zigux/phase15-shared-summary-gap.md",
        "zigux-alpha/README.md",
        "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
        "zigux/tests/phase15_freeze_map_governance.zig",
        "zigux/tests/phase15_parity_scorecard.json",
        "zigux/tests/phase15_parity_scorecard.zig",
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
        "zigux/tests/phase15_architecture_council_review_process.zig",
        "zigux/tests/phase15_architecture_council_review_process_build.zig",
        "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
        "zigux/tests/phase15_governance_lane_sequencing.zig",
        "zigux/tests/phase15_readiness_gate_manifest.json",
        "zigux/tests/phase15_handoff_next_steps_manifest.json",
        "zigux/tests/phase15_handoff_next_steps.zig",
        "zigux/tests/phase15_build.zig",
        "zigux/tests/phase15_indefinite_c_policy.json",
        "zigux/tests/phase15_indefinite_c_policy.zig",
        "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
        "scripts/zigux/check-phase15-docs-readme-alignment.py",
        "scripts/zigux/check-phase15-scripts-readme-alignment.py",
        "scripts/zigux/check-phase15-review-process-handoff.py",
        "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
        "scripts/zigux/check-phase15-readiness-gate-packet.py",
        "scripts/zigux/check-phase15-tests-readme-alignment.py",
        "scripts/zigux/check-phase15-architecture-council-packet.py",
        "scripts/zigux/check-phase15-shared-summary-gap.py",
        "scripts/zigux/check-phase15-handoff-note-alignment.py",
        "scripts/zigux/validate-phase15.py",
    ],
    "still_missing_paths": [],
    "required_markers": [
        "PHASE15_STATUS=handoff_next_steps_survey_landed",
        "PHASE15_LANE_KEY=P15-L12",
        "PHASE15_PROVENANCE_MODE=dated_master_readback",
        "The dedicated governance-lane sequencing manifest `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, the focused governance-lane sequencing Zig replay `zigux/tests/phase15_governance_lane_sequencing.zig`, the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json`, and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`",
        "The focused freeze-map governance replay `zigux/tests/phase15_freeze_map_governance.zig`, the focused parity-scorecard machine-readable companion `zigux/tests/phase15_parity_scorecard.json`, and the focused parity-scorecard Zig replay `zigux/tests/phase15_parity_scorecard.zig` are also directly materialized on current `master`.",
        "The dedicated deep-core blocker survey `Documentation/zigux/phase15-deep-core-blocker-survey.md` is also directly materialized on current `master` and keeps the roadmap-versus-current-master blocker crosswalk explicit beside the broader handoff packet.",
        "Treat this note together with `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `zigux/tests/phase15_build.zig` as the handoff-specific source of truth while the blocked route bodies and shared-CI route remain gap-tracked.",
        "The dedicated validator `scripts/zigux/validate-phase15.py`, the dedicated Architecture Council packet checker `scripts/zigux/check-phase15-architecture-council-packet.py`, and shared build companion `zigux/tests/phase15_build.zig` are directly materialized on current `master`, but they do not by themselves land the broader dedicated `phase15*` wrapper routes or shared-CI route.",
        "an Architecture Council approval workflow implementation",
        "a direct port-readiness decision for any Phase 15 anchor",
    ],
    "checker_group_markers": [
        "one focused docs-readme checker",
        "one focused scripts-readme checker",
        "one focused review-process checker",
        "one focused review-checklist study-only checker",
        "one focused readiness-packet checker",
        "one focused tests-readme checker",
        "one focused Architecture Council packet checker",
        "the shared-summary gap checker",
        "the focused handoff-note checker",
    ],
    "handoff_rule_markers": [
        "if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts",
        "if dedicated `phase15*` wrapper routes or a dedicated shared-CI route are published later, reread this note together with those new direct paths before presenting them as current evidence here",
    ],
    "roadmap_alignment_markers": [
        "The roadmap-required Phase 15 governance features are already materialized on current `master`: the freeze map, the Architecture Council review process, the parity scorecard, and the policy for code that remains in C indefinitely all have directly readable owner notes in the current packet.",
        "`zigux-alpha/README.md` and `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md` keep the bootstrap boundary explicit: the ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so later-lane Phase 15 status still has to be confirmed in the live product docs, current repo tree, and active lane notes.",
        "These are handoff and reminder-surface gaps, not missing ownership of the roadmap's four required governance features.",
    ],
    "pending_next_step_markers": [
        "compare the live Phase 15 governance packet against the roadmap first and use the bootstrap ledger only as early-tranche context, because the ledger does not own later-lane status",
        "tighten the smallest shared reminder surface first if docs-root, checklist, scripts-root, or tests-root wording drifts away from the directly materialized governance packet",
        "reread this handoff note together with any newly landed dedicated `phase15*` wrapper or shared-CI route recovery before treating that broader replay surface as current evidence here",
        "revisit freeze-map or parity-scorecard status only if an owning governance packet changes or a deep-core blocker disposition actually moves",
    ],
    "missing_route_markers": [
        "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
        "no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`",
    ],
}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing file: {path}") from exc


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing file: {path}") from exc


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _expect_equal(failures: list[str], label: str, actual, expected) -> None:
    if actual != expected:
        failures.append(f"{label}:expected={expected!r}:actual={actual!r}")


def collect_failures(root: Path) -> list[str]:
    note = _read_text(root / HANDOFF_NOTE_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    failures: list[str] = []

    for key in ("lane_key", "phase", "surveyed_commit", "handoff_note", "checker"):
        _expect_equal(failures, f"manifest:{key}", manifest.get(key), EXPECTED_MANIFEST[key])

    for key in (
        "present_paths",
        "still_missing_paths",
        "required_markers",
        "checker_group_markers",
        "handoff_rule_markers",
        "roadmap_alignment_markers",
        "pending_next_step_markers",
        "missing_route_markers",
    ):
        _expect_equal(failures, f"manifest:{key}", manifest.get(key), EXPECTED_MANIFEST[key])

    for path in EXPECTED_MANIFEST["present_paths"]:
        if f"`{path}`" not in note and path not in note:
            failures.append(f"handoff_note:missing_path:`{path}`")
        if not (root / path).exists():
            failures.append(f"repo:missing_present_path:{path}")

    for path in EXPECTED_MANIFEST["still_missing_paths"]:
        if f"`{path}`" not in note and path not in note:
            failures.append(f"handoff_note:missing_gap_path:`{path}`")
        if (root / path).exists():
            failures.append(f"repo:returned_missing_path:{path}")

    marker_groups = (
        "required_markers",
        "checker_group_markers",
        "handoff_rule_markers",
        "roadmap_alignment_markers",
        "pending_next_step_markers",
        "missing_route_markers",
    )
    for group in marker_groups:
        for marker in EXPECTED_MANIFEST[group]:
            if marker not in note:
                failures.append(f"handoff_note:missing_marker:{marker}")

    return failures


def _sample_handoff_note() -> str:
    present_paths = "\n".join(f"- `{path}`" for path in EXPECTED_MANIFEST["present_paths"])
    required_markers = "\n".join(f"- {marker}" for marker in EXPECTED_MANIFEST["required_markers"])
    checker_markers = "\n".join(f"- {marker}" for marker in EXPECTED_MANIFEST["checker_group_markers"])
    handoff_rules = "\n".join(f"- {marker}" for marker in EXPECTED_MANIFEST["handoff_rule_markers"])
    roadmap_markers = "\n".join(f"- {marker}" for marker in EXPECTED_MANIFEST["roadmap_alignment_markers"])
    pending_steps = "\n".join(f"- {marker}" for marker in EXPECTED_MANIFEST["pending_next_step_markers"])
    missing_routes = "\n".join(f"- {marker}" for marker in EXPECTED_MANIFEST["missing_route_markers"])
    return f"""# Phase 15 Handoff Next Steps Survey

## Status

- `PHASE15_STATUS=handoff_next_steps_survey_landed`
- `PHASE15_LANE_KEY=P15-L12`
- `PHASE15_SLICE=existing_governance_packet_handoff_inventory`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{EXPECTED_MANIFEST['surveyed_commit']}`

## Current handed-off packet on current master

{present_paths}

## Required markers

{required_markers}

## Checker group markers

{checker_markers}

## Roadmap alignment

{roadmap_markers}

## Pending next-step order

{pending_steps}

## Handoff rules

{handoff_rules}

## Missing broader route markers

{missing_routes}
"""


def _seed_repo(root: Path) -> None:
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    _write(root / MANIFEST_PATH, json.dumps(EXPECTED_MANIFEST, indent=2) + "\n")
    for path in EXPECTED_MANIFEST["present_paths"]:
        if Path(path) == MANIFEST_PATH:
            continue
        _write(root / path, "present\n")


def _write_sample_root(root: Path) -> None:
    if root.exists():
        raise RuntimeError(f"sample root already exists: {root}")
    _seed_repo(root)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_handoff_next_steps_") as tmpdir:
        root = Path(tmpdir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        wrong_lane_root = root / "wrong_lane"
        _seed_repo(wrong_lane_root)
        manifest = _read_json(wrong_lane_root / MANIFEST_PATH)
        manifest["lane_key"] = "P15-L11"
        _write(wrong_lane_root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        failures = collect_failures(wrong_lane_root)
        expected = ["manifest:lane_key:expected='P15-L12':actual='P15-L11'"]
        if failures != expected:
            raise AssertionError(f"unexpected wrong-lane failure: {failures}")

        missing_path_root = root / "missing_path"
        _seed_repo(missing_path_root)
        (missing_path_root / "zigux/tests/phase15_build.zig").unlink()
        failures = collect_failures(missing_path_root)
        expected = ["repo:missing_present_path:zigux/tests/phase15_build.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-path failure: {failures}")

        missing_marker_root = root / "missing_marker"
        _seed_repo(missing_marker_root)
        marker = EXPECTED_MANIFEST["required_markers"][6]
        _write(
            missing_marker_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(marker, "", 1),
        )
        failures = collect_failures(missing_marker_root)
        expected = [f"handoff_note:missing_marker:{marker}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")

        manifest_drift_root = root / "manifest_drift"
        _seed_repo(manifest_drift_root)
        manifest = _read_json(manifest_drift_root / MANIFEST_PATH)
        manifest["missing_route_markers"] = manifest["missing_route_markers"][:-1]
        _write(manifest_drift_root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        failures = collect_failures(manifest_drift_root)
        expected = [
            "manifest:missing_route_markers:expected=['no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`', 'no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`']:actual=['no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`']"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected manifest-drift failure: {failures}")

        missing_manifest_root = root / "missing_manifest"
        _seed_repo(missing_manifest_root)
        (missing_manifest_root / MANIFEST_PATH).unlink()
        try:
            collect_failures(missing_manifest_root)
        except RuntimeError as exc:
            if str(exc) != f"missing file: {missing_manifest_root / MANIFEST_PATH}":
                raise AssertionError(f"unexpected missing-manifest error: {exc}") from exc
        else:
            raise AssertionError("missing manifest root should raise RuntimeError")

    print("PHASE15_HANDOFF_NEXT_STEPS_SURVEY_SELF_TEST=pass")
    print("PHASE15_HANDOFF_NEXT_STEPS_SURVEY_SELF_TEST_CASES=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 handoff-next-steps survey matches the live P15-L12 packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux, scripts/zigux, zigux-alpha, and zigux/tests",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a synthetic current-like root for focused checker validation",
    )
    parser.add_argument("--self-test", action="store_true", help="run the built-in synthetic self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        try:
            _write_sample_root(args.write_sample_root)
        except RuntimeError as exc:
            print(f"ERROR: {exc}")
            return 1
        return 0

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
    print(f"PHASE15_HANDOFF_NEXT_STEPS_SURVEY_PRESENT_PATH_COUNT={len(EXPECTED_MANIFEST['present_paths'])}")
    print(f"PHASE15_HANDOFF_NEXT_STEPS_SURVEY_MISSING_PATH_COUNT={len(EXPECTED_MANIFEST['still_missing_paths'])}")
    print(f"PHASE15_HANDOFF_NEXT_STEPS_SURVEY_PENDING_STEP_COUNT={len(EXPECTED_MANIFEST['pending_next_step_markers'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

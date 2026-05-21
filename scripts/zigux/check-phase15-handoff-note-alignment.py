#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_handoff_next_steps_manifest.json")
CHECKER_PATH = Path("scripts/zigux/check-phase15-handoff-note-alignment.py")
EXPECTED_LANE_KEY = "P15-L10"
EXPECTED_PHASE = "Phase 15"
EXPECTED_SLICE = "existing_governance_packet_handoff_inventory"
RETIRED_MISSING_REPLAY_MARKER = "no dedicated handoff-specific Zig replay is directly materialized on current `master`"
REQUIRED_BOUNDARY_MARKERS = (
    "keep the four freeze-in-C anchors parked",
    "keep the two roadmap study-only anchors parked",
    "treat broader docs-root, checklist, scripts-root, tests-root, and validator-first Phase 15 wording drift as truthfulness gaps, not as already-landed evidence",
    "do not treat any direct Zig deep-core bridge as a next-phase commitment while the current blocker posture remains unchanged",
)
REQUIRED_FREEZE_IN_C_PATHS = (
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
)
REQUIRED_STUDY_ONLY_PATHS = (
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_failures(root: Path) -> list[str]:
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)
    failures: list[str] = []

    if manifest["lane_key"] != EXPECTED_LANE_KEY:
        failures.append(
            f"handoff manifest lane key drifted from {EXPECTED_LANE_KEY}: {manifest['lane_key']}"
        )

    if manifest["phase"] != EXPECTED_PHASE:
        failures.append(
            f"handoff manifest phase drifted from {EXPECTED_PHASE}: {manifest['phase']}"
        )

    manifest_slice = manifest.get("slice")
    if manifest_slice != EXPECTED_SLICE:
        failures.append(
            f"handoff manifest slice drifted from {EXPECTED_SLICE}: {manifest_slice}"
        )

    if manifest["handoff_note"] != HANDOFF_NOTE_PATH.as_posix():
        failures.append(
            f"handoff manifest note path drifted from {HANDOFF_NOTE_PATH.as_posix()}: {manifest['handoff_note']}"
        )

    if manifest["checker"] != CHECKER_PATH.as_posix():
        failures.append(
            f"handoff manifest checker path drifted from {CHECKER_PATH.as_posix()}: {manifest['checker']}"
        )

    if manifest["surveyed_commit"] not in handoff_note:
        failures.append("handoff note is missing the manifest surveyed_commit marker")

    if manifest_slice is not None and f"`PHASE15_SLICE={manifest_slice}`" not in handoff_note and f"PHASE15_SLICE={manifest_slice}" not in handoff_note:
        failures.append("handoff note is missing the manifest slice marker")

    if f"`{manifest['checker']}`" not in handoff_note:
        failures.append("handoff note is missing the focused handoff-note checker path")

    if RETIRED_MISSING_REPLAY_MARKER in handoff_note:
        failures.append("handoff note still frames the focused handoff replay as missing")

    for marker in manifest["required_markers"]:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing required marker: {marker}")

    for marker in manifest["checker_group_markers"]:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing checker-group marker: {marker}")

    for marker in manifest["handoff_rule_markers"]:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing handoff-rule marker: {marker}")

    for marker in manifest["roadmap_alignment_markers"]:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing roadmap-alignment marker: {marker}")

    for marker in manifest["pending_next_step_markers"]:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing pending-next-step marker: {marker}")

    for marker in manifest.get("shared_reminder_packet_markers", []):
        if marker not in handoff_note:
            failures.append(f"handoff note is missing shared-reminder packet marker: {marker}")

    for marker in manifest.get("future_target_markers", []):
        if marker not in handoff_note:
            failures.append(f"handoff note is missing future-target marker: {marker}")

    for marker in manifest["missing_route_markers"]:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing missing-route marker: {marker}")

    for marker in REQUIRED_BOUNDARY_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing boundary marker: {marker}")

    for repo_path in manifest["present_paths"]:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing present-path marker: {marker}")
        if not (root / repo_path).exists():
            failures.append(f"handoff note claims present path missing from repo: {marker}")

    for repo_path in manifest.get("shared_reminder_surface_paths", []):
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing shared-reminder surface marker: {marker}")
        if not (root / repo_path).exists():
            failures.append(f"handoff note claims shared reminder surface missing from repo: {marker}")

    for repo_path in manifest["still_missing_paths"]:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing gap-path marker: {marker}")
        if (root / repo_path).exists():
            failures.append(f"handoff note still frames shipped path as missing gap: {marker}")

    for repo_path in REQUIRED_FREEZE_IN_C_PATHS:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing freeze-in-c path marker: {marker}")

    for repo_path in REQUIRED_STUDY_ONLY_PATHS:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing study-only path marker: {marker}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P15-L10",
            "phase": "Phase 15",
            "slice": "existing_governance_packet_handoff_inventory",
            "surveyed_commit": "current-master-readback-2026-05-20",
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
                "zigux/tests/phase15_architecture_council_review_process.zig",
                "zigux/tests/phase15_architecture_council_review_process_build.zig",
                "zigux/tests/phase15_readiness_gate_manifest.json",
                "zigux/tests/phase15_handoff_next_steps_manifest.json",
                "zigux/tests/phase15_handoff_next_steps.zig",
                "zigux/tests/phase15_indefinite_c_policy.json",
                "zigux/tests/phase15_indefinite_c_policy.zig",
                "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
                "scripts/zigux/check-phase15-review-process-handoff.py",
                "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
                "scripts/zigux/check-phase15-readiness-gate-packet.py",
                "scripts/zigux/check-phase15-tests-readme-alignment.py",
                "scripts/zigux/check-phase15-shared-summary-gap.py",
                "scripts/zigux/check-phase15-handoff-note-alignment.py",
            ],
            "shared_reminder_surface_paths": [
                "Documentation/zigux/README.md",
                "zigux/tests/README.md",
            ],
            "still_missing_paths": [
                "scripts/zigux/validate-phase15.py",
                "zigux/tests/phase15_build.zig",
            ],
            "required_markers": [
                "PHASE15_STATUS=handoff_next_steps_survey_landed",
                "PHASE15_LANE_KEY=P15-L10",
                "PHASE15_PROVENANCE_MODE=dated_master_readback",
                "the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json` and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`",
                "Treat this note together with `zigux/tests/phase15_handoff_next_steps_manifest.json` and `zigux/tests/phase15_handoff_next_steps.zig` as the handoff-specific source of truth while the broader validator-first and dedicated-build companions remain gap-tracked.",
                "an Architecture Council approval workflow implementation",
                "a direct port-readiness decision for any Phase 15 anchor",
            ],
            "checker_group_markers": [
                "one focused review-process checker",
                "one focused review-checklist study-only checker",
                "one focused readiness-packet checker",
                "one focused tests-readme checker",
                "the shared-summary gap checker",
                "the focused handoff-note checker",
            ],
            "handoff_rule_markers": [
                "if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts",
                "if dedicated handoff-specific companions are published later, reread this note together with those new direct paths before presenting them as current evidence here",
            ],
            "roadmap_alignment_markers": [
                "The roadmap-required Phase 15 governance features are already materialized on current `master`: the freeze map, the Architecture Council review process, the parity scorecard, and the policy for code that remains in C indefinitely all have directly readable owner notes in the current packet.",
                "These are handoff and reminder-surface gaps, not missing ownership of the roadmap's four required governance features.",
            ],
            "pending_next_step_markers": [
                "tighten the smallest shared reminder surface first if docs-root, checklist, scripts-root, or tests-root wording drifts away from the directly materialized governance packet",
                "reread this handoff note together with any newly landed handoff-specific validator-first or dedicated-build companion before treating that companion as current evidence here",
                "revisit freeze-map or parity-scorecard status only if an owning governance packet changes or a deep-core blocker disposition actually moves",
            ],
            "shared_reminder_packet_markers": [
                "the broad docs-root reminder surface `Documentation/zigux/README.md`, which already carries dedicated Phase 15 wording on current `master` and should be treated as a shared-summary gap source only when that wording drifts away from the directly materialized governance packet",
                "the broad `zigux/tests/README.md` reminder surface, which should be reread with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the dedicated Phase 15 governance packet instead of being carried here as an unlanded future target by default",
            ],
            "future_target_markers": [
                "reread `zigux/tests/README.md` together with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the current directly materialized governance packet whenever the tests-root reminder drifts, rather than treating a dedicated Phase 15 review section as still-unlanded by default",
                "refresh the broad docs-root reminder surface `Documentation/zigux/README.md` only if its existing dedicated Phase 15 wording drifts, a smaller shared-summary truthfulness gap forces it back into scope, or fresh repo inspection materially changes which Phase 15 governance companions that docs-root packet can name honestly",
            ],
            "missing_route_markers": [
                "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
            ],
        },
        indent=2,
    ) + "\n"


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `PHASE15_STATUS=handoff_next_steps_survey_landed`
- `PHASE15_LANE_KEY=P15-L10`
- `PHASE15_SLICE=existing_governance_packet_handoff_inventory`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-20`
- the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json` and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`
- Treat this note together with `zigux/tests/phase15_handoff_next_steps_manifest.json` and `zigux/tests/phase15_handoff_next_steps.zig` as the handoff-specific source of truth while the broader validator-first and dedicated-build companions remain gap-tracked.

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
- `zigux/tests/phase15_architecture_council_review_process.zig`, which keeps the focused review-process replay materialized beside the review-process note, the manifest, and the focused build-file replay without implying that the broader validator-first or shared Phase 15 build routes have landed
- `zigux/tests/phase15_architecture_council_review_process_build.zig`, which keeps a focused `zig build test --build-file zigux/tests/phase15_architecture_council_review_process_build.zig` replay available for the review-process packet without implying that the broader validator-first or shared Phase 15 build routes have landed
- `zigux/tests/phase15_readiness_gate_manifest.json`, which records the current dated readback of the smaller readiness packet without implying that the broader validator-first route has fully landed
- `zigux/tests/phase15_handoff_next_steps_manifest.json`, which records the current handed-off packet and the remaining broader reminder-surface gaps in one machine-readable inventory without implying that the broader validator-first route or shared Phase 15 build routes have landed
- `zigux/tests/phase15_handoff_next_steps.zig`, which keeps the focused handoff-specific replay materialized beside the manifest and the note without implying that the broader validator-first or dedicated-build companions have landed
- `zigux/tests/phase15_indefinite_c_policy.json`, which keeps the roadmap-required stay-in-C policy packet machine-readable beside the policy note, the decision-record template, and the focused lane-owner replay without implying that the broader validator-first or shared Phase 15 build routes have landed
- `zigux/tests/phase15_indefinite_c_policy.zig`, which keeps the focused indefinite-C policy replay materialized beside the policy note, the manifest, and the lane-owner alignment companion without implying that the broader validator-first or shared Phase 15 build routes have landed
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, which keeps the focused indefinite-C lane-owner replay materialized beside the indefinite-C policy note, the review-process packet, and the decision-record template without implying that the broader validator-first or shared Phase 15 build routes have landed
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
- `scripts/zigux/check-phase15-readiness-gate-packet.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`
- `scripts/zigux/check-phase15-handoff-note-alignment.py`, which together keep one focused review-process checker, one focused review-checklist study-only checker, one focused readiness-packet checker, one focused tests-readme checker, the shared-summary gap checker, and the focused handoff-note checker materialized on current `master`
- the broad docs-root reminder surface `Documentation/zigux/README.md`, which already carries dedicated Phase 15 wording on current `master` and should be treated as a shared-summary gap source only when that wording drifts away from the directly materialized governance packet
- the broad `zigux/tests/README.md` reminder surface, which should be reread with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the dedicated Phase 15 governance packet instead of being carried here as an unlanded future target by default

## Current governance posture to preserve

- keep the four freeze-in-C anchors parked: `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`
- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`
- treat broader docs-root, checklist, scripts-root, tests-root, and validator-first Phase 15 wording drift as truthfulness gaps, not as already-landed evidence
- do not treat any direct Zig deep-core bridge as a next-phase commitment while the current blocker posture remains unchanged

## Roadmap-backed open handoff gaps

The roadmap-required Phase 15 governance features are already materialized on current `master`: the freeze map, the Architecture Council review process, the parity scorecard, and the policy for code that remains in C indefinitely all have directly readable owner notes in the current packet.

- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
- no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`

These are handoff and reminder-surface gaps, not missing ownership of the roadmap's four required governance features.

## Pending next-step order

1. tighten the smallest shared reminder surface first if docs-root, checklist, scripts-root, or tests-root wording drifts away from the directly materialized governance packet
2. reread this handoff note together with any newly landed handoff-specific validator-first or dedicated-build companion before treating that companion as current evidence here
3. revisit freeze-map or parity-scorecard status only if an owning governance packet changes or a deep-core blocker disposition actually moves

## Next bounded future targets

1. reread `zigux/tests/README.md` together with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the current directly materialized governance packet whenever the tests-root reminder drifts, rather than treating a dedicated Phase 15 review section as still-unlanded by default
2. refresh the broad docs-root reminder surface `Documentation/zigux/README.md` only if its existing dedicated Phase 15 wording drifts, a smaller shared-summary truthfulness gap forces it back into scope, or fresh repo inspection materially changes which Phase 15 governance companions that docs-root packet can name honestly

## Handoff rules

- if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts, refresh this handoff note so it points to the current direct surfaces, the focused tests-readme checker, the checker-backed shared-gap packet, the focused handoff-note checker, and the focused handoff-specific replay instead of carrying stale future-target language
- if dedicated handoff-specific companions are published later, reread this note together with those new direct paths before presenting them as current evidence here

## Non-goals

- an Architecture Council approval workflow implementation
- a direct port-readiness decision for any Phase 15 anchor
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_handoff_note_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(root / MANIFEST_PATH, _sample_manifest())

        manifest = _read_manifest(root / MANIFEST_PATH)
        for repo_path in manifest["present_paths"]:
            if repo_path == MANIFEST_PATH.as_posix():
                continue
            _write(root / repo_path, "# fixture\n")
        for repo_path in manifest.get("shared_reminder_surface_paths", []):
            _write(root / repo_path, "# fixture\n")

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_slice_root = root / "missing_slice"
        _write(
            missing_slice_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace("- `PHASE15_SLICE=existing_governance_packet_handoff_inventory`\n", "", 1),
        )
        _write(missing_slice_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(missing_slice_root / MANIFEST_PATH)
        for repo_path in manifest["present_paths"]:
            if repo_path == MANIFEST_PATH.as_posix():
                continue
            _write(missing_slice_root / repo_path, "# fixture\n")
        for repo_path in manifest.get("shared_reminder_surface_paths", []):
            _write(missing_slice_root / repo_path, "# fixture\n")
        failures = collect_failures(missing_slice_root)
        expected = ["handoff note is missing the manifest slice marker"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-slice failure: {failures}")
        case_count += 1

        missing_docs_root_root = root / "missing_docs_root_shared_surface"
        _write(
            missing_docs_root_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- the broad docs-root reminder surface `Documentation/zigux/README.md`, which already carries dedicated Phase 15 wording on current `master` and should be treated as a shared-summary gap source only when that wording drifts away from the directly materialized governance packet\n",
                "",
                1,
            ),
        )
        _write(missing_docs_root_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(missing_docs_root_root / MANIFEST_PATH)
        for repo_path in manifest["present_paths"]:
            if repo_path == MANIFEST_PATH.as_posix():
                continue
            _write(missing_docs_root_root / repo_path, "# fixture\n")
        for repo_path in manifest.get("shared_reminder_surface_paths", []):
            _write(missing_docs_root_root / repo_path, "# fixture\n")
        failures = collect_failures(missing_docs_root_root)
        expected = [
            "handoff note is missing shared-reminder packet marker: the broad docs-root reminder surface `Documentation/zigux/README.md`, which already carries dedicated Phase 15 wording on current `master` and should be treated as a shared-summary gap source only when that wording drifts away from the directly materialized governance packet",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-docs-root-surface failure: {failures}")
        case_count += 1

        missing_tests_future_target_root = root / "missing_tests_future_target"
        _write(
            missing_tests_future_target_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "1. reread `zigux/tests/README.md` together with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the current directly materialized governance packet whenever the tests-root reminder drifts, rather than treating a dedicated Phase 15 review section as still-unlanded by default\n",
                "",
                1,
            ),
        )
        _write(missing_tests_future_target_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(missing_tests_future_target_root / MANIFEST_PATH)
        for repo_path in manifest["present_paths"]:
            if repo_path == MANIFEST_PATH.as_posix():
                continue
            _write(missing_tests_future_target_root / repo_path, "# fixture\n")
        for repo_path in manifest.get("shared_reminder_surface_paths", []):
            _write(missing_tests_future_target_root / repo_path, "# fixture\n")
        failures = collect_failures(missing_tests_future_target_root)
        expected = [
            "handoff note is missing future-target marker: reread `zigux/tests/README.md` together with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the current directly materialized governance packet whenever the tests-root reminder drifts, rather than treating a dedicated Phase 15 review section as still-unlanded by default"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-tests-future-target failure: {failures}")
        case_count += 1

    print("PHASE15_HANDOFF_NOTE_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_HANDOFF_NOTE_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
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

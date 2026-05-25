#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_handoff_next_steps_manifest.json")
CHECKER_PATH = Path("scripts/zigux/check-phase15-handoff-note-alignment.py")

EXPECTED_LANE_KEY = "P15-L12"
EXPECTED_PHASE = "Phase 15"
RETIRED_MISSING_REPLAY_MARKER = (
    "no dedicated handoff-specific Zig replay is directly materialized on current `master`"
)
REQUIRED_BOUNDARY_MARKERS = (
    "keep the four freeze-in-C anchors parked",
    "keep the two roadmap study-only anchors parked",
    "treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps, not as already-landed evidence",
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

SAMPLE_MANIFEST = {
    "lane_key": "P15-L12",
    "phase": "Phase 15",
    "surveyed_commit": "current-master-readback-2026-05-24",
    "handoff_note": HANDOFF_NOTE_PATH.as_posix(),
    "checker": CHECKER_PATH.as_posix(),
    "present_paths": [
        "Documentation/zigux/freeze-map.md",
        "Documentation/zigux/review-checklist.md",
        "Documentation/zigux/phase15-freeze-map-governance.md",
        "Documentation/zigux/phase15-deep-core-blocker-survey.md",
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
        "Documentation/zigux/phase15-indefinite-c-policy.md",
        "Documentation/zigux/phase15-parity-scorecard.md",
        "Documentation/zigux/phase15-parity-scorecard-survey.md",
        "Documentation/zigux/phase15-readiness-gate-survey.md",
        "Documentation/zigux/phase15-governance-lane-sequencing.md",
        "Documentation/zigux/phase15-study-only-anchor-accounting.md",
        "Documentation/zigux/phase15-shared-summary-gap.md",
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
        "zigux/tests/phase15_indefinite_c_policy.json",
        "zigux/tests/phase15_indefinite_c_policy.zig",
        "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
        "scripts/zigux/check-phase15-docs-readme-alignment.py",
        "scripts/zigux/check-phase15-review-process-handoff.py",
        "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
        "scripts/zigux/check-phase15-readiness-gate-packet.py",
        "scripts/zigux/check-phase15-tests-readme-alignment.py",
        "scripts/zigux/check-phase15-shared-summary-gap.py",
        "scripts/zigux/check-phase15-handoff-note-alignment.py",
        "scripts/zigux/validate-phase15.py",
    ],
    "still_missing_paths": [
        "zigux/tests/phase15_build.zig",
    ],
    "required_markers": [
        "PHASE15_STATUS=handoff_next_steps_survey_landed",
        "PHASE15_LANE_KEY=P15-L12",
        "PHASE15_PROVENANCE_MODE=dated_master_readback",
        "the dedicated governance-lane sequencing manifest `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, the focused governance-lane sequencing Zig replay `zigux/tests/phase15_governance_lane_sequencing.zig`, the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json`, and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`",
        "The focused freeze-map governance replay `zigux/tests/phase15_freeze_map_governance.zig`, the focused parity-scorecard machine-readable companion `zigux/tests/phase15_parity_scorecard.json`, and the focused parity-scorecard Zig replay `zigux/tests/phase15_parity_scorecard.zig` are also directly materialized on current `master`.",
        "The dedicated deep-core blocker survey `Documentation/zigux/phase15-deep-core-blocker-survey.md` is also directly materialized on current `master` and keeps the roadmap-versus-current-master blocker crosswalk explicit beside the broader handoff packet.",
        "Treat this note together with `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, and `zigux/tests/phase15_handoff_next_steps.zig` as the handoff-specific source of truth while the dedicated shared-build companion and blocked route bodies remain gap-tracked.",
        "The dedicated validator `scripts/zigux/validate-phase15.py` is directly materialized on current `master` as a maintenance gate, but it does not by itself land the broader shared Phase 15 build replay or route bodies.",
        "an Architecture Council approval workflow implementation",
        "a direct port-readiness decision for any Phase 15 anchor",
    ],
    "checker_group_markers": [
        "one focused docs-readme checker",
        "one focused review-process checker",
        "one focused review-checklist study-only checker",
        "one focused readiness-packet checker",
        "one focused tests-readme checker",
        "the shared-summary gap checker",
        "the focused handoff-note checker",
    ],
    "handoff_rule_markers": [
        "if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts",
        "if the dedicated shared-build companion or blocked route bodies are published later, reread this note together with those new direct paths before presenting them as current evidence here",
    ],
    "roadmap_alignment_markers": [
        "The roadmap-required Phase 15 governance features are already materialized on current `master`: the freeze map, the Architecture Council review process, the parity scorecard, and the policy for code that remains in C indefinitely all have directly readable owner notes in the current packet.",
        "These are handoff and reminder-surface gaps, not missing ownership of the roadmap's four required governance features.",
    ],
    "pending_next_step_markers": [
        "tighten the smallest shared reminder surface first if docs-root, checklist, scripts-root, or tests-root wording drifts away from the directly materialized governance packet",
        "reread this handoff note together with any newly landed dedicated shared-build companion or route-body recovery before treating that broader replay surface as current evidence here",
        "revisit freeze-map or parity-scorecard status only if an owning governance packet changes or a deep-core blocker disposition actually moves",
    ],
    "missing_route_markers": [
        "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
    ],
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest() -> str:
    return json.dumps(SAMPLE_MANIFEST, indent=2) + "\n"


def _sample_handoff_note() -> str:
    manifest = SAMPLE_MANIFEST
    lines = [
        "# Phase 15 Handoff Next Steps Survey",
        "",
        "- `PHASE15_STATUS=handoff_next_steps_survey_landed`",
        "- `PHASE15_LANE_KEY=P15-L12`",
        "- `PHASE15_PROVENANCE_MODE=dated_master_readback`",
        f"- surveyed against dated current-master readback marker `{manifest['surveyed_commit']}`",
        f"- {manifest['required_markers'][3]}",
        f"- {manifest['required_markers'][4]}",
        f"- {manifest['required_markers'][5]}",
        f"- {manifest['required_markers'][6]}",
        "- `scripts/zigux/check-phase15-handoff-note-alignment.py`, which together keep one focused docs-readme checker, one focused review-process checker, one focused review-checklist study-only checker, one focused readiness-packet checker, one focused tests-readme checker, the shared-summary gap checker, and the focused handoff-note checker materialized on current `master`",
        "- `scripts/zigux/validate-phase15.py`, which keeps the dedicated validator directly materialized as a maintenance gate without implying that the broader shared Phase 15 build replay or route bodies are landed",
        "",
        "## Current handed-off packet on current master",
    ]
    lines.extend(f"- `{path}`" for path in manifest["present_paths"])
    lines.extend(
        [
            "",
            "## Current governance posture to preserve",
            "- keep the four freeze-in-C anchors parked: `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`",
            "- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
            "- treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps, not as already-landed evidence",
            "- do not treat any direct Zig deep-core bridge as a next-phase commitment while the current blocker posture remains unchanged",
            "",
            "## Roadmap-backed open handoff gaps",
            f"- {manifest['roadmap_alignment_markers'][0]}",
            f"- {manifest['required_markers'][7]}",
        ]
    )
    lines.extend(f"- no dedicated shared Phase 15 build replay `{path}` is directly materialized on current `master`" for path in manifest["still_missing_paths"])
    lines.extend(
        [
            f"- {manifest['missing_route_markers'][0]}",
            "- no Architecture Council approval is currently recorded for a freeze-map status change, so the packet remains in maintenance-mode blocker accounting rather than port-readiness",
            f"- {manifest['roadmap_alignment_markers'][1]}",
            "",
            "## Pending next-step order",
            f"1. {manifest['pending_next_step_markers'][0]}",
            f"2. {manifest['pending_next_step_markers'][1]}",
            f"3. {manifest['pending_next_step_markers'][2]}",
            "",
            "## Handoff rules",
            f"- {manifest['handoff_rule_markers'][0]}",
            f"- {manifest['handoff_rule_markers'][1]}",
            "- if the freeze-map anchor set or any blocker disposition changes, reopen `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and `Documentation/zigux/phase15-parity-scorecard.md` before widening this note",
            "",
            "## Non-goals",
            "- an Architecture Council approval workflow implementation",
            "- a direct port-readiness decision for any Phase 15 anchor",
            "- that the broader Phase 15 shared-build companion or route bodies are already shipped on current `master`",
            "",
        ]
    )
    return "\n".join(lines)


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
    if f"`{manifest['checker']}`" not in handoff_note:
        failures.append("handoff note is missing the focused handoff-note checker path")
    if RETIRED_MISSING_REPLAY_MARKER in handoff_note:
        failures.append("handoff note still frames the focused handoff replay as missing")

    for key, label in (
        ("required_markers", "required marker"),
        ("checker_group_markers", "checker-group marker"),
        ("handoff_rule_markers", "handoff-rule marker"),
        ("roadmap_alignment_markers", "roadmap-alignment marker"),
        ("pending_next_step_markers", "pending-next-step marker"),
        ("missing_route_markers", "missing-route marker"),
    ):
        for marker in manifest[key]:
            if marker not in handoff_note:
                failures.append(f"handoff note is missing {label}: {marker}")

    for marker in REQUIRED_BOUNDARY_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing boundary marker: {marker}")

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

    for repo_path in REQUIRED_FREEZE_IN_C_PATHS:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing freeze-in-c path marker: {marker}")

    for repo_path in REQUIRED_STUDY_ONLY_PATHS:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing study-only path marker: {marker}")

    return failures


def _seed_present_paths(root: Path, manifest: dict) -> None:
    for repo_path in manifest["present_paths"]:
        if repo_path == MANIFEST_PATH.as_posix():
            continue
        _write(root / repo_path, "# fixture\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_handoff_note_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(root / MANIFEST_PATH)
        _seed_present_paths(root, manifest)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_gap_boundary_root = root / "missing_gap_boundary"
        _write(
            missing_gap_boundary_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps, not as already-landed evidence\n",
                "",
                1,
            ),
        )
        _write(missing_gap_boundary_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(missing_gap_boundary_root / MANIFEST_PATH)
        _seed_present_paths(missing_gap_boundary_root, manifest)
        failures = collect_failures(missing_gap_boundary_root)
        expected = [
            "handoff note is missing boundary marker: treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps, not as already-landed evidence",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-gap-boundary failure: {failures}")

        manifest_identity_drift_root = root / "manifest_identity_drift"
        _write(manifest_identity_drift_root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(
            manifest_identity_drift_root / MANIFEST_PATH,
            _sample_manifest()
            .replace('"lane_key": "P15-L12"', '"lane_key": "P15-L99"', 1)
            .replace('"phase": "Phase 15"', '"phase": "Phase 15 drift"', 1)
            .replace(
                '"handoff_note": "Documentation/zigux/phase15-handoff-next-steps-survey.md"',
                '"handoff_note": "Documentation/zigux/phase15-handoff-next-step-survey.md"',
                1,
            )
            .replace(
                '"checker": "scripts/zigux/check-phase15-handoff-note-alignment.py"',
                '"checker": "scripts/zigux/check-phase15-handoff-alignment.py"',
                1,
            ),
        )
        manifest = _read_manifest(manifest_identity_drift_root / MANIFEST_PATH)
        _seed_present_paths(manifest_identity_drift_root, manifest)
        failures = collect_failures(manifest_identity_drift_root)
        expected = [
            "handoff manifest lane key drifted from P15-L12: P15-L99",
            "handoff manifest phase drifted from Phase 15: Phase 15 drift",
            "handoff manifest note path drifted from Documentation/zigux/phase15-handoff-next-steps-survey.md: Documentation/zigux/phase15-handoff-next-step-survey.md",
            "handoff manifest checker path drifted from scripts/zigux/check-phase15-handoff-note-alignment.py: scripts/zigux/check-phase15-handoff-alignment.py",
            "handoff note is missing the focused handoff-note checker path",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected manifest-identity-drift failure: {failures}")

        missing_surveyed_commit_root = root / "missing_surveyed_commit"
        _write(
            missing_surveyed_commit_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace("`current-master-readback-2026-05-24`", "`current-master-readback-YYYY-MM-DD`", 1),
        )
        _write(missing_surveyed_commit_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(missing_surveyed_commit_root / MANIFEST_PATH)
        _seed_present_paths(missing_surveyed_commit_root, manifest)
        failures = collect_failures(missing_surveyed_commit_root)
        expected = [
            "handoff note is missing the manifest surveyed_commit marker",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-surveyed-commit failure: {failures}")

        missing_checker_path_root = root / "missing_checker_path"
        _write(
            missing_checker_path_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- `scripts/zigux/check-phase15-handoff-note-alignment.py`, which together keep one focused docs-readme checker, one focused review-process checker, one focused review-checklist study-only checker, one focused readiness-packet checker, one focused tests-readme checker, the shared-summary gap checker, and the focused handoff-note checker materialized on current `master`\n",
                "",
                1,
            ),
        )
        _write(missing_checker_path_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(missing_checker_path_root / MANIFEST_PATH)
        _seed_present_paths(missing_checker_path_root, manifest)
        failures = collect_failures(missing_checker_path_root)
        expected = [
            "handoff note is missing checker-group marker: one focused docs-readme checker",
            "handoff note is missing checker-group marker: one focused review-process checker",
            "handoff note is missing checker-group marker: one focused review-checklist study-only checker",
            "handoff note is missing checker-group marker: one focused readiness-packet checker",
            "handoff note is missing checker-group marker: one focused tests-readme checker",
            "handoff note is missing checker-group marker: the shared-summary gap checker",
            "handoff note is missing checker-group marker: the focused handoff-note checker",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-checker-path failure: {failures}")

        missing_present_root = root / "missing_present"
        _write(missing_present_root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(missing_present_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(missing_present_root / MANIFEST_PATH)
        _seed_present_paths(missing_present_root, manifest)
        (missing_present_root / "zigux/tests/phase15_handoff_next_steps.zig").unlink()
        failures = collect_failures(missing_present_root)
        expected = [
            "handoff note claims present path missing from repo: `zigux/tests/phase15_handoff_next_steps.zig`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-present failure: {failures}")

        missing_route_marker_root = root / "missing_route_marker"
        _write(
            missing_route_marker_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`\n",
                "",
                1,
            ),
        )
        _write(missing_route_marker_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(missing_route_marker_root / MANIFEST_PATH)
        _seed_present_paths(missing_route_marker_root, manifest)
        failures = collect_failures(missing_route_marker_root)
        expected = [
            "handoff note is missing missing-route marker: no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-route-marker failure: {failures}")

        retired_gap_root = root / "retired_gap"
        _write(
            retired_gap_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note() + "\n- no dedicated handoff-specific Zig replay is directly materialized on current `master`\n",
        )
        _write(retired_gap_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(retired_gap_root / MANIFEST_PATH)
        _seed_present_paths(retired_gap_root, manifest)
        failures = collect_failures(retired_gap_root)
        expected = [
            "handoff note still frames the focused handoff replay as missing",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected retired-gap failure: {failures}")

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

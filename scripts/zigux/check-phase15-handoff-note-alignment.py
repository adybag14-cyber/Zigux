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
            "lane_key": "P15-L12",
            "phase": "Phase 15",
            "surveyed_commit": "current-master-readback-2026-05-22",
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
                "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
                "zigux/tests/phase15_governance_lane_sequencing.zig",
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
            "still_missing_paths": [
                "scripts/zigux/validate-phase15.py",
                "zigux/tests/phase15_build.zig",
            ],
            "required_markers": [
                "PHASE15_STATUS=handoff_next_steps_survey_landed",
                "PHASE15_LANE_KEY=P15-L12",
                "PHASE15_PROVENANCE_MODE=dated_master_readback",
                "the dedicated governance-lane sequencing manifest `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, the focused governance-lane sequencing Zig replay `zigux/tests/phase15_governance_lane_sequencing.zig`, the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json`, and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`",
                "Treat this note together with `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, and `zigux/tests/phase15_handoff_next_steps.zig` as the handoff-specific source of truth while the broader validator-first and dedicated-build companions remain gap-tracked.",
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
            "missing_route_markers": [
                "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
            ],
        },
        indent=2,
    ) + "\n"
EOF
python3 -m py_compile "$tmpdir/check-phase15-handoff-note-alignment.py"
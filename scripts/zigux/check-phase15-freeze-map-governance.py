#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
GOVERNANCE_NOTE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
MANIFEST_PATH = Path("zigux/tests/phase15_freeze_map_manifest.json")
GOVERNANCE_ZIG_PATH = Path("zigux/tests/phase15_freeze_map_governance.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
RCU_NOTE_PATH = Path("Documentation/zigux/phase14-rcu-tree-survey.md")
SKBUFF_NOTE_PATH = Path("Documentation/zigux/phase14-skbuff-bridge-survey.md")
TRACEABILITY_NOTE_PATH = Path("Documentation/zigux/phase14-core-boundary-traceability.md")

DIRECT_PACKET_PATHS = (
    str(FREEZE_MAP_PATH),
    str(GOVERNANCE_NOTE_PATH),
    str(MANIFEST_PATH),
    str(GOVERNANCE_ZIG_PATH),
    str(RCU_NOTE_PATH),
    str(SKBUFF_NOTE_PATH),
    str(TRACEABILITY_NOTE_PATH),
)

BLOCKED_BROADER_PATHS = (
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
)

BLOCKED_MAKEFILE_MARKERS = (
    "phase15-validate:",
    "phase15-test:",
    "phase15:",
    ".PHONY: phase15",
)

REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=governance_slice_landed",
    "PHASE15_LANE_KEY=P15-L04",
    "PHASE15_SLICE=freeze-map-deep-core-blocker-dated-readback-alignment",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "current-master-readback-2026-05-18",
    "shared reminder surfaces still carry as repo-reality gaps on current `master`",
    "exact branch-head parity is not recorded",
    "blocked_no_bounded_scheduler_seam",
    "blocked_no_bounded_allocator_seam",
    "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
    "blocked_packet_lifetime_boundary_still_too_wide",
    "## Maintenance-Mode Handoff",
    "current lane posture: `maintenance_mode`",
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_build.zig",
    "current-master contents reads now resolve `zigux/Makefile`",
    "those wrapper route names remain gap vocabulary rather than direct landed evidence",
    "phase15-freeze-map-manifest",
    "phase15-freeze-map-governance-gate",
    "phase15-shared-validator-route-readback",
    "phase15-shared-build-route-readback",
    "phase15-shared-wrapper-route-readback",
)

REQUIRED_RCU_MARKERS = (
    "PHASE14_LANE_KEY=P14-L14",
    "blocked by `phase14-rcu-tree-bridge-blocker`",
    "That is still a freeze-in-C posture, not a review-ready bridge seam.",
)

REQUIRED_SKBUFF_MARKERS = (
    "PHASE14_LANE_KEY=P14-L11",
    "PHASE14_BLOCKED_GAP=phase14-skbuff-anchor-packet-missing",
    "current `master` no longer exposes the earlier `P14-L11` skbuff anchor packet files",
    "review-first, freeze-in-C posture",
)

REQUIRED_TRACEABILITY_MARKERS = (
    "`net/core/skbuff.c`: `Freeze In C Initially`",
    "retained-in-C posture",
    "must not imply a live `net/core/skbuff_bridge.zig` helper or any skbuff-local compile route",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(_read_text(path))


def _require_contains(haystack: str, needle: str, failures: list[str], label: str) -> None:
    if needle not in haystack:
        failures.append(f"{label}:missing:{needle}")


def _find_gap(manifest: dict, gap_id: str) -> dict | None:
    for gap in manifest.get("gaps", []):
        if gap.get("id") == gap_id:
            return gap
    return None


def collect_failures(root: Path) -> list[str]:
    freeze_map = _read_text(root / FREEZE_MAP_PATH)
    governance_note = _read_text(root / GOVERNANCE_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)
    makefile = _read_text(root / MAKEFILE_PATH)
    rcu_note = _read_text(root / RCU_NOTE_PATH)
    skbuff_note = _read_text(root / SKBUFF_NOTE_PATH)
    traceability_note = _read_text(root / TRACEABILITY_NOTE_PATH)

    failures: list[str] = []

    for rel in DIRECT_PACKET_PATHS:
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_packet:{rel}")

    if manifest.get("lane_key") != "P15-L04":
        failures.append("manifest:lane_key_drift")
    if manifest.get("phase") != "Phase 15":
        failures.append("manifest:phase_drift")
    if manifest.get("surveyed_commit") != "current-master-readback-2026-05-18":
        failures.append("manifest:surveyed_commit_drift")
    if manifest.get("anchor") != str(FREEZE_MAP_PATH):
        failures.append("manifest:anchor_drift")
    if manifest.get("maintenance_handoff", {}).get("current_lane_posture") != "maintenance_mode":
        failures.append("manifest:maintenance_posture_drift")

    freeze_targets = manifest.get("freeze_in_c_targets", [])
    if freeze_targets != [
        "kernel/sched/core.c",
        "mm/page_alloc.c",
        "kernel/rcu/tree.c",
        "net/core/skbuff.c",
    ]:
        failures.append("manifest:freeze_in_c_targets_drift")

    study_targets = manifest.get("study_only_targets", [])
    if study_targets != ["kernel/workqueue.c", "kernel/trace/ring_buffer.c"]:
        failures.append("manifest:study_only_targets_drift")

    replay_commands = manifest.get("maintenance_handoff", {}).get("replay_before_trusting", [])
    for command in (
        "python3 scripts/zigux/check-phase15-docs-readme-alignment.py",
        "python3 scripts/zigux/check-phase15-scripts-readme-alignment.py",
        "python3 scripts/zigux/check-phase15-review-process-handoff.py",
        "python3 scripts/zigux/check-phase15-shared-summary-gap.py",
        "zig test zigux/tests/phase15_freeze_map_governance.zig",
    ):
        if command not in replay_commands:
            failures.append(f"manifest:missing_replay_command:{command}")
        _require_contains(governance_note, command, failures, "governance_note")

    gap_checks = {
        "phase15-shared-validator-route-readback": "scripts/zigux/validate-phase15.py",
        "phase15-shared-build-route-readback": "zigux/tests/phase15_build.zig",
        "phase15-shared-wrapper-route-readback": "zigux/Makefile",
    }
    for gap_id, destination in gap_checks.items():
        gap = _find_gap(manifest, gap_id)
        if gap is None:
            failures.append(f"manifest:missing_gap:{gap_id}")
            continue
        if gap.get("zigux_destination") != destination:
            failures.append(f"manifest:gap_destination_drift:{gap_id}")

    for term_group in manifest.get("governance_requirements", []):
        for term in term_group.get("required_terms", []):
            _require_contains(freeze_map, term, failures, "freeze_map")

    for marker in REQUIRED_NOTE_MARKERS:
        _require_contains(governance_note, marker, failures, "governance_note")

    for blocker in manifest.get("blocker_ownership", []):
        for key in (
            "anchor",
            "owner",
            "required_approver_set",
            "rollback_owner",
            "evidence_archive_path",
            "benchmark_notes",
            "replay_command",
            "latest_blocker_disposition",
        ):
            value = blocker.get(key)
            if value:
                _require_contains(governance_note, value, failures, "governance_note")

    for survey in manifest.get("deep_core_blocker_survey", []):
        for key in ("anchor", "roadmap_basis", "current_blocker"):
            value = survey.get(key)
            if value:
                _require_contains(governance_note, value, failures, "governance_note")

    for rel in BLOCKED_BROADER_PATHS:
        _require_contains(governance_note, rel, failures, "governance_note")
        if (root / rel).exists():
            failures.append(f"repo:blocked_path_returned:{rel}")

    for marker in BLOCKED_MAKEFILE_MARKERS:
        if marker in makefile:
            failures.append(f"makefile:unexpected_phase15_route:{marker}")

    for marker in REQUIRED_RCU_MARKERS:
        _require_contains(rcu_note, marker, failures, "rcu_note")

    for marker in REQUIRED_SKBUFF_MARKERS:
        _require_contains(skbuff_note, marker, failures, "skbuff_note")

    for marker in REQUIRED_TRACEABILITY_MARKERS:
        _require_contains(traceability_note, marker, failures, "traceability_note")

    return failures


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P15-L04",
            "phase": "Phase 15",
            "surveyed_commit": "current-master-readback-2026-05-18",
            "anchor": "Documentation/zigux/freeze-map.md",
            "freeze_in_c_targets": [
                "kernel/sched/core.c",
                "mm/page_alloc.c",
                "kernel/rcu/tree.c",
                "net/core/skbuff.c",
            ],
            "study_only_targets": [
                "kernel/workqueue.c",
                "kernel/trace/ring_buffer.c",
            ],
            "governance_requirements": [
                {
                    "required_terms": [
                        "Architecture Council",
                        "written rationale",
                    ]
                },
                {
                    "required_terms": [
                        "owner, phase, status bucket, validation gate summary, and rollback owner",
                    ]
                },
                {
                    "required_terms": [
                        "required approver set",
                        "automatic return-to-blocked trigger",
                        "retired_from_active_discussion",
                        "reopen triggers",
                        "trigger-specific evidence refresh",
                        "no silent exception path",
                    ]
                },
            ],
            "maintenance_handoff": {
                "current_lane_posture": "maintenance_mode",
                "replay_before_trusting": [
                    "python3 scripts/zigux/check-phase15-docs-readme-alignment.py",
                    "python3 scripts/zigux/check-phase15-scripts-readme-alignment.py",
                    "python3 scripts/zigux/check-phase15-review-process-handoff.py",
                    "python3 scripts/zigux/check-phase15-shared-summary-gap.py",
                    "zig test zigux/tests/phase15_freeze_map_governance.zig",
                ],
            },
            "blocker_ownership": [
                {
                    "anchor": "kernel/sched/core.c",
                    "owner": "Architecture Council",
                    "required_approver_set": "Architecture Council + PMO / Release Management",
                    "rollback_owner": "Architecture Council + PMO / Release Management",
                    "evidence_archive_path": "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
                    "benchmark_notes": "pending_until_bounded_scheduler_seam_exists",
                    "replay_command": "zig test zigux/tests/phase15_freeze_map_governance.zig",
                    "latest_blocker_disposition": "blocked_no_bounded_scheduler_seam",
                },
                {
                    "anchor": "mm/page_alloc.c",
                    "owner": "Architecture Council",
                    "required_approver_set": "Architecture Council + Validation and Perf Team",
                    "rollback_owner": "Architecture Council + Validation and Perf Team",
                    "evidence_archive_path": "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
                    "benchmark_notes": "pending_until_bounded_allocator_seam_exists",
                    "replay_command": "zig test zigux/tests/phase15_freeze_map_governance.zig",
                    "latest_blocker_disposition": "blocked_no_bounded_allocator_seam",
                },
            ],
            "deep_core_blocker_survey": [
                {
                    "anchor": "kernel/rcu/tree.c",
                    "roadmap_basis": "Phase 15 keeps Tree RCU frozen unless a narrower-than-freeze follow-up answers the current blocker with Architecture Council reviewable evidence.",
                    "current_blocker": "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
                },
                {
                    "anchor": "net/core/skbuff.c",
                    "roadmap_basis": "Phase 15 keeps skbuff frozen unless a narrower-than-lifetime follow-up answers the current blocker with Architecture Council reviewable evidence.",
                    "current_blocker": "blocked_packet_lifetime_boundary_still_too_wide",
                },
            ],
            "gaps": [
                {
                    "id": "phase15-shared-validator-route-readback",
                    "zigux_destination": "scripts/zigux/validate-phase15.py",
                },
                {
                    "id": "phase15-shared-build-route-readback",
                    "zigux_destination": "zigux/tests/phase15_build.zig",
                },
                {
                    "id": "phase15-shared-wrapper-route-readback",
                    "zigux_destination": "zigux/Makefile",
                },
            ],
        },
        indent=2,
    ) + "\n"


def _sample_governance_note() -> str:
    return """# Phase 15 Freeze-Map Governance

## Status
- `PHASE15_STATUS=governance_slice_landed`
- `PHASE15_LANE_KEY=P15-L04`
- `PHASE15_SLICE=freeze-map-deep-core-blocker-dated-readback-alignment`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-18`
- shared reminder surfaces still carry as repo-reality gaps on current `master`
- exact branch-head parity is not recorded

## Current blocker posture
- `blocked_no_bounded_scheduler_seam`
- `blocked_no_bounded_allocator_seam`
- `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- `blocked_packet_lifetime_boundary_still_too_wide`

## Maintenance-Mode Handoff
- current lane posture: `maintenance_mode`
- `python3 scripts/zigux/check-phase15-docs-readme-alignment.py`
- `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`
- `python3 scripts/zigux/check-phase15-review-process-handoff.py`
- `python3 scripts/zigux/check-phase15-shared-summary-gap.py`
- `zig test zigux/tests/phase15_freeze_map_governance.zig`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `zigux/tests/phase15_build.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
- current-master contents reads now resolve `zigux/Makefile`
- those wrapper route names remain gap vocabulary rather than direct landed evidence

## Recorded gaps
- `phase15-freeze-map-manifest`
- `phase15-freeze-map-governance-gate`
- `phase15-shared-validator-route-readback`
- `phase15-shared-build-route-readback`
- `phase15-shared-wrapper-route-readback`

## Ownership
- `kernel/sched/core.c`
- `Architecture Council`
- `Architecture Council + PMO / Release Management`
- `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`
- `pending_until_bounded_scheduler_seam_exists`
- `zig test zigux/tests/phase15_freeze_map_governance.zig`
- `mm/page_alloc.c`
- `Architecture Council + Validation and Perf Team`
- `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`
- `pending_until_bounded_allocator_seam_exists`
- `kernel/rcu/tree.c`
- `Phase 15 keeps Tree RCU frozen unless a narrower-than-freeze follow-up answers the current blocker with Architecture Council reviewable evidence.`
- `net/core/skbuff.c`
- `Phase 15 keeps skbuff frozen unless a narrower-than-lifetime follow-up answers the current blocker with Architecture Council reviewable evidence.`
"""


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map
Architecture Council
written rationale
owner, phase, status bucket, validation gate summary, and rollback owner
required approver set
automatic return-to-blocked trigger
retired_from_active_discussion
reopen triggers
trigger-specific evidence refresh
there is no silent exception path around the stay-in-C policy
"""


def _sample_makefile() -> str:
    return "PYTHON ?= python3\n.PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2 phase3-validate phase3\n"


def _sample_rcu_note() -> str:
    return """# Phase 14 RCU Tree Survey
- `PHASE14_LANE_KEY=P14-L14`
This lane is blocked by `phase14-rcu-tree-bridge-blocker`.
That is still a freeze-in-C posture, not a review-ready bridge seam.
"""


def _sample_skbuff_note() -> str:
    return """# Phase 14 Skbuff Bridge Survey
- `PHASE14_LANE_KEY=P14-L11`
- `PHASE14_BLOCKED_GAP=phase14-skbuff-anchor-packet-missing`
current `master` no longer exposes the earlier `P14-L11` skbuff anchor packet files.
Against the Phase 14 roadmap, `net/core/skbuff.c` still belongs in a bounded review-first, freeze-in-C posture.
"""


def _sample_traceability_note() -> str:
    return """# Phase 14 Core Boundary Traceability
- `net/core/skbuff.c`: `Freeze In C Initially`
This note keeps the retained-in-C posture explicit.
It must not imply a live `net/core/skbuff_bridge.zig` helper or any skbuff-local compile route.
"""


def _seed_repo(root: Path) -> None:
    _write(root / GOVERNANCE_NOTE_PATH, _sample_governance_note())
    _write(root / FREEZE_MAP_PATH, _sample_freeze_map())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / GOVERNANCE_ZIG_PATH, "test {}\n")
    _write(root / MAKEFILE_PATH, _sample_makefile())
    _write(root / RCU_NOTE_PATH, _sample_rcu_note())
    _write(root / SKBUFF_NOTE_PATH, _sample_skbuff_note())
    _write(root / TRACEABILITY_NOTE_PATH, _sample_traceability_note())


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_freeze_map_governance_") as tmpdir:
        root = Path(tmpdir)
        _seed_repo(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_marker_root = root / "missing_marker"
        _seed_repo(missing_marker_root)
        _write(
            missing_marker_root / GOVERNANCE_NOTE_PATH,
            _sample_governance_note().replace("phase15-shared-build-route-readback", "", 1),
        )
        failures = collect_failures(missing_marker_root)
        expected = ["governance_note:missing:phase15-shared-build-route-readback"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")

        returned_gap_root = root / "returned_gap"
        _seed_repo(returned_gap_root)
        _write(returned_gap_root / "zigux/tests/phase15_build.zig", "present\n")
        failures = collect_failures(returned_gap_root)
        expected = ["repo:blocked_path_returned:zigux/tests/phase15_build.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected returned-gap failure: {failures}")

        makefile_root = root / "makefile_route"
        _seed_repo(makefile_root)
        _write(makefile_root / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(makefile_root)
        expected = ["makefile:unexpected_phase15_route:phase15-validate:"]
        if failures != expected:
            raise AssertionError(f"unexpected makefile failure: {failures}")

        freeze_map_root = root / "freeze_map_drift"
        _seed_repo(freeze_map_root)
        _write(
            freeze_map_root / FREEZE_MAP_PATH,
            _sample_freeze_map().replace("trigger-specific evidence refresh\n", "", 1),
        )
        failures = collect_failures(freeze_map_root)
        expected = ["freeze_map:missing:trigger-specific evidence refresh"]
        if failures != expected:
            raise AssertionError(f"unexpected freeze-map failure: {failures}")

        rcu_root = root / "rcu_drift"
        _seed_repo(rcu_root)
        _write(
            rcu_root / RCU_NOTE_PATH,
            _sample_rcu_note().replace("That is still a freeze-in-C posture, not a review-ready bridge seam.\n", "", 1),
        )
        failures = collect_failures(rcu_root)
        expected = [
            "rcu_note:missing:That is still a freeze-in-C posture, not a review-ready bridge seam."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected rcu failure: {failures}")

    print("PHASE15_FREEZE_MAP_GOVERNANCE_SELF_TEST=pass")
    print("PHASE15_FREEZE_MAP_GOVERNANCE_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 freeze-map governance packet stays aligned with the current root policy and blocker posture."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE15_FREEZE_MAP_GOVERNANCE=pass")
    print("PHASE15_FREEZE_MAP_GOVERNANCE_DIRECT_PACKET_COUNT=7")
    print(f"PHASE15_FREEZE_MAP_GOVERNANCE_BLOCKED_GAP_COUNT={len(BLOCKED_BROADER_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

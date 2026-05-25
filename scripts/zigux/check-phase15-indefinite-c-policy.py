#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

POLICY_NOTE_REL = "Documentation/zigux/phase15-indefinite-c-policy.md"
POLICY_JSON_REL = "zigux/tests/phase15_indefinite_c_policy.json"
POLICY_TEST_REL = "zigux/tests/phase15_indefinite_c_policy.zig"
LANE_OWNER_ALIGNMENT_REL = "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig"
FREEZE_MAP_REL = "Documentation/zigux/freeze-map.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
DOCS_README_REL = "Documentation/zigux/README.md"
FREEZE_GOVERNANCE_REL = "Documentation/zigux/phase15-freeze-map-governance.md"
REVIEW_PROCESS_REL = "Documentation/zigux/phase15-architecture-council-review-process.md"
DECISION_TEMPLATE_REL = "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
PARITY_SCORECARD_REL = "Documentation/zigux/phase15-parity-scorecard.md"

REQUIRED_FILES = (
    POLICY_NOTE_REL,
    POLICY_JSON_REL,
    POLICY_TEST_REL,
    LANE_OWNER_ALIGNMENT_REL,
    FREEZE_MAP_REL,
    REVIEW_CHECKLIST_REL,
    DOCS_README_REL,
    FREEZE_GOVERNANCE_REL,
    REVIEW_PROCESS_REL,
    DECISION_TEMPLATE_REL,
    PARITY_SCORECARD_REL,
)

REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=indefinite_c_policy_packet_landed",
    "PHASE15_LANE_KEY=P15-L16",
    "PHASE15_SLICE=maintenance-mode-policy-truthfulness",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "surveyed against dated current-master readback marker `current-master-readback-2026-05-21`",
    "This packet keeps that policy surface explicit without claiming a new deep-core Zig bridge, a status change approval, or a broader Phase 15 closure.",
    "the anchor is still in the freeze-in-C set recorded by `Documentation/zigux/freeze-map.md`",
    "the C implementation remains the source of truth for the present plan horizon",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "decision record ID",
    "lane owner",
    "required approver set",
    "rollback owner",
    "automatic return-to-blocked trigger",
    "`retired_from_active_discussion` state",
    "trigger-specific evidence refresh",
    "parity scorecard link or blocker record",
    "explicit non-goals",
    "written rationale",
    "There is no silent exception path around the indefinite-C policy.",
    "Architecture Council reopen request",
    "narrower_followup_answers_blocker",
    "evidence_packet_stale_or_contradictory",
    "ownership_or_validation_changed",
    "zig test zigux/tests/phase15_indefinite_c_policy.zig",
    "zig test zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "phase15-indefinite-c-policy-note",
    "phase15-indefinite-c-policy-manifest",
    "phase15-indefinite-c-policy-test",
    "phase15-indefinite-c-lane-owner-companion-sync",
    "phase15-deep-core-status-change-blocker",
)

EXPECTED_MANIFEST = {
    "lane_key": "P15-L16",
    "phase": "Phase 15",
    "surveyed_commit": "current-master-readback-2026-05-21",
    "surveyed_commit_mode": "dated_master_readback",
    "roadmap_requirement": "policy for code that remains in C indefinitely",
    "anchors": [
        "kernel/sched/core.c",
        "mm/page_alloc.c",
        "kernel/rcu/tree.c",
        "net/core/skbuff.c",
    ],
    "supporting_artifacts": [
        FREEZE_MAP_REL,
        REVIEW_CHECKLIST_REL,
        FREEZE_GOVERNANCE_REL,
        REVIEW_PROCESS_REL,
        DECISION_TEMPLATE_REL,
        PARITY_SCORECARD_REL,
        DOCS_README_REL,
        LANE_OWNER_ALIGNMENT_REL,
    ],
}

EXPECTED_REQUIREMENT_IDS = (
    "indefinite-c-source-of-truth",
    "indefinite-c-recordkeeping",
    "indefinite-c-exception-path",
    "indefinite-c-reopen-trigger-catalog",
)

EXPECTED_GAP_IDS = (
    "phase15-indefinite-c-policy-note",
    "phase15-indefinite-c-policy-manifest",
    "phase15-indefinite-c-policy-test",
    "phase15-indefinite-c-roadmap-gap-restoration",
    "phase15-indefinite-c-review-process-companion-sync",
    "phase15-indefinite-c-ownership-template-sync",
    "phase15-indefinite-c-lane-owner-companion-sync",
    "phase15-deep-core-status-change-blocker",
)

EXPECTED_REOPEN_CONDITIONS = (
    "the freeze-in-C blocker posture changes",
    "the review-process packet changes its required field inventory for a stay-in-C closeout",
    "the parity scorecard changes the blocked-posture accounting that this policy references",
)

POLICY_REFERENCE_MARKER = f"`{POLICY_NOTE_REL}`"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_markers(text: str, markers: tuple[str, ...], prefix: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{prefix}:missing:{marker}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    note = _read(root / POLICY_NOTE_REL)
    manifest = json.loads(_read(root / POLICY_JSON_REL))
    _require_markers(note, REQUIRED_NOTE_MARKERS, "policy_note", failures)

    for key, expected in EXPECTED_MANIFEST.items():
        if manifest.get(key) != expected:
            failures.append(f"manifest:{key}:{manifest.get(key)!r}")

    requirement_ids = tuple(item.get("id") for item in manifest.get("indefinite_c_requirements", []))
    if requirement_ids != EXPECTED_REQUIREMENT_IDS:
        failures.append(f"manifest:indefinite_c_requirements:{requirement_ids!r}")

    gap_ids = tuple(item.get("id") for item in manifest.get("gaps", []))
    if gap_ids != EXPECTED_GAP_IDS:
        failures.append(f"manifest:gaps:{gap_ids!r}")

    maintenance = manifest.get("maintenance_handoff", {})
    if maintenance.get("current_lane_posture") != "maintenance_mode":
        failures.append(f"manifest:current_lane_posture:{maintenance.get('current_lane_posture')!r}")
    if maintenance.get("replay_before_trusting") != [
        "zig test zigux/tests/phase15_indefinite_c_policy.zig",
        "zig test zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    ]:
        failures.append("manifest:replay_before_trusting")
    if tuple(maintenance.get("reopen_conditions", [])) != EXPECTED_REOPEN_CONDITIONS:
        failures.append("manifest:reopen_conditions")

    for rel in (
        FREEZE_MAP_REL,
        REVIEW_CHECKLIST_REL,
        DOCS_README_REL,
        FREEZE_GOVERNANCE_REL,
        REVIEW_PROCESS_REL,
        DECISION_TEMPLATE_REL,
        PARITY_SCORECARD_REL,
    ):
        text = _read(root / rel)
        if POLICY_REFERENCE_MARKER not in text and POLICY_NOTE_REL not in text:
            failures.append(f"supporting_ref_missing:{rel}")

    lane_owner_alignment = _read(root / LANE_OWNER_ALIGNMENT_REL)
    for marker in (
        "PHASE15_LANE_KEY=P15-L16",
        "Documentation/zigux/phase15-indefinite-c-policy.md",
        "lane owner",
        "required approver set",
        "rollback owner",
    ):
        if marker not in lane_owner_alignment:
            failures.append(f"lane_owner_alignment:missing:{marker}")

    return failures


def _sample_policy_note() -> str:
    return """# Phase 15 Indefinite-C Policy

## Status

- `PHASE15_STATUS=indefinite_c_policy_packet_landed`
- `PHASE15_LANE_KEY=P15-L16`
- `PHASE15_SLICE=maintenance-mode-policy-truthfulness`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-21`

This packet keeps that policy surface explicit without claiming a new deep-core Zig bridge, a status change approval, or a broader Phase 15 closure.

- the anchor is still in the freeze-in-C set recorded by `Documentation/zigux/freeze-map.md`
- the C implementation remains the source of truth for the present plan horizon
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- decision record ID
- lane owner
- required approver set
- rollback owner
- automatic return-to-blocked trigger
- retained `retired_from_active_discussion` state
- trigger-specific evidence refresh
- parity scorecard link or blocker record
- explicit non-goals
- written rationale
- There is no silent exception path around the indefinite-C policy.
- Architecture Council reopen request
- `narrower_followup_answers_blocker`
- `evidence_packet_stale_or_contradictory`
- `ownership_or_validation_changed`
- `zig test zigux/tests/phase15_indefinite_c_policy.zig`
- `zig test zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
- landed `phase15-indefinite-c-policy-note`
- landed `phase15-indefinite-c-policy-manifest`
- landed `phase15-indefinite-c-policy-test`
- landed `phase15-indefinite-c-lane-owner-companion-sync`
- blocked_on_stay_in_c_evidence `phase15-deep-core-status-change-blocker`
"""


def _sample_manifest() -> str:
    payload = {
        **EXPECTED_MANIFEST,
        "indefinite_c_requirements": [
            {"id": "indefinite-c-source-of-truth"},
            {"id": "indefinite-c-recordkeeping"},
            {"id": "indefinite-c-exception-path"},
            {"id": "indefinite-c-reopen-trigger-catalog"},
        ],
        "maintenance_handoff": {
            "current_lane_posture": "maintenance_mode",
            "replay_before_trusting": [
                "zig test zigux/tests/phase15_indefinite_c_policy.zig",
                "zig test zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
            ],
            "reopen_conditions": list(EXPECTED_REOPEN_CONDITIONS),
        },
        "gaps": [{"id": gap_id} for gap_id in EXPECTED_GAP_IDS],
    }
    return json.dumps(payload, indent=2) + "\n"


def _seed(root: Path) -> None:
    _write(root / POLICY_NOTE_REL, _sample_policy_note())
    _write(root / POLICY_JSON_REL, _sample_manifest())
    _write(root / POLICY_TEST_REL, "test \"phase15 indefinite c policy packet\" {}\n")
    _write(
        root / LANE_OWNER_ALIGNMENT_REL,
        "const lane = \"PHASE15_LANE_KEY=P15-L16\";\n"
        "// Documentation/zigux/phase15-indefinite-c-policy.md\n"
        "// lane owner\n"
        "// required approver set\n"
        "// rollback owner\n",
    )
    for rel in (
        FREEZE_MAP_REL,
        REVIEW_CHECKLIST_REL,
        DOCS_README_REL,
        FREEZE_GOVERNANCE_REL,
        REVIEW_PROCESS_REL,
        DECISION_TEMPLATE_REL,
        PARITY_SCORECARD_REL,
    ):
        _write(root / rel, f"# placeholder\n\n- `{POLICY_NOTE_REL}`\n")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase15_indefinite_c_policy_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = validate(root)
        if failures:
            raise SystemExit("self-test unexpected failures: " + "; ".join(failures))

        broken = root / POLICY_NOTE_REL
        broken.write_text(_sample_policy_note().replace("Architecture Council reopen request", ""), encoding="utf-8")
        failures = validate(root)
        if not any(item.startswith("policy_note:missing:Architecture Council reopen request") for item in failures):
            raise SystemExit("self-test failed to detect missing reopen-request marker")

    print("PHASE15_INDEFINITE_C_POLICY_SELF_TEST=pass")
    print("PHASE15_INDEFINITE_C_POLICY_SELF_TEST_CASES=2")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the Phase 15 indefinite-C policy packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure)
        raise SystemExit(1)

    print("Phase 15 indefinite-C policy check passed.")


if __name__ == "__main__":
    main()

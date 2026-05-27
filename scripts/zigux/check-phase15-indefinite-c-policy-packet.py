#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

POLICY_NOTE_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
SEQUENCING_NOTE_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
MANIFEST_PATH = Path("zigux/tests/phase15_indefinite_c_policy.json")
POLICY_ZIG_PATH = Path("zigux/tests/phase15_indefinite_c_policy.zig")
LANE_OWNER_PATH = Path("zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_PATHS = (
    POLICY_NOTE_PATH,
    FREEZE_MAP_PATH,
    REVIEW_CHECKLIST_PATH,
    DOCS_README_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    SEQUENCING_NOTE_PATH,
    MANIFEST_PATH,
    POLICY_ZIG_PATH,
    LANE_OWNER_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
)

EXPECTED_ANCHORS = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
]

REQUIRED_POLICY_NOTE_MARKERS = (
    "PHASE15_STATUS=indefinite_c_policy_packet_landed",
    "PHASE15_LANE_KEY=P15-L16",
    "PHASE15_SLICE=maintenance-mode-policy-truthfulness",
    "current-master-readback-2026-05-26",
    "roadmap requirement: `policy for code that remains in C indefinitely`",
    "There is no silent exception path around the indefinite-C policy.",
    "blocked_on_stay_in_c_evidence `phase15-deep-core-status-change-blocker`",
    "zig test zigux/tests/phase15_indefinite_c_policy.zig",
    "zig test zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
)

REQUIRED_DOCS_MARKERS = (
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
)

REQUIRED_REVIEW_MARKERS = (
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "trigger-specific evidence refresh",
)

REQUIRED_SCRIPTS_MARKERS = (
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
)

REQUIRED_TESTS_MARKERS = (
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
)

REQUIRED_SEQUENCING_MARKERS = (
    "Documentation/zigux/phase15-indefinite-c-policy.md` owns the stay-in-C policy vocabulary",
    "the focused indefinite-C lane-owner companion is landed",
    "refresh the indefinite-C policy packet only if the stay-in-C vocabulary or reopen-trigger catalog changed",
)

EXPECTED_SUPPORTING_ARTIFACTS = [
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/README.md",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
]

EXPECTED_REOPEN_TRIGGERS = [
    "narrower_followup_answers_blocker",
    "evidence_packet_stale_or_contradictory",
    "ownership_or_validation_changed",
]

EXPECTED_REPLAY_BEFORE_TRUSTING = [
    "zig test zigux/tests/phase15_indefinite_c_policy.zig",
    "zig test zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
]

EXPECTED_REOPEN_CONDITIONS = [
    "the freeze-in-C blocker posture changes",
    "the review-process packet changes its required field inventory for a stay-in-C closeout",
    "the parity scorecard changes the blocked-posture accounting that this policy references",
]

REQUIRED_GAPS = {
    "phase15-indefinite-c-policy-note": ("landed", "documentation"),
    "phase15-indefinite-c-policy-manifest": ("landed", "validation"),
    "phase15-indefinite-c-policy-test": ("landed", "validation"),
    "phase15-indefinite-c-lane-owner-companion-sync": ("landed", "companion_sync"),
    "phase15-deep-core-status-change-blocker": ("blocked_on_stay_in_c_evidence", "freeze_map"),
}

BLOCKED_ROUTE_MARKERS = (
    "phase15-validate:",
    "phase15-test:",
    "\nphase15:",
    ".PHONY: phase15",
)

BLOCKED_WORKFLOW_MARKERS = (
    "phase15-validate",
    "phase15-test",
    "phase15:",
    "validate-phase15.py",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            failures.append(f"missing_path:{rel}")
    if failures:
        return failures

    policy_note = _read(root / POLICY_NOTE_PATH)
    freeze_map = _read(root / FREEZE_MAP_PATH)
    review_checklist = _read(root / REVIEW_CHECKLIST_PATH)
    docs_readme = _read(root / DOCS_README_PATH)
    scripts_readme = _read(root / SCRIPTS_README_PATH)
    tests_readme = _read(root / TESTS_README_PATH)
    sequencing_note = _read(root / SEQUENCING_NOTE_PATH)
    policy_zig = _read(root / POLICY_ZIG_PATH)
    lane_owner = _read(root / LANE_OWNER_PATH)
    validator = _read(root / VALIDATOR_PATH)
    makefile = _read(root / MAKEFILE_PATH)
    workflow = _read(root / WORKFLOW_PATH)
    manifest = json.loads(_read(root / MANIFEST_PATH))

    for marker in REQUIRED_POLICY_NOTE_MARKERS:
        if marker not in policy_note:
            failures.append(f"policy_note_missing:{marker}")

    for marker in EXPECTED_ANCHORS:
        if marker not in freeze_map:
            failures.append(f"freeze_map_missing_anchor:{marker}")
        if marker not in policy_zig:
            failures.append(f"policy_zig_missing_anchor:{marker}")

    for marker in REQUIRED_DOCS_MARKERS:
        if marker not in docs_readme:
            failures.append(f"docs_readme_missing:{marker}")

    for marker in REQUIRED_REVIEW_MARKERS:
        if marker not in review_checklist:
            failures.append(f"review_checklist_missing:{marker}")

    for marker in REQUIRED_SCRIPTS_MARKERS:
        if marker not in scripts_readme:
            failures.append(f"scripts_readme_missing:{marker}")

    for marker in REQUIRED_TESTS_MARKERS:
        if marker not in tests_readme:
            failures.append(f"tests_readme_missing:{marker}")

    for marker in REQUIRED_SEQUENCING_MARKERS:
        if marker not in sequencing_note:
            failures.append(f"sequencing_note_missing:{marker}")

    if "PHASE15_VALIDATION=pass" not in validator:
        failures.append("validator_missing_success_marker")

    if manifest.get("lane_key") != "P15-L16":
        failures.append("manifest_lane_key_drift")
    if manifest.get("surveyed_commit") != "current-master-readback-2026-05-26":
        failures.append("manifest_surveyed_commit_drift")
    if manifest.get("roadmap_requirement") != "policy for code that remains in C indefinitely":
        failures.append("manifest_roadmap_requirement_drift")
    if manifest.get("anchors") != EXPECTED_ANCHORS:
        failures.append("manifest_anchor_inventory_drift")
    if manifest.get("supporting_artifacts") != EXPECTED_SUPPORTING_ARTIFACTS:
        failures.append("manifest_supporting_artifacts_drift")

    requirements = {entry["id"]: entry for entry in manifest.get("indefinite_c_requirements", [])}
    if requirements.get("indefinite-c-reopen-trigger-catalog", {}).get("required_terms") != EXPECTED_REOPEN_TRIGGERS:
        failures.append("manifest_reopen_trigger_catalog_drift")

    handoff = manifest.get("maintenance_handoff", {})
    if handoff.get("current_lane_posture") != "maintenance_mode":
        failures.append("manifest_handoff_posture_drift")
    if handoff.get("replay_before_trusting") != EXPECTED_REPLAY_BEFORE_TRUSTING:
        failures.append("manifest_handoff_replay_drift")
    if handoff.get("reopen_conditions") != EXPECTED_REOPEN_CONDITIONS:
        failures.append("manifest_handoff_reopen_conditions_drift")

    gaps = {entry["id"]: entry for entry in manifest.get("gaps", [])}
    for gap_id, (expected_status, expected_kind) in REQUIRED_GAPS.items():
        gap = gaps.get(gap_id)
        if gap is None:
            failures.append(f"manifest_missing_gap:{gap_id}")
            continue
        if gap.get("status") != expected_status:
            failures.append(f"manifest_gap_status_drift:{gap_id}")
        if gap.get("kind") != expected_kind:
            failures.append(f"manifest_gap_kind_drift:{gap_id}")

    if "Documentation/zigux/phase15-indefinite-c-policy.md" not in lane_owner:
        failures.append("lane_owner_missing_policy_note")
    if "lane owner" not in lane_owner:
        failures.append("lane_owner_missing_lane_owner_marker")
    if "required approver set" not in lane_owner:
        failures.append("lane_owner_missing_required_approver_marker")

    for marker in BLOCKED_ROUTE_MARKERS:
        if marker in makefile:
            failures.append(f"blocked_make_route_returned:{marker}")

    for marker in BLOCKED_WORKFLOW_MARKERS:
        if marker in workflow:
            failures.append(f"blocked_workflow_route_returned:{marker}")

    return failures


def write_sample_root(root: Path) -> None:
    anchors_text = "\n".join(EXPECTED_ANCHORS) + "\n"

    _write(
        root / POLICY_NOTE_PATH,
        f"""# Phase 15 Indefinite-C Policy

- `PHASE15_STATUS=indefinite_c_policy_packet_landed`
- `PHASE15_LANE_KEY=P15-L16`
- `PHASE15_SLICE=maintenance-mode-policy-truthfulness`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-26`
- roadmap requirement: `policy for code that remains in C indefinitely`
- blocked_on_stay_in_c_evidence `phase15-deep-core-status-change-blocker`
- replay before trusting:
  - `zig test zigux/tests/phase15_indefinite_c_policy.zig`
  - `zig test zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`

There is no silent exception path around the indefinite-C policy.
""",
    )
    _write(
        root / FREEZE_MAP_PATH,
        "# Zigux Freeze Map\n\n## Freeze In C Initially\n"
        + "\n".join(f"- `{anchor}`" for anchor in EXPECTED_ANCHORS)
        + "\n",
    )
    _write(
        root / REVIEW_CHECKLIST_PATH,
        """# Zigux Review Checklist

- `Documentation/zigux/phase15-indefinite-c-policy.md`
- trigger-specific evidence refresh
""",
    )
    _write(
        root / DOCS_README_PATH,
        """# Zigux Documentation

Phase 15 notes
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-readiness-gate-survey.md`
""",
    )
    _write(
        root / SCRIPTS_README_PATH,
        """# scripts/zigux

- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `zigux/tests/phase15_indefinite_c_policy.json`
- `zigux/tests/phase15_indefinite_c_policy.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
""",
    )
    _write(
        root / TESTS_README_PATH,
        """# zigux/tests

- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `zigux/tests/phase15_indefinite_c_policy.json`
- `zigux/tests/phase15_indefinite_c_policy.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
""",
    )
    _write(
        root / SEQUENCING_NOTE_PATH,
        """# Phase 15 Governance Lane Sequencing

- `Documentation/zigux/phase15-indefinite-c-policy.md` owns the stay-in-C policy vocabulary
- the focused indefinite-C lane-owner companion is landed
- refresh the indefinite-C policy packet only if the stay-in-C vocabulary or reopen-trigger catalog changed
""",
    )
    manifest = {
        "lane_key": "P15-L16",
        "phase": "Phase 15",
        "surveyed_commit": "current-master-readback-2026-05-26",
        "surveyed_commit_mode": "dated_master_readback",
        "roadmap_requirement": "policy for code that remains in C indefinitely",
        "anchors": EXPECTED_ANCHORS,
        "supporting_artifacts": EXPECTED_SUPPORTING_ARTIFACTS,
        "indefinite_c_requirements": [
            {"id": "indefinite-c-reopen-trigger-catalog", "required_terms": EXPECTED_REOPEN_TRIGGERS},
        ],
        "maintenance_handoff": {
            "current_lane_posture": "maintenance_mode",
            "replay_before_trusting": EXPECTED_REPLAY_BEFORE_TRUSTING,
            "reopen_conditions": EXPECTED_REOPEN_CONDITIONS,
        },
        "gaps": [
            {"id": gap_id, "status": status, "kind": kind}
            for gap_id, (status, kind) in REQUIRED_GAPS.items()
        ],
    }
    _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    _write(root / POLICY_ZIG_PATH, anchors_text)
    _write(
        root / LANE_OWNER_PATH,
        """const std = @import(\"std\");

test \"lane owner alignment\" {
    _ = \"Documentation/zigux/phase15-indefinite-c-policy.md\";
    _ = \"lane owner\";
    _ = \"required approver set\";
}
""",
    )
    _write(
        root / VALIDATOR_PATH,
        """#!/usr/bin/env python3
print(\"PHASE15_VALIDATION=pass\")
""",
    )
    _write(root / MAKEFILE_PATH, "phase14-validate:\n\t@true\n")
    _write(root / WORKFLOW_PATH, "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: python3 scripts/zigux/check-phase14-shared-smoke-route.py\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_indefinite_c_policy_packet_") as tmp_dir:
        root = Path(tmp_dir)
        baseline = root / "baseline"
        write_sample_root(baseline)
        failures = collect_failures(baseline)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_policy_marker = root / "missing_policy_marker"
        write_sample_root(missing_policy_marker)
        _write(
            missing_policy_marker / POLICY_NOTE_PATH,
            _read(missing_policy_marker / POLICY_NOTE_PATH).replace(
                "There is no silent exception path around the indefinite-C policy.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_policy_marker)
        expected = ["policy_note_missing:There is no silent exception path around the indefinite-C policy."]
        if failures != expected:
            raise AssertionError(f"unexpected policy-marker failure: {failures}")
        case_count += 1

        anchor_drift = root / "anchor_drift"
        write_sample_root(anchor_drift)
        manifest = json.loads(_read(anchor_drift / MANIFEST_PATH))
        manifest["anchors"][3] = "net/core/other.c"
        _write(anchor_drift / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        failures = collect_failures(anchor_drift)
        expected = ["manifest_anchor_inventory_drift"]
        if failures != expected:
            raise AssertionError(f"unexpected anchor-drift failure: {failures}")
        case_count += 1

        lane_owner_drift = root / "lane_owner_drift"
        write_sample_root(lane_owner_drift)
        _write(
            lane_owner_drift / LANE_OWNER_PATH,
            _read(lane_owner_drift / LANE_OWNER_PATH).replace("required approver set", "approver set", 1),
        )
        failures = collect_failures(lane_owner_drift)
        expected = ["lane_owner_missing_required_approver_marker"]
        if failures != expected:
            raise AssertionError(f"unexpected lane-owner failure: {failures}")
        case_count += 1

        make_route_returned = root / "make_route_returned"
        write_sample_root(make_route_returned)
        _write(make_route_returned / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(make_route_returned)
        expected = ["blocked_make_route_returned:phase15-validate:"]
        if failures != expected:
            raise AssertionError(f"unexpected make-route failure: {failures}")
        case_count += 1

        workflow_route_returned = root / "workflow_route_returned"
        write_sample_root(workflow_route_returned)
        _write(
            workflow_route_returned / WORKFLOW_PATH,
            "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: python3 scripts/zigux/validate-phase15.py\n",
        )
        failures = collect_failures(workflow_route_returned)
        expected = ["blocked_workflow_route_returned:validate-phase15.py"]
        if failures != expected:
            raise AssertionError(f"unexpected workflow-route failure: {failures}")
        case_count += 1

    print("PHASE15_INDEFINITE_C_POLICY_PACKET_SELF_TEST=pass")
    print(f"PHASE15_INDEFINITE_C_POLICY_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the landed Phase 15 indefinite-C policy packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run synthetic fixture coverage")
    parser.add_argument("--write-sample-root", type=Path, help="write a focused current-like sample root")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE15_INDEFINITE_C_POLICY_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_INDEFINITE_C_POLICY_PACKET=pass")
    print(f"PHASE15_INDEFINITE_C_POLICY_PACKET_ANCHOR_COUNT={len(EXPECTED_ANCHORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

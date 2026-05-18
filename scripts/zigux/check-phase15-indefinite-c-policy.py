#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

POLICY_NOTE_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
README_PATH = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
FREEZE_GOVERNANCE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
PARITY_SCORECARD_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
MANIFEST_PATH = Path("zigux/tests/phase15_indefinite_c_policy.json")
TEST_PATH = Path("zigux/tests/phase15_indefinite_c_policy.zig")

CURRENT_READBACK_MARKER = "current-master-readback-2026-05-18"

REQUIRED_POLICY_MARKERS = (
    "PHASE15_STATUS=indefinite_c_policy_packet_landed",
    "PHASE15_LANE_KEY=P15-L13",
    "PHASE15_SLICE=maintenance-mode-policy-truthfulness",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    f"surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`",
    "the C implementation remains the source of truth",
    "evidence archive path",
    "automatic return-to-blocked trigger",
    "retired_from_active_discussion",
    "trigger-specific evidence refresh",
    "There is no silent exception path around the indefinite-C policy.",
    "zig test zigux/tests/phase15_indefinite_c_policy.zig",
    "phase15-indefinite-c-review-process-companion-sync",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/review-checklist.md`",
)

README_REQUIRED_MARKERS = (
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

REVIEW_CHECKLIST_REQUIRED_MARKERS = (
    "indefinite-C policy link or explicit non-applicability note",
    "automatic return-to-blocked trigger",
    "trigger-specific evidence refresh",
)

FREEZE_MAP_REQUIRED_MARKERS = (
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "there is no silent exception path around the stay-in-C policy",
    "automatic return-to-blocked trigger",
    "trigger-specific evidence refresh",
)

FREEZE_GOVERNANCE_REQUIRED_MARKERS = (
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "there is no silent exception path around the stay-in-C policy",
    "phase15-shared-validator-route-readback",
    "phase15-deep-core-status-change-blocker",
)

REVIEW_PROCESS_REQUIRED_MARKERS = (
    "`Documentation/zigux/phase15-indefinite-c-policy.md` keeps the stay-in-C policy companion explicit",
    "indefinite-C policy link or explicit non-applicability note",
    "retired_from_active_discussion",
)

PARITY_SCORECARD_REQUIRED_MARKERS = (
    "blocked status-change anchor count: `4`",
    "Architecture Council approvals recorded for status change: `0`",
    "the freeze map, the review-process note, and the indefinite-C policy aligned around the same blocked posture",
    "zig test zigux/tests/phase15_indefinite_c_policy.zig",
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing file: {path}") from exc


def _read_manifest(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing file: {path}") from exc


def _check_markers(text: str, markers: tuple[str, ...], label: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label} missing required marker: {marker}")


def collect_failures(root: Path) -> list[str]:
    policy_note = _read_text(root / POLICY_NOTE_PATH)
    readme = _read_text(root / README_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    freeze_map = _read_text(root / FREEZE_MAP_PATH)
    freeze_governance = _read_text(root / FREEZE_GOVERNANCE_PATH)
    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    parity_scorecard = _read_text(root / PARITY_SCORECARD_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)
    normalized_policy_note = policy_note.replace("`", "")

    failures: list[str] = []

    expected_supporting_artifacts = [
        "Documentation/zigux/freeze-map.md",
        "Documentation/zigux/review-checklist.md",
        "Documentation/zigux/phase15-freeze-map-governance.md",
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        "Documentation/zigux/phase15-parity-scorecard.md",
        "Documentation/zigux/README.md",
    ]

    if manifest.get("lane_key") != "P15-L13":
        failures.append("manifest lane_key drifted away from P15-L13")
    if manifest.get("phase") != "Phase 15":
        failures.append("manifest phase drifted away from Phase 15")
    if manifest.get("surveyed_commit") != CURRENT_READBACK_MARKER:
        failures.append("manifest surveyed_commit drifted away from the current dated readback marker")
    if manifest.get("surveyed_commit_mode") != "dated_master_readback":
        failures.append("manifest surveyed_commit_mode drifted away from dated_master_readback")
    if manifest.get("roadmap_requirement") != "policy for code that remains in C indefinitely":
        failures.append("manifest roadmap_requirement drifted away from the indefinite-C policy charter")

    anchors = manifest.get("anchors", [])
    if anchors != [
        "kernel/sched/core.c",
        "mm/page_alloc.c",
        "kernel/rcu/tree.c",
        "net/core/skbuff.c",
    ]:
        failures.append("manifest anchors no longer match the freeze-in-C anchor inventory")

    supporting_artifacts = manifest.get("supporting_artifacts", [])
    if supporting_artifacts != expected_supporting_artifacts:
        failures.append("manifest supporting_artifacts drifted away from the expected Lane 02 reminder surfaces")

    requirements = manifest.get("indefinite_c_requirements", [])
    if len(requirements) != 4:
        failures.append("manifest indefinite_c_requirements count drifted away from 4")

    requirement_by_id = {item.get("id"): item for item in requirements}

    recordkeeping_terms = requirement_by_id.get("indefinite-c-recordkeeping", {}).get("required_terms", [])
    for term in (
        "lane owner",
        "required approver set",
        "rollback owner",
        "evidence archive path",
        "automatic return-to-blocked trigger",
        "retired_from_active_discussion state",
        "reopen triggers",
        "trigger-specific evidence refresh",
        "explicit non-goals",
        "written rationale",
    ):
        if term not in recordkeeping_terms:
            failures.append(f"manifest recordkeeping terms missing required entry: {term}")
        if term not in normalized_policy_note:
            failures.append(f"policy note missing recordkeeping term: {term}")

    exception_terms = requirement_by_id.get("indefinite-c-exception-path", {}).get("required_terms", [])
    for term in (
        "no silent exception path",
        "Architecture Council reopen request",
        "trigger-specific evidence refresh",
    ):
        if term not in exception_terms:
            failures.append(f"manifest exception-path terms missing required entry: {term}")

    reopen_terms = requirement_by_id.get("indefinite-c-reopen-trigger-catalog", {}).get("required_terms", [])
    for term in (
        "narrower_followup_answers_blocker",
        "evidence_packet_stale_or_contradictory",
        "ownership_or_validation_changed",
    ):
        if term not in reopen_terms:
            failures.append(f"manifest reopen-trigger catalog missing required entry: {term}")
        if term not in policy_note:
            failures.append(f"policy note missing reopen-trigger marker: {term}")

    handoff = manifest.get("maintenance_handoff", {})
    if handoff.get("current_lane_posture") != "maintenance_mode":
        failures.append("manifest maintenance_handoff current_lane_posture drifted away from maintenance_mode")
    if handoff.get("replay_before_trusting") != ["zig test zigux/tests/phase15_indefinite_c_policy.zig"]:
        failures.append("manifest maintenance_handoff replay_before_trusting drifted away from the direct Zig replay")

    for marker in handoff.get("reopen_conditions", []):
        if marker not in policy_note:
            failures.append(f"policy note missing maintenance-handoff reopen condition: {marker}")

    if not (root / TEST_PATH).exists():
        failures.append("focused indefinite-C Zig replay is missing from repo: `zigux/tests/phase15_indefinite_c_policy.zig`")

    _check_markers(policy_note, REQUIRED_POLICY_MARKERS, "policy note", failures)
    _check_markers(readme, README_REQUIRED_MARKERS, "docs root README", failures)
    _check_markers(review_checklist, REVIEW_CHECKLIST_REQUIRED_MARKERS, "review checklist", failures)
    _check_markers(freeze_map, FREEZE_MAP_REQUIRED_MARKERS, "freeze map", failures)
    _check_markers(freeze_governance, FREEZE_GOVERNANCE_REQUIRED_MARKERS, "freeze-map governance note", failures)
    _check_markers(review_process, REVIEW_PROCESS_REQUIRED_MARKERS, "review-process note", failures)
    _check_markers(parity_scorecard, PARITY_SCORECARD_REQUIRED_MARKERS, "parity scorecard", failures)

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P15-L13",
            "phase": "Phase 15",
            "surveyed_commit": CURRENT_READBACK_MARKER,
            "surveyed_commit_mode": "dated_master_readback",
            "roadmap_requirement": "policy for code that remains in C indefinitely",
            "anchors": [
                "kernel/sched/core.c",
                "mm/page_alloc.c",
                "kernel/rcu/tree.c",
                "net/core/skbuff.c",
            ],
            "supporting_artifacts": [
                "Documentation/zigux/freeze-map.md",
                "Documentation/zigux/review-checklist.md",
                "Documentation/zigux/phase15-freeze-map-governance.md",
                "Documentation/zigux/phase15-architecture-council-review-process.md",
                "Documentation/zigux/phase15-parity-scorecard.md",
                "Documentation/zigux/README.md",
            ],
            "indefinite_c_requirements": [
                {
                    "id": "indefinite-c-source-of-truth",
                    "required_terms": ["product source of truth", "remains in C indefinitely"],
                },
                {
                    "id": "indefinite-c-recordkeeping",
                    "required_terms": [
                        "Linux anchor path",
                        "current roadmap phase",
                        "current status bucket",
                        "requested decision bucket",
                        "decision record ID",
                        "lane owner",
                        "required approver set",
                        "rollback owner",
                        "validation gate summary",
                        "benchmark-notes status",
                        "replay command",
                        "latest blocker disposition",
                        "evidence archive path",
                        "automatic return-to-blocked trigger",
                        "retired_from_active_discussion state",
                        "reopen triggers",
                        "trigger-specific evidence refresh",
                        "parity scorecard link or blocker record",
                        "explicit non-goals",
                        "written rationale",
                    ],
                },
                {
                    "id": "indefinite-c-exception-path",
                    "required_terms": [
                        "no silent exception path",
                        "Architecture Council reopen request",
                        "trigger-specific evidence refresh",
                    ],
                },
                {
                    "id": "indefinite-c-reopen-trigger-catalog",
                    "required_terms": [
                        "narrower_followup_answers_blocker",
                        "evidence_packet_stale_or_contradictory",
                        "ownership_or_validation_changed",
                    ],
                },
            ],
            "maintenance_handoff": {
                "current_lane_posture": "maintenance_mode",
                "replay_before_trusting": ["zig test zigux/tests/phase15_indefinite_c_policy.zig"],
                "reopen_conditions": [
                    "the freeze-in-C blocker posture changes",
                    "the review-process packet changes its required field inventory for a stay-in-C closeout",
                    "the parity scorecard changes the blocked-posture accounting that this policy references",
                ],
            },
        },
        indent=2,
    ) + "\n"


def _sample_policy_note() -> str:
    return f"""# Phase 15 Indefinite-C Policy

- `PHASE15_STATUS=indefinite_c_policy_packet_landed`
- `PHASE15_LANE_KEY=P15-L13`
- `PHASE15_SLICE=maintenance-mode-policy-truthfulness`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`
- the C implementation remains the source of truth
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/review-checklist.md`
- evidence archive path
- automatic return-to-blocked trigger
- retired_from_active_discussion
- retired_from_active_discussion state
- reopen triggers
- trigger-specific evidence refresh
- There is no silent exception path around the indefinite-C policy.
- replay before trusting this parked handoff:
  - `zig test zigux/tests/phase15_indefinite_c_policy.zig`
- phase15-indefinite-c-review-process-companion-sync
- lane owner
- required approver set
- rollback owner
- explicit non-goals
- written rationale
- narrower_followup_answers_blocker
- evidence_packet_stale_or_contradictory
- ownership_or_validation_changed
- the freeze-in-C blocker posture changes
- the review-process packet changes its required field inventory for a stay-in-C closeout
- the parity scorecard changes the blocked-posture accounting that this policy references
"""


def _sample_readme() -> str:
    return """# Zigux Documentation

- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
"""


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

- indefinite-C policy link or explicit non-applicability note
- automatic return-to-blocked trigger
- trigger-specific evidence refresh
"""


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

- `Documentation/zigux/phase15-indefinite-c-policy.md`
- there is no silent exception path around the stay-in-C policy
- automatic return-to-blocked trigger
- trigger-specific evidence refresh
"""


def _sample_freeze_governance() -> str:
    return """# Phase 15 Freeze-Map Governance

- `Documentation/zigux/phase15-indefinite-c-policy.md`
- there is no silent exception path around the stay-in-C policy
- phase15-shared-validator-route-readback
- phase15-deep-core-status-change-blocker
"""


def _sample_review_process() -> str:
    return """# Phase 15 Architecture Council Review Process

- `Documentation/zigux/phase15-indefinite-c-policy.md` keeps the stay-in-C policy companion explicit
- indefinite-C policy link or explicit non-applicability note
- retained retired_from_active_discussion marker
"""


def _sample_parity_scorecard() -> str:
    return """# Phase 15 Parity Scorecard

- blocked status-change anchor count: `4`
- Architecture Council approvals recorded for status change: `0`
- the freeze map, the review-process note, and the indefinite-C policy aligned around the same blocked posture
- `zig test zigux/tests/phase15_indefinite_c_policy.zig`
"""


def _sample_test_file() -> str:
    return """const std = @import("std");

test "placeholder indefinite-C replay exists" {
    try std.testing.expect(true);
}
"""


def _seed_repo(root: Path) -> None:
    _write(root / POLICY_NOTE_PATH, _sample_policy_note())
    _write(root / README_PATH, _sample_readme())
    _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
    _write(root / FREEZE_MAP_PATH, _sample_freeze_map())
    _write(root / FREEZE_GOVERNANCE_PATH, _sample_freeze_governance())
    _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
    _write(root / PARITY_SCORECARD_PATH, _sample_parity_scorecard())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / TEST_PATH, _sample_test_file())


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_indefinite_policy_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        policy_root = root / "policy"
        _seed_repo(policy_root)
        _write(
            policy_root / POLICY_NOTE_PATH,
            _sample_policy_note().replace(
                "There is no silent exception path around the indefinite-C policy.\n", "", 1
            ),
        )
        failures = collect_failures(policy_root)
        expected = [
            "policy note missing required marker: There is no silent exception path around the indefinite-C policy."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected policy-marker failure: {failures}")

        manifest_root = root / "manifest"
        _seed_repo(manifest_root)
        manifest = json.loads(_sample_manifest())
        manifest["supporting_artifacts"] = manifest["supporting_artifacts"][:-1]
        _write(manifest_root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        failures = collect_failures(manifest_root)
        expected = [
            "manifest supporting_artifacts drifted away from the expected Lane 02 reminder surfaces"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected manifest failure: {failures}")

        readme_root = root / "readme"
        _seed_repo(readme_root)
        _write(
            readme_root / README_PATH,
            _sample_readme().replace("`Documentation/zigux/phase15-indefinite-c-policy.md`\n", "", 1),
        )
        failures = collect_failures(readme_root)
        expected = [
            "docs root README missing required marker: `Documentation/zigux/phase15-indefinite-c-policy.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected readme failure: {failures}")

        freeze_root = root / "freeze"
        _seed_repo(freeze_root)
        _write(
            freeze_root / FREEZE_MAP_PATH,
            _sample_freeze_map().replace(
                "there is no silent exception path around the stay-in-C policy\n", "", 1
            ),
        )
        failures = collect_failures(freeze_root)
        expected = [
            "freeze map missing required marker: there is no silent exception path around the stay-in-C policy"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected freeze-map failure: {failures}")

        review_root = root / "review"
        _seed_repo(review_root)
        _write(
            review_root / REVIEW_PROCESS_PATH,
            _sample_review_process().replace(
                "`Documentation/zigux/phase15-indefinite-c-policy.md` keeps the stay-in-C policy companion explicit\n",
                "",
                1,
            ),
        )
        failures = collect_failures(review_root)
        expected = [
            "review-process note missing required marker: `Documentation/zigux/phase15-indefinite-c-policy.md` keeps the stay-in-C policy companion explicit"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected review-process failure: {failures}")

        test_root = root / "test"
        _seed_repo(test_root)
        (test_root / TEST_PATH).unlink()
        failures = collect_failures(test_root)
        expected = [
            "focused indefinite-C Zig replay is missing from repo: `zigux/tests/phase15_indefinite_c_policy.zig`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected test-file failure: {failures}")

    print("PHASE15_INDEFINITE_C_POLICY_SELF_TEST=pass")
    print("PHASE15_INDEFINITE_C_POLICY_SELF_TEST_CASES=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 indefinite-C policy packet stays aligned with its Lane 02 governance surfaces."
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
        help="run the built-in synthetic self-test",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        failures = collect_failures(args.root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 indefinite-C policy check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

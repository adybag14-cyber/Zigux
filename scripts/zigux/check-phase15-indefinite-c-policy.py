#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

POLICY_NOTE_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
MANIFEST_PATH = Path("zigux/tests/phase15_indefinite_c_policy.json")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
FREEZE_GOVERNANCE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
DECISION_TEMPLATE_PATH = Path(
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
PARITY_SCORECARD_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
LANE_OWNER_ALIGNMENT_PATH = Path(
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig"
)
POLICY_TEST_PATH = Path("zigux/tests/phase15_indefinite_c_policy.zig")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")

REQUIRED_STATUS_MARKERS = (
    "PHASE15_STATUS=indefinite_c_policy_packet_landed",
    "PHASE15_LANE_KEY=P15-L16",
    "PHASE15_SLICE=maintenance-mode-policy-truthfulness",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
)

REQUIRED_POLICY_MARKERS = (
    "product source of truth",
    "remains in C indefinitely",
    "no silent exception path",
    "Architecture Council reopen request",
    "trigger-specific evidence refresh",
    "narrower_followup_answers_blocker",
    "evidence_packet_stale_or_contradictory",
    "ownership_or_validation_changed",
    "current lane posture: `maintenance_mode`",
)

REQUIRED_REVIEW_PROCESS_MARKERS = (
    "`Documentation/zigux/phase15-indefinite-c-policy.md` keeps the stay-in-C policy companion explicit",
    "This note exists to keep that review-policy surface explicit beside",
)

REQUIRED_DECISION_TEMPLATE_MARKERS = (
    "indefinite-C policy link or explicit non-applicability note:",
    "the retained `freeze_in_c` decision:",
    "the automatic return-to-blocked trigger:",
    "the trigger-specific evidence refresh:",
)

REQUIRED_CHECKLIST_MARKERS = (
    "`Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion",
    "if the change touches the shared Phase 15 governance packet",
)

REQUIRED_DOCS_README_MARKERS = (
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`zigux/tests/phase15_indefinite_c_policy.json`",
    "`zigux/tests/phase15_indefinite_c_policy.zig`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
)

REQUIRED_HANDOFF_MARKERS = (
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
)

TERM_ALIASES = {
    "current roadmap phase": ("current roadmap phase", "roadmap phase"),
    "retired_from_active_discussion state": (
        "retired_from_active_discussion state",
        "`retired_from_active_discussion` state",
    ),
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _text_has_term(text: str, term: str) -> bool:
    choices = TERM_ALIASES.get(term, (term,))
    return any(choice in text for choice in choices)


def collect_failures(root: Path) -> list[str]:
    note = _read_text(root / POLICY_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)
    freeze_map = _read_text(root / FREEZE_MAP_PATH)
    freeze_governance = _read_text(root / FREEZE_GOVERNANCE_PATH)
    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    decision_template = _read_text(root / DECISION_TEMPLATE_PATH)
    parity_scorecard = _read_text(root / PARITY_SCORECARD_PATH)
    docs_readme = _read_text(root / DOCS_README_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)

    failures: list[str] = []

    for marker in REQUIRED_STATUS_MARKERS:
        if marker not in note:
            failures.append(f"policy note missing status marker: {marker}")

    if manifest["surveyed_commit"] not in note:
        failures.append("policy note is missing the manifest surveyed_commit marker")
    if manifest["surveyed_commit_mode"] not in note:
        failures.append("policy note is missing the manifest surveyed_commit_mode marker")

    for marker in REQUIRED_POLICY_MARKERS:
        if marker not in note:
            failures.append(f"policy note missing required marker: {marker}")

    for path in manifest["supporting_artifacts"]:
        if not (root / path).exists():
            failures.append(f"supporting artifact missing from repo: `{path}`")
        if f"`{path}`" not in note and f"`{path}`" not in docs_readme:
            failures.append(f"policy packet lost supporting artifact marker: `{path}`")

    for item in manifest["indefinite_c_requirements"]:
        for term in item["required_terms"]:
            if not _text_has_term(note, term):
                failures.append(
                    f"policy note is missing required indefinite-C term: {term}"
                )

    handoff = manifest["maintenance_handoff"]
    if f"current lane posture: `{handoff['current_lane_posture']}`" not in note:
        failures.append("policy note is missing the maintenance_mode handoff posture")

    for command in handoff["replay_before_trusting"]:
        if command not in note:
            failures.append(f"policy note is missing replay command: {command}")

    for condition in handoff["reopen_conditions"]:
        if condition not in note:
            failures.append(f"policy note is missing reopen condition: {condition}")

    for gap in manifest["gaps"]:
        if gap["id"] not in note:
            failures.append(f"policy note is missing gap marker: {gap['id']}")
        if gap["zigux_destination"] not in note and gap["zigux_destination"] not in docs_readme:
            failures.append(
                f"policy packet lost destination marker for gap `{gap['id']}`: `{gap['zigux_destination']}`"
            )

    for marker in REQUIRED_REVIEW_PROCESS_MARKERS:
        if marker not in review_process:
            failures.append(f"review-process note missing policy companion marker: {marker}")

    for marker in REQUIRED_DECISION_TEMPLATE_MARKERS:
        if marker not in decision_template:
            failures.append(
                f"decision-record template missing stay-in-C field marker: {marker}"
            )

    for marker in REQUIRED_CHECKLIST_MARKERS:
        if marker not in review_checklist:
            failures.append(f"review checklist missing policy boundary marker: {marker}")

    for marker in REQUIRED_DOCS_README_MARKERS:
        if marker not in docs_readme:
            failures.append(f"docs README missing indefinite-C packet marker: {marker}")

    for marker in REQUIRED_HANDOFF_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff note missing policy packet marker: {marker}")

    for anchor in manifest["anchors"]:
        if f"`{anchor}`" not in freeze_map:
            failures.append(f"freeze map is missing anchor marker: `{anchor}`")
        if f"`{anchor}`" not in freeze_governance:
            failures.append(f"freeze governance note is missing anchor marker: `{anchor}`")
        if f"`{anchor}`" not in parity_scorecard:
            failures.append(f"parity scorecard is missing anchor marker: `{anchor}`")

    if not (root / POLICY_TEST_PATH).exists():
        failures.append(
            "policy replay is missing from repo: `zigux/tests/phase15_indefinite_c_policy.zig`"
        )
    if not (root / LANE_OWNER_ALIGNMENT_PATH).exists():
        failures.append(
            "lane-owner alignment replay is missing from repo: `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`"
        )

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_policy_note() -> str:
    return """# Phase 15 Indefinite-C Policy

## Status

- `PHASE15_STATUS=indefinite_c_policy_packet_landed`
- `PHASE15_LANE_KEY=P15-L16`
- `PHASE15_SLICE=maintenance-mode-policy-truthfulness`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-20`

## Why this slice exists

The existing C implementation remains the product source of truth while the anchor remains in C indefinitely.

## Required recorded fields

Those ownership, validation, and rollback fields stay coupled to `Documentation/zigux/phase15-architecture-council-decision-record-template.md` so the stay-in-C closeout record reuses the same reviewable ownership vocabulary as the broader Phase 15 governance packet.

- the Linux anchor path, roadmap phase, current status bucket, and requested decision bucket
- the decision record ID, lane owner, required approver set, and rollback owner
- the validation gate summary, benchmark-notes status, replay command, latest blocker disposition, and evidence archive path
- the automatic return-to-blocked trigger, retained `retired_from_active_discussion` state, reopen triggers, and trigger-specific evidence refresh
- the parity scorecard link or blocker record, explicit non-goals, and written rationale for why the anchor remains in C

## Exception posture

There is no silent exception path around the indefinite-C policy.

The only allowed exception is a documented Architecture Council reopen request that cites a named reopen trigger and carries the trigger-specific evidence refresh showing why the older blocker is no longer the current product truth.

## Reopen Trigger Catalog

- `narrower_followup_answers_blocker`
- `evidence_packet_stale_or_contradictory`
- `ownership_or_validation_changed`

## Maintenance-Mode Handoff

- current lane posture: `maintenance_mode`
- replay before trusting this parked handoff:
  - `zig test zigux/tests/phase15_indefinite_c_policy.zig`
  - `zig test zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
- reopen only when one of the packet-local conditions below becomes true:
  - the freeze-in-C blocker posture changes
  - the review-process packet changes its required field inventory for a stay-in-C closeout
  - the parity scorecard changes the blocked-posture accounting that this policy references

## Recorded gaps

- landed `phase15-indefinite-c-policy-note`
- landed `phase15-indefinite-c-policy-manifest`
- landed `phase15-indefinite-c-policy-test`
- landed `phase15-indefinite-c-roadmap-gap-restoration`
- landed `phase15-indefinite-c-review-process-companion-sync`
- landed `phase15-indefinite-c-ownership-template-sync`
- landed `phase15-indefinite-c-lane-owner-companion-sync`
- blocked_on_stay_in_c_evidence `phase15-deep-core-status-change-blocker`

## Companion paths

- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/README.md`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
- `zigux/tests/phase15_indefinite_c_policy.zig`
- `zigux/tests/phase15_indefinite_c_policy.json`
"""


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P15-L16",
            "phase": "Phase 15",
            "surveyed_commit": "current-master-readback-2026-05-20",
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
                "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
                "Documentation/zigux/phase15-parity-scorecard.md",
                "Documentation/zigux/README.md",
                "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
            ],
            "indefinite_c_requirements": [
                {
                    "id": "indefinite-c-source-of-truth",
                    "required_terms": [
                        "product source of truth",
                        "remains in C indefinitely",
                    ],
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
                "replay_before_trusting": [
                    "zig test zigux/tests/phase15_indefinite_c_policy.zig",
                    "zig test zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
                ],
                "reopen_conditions": [
                    "the freeze-in-C blocker posture changes",
                    "the review-process packet changes its required field inventory for a stay-in-C closeout",
                    "the parity scorecard changes the blocked-posture accounting that this policy references",
                ],
            },
            "gaps": [
                {
                    "id": "phase15-indefinite-c-policy-note",
                    "zigux_destination": "Documentation/zigux/phase15-indefinite-c-policy.md",
                },
                {
                    "id": "phase15-indefinite-c-policy-manifest",
                    "zigux_destination": "zigux/tests/phase15_indefinite_c_policy.json",
                },
                {
                    "id": "phase15-indefinite-c-policy-test",
                    "zigux_destination": "zigux/tests/phase15_indefinite_c_policy.zig",
                },
                {
                    "id": "phase15-indefinite-c-roadmap-gap-restoration",
                    "zigux_destination": "Documentation/zigux/phase15-indefinite-c-policy.md",
                },
                {
                    "id": "phase15-indefinite-c-review-process-companion-sync",
                    "zigux_destination": "Documentation/zigux/phase15-architecture-council-review-process.md",
                },
                {
                    "id": "phase15-indefinite-c-ownership-template-sync",
                    "zigux_destination": "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
                },
                {
                    "id": "phase15-indefinite-c-lane-owner-companion-sync",
                    "zigux_destination": "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
                },
                {
                    "id": "phase15-deep-core-status-change-blocker",
                    "zigux_destination": "Documentation/zigux/phase15-parity-scorecard.md",
                },
            ],
        },
        indent=2,
    ) + "\n"


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

## Freeze In C Initially
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`
"""


def _sample_freeze_governance() -> str:
    return """# Phase 15 Freeze-Map Governance

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`
"""


def _sample_review_process() -> str:
    return """# Phase 15 Architecture Council Review Process

This note exists to keep that review-policy surface explicit beside `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`.

- `Documentation/zigux/phase15-indefinite-c-policy.md` keeps the stay-in-C policy companion explicit
"""


def _sample_decision_template() -> str:
    return """# Phase 15 Architecture Council Decision Record Template

- indefinite-C policy link or explicit non-applicability note:
- the retained `freeze_in_c` decision:
- the automatic return-to-blocked trigger:
- the trigger-specific evidence refresh:
"""


def _sample_parity_scorecard() -> str:
    return """# Phase 15 Parity Scorecard

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`
"""


def _sample_docs_readme() -> str:
    return """# Zigux Documentation

- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `zigux/tests/phase15_indefinite_c_policy.json`
- `zigux/tests/phase15_indefinite_c_policy.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
"""


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

- `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion
- if the change touches the shared Phase 15 governance packet
"""


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
"""


def _seed_repo(root: Path) -> None:
    _write(root / POLICY_NOTE_PATH, _sample_policy_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / FREEZE_MAP_PATH, _sample_freeze_map())
    _write(root / FREEZE_GOVERNANCE_PATH, _sample_freeze_governance())
    _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
    _write(root / DECISION_TEMPLATE_PATH, _sample_decision_template())
    _write(root / PARITY_SCORECARD_PATH, _sample_parity_scorecard())
    _write(root / DOCS_README_PATH, _sample_docs_readme())
    _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    _write(root / POLICY_TEST_PATH, "// replay present\n")
    _write(root / LANE_OWNER_ALIGNMENT_PATH, "// alignment replay present\n")


def write_sample_root(root: Path) -> None:
    _seed_repo(root)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_indefinite_c_policy_") as tmpdir:
        root = Path(tmpdir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_policy_root = root / "missing_policy_term"
        _seed_repo(missing_policy_root)
        text = _read_text(missing_policy_root / POLICY_NOTE_PATH)
        _write(
            missing_policy_root / POLICY_NOTE_PATH,
            text.replace("ownership_or_validation_changed", "", 1),
        )
        failures = collect_failures(missing_policy_root)
        expected = [
            "policy note missing required marker: ownership_or_validation_changed",
            "policy note is missing required indefinite-C term: ownership_or_validation_changed",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-term failure: {failures}")
        case_count += 1

        missing_doc_root = root / "missing_doc_marker"
        _seed_repo(missing_doc_root)
        text = _read_text(missing_doc_root / DOCS_README_PATH)
        _write(
            missing_doc_root / DOCS_README_PATH,
            text.replace("`zigux/tests/phase15_indefinite_c_policy.json`\n", "", 1),
        )
        failures = collect_failures(missing_doc_root)
        expected = [
            "docs README missing indefinite-C packet marker: `zigux/tests/phase15_indefinite_c_policy.json`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected docs failure: {failures}")
        case_count += 1

        missing_template_root = root / "missing_template_marker"
        _seed_repo(missing_template_root)
        text = _read_text(missing_template_root / DECISION_TEMPLATE_PATH)
        _write(
            missing_template_root / DECISION_TEMPLATE_PATH,
            text.replace(
                "- indefinite-C policy link or explicit non-applicability note:\n", "", 1
            ),
        )
        failures = collect_failures(missing_template_root)
        expected = [
            "decision-record template missing stay-in-C field marker: indefinite-C policy link or explicit non-applicability note:"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected template failure: {failures}")
        case_count += 1

        missing_anchor_root = root / "missing_anchor_marker"
        _seed_repo(missing_anchor_root)
        text = _read_text(missing_anchor_root / PARITY_SCORECARD_PATH)
        _write(
            missing_anchor_root / PARITY_SCORECARD_PATH,
            text.replace("- `kernel/rcu/tree.c`\n", "", 1),
        )
        failures = collect_failures(missing_anchor_root)
        expected = [
            "parity scorecard is missing anchor marker: `kernel/rcu/tree.c`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected anchor failure: {failures}")
        case_count += 1

    print("PHASE15_INDEFINITE_C_POLICY_SELF_TEST=pass")
    print(f"PHASE15_INDEFINITE_C_POLICY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 15 indefinite-C policy packet for drift."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the Zigux Phase 15 policy packet",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in synthetic coverage for the checker",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like sample repo root for checker replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(
            f"PHASE15_INDEFINITE_C_POLICY_SAMPLE_ROOT={args.write_sample_root.resolve()}"
        )
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("PHASE15_INDEFINITE_C_POLICY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

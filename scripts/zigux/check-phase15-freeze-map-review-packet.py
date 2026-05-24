#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
FREEZE_GOVERNANCE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
DECISION_TEMPLATE_PATH = Path(
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
INDEFINITE_C_POLICY_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
MANIFEST_PATH = Path("zigux/tests/phase15_freeze_map_manifest.json")

REVIEW_CHECKLIST_PROMPT = (
    "if a freeze-map anchor is entering Architecture Council status review"
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _line_containing(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line
    return None


def _collect_required_terms(manifest: dict) -> list[str]:
    terms: list[str] = []
    for requirement in manifest.get("governance_requirements", []):
        for term in requirement.get("required_terms", []):
            if term not in terms:
                terms.append(term)
    return terms


def collect_failures(root: Path) -> list[str]:
    required_paths = (
        FREEZE_MAP_PATH,
        REVIEW_CHECKLIST_PATH,
        FREEZE_GOVERNANCE_PATH,
        REVIEW_PROCESS_PATH,
        DECISION_TEMPLATE_PATH,
        INDEFINITE_C_POLICY_PATH,
        MANIFEST_PATH,
    )
    failures: list[str] = []
    for rel in required_paths:
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures

    freeze_map = _read_text(root / FREEZE_MAP_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    freeze_governance = _read_text(root / FREEZE_GOVERNANCE_PATH)
    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    decision_template = _read_text(root / DECISION_TEMPLATE_PATH)
    indefinite_c_policy = _read_text(root / INDEFINITE_C_POLICY_PATH)
    manifest = _load_manifest(root / MANIFEST_PATH)

    if manifest.get("lane_key") != "P15-L04":
        failures.append(f"lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("phase") != "Phase 15":
        failures.append(f"phase:{manifest.get('phase')!r}")
    if manifest.get("anchor") != str(FREEZE_MAP_PATH):
        failures.append(f"anchor:{manifest.get('anchor')!r}")

    surveyed_commit = manifest.get("surveyed_commit")
    if surveyed_commit not in freeze_governance:
        failures.append("freeze-governance surveyed_commit drift")

    for anchor in manifest.get("freeze_in_c_targets", []):
        if f"`{anchor}`" not in freeze_map:
            failures.append(f"freeze-map missing freeze anchor:{anchor}")

    for anchor in manifest.get("study_only_targets", []):
        if f"`{anchor}`" not in freeze_map:
            failures.append(f"freeze-map missing study-only anchor:{anchor}")

    for term in _collect_required_terms(manifest):
        if term not in freeze_map:
            failures.append(f"freeze-map missing governance term:{term}")

    checklist_line = _line_containing(review_checklist, REVIEW_CHECKLIST_PROMPT)
    if checklist_line is None:
        failures.append("review-checklist missing Architecture Council prompt")
    else:
        checklist_markers = (
            "Documentation/zigux/phase15-architecture-council-review-process.md",
            "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            "owners of the exact Architecture Council field inventory",
            "stay-in-C closeout record",
            "reopen-evidence details",
            "Documentation/zigux/phase15-indefinite-c-policy.md",
            "retained blocker posture",
            "trigger-specific evidence refresh",
            "return-to-blocked wording",
        )
        for marker in checklist_markers:
            if marker not in checklist_line:
                failures.append(f"review-checklist boundary drift:{marker}")

    shared_policy_fields = (
        "required approver set",
        "evidence archive path",
        "latest blocker disposition",
        "replay command",
        "rollback threshold",
        "retired_from_active_discussion",
        "reopen triggers",
        "trigger-specific evidence refresh",
        "parity scorecard link or blocker record",
        "indefinite-C policy link or explicit non-applicability note",
        "governance lane sequencing link or explicit scope note",
        "study-only anchor accounting link or explicit freeze-map-anchor confirmation",
        "explicit non-goals",
        "written rationale",
    )
    for marker in shared_policy_fields:
        if marker not in review_process:
            failures.append(f"review-process missing field:{marker}")
        if marker not in decision_template:
            failures.append(f"decision-template missing field:{marker}")

    for marker in (
        "required approver set",
        "automatic return-to-blocked trigger",
        "trigger-specific evidence refresh",
        "parity scorecard link or blocker record",
    ):
        if marker not in indefinite_c_policy:
            failures.append(f"indefinite-c-policy missing field:{marker}")

    for marker in (
        "no Architecture Council approval is currently recorded for a freeze-map status change",
        "keep the anchor in `freeze_in_c`",
        "reopen review later with narrower evidence",
        "approve a status-bucket change in a separately linked decision record",
    ):
        if marker not in review_process:
            failures.append(f"review-process missing outcome marker:{marker}")

    for marker in (
        "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.",
        "If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.",
    ):
        if marker not in decision_template:
            failures.append(f"decision-template missing usage rule:{marker}")

    for ownership in manifest.get("blocker_ownership", []):
        snippet = (
            f"- `{ownership['anchor']}`: owner `{ownership['owner']}`; phase "
            f"`{ownership['phase']}`; status bucket `{ownership['status_bucket']}`; "
            f"required approver set `{ownership['required_approver_set']}`; validation gate "
            f"`{ownership['validation_gate']}`; rollback owner `{ownership['rollback_owner']}`; "
            f"evidence archive path `{ownership['evidence_archive_path']}`; benchmark notes "
            f"`{ownership['benchmark_notes']}`; replay command `{ownership['replay_command']}`; "
            f"latest blocker disposition `{ownership['latest_blocker_disposition']}`"
        )
        if snippet not in freeze_governance:
            failures.append(f"freeze-governance blocker inventory drift:{ownership['anchor']}")

    return failures


def _sample_manifest() -> str:
    payload = {
        "lane_key": "P15-L04",
        "phase": "Phase 15",
        "surveyed_commit": "current-master-readback-2026-05-22",
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
                    "required approver set",
                    "evidence archive path",
                    "latest blocker disposition",
                    "replay command",
                    "rollback threshold",
                    "retired_from_active_discussion",
                    "reopen triggers",
                    "trigger-specific evidence refresh",
                    "parity scorecard link or blocker record",
                    "indefinite-C policy link or non-applicability note",
                    "explicit non-goals",
                    "governance lane sequencing link or explicit scope note",
                    "study-only anchor accounting link or explicit freeze-map-anchor confirmation",
                    "no silent exception path",
                    "## Stay-In-C Policy",
                    "keep the code in C and record the blocker",
                ]
            }
        ],
        "blocker_ownership": [
            {
                "anchor": "kernel/sched/core.c",
                "owner": "Architecture Council",
                "phase": "Phase 15",
                "status_bucket": "freeze_in_c",
                "required_approver_set": "Architecture Council + PMO / Release Management",
                "validation_gate": "Phase 15 parity scorecard plus Architecture Council reopen record",
                "rollback_owner": "Architecture Council + PMO / Release Management",
                "evidence_archive_path": "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
                "benchmark_notes": "pending_until_bounded_scheduler_seam_exists",
                "replay_command": "zig test zigux/tests/phase15_freeze_map_governance.zig",
                "latest_blocker_disposition": "blocked_no_bounded_scheduler_seam",
            }
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

## Freeze In C Initially
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Governance For Freeze-Map Changes
- changes to either list require an explicit Architecture Council decision with written rationale
- freeze-map status-change requests must keep the root policy layer aligned with the broader Architecture Council review packet fields, including required approver set, evidence archive path, latest blocker disposition, replay command, rollback threshold, `retired_from_active_discussion`, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, governance lane sequencing link or explicit scope note, study-only anchor accounting link or explicit freeze-map-anchor confirmation, explicit non-goals, and written rationale
- there is no silent exception path around the stay-in-C policy

## Stay-In-C Policy
- if validation is incomplete, contradictory, or too weak to justify a status change, keep the code in C and record the blocker
"""


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

  * if a freeze-map anchor is entering Architecture Council status review, does this checklist keep the shared entry-review prompt explicit while `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details, and `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording?
"""


def _sample_freeze_governance() -> str:
    return """# Phase 15 Freeze-Map Governance

- surveyed against dated current-master readback marker `current-master-readback-2026-05-22`
- `kernel/sched/core.c`: owner `Architecture Council`; phase `Phase 15`; status bucket `freeze_in_c`; required approver set `Architecture Council + PMO / Release Management`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + PMO / Release Management`; evidence archive path `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`; benchmark notes `pending_until_bounded_scheduler_seam_exists`; replay command `zig test zigux/tests/phase15_freeze_map_governance.zig`; latest blocker disposition `blocked_no_bounded_scheduler_seam`
"""


def _sample_review_process() -> str:
    return """# Phase 15 Architecture Council Review Process

- no Architecture Council approval is currently recorded for a freeze-map status change
- keep the anchor in `freeze_in_c`
- reopen review later with narrower evidence
- approve a status-bucket change in a separately linked decision record
- required approver set
- evidence archive path
- latest blocker disposition
- replay command
- rollback threshold
- `retired_from_active_discussion` state
- reopen triggers
- trigger-specific evidence refresh
- parity scorecard link or blocker record
- indefinite-C policy link or explicit non-applicability note
- governance lane sequencing link or explicit scope note
- study-only anchor accounting link or explicit freeze-map-anchor confirmation
- explicit non-goals
- written rationale
"""


def _sample_decision_template() -> str:
    return """# Phase 15 Architecture Council Decision Record Template

- required approver set:
- evidence archive path:
- latest blocker disposition:
- replay command:
- rollback threshold:
- `retired_from_active_discussion` state:
- reopen triggers:
- trigger-specific evidence refresh:
- parity scorecard link or blocker record:
- indefinite-C policy link or explicit non-applicability note:
- governance lane sequencing link or explicit scope note:
- study-only anchor accounting link or explicit freeze-map-anchor confirmation:
- explicit non-goals:
- written rationale:

- Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.
- If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.
"""


def _sample_indefinite_c_policy() -> str:
    return """# Phase 15 Indefinite-C Policy

- the decision record ID, lane owner, required approver set, and rollback owner
- the automatic return-to-blocked trigger, retained `retired_from_active_discussion` state, reopen triggers, and trigger-specific evidence refresh
- the parity scorecard link or blocker record, explicit non-goals, and written rationale for why the anchor remains in C
"""


def write_fixture_root(root: Path) -> None:
    _write(root / FREEZE_MAP_PATH, _sample_freeze_map())
    _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
    _write(root / FREEZE_GOVERNANCE_PATH, _sample_freeze_governance())
    _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
    _write(root / DECISION_TEMPLATE_PATH, _sample_decision_template())
    _write(root / INDEFINITE_C_POLICY_PATH, _sample_indefinite_c_policy())
    _write(root / MANIFEST_PATH, _sample_manifest())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_freeze_map_review_") as tmp_dir:
        base = Path(tmp_dir)

        root = base / "baseline"
        write_fixture_root(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        checklist_root = base / "checklist"
        write_fixture_root(checklist_root)
        _write(
            checklist_root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace("reopen-evidence details", "reopen details", 1),
        )
        failures = collect_failures(checklist_root)
        if failures != ["review-checklist boundary drift:reopen-evidence details"]:
            raise AssertionError(f"unexpected review-checklist failure: {failures}")
        case_count += 1

        field_root = base / "field"
        write_fixture_root(field_root)
        _write(
            field_root / REVIEW_PROCESS_PATH,
            _sample_review_process().replace(
                "- study-only anchor accounting link or explicit freeze-map-anchor confirmation\n",
                "",
                1,
            ),
        )
        failures = collect_failures(field_root)
        if failures != [
            "review-process missing field:study-only anchor accounting link or explicit freeze-map-anchor confirmation"
        ]:
            raise AssertionError(f"unexpected review-process field failure: {failures}")
        case_count += 1

        blocker_root = base / "blocker"
        write_fixture_root(blocker_root)
        _write(
            blocker_root / FREEZE_GOVERNANCE_PATH,
            _sample_freeze_governance().replace(
                "latest blocker disposition `blocked_no_bounded_scheduler_seam`",
                "latest blocker disposition `drifted_blocker`",
                1,
            ),
        )
        failures = collect_failures(blocker_root)
        if failures != [
            "freeze-governance blocker inventory drift:kernel/sched/core.c"
        ]:
            raise AssertionError(f"unexpected blocker failure: {failures}")
        case_count += 1

    print("PHASE15_FREEZE_MAP_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE15_FREEZE_MAP_REVIEW_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the Phase 15 freeze-map packet stays aligned with the "
            "shared Architecture Council review inventory."
        )
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 freeze-map review packet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

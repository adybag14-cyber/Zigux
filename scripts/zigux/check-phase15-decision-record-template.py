#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
DECISION_TEMPLATE_PATH = Path(
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
INDEFINITE_C_POLICY_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
HANDOFF_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_architecture_council_review_process_manifest.json")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_line(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line
    return None


def collect_failures(root: Path) -> list[str]:
    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    decision_template = _read_text(root / DECISION_TEMPLATE_PATH)
    indefinite_c_policy = _read_text(root / INDEFINITE_C_POLICY_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    handoff = _read_text(root / HANDOFF_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)

    failures: list[str] = []

    if manifest["decision_record_template"] != DECISION_TEMPLATE_PATH.as_posix():
        failures.append("review-process manifest points at an unexpected decision-record-template path")

    if manifest["decision_record_template"] not in review_process:
        failures.append("review-process note is missing the decision-record template path")

    if manifest["review_checklist_boundary_rule"] not in review_process:
        failures.append("review-process note is missing the review-checklist boundary rule")

    for marker in manifest["decision_record_template_required_markers"]:
        if marker not in decision_template:
            failures.append(f"decision-record template is missing required marker: {marker}")

    for field in manifest["required_review_fields"]:
        if field not in decision_template:
            failures.append(f"decision-record template is missing required review field: {field}")

    for field in manifest["stay_in_c_closeout_fields"]:
        if field not in decision_template:
            failures.append(f"decision-record template is missing stay-in-C closeout field: {field}")

    for field in manifest["reopen_evidence_fields"]:
        if field not in decision_template:
            failures.append(f"decision-record template is missing reopen-evidence field: {field}")

    checklist_line = _find_line(review_checklist, manifest["review_checklist_entry_prompt"])
    if checklist_line is None:
        failures.append("review checklist is missing the Phase 15 Architecture Council entry-review prompt")
    else:
        for field in manifest["required_review_fields"]:
            if field not in checklist_line:
                failures.append(
                    f"review checklist entry prompt is missing required review field: {field}"
                )

    for marker in manifest["indefinite_c_policy_required_markers"]:
        if marker not in indefinite_c_policy:
            failures.append(f"indefinite-C policy note is missing required marker: {marker}")

    for marker in (
        f"`{DECISION_TEMPLATE_PATH.as_posix()}`",
        "`scripts/zigux/check-phase15-review-process-handoff.py`",
        "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
    ):
        if marker not in handoff:
            failures.append(f"handoff note is missing required marker: {marker}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P15-L08",
            "phase": "Phase 15",
            "surveyed_commit": "current-master-readback-2026-05-18",
            "review_process_note": "Documentation/zigux/phase15-architecture-council-review-process.md",
            "decision_record_template": "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            "indefinite_c_policy_note": "Documentation/zigux/phase15-indefinite-c-policy.md",
            "handoff_note": "Documentation/zigux/phase15-handoff-next-steps-survey.md",
            "shared_summary_gap_note": "Documentation/zigux/phase15-shared-summary-gap.md",
            "checker": "scripts/zigux/check-phase15-review-process-handoff.py",
            "build_gate": "zigux/tests/phase15_architecture_council_review_process_build.zig",
            "review_checklist_entry_prompt": "if a freeze-map anchor is entering Architecture Council status review",
            "review_checklist_boundary_rule": "`Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit, but the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
            "required_review_fields": [
                "exact Linux anchor path",
                "roadmap phase",
                "decision record ID",
                "lane owner",
                "current status bucket",
                "requested decision bucket",
                "required approver set",
                "rollback owner",
                "validation gate summary",
                "evidence archive path",
                "latest blocker disposition",
                "benchmark notes",
                "replay command",
                "rollback threshold",
                "automatic return-to-blocked trigger",
                "`retired_from_active_discussion` state",
                "reopen triggers",
                "trigger-specific evidence refresh",
                "parity scorecard link or blocker record",
                "indefinite-C policy link or explicit non-applicability note",
                "explicit non-goals",
                "written rationale",
            ],
            "stay_in_c_closeout_fields": [
                "the retained `freeze_in_c` decision",
                "the current blocker",
                "the required approver set",
                "`retired_from_active_discussion` state",
                "the automatic return-to-blocked trigger",
                "the reopen triggers",
                "the trigger-specific evidence refresh",
                "the evidence archive path that will be refreshed before any later reopen request",
            ],
            "reopen_evidence_fields": [
                "the exact reopen trigger being exercised",
                "refreshed evidence by path",
                "the blocker disposition being challenged",
                "the narrower seam or policy change that makes the new review safe to consider",
            ],
            "indefinite_c_policy_required_markers": [
                "required approver set",
                "automatic return-to-blocked trigger",
                "trigger-specific evidence refresh",
                "parity scorecard link or blocker record",
            ],
            "decision_record_template_required_markers": [
                "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
                "`SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`",
                "exact-head provenance exception note:",
                "Prefer the dated master readback form for parked governance and stay-in-C review packets.",
                "Only record an exact head when the linked review needs it to anchor a named published decision",
            ],
        },
        indent=2,
    ) + "\n"


def _sample_review_process() -> str:
    return """# Phase 15 Architecture Council Review Process

- `PHASE15_STATUS=architecture_council_review_process_landed`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-18`
- `Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit, but the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- the dedicated decision-record template remains explicit through `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
"""


def _sample_decision_template() -> str:
    return """# Phase 15 Architecture Council Decision Record Template

Use this template when a freeze-map anchor enters Architecture Council status review.

- `DECISION_RECORD_ID=<replace-with-stable-id>`
- decision record ID:
- `PHASE=Phase 15`
- `LANE_KEY=P15-L08`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- `SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`
- exact-head provenance exception note:
- `REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>`

- exact Linux anchor path:
- roadmap phase:
- decision record ID:
- lane owner:
- current status bucket:
- requested decision bucket:
- required approver set:
- rollback owner:
- validation gate summary:
- evidence archive path:
- latest blocker disposition:
- benchmark notes:
- replay command:
- rollback threshold:
- automatic return-to-blocked trigger:
- `retired_from_active_discussion` state:
- reopen triggers:
- trigger-specific evidence refresh:
- parity scorecard link or blocker record:
- indefinite-C policy link or explicit non-applicability note:
- explicit non-goals:
- written rationale:

- the retained `freeze_in_c` decision:
- the current blocker:
- the required approver set:
- `retired_from_active_discussion` state:
- the automatic return-to-blocked trigger:
- the reopen triggers:
- the trigger-specific evidence refresh:
- the evidence archive path that will be refreshed before any later reopen request:

- the exact reopen trigger being exercised:
- refreshed evidence by path:
- the blocker disposition being challenged:
- the narrower seam or policy change that makes the new review safe to consider:

- Prefer the dated master readback form for parked governance and stay-in-C review packets.
- Only record an exact head when the linked review needs it to anchor a named published decision, and explain that exception in the exact-head provenance note.
"""


def _sample_indefinite_c_policy() -> str:
    return """# Phase 15 Indefinite-C Policy

- the required approver set remains explicit
- the automatic return-to-blocked trigger remains explicit
- the trigger-specific evidence refresh remains explicit
- the parity scorecard link or blocker record remains explicit
"""


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

  * if a freeze-map anchor is entering Architecture Council status review, are the exact Linux anchor path, roadmap phase, decision record ID, lane owner, current status bucket, requested decision bucket, required approver set, rollback owner, validation gate summary, evidence archive path, latest blocker disposition, benchmark notes, replay command, rollback threshold, automatic return-to-blocked trigger, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or explicit non-applicability note, explicit non-goals, and written rationale explicit?
"""


def _sample_handoff() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
"""


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_decision_template_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(root / DECISION_TEMPLATE_PATH, _sample_decision_template())
        _write(root / INDEFINITE_C_POLICY_PATH, _sample_indefinite_c_policy())
        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
        _write(root / HANDOFF_PATH, _sample_handoff())
        _write(root / MANIFEST_PATH, _sample_manifest())

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        _write(
            root / DECISION_TEMPLATE_PATH,
            _sample_decision_template().replace("- rollback owner:\n", "", 1),
        )
        failures = collect_failures(root)
        expected = ["decision-record template is missing required review field: rollback owner"]
        if failures != expected:
            raise AssertionError(f"unexpected rollback-owner failure: {failures}")

        _write(root / DECISION_TEMPLATE_PATH, _sample_decision_template())
        _write(
            root / DECISION_TEMPLATE_PATH,
            _sample_decision_template().replace("exact-head provenance exception note:\n", "", 1),
        )
        failures = collect_failures(root)
        expected = [
            "decision-record template is missing required marker: exact-head provenance exception note:"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected provenance-marker failure: {failures}")

        _write(root / DECISION_TEMPLATE_PATH, _sample_decision_template())
        _write(root / REVIEW_CHECKLIST_PATH, "# Zigux Review Checklist\n")
        failures = collect_failures(root)
        expected = [
            "review checklist is missing the Phase 15 Architecture Council entry-review prompt"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected checklist-prompt failure: {failures}")

        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace("required approver set, ", "", 1),
        )
        failures = collect_failures(root)
        expected = [
            "review checklist entry prompt is missing required review field: required approver set"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected checklist-field failure: {failures}")

        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
        _write(
            root / INDEFINITE_C_POLICY_PATH,
            _sample_indefinite_c_policy().replace(
                "- the automatic return-to-blocked trigger remains explicit\n", "", 1
            ),
        )
        failures = collect_failures(root)
        expected = [
            "indefinite-C policy note is missing required marker: automatic return-to-blocked trigger"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected indefinite-c failure: {failures}")

        _write(root / INDEFINITE_C_POLICY_PATH, _sample_indefinite_c_policy())
        _write(root / HANDOFF_PATH, "# Phase 15 Handoff Next Steps Survey\n")
        failures = collect_failures(root)
        expected = [
            "handoff note is missing required marker: `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
            "handoff note is missing required marker: `scripts/zigux/check-phase15-review-process-handoff.py`",
            "handoff note is missing required marker: `scripts/zigux/check-phase15-tests-readme-alignment.py`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected handoff-marker failure: {failures}")

    print("PHASE15_DECISION_RECORD_TEMPLATE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the landed Phase 15 decision-record template stays aligned with its governance packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux and zigux/tests",
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

    print("Phase 15 decision-record template check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

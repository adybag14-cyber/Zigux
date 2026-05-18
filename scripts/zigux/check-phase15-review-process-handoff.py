#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
DECISION_RECORD_TEMPLATE_PATH = Path(
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
MANIFEST_PATH = Path("zigux/tests/phase15_architecture_council_review_process_manifest.json")
TEST_PATH = Path("zigux/tests/phase15_architecture_council_review_process.zig")
CHECKLIST_ENTRY_REVIEW_PROMPT = "if a freeze-map anchor is entering Architecture Council status review"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _marker_to_repo_path(marker: str) -> Path | None:
    if marker.startswith("`") and marker.endswith("`") and "/" in marker:
        return Path(marker.strip("`"))
    return None


def _line_containing(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line
    return None


def collect_failures(root: Path) -> list[str]:
    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    decision_record_template = _read_text(root / DECISION_RECORD_TEMPLATE_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    gap_note = _read_text(root / SHARED_GAP_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)

    failures: list[str] = []

    if manifest["surveyed_commit"] not in review_process:
        failures.append("review-process note is missing the manifest surveyed_commit marker")

    if manifest["decision_record_template"] not in review_process:
        failures.append("review-process note is missing the decision-record template path")

    if manifest["decision_record_template"] not in handoff_note:
        failures.append("handoff note is missing the decision-record template path")

    for marker in (
        "PHASE15_STATUS=architecture_council_review_process_landed",
        "PHASE15_LANE_KEY=P15-L08",
        "PHASE15_PROVENANCE_MODE=dated_master_readback",
        "`scripts/zigux/check-phase15-review-process-handoff.py`",
        "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
        "`zigux/tests/phase15_architecture_council_review_process.zig`",
    ):
        if marker not in review_process:
            failures.append(f"review-process note is missing required marker: {marker}")

    for field in manifest["required_review_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing required review field: {field}")
        if field not in decision_record_template:
            failures.append(f"decision-record template is missing required review field: {field}")

    checklist_entry_prompt = _line_containing(review_checklist, CHECKLIST_ENTRY_REVIEW_PROMPT)
    if checklist_entry_prompt is None:
        failures.append(
            "review checklist is missing the Phase 15 Architecture Council entry-review prompt"
        )
    else:
        for field in manifest["required_review_fields"]:
            if field not in checklist_entry_prompt:
                failures.append(f"review checklist prompt is missing required review field: {field}")

    for field in manifest["stay_in_c_closeout_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing stay-in-C closeout field: {field}")
        if field not in decision_record_template:
            failures.append(f"decision-record template is missing stay-in-C closeout field: {field}")

    for field in manifest["reopen_evidence_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing reopen-evidence field: {field}")
        if field not in decision_record_template:
            failures.append(f"decision-record template is missing reopen-evidence field: {field}")

    for marker in manifest["handoff_required_markers"]:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing required marker: {marker}")

    for marker in manifest["shared_gap_expected_present_paths"]:
        if marker not in gap_note:
            failures.append(f"shared-summary gap note is missing newly landed path: {marker}")

        repo_path = _marker_to_repo_path(marker)
        if repo_path is not None and not (root / repo_path).exists():
            failures.append(f"shared-summary gap note claims materialized path is missing from repo: {marker}")

    for path in manifest["shared_gap_expected_missing_paths"]:
        if path not in gap_note:
            failures.append(f"shared-summary gap note is missing still-blocked path: {path}")

    if not (root / TEST_PATH).exists():
        failures.append(
            "focused review-process Zig replay is missing from repo: `zigux/tests/phase15_architecture_council_review_process.zig`"
        )

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
            "decision_record_template": "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
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
                "retained discussion state",
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
            "handoff_required_markers": [
                "`Documentation/zigux/review-checklist.md`",
                "`Documentation/zigux/README.md`",
                "`Documentation/zigux/phase15-architecture-council-review-process.md`",
                "`Documentation/zigux/phase15-indefinite-c-policy.md`",
                "`Documentation/zigux/phase15-shared-summary-gap.md`",
                "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
                "`scripts/zigux/check-phase15-review-process-handoff.py`",
                "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
                "one focused review-process checker, one focused tests-readme checker, and the shared-summary gap checker",
            ],
            "shared_gap_expected_present_paths": [
                "`zigux/tests/phase15_architecture_council_review_process.zig`",
                "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
                "`scripts/zigux/check-phase15-review-process-handoff.py`",
            ],
            "shared_gap_expected_missing_paths": [
                "`scripts/zigux/validate-phase15.py`",
                "`zigux/tests/phase15_build.zig`",
                "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
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
- this note keeps the docs-root field inventory, the dedicated decision-record template, the dedicated review-process manifest, the focused review-process handoff checker, and the focused Zig replay are landed through `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, and `zigux/tests/phase15_architecture_council_review_process.zig`

Any freeze-map anchor entering Architecture Council status review must keep all of the following explicit:
- exact Linux anchor path
- roadmap phase
- decision record ID
- lane owner
- current status bucket
- requested decision bucket
- required approver set
- rollback owner
- validation gate summary
- evidence archive path
- latest blocker disposition
- benchmark notes
- replay command
- rollback threshold
- automatic return-to-blocked trigger
- retained discussion state
- reopen triggers
- trigger-specific evidence refresh
- parity scorecard link or blocker record
- indefinite-C policy link or explicit non-applicability note
- explicit non-goals
- written rationale

If a freeze-in-C review closes without a status change, the closeout record must keep all of the following explicit:
- the retained `freeze_in_c` decision
- the current blocker
- the required approver set
- `retired_from_active_discussion` state
- the automatic return-to-blocked trigger
- the reopen triggers
- the trigger-specific evidence refresh
- the evidence archive path that will be refreshed before any later reopen request

A later reopen request must not rely on generic intent alone. It must cite:
- the exact reopen trigger being exercised
- refreshed evidence by path
- the blocker disposition being challenged
- the narrower seam or policy change that makes the new review safe to consider
"""


def _sample_decision_record_template() -> str:
    return """# Phase 15 Architecture Council Decision Record Template

- `DECISION_RECORD_ID=<replace-with-stable-id>`

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
- retained discussion state:
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
"""


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

  * if a freeze-map anchor is entering Architecture Council status review, are the exact Linux anchor path, roadmap phase, decision record ID, lane owner, current status bucket, requested decision bucket, required approver set, rollback owner, validation gate summary, evidence archive path, latest blocker disposition, benchmark notes, replay command, rollback threshold, automatic return-to-blocked trigger, retained discussion state, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or explicit non-applicability note, explicit non-goals, and written rationale explicit?
"""


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`, which together keep one focused review-process checker, one focused tests-readme checker, and the shared-summary gap checker materialized on current `master`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
"""


def _sample_gap_note() -> str:
    return """# Phase 15 Shared Summary Gap

- `zigux/tests/phase15_architecture_council_review_process.zig`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
"""


def _sample_test_file() -> str:
    return """const std = @import("std");

test "placeholder focused review-process replay exists" {
    try std.testing.expect(true);
}
"""


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_review_process_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(root / DECISION_RECORD_TEMPLATE_PATH, _sample_decision_record_template())
        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(root / SHARED_GAP_NOTE_PATH, _sample_gap_note())
        _write(root / MANIFEST_PATH, _sample_manifest())
        _write(root / Path("scripts/zigux/check-phase15-review-process-handoff.py"), "# fixture\n")
        _write(root / TEST_PATH, _sample_test_file())

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        _write(
            root / REVIEW_PROCESS_PATH,
            _sample_review_process().replace("- roadmap phase\n", "", 1),
        )
        failures = collect_failures(root)
        if failures != ["review-process note is missing required review field: roadmap phase"]:
            raise AssertionError(f"unexpected roadmap-phase failure: {failures}")

        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(
            root / DECISION_RECORD_TEMPLATE_PATH,
            _sample_decision_record_template().replace("- roadmap phase:\n", "", 1),
        )
        failures = collect_failures(root)
        if failures != ["decision-record template is missing required review field: roadmap phase"]:
            raise AssertionError(f"unexpected decision-template review-field failure: {failures}")

        _write(root / DECISION_RECORD_TEMPLATE_PATH, _sample_decision_record_template())
        _write(
            root / REVIEW_PROCESS_PATH,
            _sample_review_process().replace(
                "- the automatic return-to-blocked trigger\n", "", 1
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "review-process note is missing stay-in-C closeout field: the automatic return-to-blocked trigger"
        ]:
            raise AssertionError(f"unexpected stay-in-C closeout failure: {failures}")

        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace("exact Linux anchor path, ", "", 1),
        )
        failures = collect_failures(root)
        if failures != ["review checklist prompt is missing required review field: exact Linux anchor path"]:
            raise AssertionError(f"unexpected checklist failure: {failures}")

        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
        _write(
            root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if failures != ["handoff note is missing the decision-record template path"]:
            raise AssertionError(f"unexpected decision-template handoff failure: {failures}")

        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(
            root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- `Documentation/zigux/review-checklist.md`\n", "", 1
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "handoff note is missing required marker: `Documentation/zigux/review-checklist.md`"
        ]:
            raise AssertionError(f"unexpected handoff failure: {failures}")

        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(
            root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- `scripts/zigux/check-phase15-tests-readme-alignment.py`\n", "", 1
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "handoff note is missing required marker: `scripts/zigux/check-phase15-tests-readme-alignment.py`"
        ]:
            raise AssertionError(f"unexpected tests-readme handoff failure: {failures}")

        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(
            root / SHARED_GAP_NOTE_PATH,
            _sample_gap_note().replace(
                "- `zigux/tests/phase15_architecture_council_review_process.zig`\n", "", 1
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "shared-summary gap note is missing newly landed path: `zigux/tests/phase15_architecture_council_review_process.zig`"
        ]:
            raise AssertionError(f"unexpected shared-gap failure: {failures}")

        _write(root / SHARED_GAP_NOTE_PATH, _sample_gap_note())
        (root / TEST_PATH).unlink()
        failures = collect_failures(root)
        expected = [
            "shared-summary gap note claims materialized path is missing from repo: `zigux/tests/phase15_architecture_council_review_process.zig`",
            "focused review-process Zig replay is missing from repo: `zigux/tests/phase15_architecture_council_review_process.zig`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-path failure: {failures}")

    print("PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 Architecture Council review-process packet and handoff note stay aligned."
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

    print("Phase 15 review-process handoff check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

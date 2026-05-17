#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
MANIFEST_PATH = Path("zigux/tests/phase15_architecture_council_review_process_manifest.json")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_failures(root: Path) -> list[str]:
    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    gap_note = _read_text(root / SHARED_GAP_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)

    failures: list[str] = []

    if manifest["surveyed_commit"] not in review_process:
        failures.append("review-process note is missing the manifest surveyed_commit marker")

    for marker in (
        "PHASE15_STATUS=architecture_council_review_process_landed",
        "PHASE15_LANE_KEY=P15-L08",
        "PHASE15_PROVENANCE_MODE=dated_master_readback",
        "`scripts/zigux/check-phase15-review-process-handoff.py`",
        "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    ):
        if marker not in review_process:
            failures.append(f"review-process note is missing required marker: {marker}")

    for field in manifest["required_review_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing required review field: {field}")

    for field in manifest["stay_in_c_closeout_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing stay-in-C closeout field: {field}")

    for field in manifest["reopen_evidence_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing reopen-evidence field: {field}")

    for marker in manifest["handoff_required_markers"]:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing required marker: {marker}")

    for marker in manifest["shared_gap_expected_present_paths"]:
        if marker not in gap_note:
            failures.append(f"shared-summary gap note is missing newly landed path: {marker}")

    for path in manifest["shared_gap_expected_missing_paths"]:
        if path not in gap_note:
            failures.append(f"shared-summary gap note is missing still-blocked path: {path}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P15-L08",
            "phase": "Phase 15",
            "surveyed_commit": "current-master-readback-2026-05-16",
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
                "the reopen triggers",
                "the evidence archive path that will be refreshed before any later reopen request",
            ],
            "reopen_evidence_fields": [
                "the exact reopen trigger being exercised",
                "refreshed evidence by path",
                "the blocker disposition being challenged",
                "the narrower seam or policy change that makes the new review safe to consider",
            ],
            "handoff_required_markers": [
                "`Documentation/zigux/phase15-architecture-council-review-process.md`",
                "`Documentation/zigux/phase15-indefinite-c-policy.md`",
                "`Documentation/zigux/phase15-shared-summary-gap.md`",
                "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
                "`scripts/zigux/check-phase15-review-process-handoff.py`",
                "one focused review-process checker plus the shared-summary gap checker",
            ],
            "shared_gap_expected_present_paths": [
                "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
                "`scripts/zigux/check-phase15-review-process-handoff.py`",
            ],
            "shared_gap_expected_missing_paths": [
                "`scripts/zigux/validate-phase15.py`",
                "`zigux/tests/phase15_build.zig`",
            ],
        },
        indent=2,
    ) + "\n"


def _sample_review_process() -> str:
    return """# Phase 15 Architecture Council Review Process

- `PHASE15_STATUS=architecture_council_review_process_landed`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-16`
- this note keeps the docs-root field inventory, the dedicated review-process manifest, and the focused review-process handoff checker are landed through `scripts/zigux/check-phase15-review-process-handoff.py` and `zigux/tests/phase15_architecture_council_review_process_manifest.json`

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
- the reopen triggers
- the evidence archive path that will be refreshed before any later reopen request

A later reopen request must not rely on generic intent alone. It must cite:
- the exact reopen trigger being exercised
- refreshed evidence by path
- the blocker disposition being challenged
- the narrower seam or policy change that makes the new review safe to consider
"""


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`, which together keep one focused review-process checker plus the shared-summary gap checker materialized on current `master`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
"""


def _sample_gap_note() -> str:
    return """# Phase 15 Shared Summary Gap

- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
"""


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_review_process_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(root / SHARED_GAP_NOTE_PATH, _sample_gap_note())
        _write(root / MANIFEST_PATH, _sample_manifest())

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
            root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- `scripts/zigux/check-phase15-review-process-handoff.py`\n", "", 1
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "handoff note is missing required marker: `scripts/zigux/check-phase15-review-process-handoff.py`"
        ]:
            raise AssertionError(f"unexpected handoff failure: {failures}")

        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(
            root / SHARED_GAP_NOTE_PATH,
            _sample_gap_note().replace(
                "- `zigux/tests/phase15_architecture_council_review_process_manifest.json`\n", "", 1
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "shared-summary gap note is missing newly landed path: `zigux/tests/phase15_architecture_council_review_process_manifest.json`"
        ]:
            raise AssertionError(f"unexpected shared-gap failure: {failures}")

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

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

DECISION_INDEX_PATH = Path("Documentation/zigux/phase15-architecture-council-decision-index.md")
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")

EXPECTED_DECISION_INDEX_MARKERS = (
    "PHASE15_STATUS=architecture_council_decision_index_landed",
    "PHASE15_LANE_KEY=P15-L09",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "approved status-bucket changes recorded on current `master`: none",
    "stay-in-C closeout decision records recorded on current `master`: none",
    "no freeze-map anchor has an Architecture Council approval for a status change on current `master`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay outside this index until the freeze map changes",
)

EXPECTED_REVIEW_PROCESS_MARKER = (
    "`Documentation/zigux/phase15-architecture-council-decision-index.md` keeps the current "
    "Architecture Council decision inventory explicit, recording that no freeze-map anchor has an "
    "approved status change or stay-in-C closeout record on current `master` until a future decision record lands"
)

EXPECTED_HANDOFF_MARKERS = (
    "the Architecture Council decision index",
    "`Documentation/zigux/phase15-architecture-council-decision-index.md`",
)

EXPECTED_SHARED_GAP_MARKERS = (
    "`Documentation/zigux/phase15-architecture-council-decision-index.md`",
)

EXPECTED_VALIDATOR_MARKER = '"Documentation/zigux/phase15-architecture-council-decision-index.md"'


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (
        DECISION_INDEX_PATH,
        REVIEW_PROCESS_PATH,
        HANDOFF_NOTE_PATH,
        SHARED_GAP_NOTE_PATH,
        VALIDATOR_PATH,
    ):
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures

    decision_index = _read_text(root / DECISION_INDEX_PATH)
    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    shared_gap_note = _read_text(root / SHARED_GAP_NOTE_PATH)
    validator = _read_text(root / VALIDATOR_PATH)

    for marker in EXPECTED_DECISION_INDEX_MARKERS:
        if marker not in decision_index:
            failures.append(f"missing_decision_index_marker:{marker}")

    if EXPECTED_REVIEW_PROCESS_MARKER not in review_process:
        failures.append("missing_review_process_decision_index_marker")

    for marker in EXPECTED_HANDOFF_MARKERS:
        if marker not in handoff_note:
            failures.append(f"missing_handoff_marker:{marker}")

    for marker in EXPECTED_SHARED_GAP_MARKERS:
        if marker not in shared_gap_note:
            failures.append(f"missing_shared_gap_marker:{marker}")

    if EXPECTED_VALIDATOR_MARKER not in validator:
        failures.append("missing_validator_direct_packet_marker")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_decision_index() -> str:
    return """# Phase 15 Architecture Council Decision Index

## Status

- `PHASE15_STATUS=architecture_council_decision_index_landed`
- `PHASE15_LANE_KEY=P15-L09`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`

## Current decision inventory

- approved status-bucket changes recorded on current `master`: none
- stay-in-C closeout decision records recorded on current `master`: none
- no freeze-map anchor has an Architecture Council approval for a status change on current `master`

## Index rules

- every future Architecture Council decision record must route back through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and `Documentation/zigux/phase15-parity-scorecard.md`
- `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay outside this index until the freeze map changes
"""


def _sample_review_process() -> str:
    return f"""# Phase 15 Architecture Council Review Process

## Current Phase 15 posture

- {EXPECTED_REVIEW_PROCESS_MARKER}
"""


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

Current `master` already carries the freeze map, the freeze-map governance note, the Architecture Council review-process note, the Architecture Council decision-record template, the Architecture Council decision index, the indefinite-C policy note, the parity scorecard, the parity-scorecard survey, the readiness-gate survey, the governance-lane sequencing note, the deep-core blocker survey, the study-only anchor accounting note, and the shared-summary gap note.

## Current handed-off packet on current master

- `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-architecture-council-decision-index.md`

## Next bounded future targets

1. keep the landed `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, and `Documentation/zigux/phase15-architecture-council-decision-index.md` companions aligned with the shared-summary gap note before any freeze-map status change discussion
"""


def _sample_shared_gap_note() -> str:
    return """# Phase 15 Shared Summary Gap

## Materialized Phase 15 governance assets

- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-architecture-council-decision-index.md`

## Current shared-summary watchpoints

- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-architecture-council-decision-index.md`

## Next bounded step

Keep this note parked unless a fresh reread shows one of the broad Phase 15 reminder surfaces drifting away from the materialized governance packet above, the Architecture Council review-process owner note, the decision-record template, or the Architecture Council decision index.
"""


def _sample_validator() -> str:
    payload = {
        "direct_packet_paths": [
            "Documentation/zigux/freeze-map.md",
            "Documentation/zigux/phase15-architecture-council-review-process.md",
            "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            "Documentation/zigux/phase15-architecture-council-decision-index.md",
        ]
    }
    return (
        "EXPECTED_DIRECT_PACKET_PATHS = [\n"
        '    "Documentation/zigux/freeze-map.md",\n'
        '    "Documentation/zigux/phase15-architecture-council-review-process.md",\n'
        '    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",\n'
        '    "Documentation/zigux/phase15-architecture-council-decision-index.md",\n'
        "]\n"
        f"MANIFEST_PREVIEW = {json.dumps(payload, indent=2)}\n"
    )


def _write_baseline(root: Path) -> None:
    _write(root / DECISION_INDEX_PATH, _sample_decision_index())
    _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    _write(root / SHARED_GAP_NOTE_PATH, _sample_shared_gap_note())
    _write(root / VALIDATOR_PATH, _sample_validator())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_arch_council_decision_index_") as tmp_dir:
        base = Path(tmp_dir)

        baseline = base / "baseline"
        _write_baseline(baseline)
        failures = collect_failures(baseline)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        cases = (
            (DECISION_INDEX_PATH, "approved status-bucket changes recorded on current `master`: none\n", ["missing_decision_index_marker:approved status-bucket changes recorded on current `master`: none"], False),
            (REVIEW_PROCESS_PATH, EXPECTED_REVIEW_PROCESS_MARKER, ["missing_review_process_decision_index_marker"], False),
            (HANDOFF_NOTE_PATH, "the Architecture Council decision index, ", ["missing_handoff_marker:the Architecture Council decision index"], False),
            (SHARED_GAP_NOTE_PATH, "`Documentation/zigux/phase15-architecture-council-decision-index.md`", ["missing_shared_gap_marker:`Documentation/zigux/phase15-architecture-council-decision-index.md`"], True),
            (VALIDATOR_PATH, '"Documentation/zigux/phase15-architecture-council-decision-index.md"', ["missing_validator_direct_packet_marker"], True),
        )

        for rel, marker, expected, replace_all in cases:
            case_root = base / f"case_{case_count}"
            _write_baseline(case_root)
            text = _read_text(case_root / rel)
            count = text.count(marker) if replace_all else 1
            _write(case_root / rel, text.replace(marker, "", count))
            failures = collect_failures(case_root)
            if failures != expected:
                raise AssertionError(f"unexpected failures for {rel}: {failures}")
            case_count += 1

    print("PHASE15_ARCHITECTURE_COUNCIL_DECISION_INDEX_SELF_TEST=pass")
    print(f"PHASE15_ARCHITECTURE_COUNCIL_DECISION_INDEX_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 Architecture Council decision-index packet stays visible across the narrow governance reminder surfaces."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the Zigux Phase 15 governance packet",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run synthetic fixture coverage for the decision-index checker",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 Architecture Council decision-index check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

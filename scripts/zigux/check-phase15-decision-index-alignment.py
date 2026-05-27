#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

DECISION_INDEX_PATH = Path("Documentation/zigux/phase15-architecture-council-decision-index.md")
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
DECISION_TEMPLATE_PATH = Path(
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
FREEZE_GOVERNANCE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
PARITY_SCORECARD_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
STUDY_ONLY_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
MANIFEST_PATH = Path("zigux/tests/phase15_architecture_council_decision_index_manifest.json")
TEST_PATH = Path("zigux/tests/phase15_architecture_council_decision_index.zig")

EXPECTED_LANE_KEY = "P15-L09"
EXPECTED_PHASE = "Phase 15"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-27"

REQUIRED_INDEX_MARKERS = (
    "PHASE15_STATUS=architecture_council_decision_index_landed",
    "PHASE15_LANE_KEY=P15-L09",
    "PHASE15_SLICE=decision-record-inventory",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "approved status-bucket changes recorded on current `master`: none",
    "stay-in-C closeout decision records recorded on current `master`: none",
    "no freeze-map anchor has an Architecture Council approval for a status change on current `master`",
    "decision record ID",
    "exact Linux anchor path",
    "review outcome",
    "evidence archive path",
    "surveyed commit marker",
    "next bounded step",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay outside this index until the freeze map changes",
)

REQUIRED_REVIEW_PROCESS_MARKER = (
    "`Documentation/zigux/phase15-architecture-council-decision-index.md` keeps the current "
    "Architecture Council decision inventory explicit"
)

REQUIRED_TEMPLATE_MARKER = (
    "Only record an exact head when the linked review needs it to anchor a named published decision"
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    required_paths = (
        DECISION_INDEX_PATH,
        REVIEW_PROCESS_PATH,
        DECISION_TEMPLATE_PATH,
        FREEZE_GOVERNANCE_PATH,
        PARITY_SCORECARD_PATH,
        STUDY_ONLY_PATH,
        MANIFEST_PATH,
        TEST_PATH,
    )
    for rel in required_paths:
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures

    decision_index = _read_text(root / DECISION_INDEX_PATH)
    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    decision_template = _read_text(root / DECISION_TEMPLATE_PATH)
    manifest = json.loads(_read_text(root / MANIFEST_PATH))

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("phase") != EXPECTED_PHASE:
        failures.append(f"phase:{manifest.get('phase')!r}")
    if manifest.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        failures.append(f"surveyed_commit:{manifest.get('surveyed_commit')!r}")
    if manifest.get("decision_index_note") != str(DECISION_INDEX_PATH):
        failures.append("decision_index_note")
    if manifest.get("checker") != "scripts/zigux/check-phase15-decision-index-alignment.py":
        failures.append("checker")
    if manifest.get("focused_replay") != str(TEST_PATH):
        failures.append("focused_replay")

    for marker in REQUIRED_INDEX_MARKERS:
        if marker not in decision_index:
            failures.append(f"missing_index_marker:{marker}")

    if EXPECTED_SURVEYED_COMMIT not in decision_index:
        failures.append("surveyed_commit_marker")

    if REQUIRED_REVIEW_PROCESS_MARKER not in review_process:
        failures.append("missing_review_process_decision_index_marker")

    if REQUIRED_TEMPLATE_MARKER not in decision_template:
        failures.append("missing_template_provenance_marker")

    return failures


def _sample_manifest() -> str:
    payload = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
        "surveyed_commit_mode": "dated_master_readback",
        "decision_index_note": str(DECISION_INDEX_PATH),
        "checker": "scripts/zigux/check-phase15-decision-index-alignment.py",
        "focused_replay": str(TEST_PATH),
    }
    return json.dumps(payload, indent=2) + "\n"


def _sample_decision_index() -> str:
    return """# Phase 15 Architecture Council Decision Index

## Status

- `PHASE15_STATUS=architecture_council_decision_index_landed`
- `PHASE15_LANE_KEY=P15-L09`
- `PHASE15_SLICE=decision-record-inventory`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-27`

## Current decision inventory

- approved status-bucket changes recorded on current `master`: none
- stay-in-C closeout decision records recorded on current `master`: none
- no freeze-map anchor has an Architecture Council approval for a status change on current `master`

## Index rules

- every future Architecture Council decision record for a freeze-map anchor must be linked here with decision record ID, exact Linux anchor path, review outcome, evidence archive path, surveyed commit marker, and next bounded step
- every linked record must also route back through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and `Documentation/zigux/phase15-parity-scorecard.md`
- `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay outside this index until the freeze map changes
"""


def _sample_review_process() -> str:
    return """# Phase 15 Architecture Council Review Process

- `Documentation/zigux/phase15-architecture-council-decision-index.md` keeps the current Architecture Council decision inventory explicit
"""


def _sample_template() -> str:
    return """# Phase 15 Architecture Council Decision Record Template

- Only record an exact head when the linked review needs it to anchor a named published decision
"""


def _sample_test() -> str:
    return """const std = @import("std");

test "phase15 decision index packet marker roster stays non-empty" {
    const required_markers = [_][]const u8{
        "approved status-bucket changes recorded on current `master`: none",
        "stay-in-C closeout decision records recorded on current `master`: none",
        "next bounded step",
    };
    try std.testing.expect(required_markers.len == 3);
}
"""


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_decision_index_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / DECISION_INDEX_PATH, _sample_decision_index())
        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(root / DECISION_TEMPLATE_PATH, _sample_template())
        _write(root / FREEZE_GOVERNANCE_PATH, "# fixture\n")
        _write(root / PARITY_SCORECARD_PATH, "# fixture\n")
        _write(root / STUDY_ONLY_PATH, "# fixture\n")
        _write(root / MANIFEST_PATH, _sample_manifest())
        _write(root / TEST_PATH, _sample_test())

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_index_root = root / "missing_index"
        _write(missing_index_root / DECISION_INDEX_PATH, _sample_decision_index().replace(
            "- stay-in-C closeout decision records recorded on current `master`: none\n", "", 1
        ))
        _write(missing_index_root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(missing_index_root / DECISION_TEMPLATE_PATH, _sample_template())
        _write(missing_index_root / FREEZE_GOVERNANCE_PATH, "# fixture\n")
        _write(missing_index_root / PARITY_SCORECARD_PATH, "# fixture\n")
        _write(missing_index_root / STUDY_ONLY_PATH, "# fixture\n")
        _write(missing_index_root / MANIFEST_PATH, _sample_manifest())
        _write(missing_index_root / TEST_PATH, _sample_test())
        failures = collect_failures(missing_index_root)
        expected = [
            "missing_index_marker:stay-in-C closeout decision records recorded on current `master`: none"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-index failure: {failures}")

        manifest_root = root / "manifest_drift"
        _write(manifest_root / DECISION_INDEX_PATH, _sample_decision_index())
        _write(manifest_root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(manifest_root / DECISION_TEMPLATE_PATH, _sample_template())
        _write(manifest_root / FREEZE_GOVERNANCE_PATH, "# fixture\n")
        _write(manifest_root / PARITY_SCORECARD_PATH, "# fixture\n")
        _write(manifest_root / STUDY_ONLY_PATH, "# fixture\n")
        _write(
            manifest_root / MANIFEST_PATH,
            _sample_manifest().replace('"lane_key": "P15-L09"', '"lane_key": "P15-L99"', 1),
        )
        _write(manifest_root / TEST_PATH, _sample_test())
        failures = collect_failures(manifest_root)
        expected = ["lane_key:'P15-L99'"]
        if failures != expected:
            raise AssertionError(f"unexpected manifest drift failure: {failures}")

    print("PHASE15_DECISION_INDEX_ALIGNMENT_SELF_TEST=pass")
    print("PHASE15_DECISION_INDEX_ALIGNMENT_SELF_TEST_CASES=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 Architecture Council decision index stays aligned with its owner packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_DECISION_INDEX_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
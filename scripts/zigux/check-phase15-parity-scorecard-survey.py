#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase15-parity-scorecard-survey.md")
SCORECARD_DOC_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
STUDY_ONLY_NOTE_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
SCORECARD_JSON_PATH = Path("zigux/tests/phase15_parity_scorecard.json")
SCORECARD_ZIG_PATH = Path("zigux/tests/phase15_parity_scorecard.zig")
SELF_PATH = Path("scripts/zigux/check-phase15-parity-scorecard-survey.py")

EXPECTED_STATUS_MARKERS = (
    "PHASE15_LANE_KEY=P15-L09",
    "PHASE15_STATUS=parity_scorecard_survey_landed",
    "PHASE15_SLICE=parity-roadmap-readback-alignment",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "The roadmap-required parity scorecard packet is no longer missing on current `master`.",
    "no Architecture Council approval is recorded for any freeze-map status change",
    "this survey lane should stay parked unless roadmap-versus-repo truthfulness drifts again",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _metric_line(label: str, value: int) -> str:
    return f"- {label}: `{value}`"


def collect_failures(root: Path) -> list[str]:
    survey = _read_text(root / SURVEY_PATH)
    scorecard_doc = _read_text(root / SCORECARD_DOC_PATH)
    study_only_note = _read_text(root / STUDY_ONLY_NOTE_PATH)
    scorecard = _read_json(root / SCORECARD_JSON_PATH)
    failures: list[str] = []

    for marker in EXPECTED_STATUS_MARKERS:
        if marker not in survey:
            failures.append(f"survey missing required marker: {marker}")

    if f"`{SELF_PATH}`" not in survey:
        failures.append("survey missing focused survey-checker marker")

    for rel in (SCORECARD_DOC_PATH, SCORECARD_JSON_PATH, SCORECARD_ZIG_PATH, STUDY_ONLY_NOTE_PATH):
        if not (root / rel).exists():
            failures.append(f"survey companion path missing from repo fixture: `{rel}`")
        if f"`{rel}`" not in survey:
            failures.append(f"survey missing companion-path marker: `{rel}`")

    if f"`{scorecard['surveyed_commit']}`" not in survey:
        failures.append("survey missing current surveyed-commit marker")
    if f"`{scorecard['lane_key']}`" not in survey:
        failures.append("survey missing dedicated parity-scorecard lane key")
    if f"`{scorecard['slice']}`" not in survey:
        failures.append("survey missing dedicated parity-scorecard slice")
    if f"`{scorecard['provenance_mode']}`" not in survey:
        failures.append("survey missing dedicated parity-scorecard provenance mode")
    if f"`{scorecard['posture']['scorecard_role']}`" not in survey:
        failures.append("survey missing dedicated parity-scorecard posture marker")

    metric_labels = (
        ("active freeze-in-C anchor count", scorecard["metrics"]["active_freeze_in_c_anchor_count"]),
        ("blocked status-change anchor count", scorecard["metrics"]["blocked_status_change_anchor_count"]),
        (
            "anchors blocked entirely within Phase 15 governance evidence",
            scorecard["metrics"]["phase15_governance_only_blocker_anchor_count"],
        ),
        ("Phase 14 coupled blocker anchor count", scorecard["metrics"]["phase14_coupled_blocker_anchor_count"]),
        (
            "anchors still blocked on prior-phase bridge evidence",
            scorecard["metrics"]["anchors_still_blocked_on_prior_phase_bridge_evidence"],
        ),
        (
            "study-only anchors tracked outside the scorecard",
            scorecard["metrics"]["study_only_anchors_tracked_outside_scorecard"],
        ),
        (
            "Architecture Council approvals recorded for status change",
            scorecard["metrics"]["architecture_council_status_change_approval_count"],
        ),
    )
    for label, value in metric_labels:
        rendered = _metric_line(label, value)
        if rendered not in survey:
            failures.append(f"survey missing metric line: {rendered}")

    for anchor in scorecard["anchors"]:
        if f"`{anchor['path']}`" not in survey:
            failures.append(f"survey missing anchor marker: `{anchor['path']}`")

    study_only_paths = ("kernel/workqueue.c", "kernel/trace/ring_buffer.c")
    for path in study_only_paths:
        if f"`{path}`" not in survey:
            failures.append(f"survey missing study-only anchor marker: `{path}`")
        if f"`{path}`" not in study_only_note:
            failures.append(f"study-only accounting note missing study-only anchor: `{path}`")

    count_line = (
        f"`Documentation/zigux/phase15-study-only-anchor-accounting.md` keeps "
        f"`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` parked outside the blocked status-change rows, "
        f"matching the scorecard's study-only count of "
        f"`{scorecard['metrics']['study_only_anchors_tracked_outside_scorecard']}`."
    )
    if count_line not in survey:
        failures.append("survey missing explicit study-only accounting alignment marker")

    if scorecard["metrics"]["active_freeze_in_c_anchor_count"] != len(scorecard["anchors"]):
        failures.append("scorecard fixture active-freeze count no longer matches anchor row count")

    if "blocked_posture_accounting_not_port_readiness" not in scorecard_doc:
        failures.append("scorecard note fixture lost the blocked-posture marker")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_survey() -> str:
    return """# Phase 15 Parity Scorecard Survey

## Status

- `PHASE15_LANE_KEY=P15-L09`
- `PHASE15_STATUS=parity_scorecard_survey_landed`
- `PHASE15_SLICE=parity-roadmap-readback-alignment`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`

The roadmap-required parity scorecard packet is no longer missing on current `master`.

Direct packet:
- `Documentation/zigux/phase15-parity-scorecard.md`
- `zigux/tests/phase15_parity_scorecard.json`
- `zigux/tests/phase15_parity_scorecard.zig`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `scripts/zigux/check-phase15-parity-scorecard-survey.py`

Those three dedicated parity-scorecard surfaces now agree on:
- lane key: `P15-L03`
- slice: `parity-scorecard-baseline`
- provenance mode: `dated_master_readback`
- surveyed commit marker: `current-master-readback-2026-05-19`
- posture: `blocked_posture_accounting_not_port_readiness`

The live machine-readable metrics now cover:
- active freeze-in-C anchor count: `4`
- blocked status-change anchor count: `4`
- anchors blocked entirely within Phase 15 governance evidence: `2`
- Phase 14 coupled blocker anchor count: `2`
- anchors still blocked on prior-phase bridge evidence: `2`
- study-only anchors tracked outside the scorecard: `2`
- Architecture Council approvals recorded for status change: `0`

The live anchor inventory remains:
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

`Documentation/zigux/phase15-study-only-anchor-accounting.md` keeps `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` parked outside the blocked status-change rows, matching the scorecard's study-only count of `2`.

The honest bounded Phase 15 statement on current `master` is:
- no Architecture Council approval is recorded for any freeze-map status change
- this survey lane should stay parked unless roadmap-versus-repo truthfulness drifts again
"""


def _sample_scorecard_json() -> str:
    return json.dumps(
        {
            "status": "parity_scorecard_slice_landed",
            "lane_key": "P15-L03",
            "slice": "parity-scorecard-baseline",
            "provenance_mode": "dated_master_readback",
            "surveyed_commit": "current-master-readback-2026-05-19",
            "posture": {
                "architecture_council_status_change_approval_recorded": False,
                "scorecard_role": "blocked_posture_accounting_not_port_readiness",
            },
            "metrics": {
                "active_freeze_in_c_anchor_count": 4,
                "blocked_status_change_anchor_count": 4,
                "phase15_governance_only_blocker_anchor_count": 2,
                "phase14_coupled_blocker_anchor_count": 2,
                "anchors_still_blocked_on_prior_phase_bridge_evidence": 2,
                "study_only_anchors_tracked_outside_scorecard": 2,
                "architecture_council_status_change_approval_count": 0,
            },
            "anchors": [
                {"path": "kernel/sched/core.c"},
                {"path": "mm/page_alloc.c"},
                {"path": "kernel/rcu/tree.c"},
                {"path": "net/core/skbuff.c"},
            ],
        },
        indent=2,
    ) + "\n"


def _seed_repo(root: Path) -> None:
    _write(root / SURVEY_PATH, _sample_survey())
    _write(root / SCORECARD_DOC_PATH, "blocked_posture_accounting_not_port_readiness\n")
    _write(
        root / STUDY_ONLY_NOTE_PATH,
        "`kernel/workqueue.c`\n`kernel/trace/ring_buffer.c`\n",
    )
    _write(root / SCORECARD_JSON_PATH, _sample_scorecard_json())
    _write(root / SCORECARD_ZIG_PATH, "present\n")
    _write(root / SELF_PATH, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_scorecard_survey_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        metric_root = root / "metric"
        _seed_repo(metric_root)
        _write(
            metric_root / SURVEY_PATH,
            _sample_survey().replace("- study-only anchors tracked outside the scorecard: `2`\n", "", 1),
        )
        failures = collect_failures(metric_root)
        expected = ["survey missing metric line: - study-only anchors tracked outside the scorecard: `2`"]
        if failures != expected:
            raise AssertionError(f"unexpected metric failure: {failures}")

        study_root = root / "study"
        _seed_repo(study_root)
        _write(
            study_root / SURVEY_PATH,
            _sample_survey().replace(
                "`Documentation/zigux/phase15-study-only-anchor-accounting.md` keeps `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` parked outside the blocked status-change rows, matching the scorecard's study-only count of `2`.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(study_root)
        expected = [
            "survey missing study-only anchor marker: `kernel/workqueue.c`",
            "survey missing study-only anchor marker: `kernel/trace/ring_buffer.c`",
            "survey missing explicit study-only accounting alignment marker",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected study-only alignment failure: {failures}")

        anchor_root = root / "anchor"
        _seed_repo(anchor_root)
        _write(
            anchor_root / SURVEY_PATH,
            _sample_survey().replace("- `net/core/skbuff.c`\n", "", 1),
        )
        failures = collect_failures(anchor_root)
        expected = ["survey missing anchor marker: `net/core/skbuff.c`"]
        if failures != expected:
            raise AssertionError(f"unexpected anchor failure: {failures}")

    print("PHASE15_PARITY_SCORECARD_SURVEY_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 parity-scorecard survey still matches the live scorecard packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run the synthetic self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 parity-scorecard survey check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

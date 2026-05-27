#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SURVEY_NOTE_PATH = Path("Documentation/zigux/phase15-parity-scorecard-survey.md")
SCORECARD_NOTE_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
SCORECARD_JSON_PATH = Path("zigux/tests/phase15_parity_scorecard.json")
SCORECARD_ZIG_PATH = Path("zigux/tests/phase15_parity_scorecard.zig")
READINESS_NOTE_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
SEQUENCING_NOTE_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
BUILD_PATH = Path("zigux/tests/phase15_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_SURVEY_MARKERS = (
    "PHASE15_LANE_KEY=P15-L09",
    "PHASE15_STATUS=parity_scorecard_survey_landed",
    "PHASE15_SLICE=parity-roadmap-readback-alignment",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "survey rechecked against current `master` on 2026-05-25",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`zigux/tests/phase15_parity_scorecard.json`",
    "`zigux/tests/phase15_parity_scorecard.zig`",
    "`scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig` are now present on current `master`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md` still carries the older dedicated-build-gap wording",
    "the parked `make -C zigux phase15{,-validate,-test}` wrapper routes still remain broader repo-reality gaps",
    "the neighboring governance-lane-sequencing packet now needs its own separate truthfulness refresh",
)

REQUIRED_DIRECT_PATHS = (
    str(SURVEY_NOTE_PATH),
    str(SCORECARD_NOTE_PATH),
    str(SCORECARD_JSON_PATH),
    str(SCORECARD_ZIG_PATH),
    str(READINESS_NOTE_PATH),
    str(SEQUENCING_NOTE_PATH),
    str(VALIDATOR_PATH),
    str(BUILD_PATH),
    str(MAKEFILE_PATH),
)

EXPECTED_ANCHORS = (
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
)

BLOCKED_ROUTE_MARKERS = (
    "phase15-validate:",
    "phase15-test:",
    "phase15:",
    ".PHONY: phase15",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(_read_text(path))


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in REQUIRED_DIRECT_PATHS:
        if not (root / rel).exists():
            failures.append(f"missing_direct_path:{rel}")

    survey_note = _read_text(root / SURVEY_NOTE_PATH)
    scorecard_note = _read_text(root / SCORECARD_NOTE_PATH)
    scorecard_json = _read_json(root / SCORECARD_JSON_PATH)
    scorecard_zig = _read_text(root / SCORECARD_ZIG_PATH)
    readiness_note = _read_text(root / READINESS_NOTE_PATH)
    sequencing_note = _read_text(root / SEQUENCING_NOTE_PATH)
    makefile = _read_text(root / MAKEFILE_PATH)

    for marker in REQUIRED_SURVEY_MARKERS:
        if marker not in survey_note:
            failures.append(f"survey_note_missing_marker:{marker}")

    if scorecard_json.get("lane_key") != "P15-L03":
        failures.append("scorecard_json_lane_key_drift")
    if scorecard_json.get("surveyed_commit") != "current-master-readback-2026-05-25":
        failures.append("scorecard_json_surveyed_commit_drift")
    if scorecard_json.get("posture", {}).get("scorecard_role") != "blocked_posture_accounting_not_port_readiness":
        failures.append("scorecard_json_posture_drift")

    metrics = scorecard_json.get("metrics", {})
    expected_metrics = {
        "active_freeze_in_c_anchor_count": 4,
        "blocked_status_change_anchor_count": 4,
        "phase15_governance_only_blocker_anchor_count": 2,
        "phase14_coupled_blocker_anchor_count": 2,
        "anchors_still_blocked_on_prior_phase_bridge_evidence": 2,
        "study_only_anchors_tracked_outside_scorecard": 2,
        "architecture_council_status_change_approval_count": 0,
    }
    for key, value in expected_metrics.items():
        if metrics.get(key) != value:
            failures.append(f"scorecard_json_metric_drift:{key}")

    anchors = scorecard_json.get("anchors", [])
    if len(anchors) != 4:
        failures.append("scorecard_json_anchor_count_drift")
    actual_anchor_paths = [anchor.get("path") for anchor in anchors]
    if actual_anchor_paths != list(EXPECTED_ANCHORS):
        failures.append("scorecard_json_anchor_inventory_drift")

    for anchor in EXPECTED_ANCHORS:
        if anchor not in survey_note:
            failures.append(f"survey_note_missing_anchor:{anchor}")
        if anchor not in scorecard_note:
            failures.append(f"scorecard_note_missing_anchor:{anchor}")
        if anchor not in scorecard_zig:
            failures.append(f"scorecard_zig_missing_anchor:{anchor}")

    for marker in (
        "validator-first reminder route is directly readable on current `master` through `python3 scripts/zigux/validate-phase15.py`",
        "shared replay build route is directly readable on current `master` through `zigux/tests/phase15_build.zig` and `zig build test --build-file zigux/tests/phase15_build.zig`",
    ):
        if marker not in scorecard_note:
            failures.append(f"scorecard_note_missing_marker:{marker}")

    for marker in (
        "scripts/zigux/validate-phase15.py",
        "zigux/tests/phase15_build.zig",
    ):
        if marker not in readiness_note:
            failures.append(f"readiness_note_missing_marker:{marker}")

    if "still carries the older dedicated-build-gap wording" not in survey_note:
        failures.append("survey_note_missing_neighboring_gap_marker")
    if "the dedicated shared build companion `zigux/tests/phase15_build.zig` is now directly materialized" not in sequencing_note:
        failures.append("sequencing_note_missing_build_companion_marker")

    for marker in BLOCKED_ROUTE_MARKERS:
        if marker in makefile:
            failures.append(f"blocked_route_returned:{marker}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_survey_note() -> str:
    anchors = "\n".join(f"- `{anchor}`" for anchor in EXPECTED_ANCHORS)
    return f"""# Phase 15 Parity Scorecard Survey

## Status

- `PHASE15_LANE_KEY=P15-L09`
- `PHASE15_STATUS=parity_scorecard_survey_landed`
- `PHASE15_SLICE=parity-roadmap-readback-alignment`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- survey rechecked against current `master` on 2026-05-25
- product boundary:
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `zigux/tests/phase15_parity_scorecard.json`
  - `zigux/tests/phase15_parity_scorecard.zig`
  - `Documentation/zigux/phase15-parity-scorecard-survey.md`

## Current master readback

{anchors}

- `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig` are now present on current `master`
- `Documentation/zigux/phase15-governance-lane-sequencing.md` still carries the older dedicated-build-gap wording

## Honest current posture

- the parked `make -C zigux phase15{{,-validate,-test}}` wrapper routes still remain broader repo-reality gaps
- the neighboring governance-lane-sequencing packet now needs its own separate truthfulness refresh
"""


def _sample_scorecard_note() -> str:
    return """# Phase 15 Parity Scorecard

- validator-first reminder route is directly readable on current `master` through `python3 scripts/zigux/validate-phase15.py`
- shared replay build route is directly readable on current `master` through `zigux/tests/phase15_build.zig` and `zig build test --build-file zigux/tests/phase15_build.zig`
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`
"""


def _sample_scorecard_json() -> str:
    return json.dumps(
        {
            "lane_key": "P15-L03",
            "surveyed_commit": "current-master-readback-2026-05-25",
            "posture": {
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
            "anchors": [{"path": anchor} for anchor in EXPECTED_ANCHORS],
        },
        indent=2,
    ) + "\n"


def _sample_scorecard_zig() -> str:
    return "\n".join(EXPECTED_ANCHORS) + "\n"


def _sample_readiness_note() -> str:
    return """# Phase 15 Readiness Gate Survey

- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
"""


def _sample_sequencing_note() -> str:
    return """# Phase 15 Governance Lane Sequencing

- the dedicated shared build companion `zigux/tests/phase15_build.zig` is now directly materialized
"""


def _seed_repo(root: Path) -> None:
    _write(root / SURVEY_NOTE_PATH, _sample_survey_note())
    _write(root / SCORECARD_NOTE_PATH, _sample_scorecard_note())
    _write(root / SCORECARD_JSON_PATH, _sample_scorecard_json())
    _write(root / SCORECARD_ZIG_PATH, _sample_scorecard_zig())
    _write(root / READINESS_NOTE_PATH, _sample_readiness_note())
    _write(root / SEQUENCING_NOTE_PATH, _sample_sequencing_note())
    _write(root / VALIDATOR_PATH, "present\n")
    _write(root / BUILD_PATH, "present\n")
    _write(root / MAKEFILE_PATH, "PYTHON ?= python3\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_parity_scorecard_survey_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_marker_root = root / "missing_marker"
        _seed_repo(missing_marker_root)
        _write(
            missing_marker_root / SURVEY_NOTE_PATH,
            _sample_survey_note().replace(
                "- `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig` are now present on current `master`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_marker_root)
        expected = [
            "survey_note_missing_marker:`scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig` are now present on current `master`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")

        metric_drift_root = root / "metric_drift"
        _seed_repo(metric_drift_root)
        scorecard = json.loads(_sample_scorecard_json())
        scorecard["metrics"]["active_freeze_in_c_anchor_count"] = 3
        _write(metric_drift_root / SCORECARD_JSON_PATH, json.dumps(scorecard, indent=2) + "\n")
        failures = collect_failures(metric_drift_root)
        expected = ["scorecard_json_metric_drift:active_freeze_in_c_anchor_count"]
        if failures != expected:
            raise AssertionError(f"unexpected metric-drift failure: {failures}")

        returned_route_root = root / "returned_route"
        _seed_repo(returned_route_root)
        _write(returned_route_root / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(returned_route_root)
        expected = ["blocked_route_returned:phase15-validate:"]
        if failures != expected:
            raise AssertionError(f"unexpected returned-route failure: {failures}")

        anchor_drift_root = root / "anchor_drift"
        _seed_repo(anchor_drift_root)
        scorecard = json.loads(_sample_scorecard_json())
        scorecard["anchors"][3]["path"] = "net/core/other.c"
        _write(anchor_drift_root / SCORECARD_JSON_PATH, json.dumps(scorecard, indent=2) + "\n")
        failures = collect_failures(anchor_drift_root)
        expected = ["scorecard_json_anchor_inventory_drift"]
        if failures != expected:
            raise AssertionError(f"unexpected anchor-drift failure: {failures}")

    print("PHASE15_PARITY_SCORECARD_SURVEY_SELF_TEST=pass")
    print("PHASE15_PARITY_SCORECARD_SURVEY_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 parity-scorecard survey stays aligned with the current parity-accounting packet."
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

    print("PHASE15_PARITY_SCORECARD_SURVEY=pass")
    print(f"PHASE15_PARITY_SCORECARD_SURVEY_ANCHOR_COUNT={len(EXPECTED_ANCHORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

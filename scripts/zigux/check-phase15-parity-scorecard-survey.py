#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase15-parity-scorecard-survey.md")
SCORECARD_DOC_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
SCORECARD_JSON_PATH = Path("zigux/tests/phase15_parity_scorecard.json")
SCORECARD_ZIG_PATH = Path("zigux/tests/phase15_parity_scorecard.zig")
SEQUENCING_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")

REQUIRED_SURVEY_MARKERS = (
    "PHASE15_LANE_KEY=P15-L09",
    "PHASE15_STATUS=parity_scorecard_survey_landed",
    "PHASE15_SLICE=parity-roadmap-readback-alignment",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "survey rechecked against current `master` on 2026-05-20; the dedicated parity-scorecard packet still carries dated readback marker `current-master-readback-2026-05-19`",
    "The roadmap-required parity scorecard packet is still substantively present on current `master`.",
    "the roadmap-required parity scorecard is landed as a note plus machine-readable JSON plus dedicated Zig guard",
    "no Architecture Council approval is recorded for any freeze-map status change",
    "That means the survey-local truthfulness gap is now closed.",
    "landed `phase15-parity-scorecard-survey-exact-handoff-readback`",
    "landed `phase15-parity-scorecard-dedicated-route-alignment-readback`",
    "Keep `P15-L09` parked unless a fresh reread shows one of two changes:",
    "`scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, and the parked `make -C zigux phase15{,-validate,-test}` routes actually return on current `master`",
)

FORBIDDEN_SURVEY_MARKERS = (
    "current-master-readback-2026-05-17",
    "current-master-readback-2026-05-18",
    "The roadmap-required parity scorecard packet is no longer missing on current `master`.",
    "this survey lane should stay parked unless roadmap-versus-repo truthfulness drifts again",
    "landed `phase15-parity-scorecard-survey-truthfulness-refresh`",
)

EXPECTED_ANCHORS = (
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
)

EXPECTED_METRICS = (
    ("active freeze-in-C anchor count", 4),
    ("blocked status-change anchor count", 4),
    ("anchors blocked entirely within Phase 15 governance evidence", 2),
    ("Phase 14 coupled blocker anchor count", 2),
    ("anchors still blocked on prior-phase bridge evidence", 2),
    ("study-only anchors tracked outside the scorecard", 2),
    ("Architecture Council approvals recorded for status change", 0),
)

JSON_METRIC_KEYS = {
    "active freeze-in-C anchor count": "active_freeze_in_c_anchor_count",
    "blocked status-change anchor count": "blocked_status_change_anchor_count",
    "anchors blocked entirely within Phase 15 governance evidence": "phase15_governance_only_blocker_anchor_count",
    "Phase 14 coupled blocker anchor count": "phase14_coupled_blocker_anchor_count",
    "anchors still blocked on prior-phase bridge evidence": "anchors_still_blocked_on_prior_phase_bridge_evidence",
    "study-only anchors tracked outside the scorecard": "study_only_anchors_tracked_outside_scorecard",
    "Architecture Council approvals recorded for status change": "architecture_council_status_change_approval_count",
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(_read_text(path))


def _metric_line(label: str, value: int) -> str:
    return f"{label}: `{value}`"


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    required_paths = (
        SURVEY_PATH,
        SCORECARD_DOC_PATH,
        SCORECARD_JSON_PATH,
        SCORECARD_ZIG_PATH,
        SEQUENCING_PATH,
    )
    for rel in required_paths:
        if not (root / rel).exists():
            failures.append(f"repo:missing_required_path:{rel}")

    if failures:
        return failures

    survey = _read_text(root / SURVEY_PATH)
    scorecard_doc = _read_text(root / SCORECARD_DOC_PATH)
    scorecard_json = _read_json(root / SCORECARD_JSON_PATH)
    sequencing = _read_text(root / SEQUENCING_PATH)

    for marker in REQUIRED_SURVEY_MARKERS:
        if marker not in survey:
            failures.append(f"survey:missing_marker:{marker}")

    for marker in FORBIDDEN_SURVEY_MARKERS:
        if marker in survey:
            failures.append(f"survey:forbidden_marker_present:{marker}")

    surveyed_commit = scorecard_json.get("surveyed_commit")
    if surveyed_commit != "current-master-readback-2026-05-19":
        failures.append("scorecard_json:surveyed_commit_drift")
    else:
        if surveyed_commit not in survey:
            failures.append("survey:missing_scorecard_surveyed_commit")
        if surveyed_commit not in scorecard_doc:
            failures.append("scorecard_doc:missing_surveyed_commit")

    posture = scorecard_json.get("posture", {})
    if posture.get("scorecard_role") != "blocked_posture_accounting_not_port_readiness":
        failures.append("scorecard_json:posture_role_drift")
    if posture.get("architecture_council_status_change_approval_recorded") is not False:
        failures.append("scorecard_json:approval_recorded_drift")

    metrics = scorecard_json.get("metrics", {})
    for label, value in EXPECTED_METRICS:
        key = JSON_METRIC_KEYS[label]
        if metrics.get(key) != value:
            failures.append(f"scorecard_json:metric_drift:{key}")
        line = _metric_line(label, value)
        if line not in survey:
            failures.append(f"survey:missing_metric_line:{line}")

    anchors = scorecard_json.get("anchors", [])
    anchor_paths = [anchor.get("path") for anchor in anchors]
    if anchor_paths != list(EXPECTED_ANCHORS):
        failures.append("scorecard_json:anchor_order_drift")

    for anchor in EXPECTED_ANCHORS:
        quoted = f"`{anchor}`"
        if quoted not in survey:
            failures.append(f"survey:missing_anchor_marker:{quoted}")
        if anchor not in scorecard_doc:
            failures.append(f"scorecard_doc:missing_anchor:{anchor}")

    scorecard_paths = (
        f"`{SCORECARD_DOC_PATH}`",
        f"`{SCORECARD_JSON_PATH}`",
        f"`{SCORECARD_ZIG_PATH}`",
    )
    for path_marker in scorecard_paths:
        if path_marker not in survey:
            failures.append(f"survey:missing_packet_path:{path_marker}")

    if "`scripts/zigux/validate-phase15.py`" not in sequencing:
        failures.append("sequencing:missing_validate_phase15_gap")
    if "`zigux/tests/phase15_build.zig`" not in sequencing:
        failures.append("sequencing:missing_phase15_build_gap")
    gap_sentence_markers = (
        "still returns missing for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`",
        "still returned missing for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`",
    )
    if not any(marker in survey for marker in gap_sentence_markers):
        failures.append("survey:missing_current_gap_sentence")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_survey() -> str:
    metric_lines = "\n".join(f"- {_metric_line(label, value)}" for label, value in EXPECTED_METRICS)
    anchor_lines = "\n".join(f"- `{anchor}`" for anchor in EXPECTED_ANCHORS)
    return f"""# Phase 15 Parity Scorecard Survey

## Status

- `PHASE15_LANE_KEY=P15-L09`
- `PHASE15_STATUS=parity_scorecard_survey_landed`
- `PHASE15_SLICE=parity-roadmap-readback-alignment`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- survey rechecked against current `master` on 2026-05-20; the dedicated parity-scorecard packet still carries dated readback marker `current-master-readback-2026-05-19`

## Current master readback

The roadmap-required parity scorecard packet is still substantively present on current `master`.
the roadmap-required parity scorecard is landed as a note plus machine-readable JSON plus dedicated Zig guard
no Architecture Council approval is recorded for any freeze-map status change
That means the survey-local truthfulness gap is now closed.

- `{SCORECARD_DOC_PATH}`
- `{SCORECARD_JSON_PATH}`
- `{SCORECARD_ZIG_PATH}`

{metric_lines}

{anchor_lines}

The dedicated scorecard note, the JSON companion, the dedicated Zig guard, and the broader governance sequencing note all keep the same missing-route posture for the broader validator-first and shared-build companions.
direct current-`master` readback on 2026-05-20 still returned missing for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`, so the dedicated scorecard note, JSON companion, dedicated Zig guard, and the broader governance sequencing note now agree on the same reminder-route posture
`scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, and the parked `make -C zigux phase15{{,-validate,-test}}` routes actually return on current `master`

## Recorded gaps

- landed `phase15-parity-scorecard-survey-exact-handoff-readback`
- landed `phase15-parity-scorecard-dedicated-route-alignment-readback`

## Next bounded step

Keep `P15-L09` parked unless a fresh reread shows one of two changes:
"""


def _sample_scorecard_doc() -> str:
    return """# Phase 15 Parity Scorecard

- surveyed against dated current-master readback marker `current-master-readback-2026-05-19`
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`
"""


def _sample_scorecard_json() -> str:
    return json.dumps(
        {
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
            "anchors": [{"path": anchor} for anchor in EXPECTED_ANCHORS],
        },
        indent=2,
    ) + "\n"


def _sample_sequencing() -> str:
    return """# Phase 15 Governance Lane Sequencing

- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
"""


def _seed_repo(root: Path) -> None:
    _write(root / SURVEY_PATH, _sample_survey())
    _write(root / SCORECARD_DOC_PATH, _sample_scorecard_doc())
    _write(root / SCORECARD_JSON_PATH, _sample_scorecard_json())
    _write(root / SCORECARD_ZIG_PATH, "test {}\n")
    _write(root / SEQUENCING_PATH, _sample_sequencing())


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_parity_scorecard_survey_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_metric_root = root / "missing_metric"
        _seed_repo(missing_metric_root)
        _write(
            missing_metric_root / SURVEY_PATH,
            _sample_survey().replace("- Architecture Council approvals recorded for status change: `0`\n", "", 1),
        )
        failures = collect_failures(missing_metric_root)
        expected = [
            "survey:missing_metric_line:Architecture Council approvals recorded for status change: `0`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-metric failure: {failures}")

        stale_root = root / "stale_marker"
        _seed_repo(stale_root)
        _write(
            stale_root / SURVEY_PATH,
            _sample_survey().replace(
                "The roadmap-required parity scorecard packet is still substantively present on current `master`.",
                "The roadmap-required parity scorecard packet is no longer missing on current `master`.",
                1,
            ),
        )
        failures = collect_failures(stale_root)
        expected = [
            "survey:missing_marker:The roadmap-required parity scorecard packet is still substantively present on current `master`.",
            "survey:forbidden_marker_present:The roadmap-required parity scorecard packet is no longer missing on current `master`.",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-marker failure: {failures}")

        anchor_root = root / "anchor_drift"
        _seed_repo(anchor_root)
        drifted = json.loads(_sample_scorecard_json())
        drifted["anchors"] = drifted["anchors"][:-1]
        _write(anchor_root / SCORECARD_JSON_PATH, json.dumps(drifted, indent=2) + "\n")
        failures = collect_failures(anchor_root)
        expected = ["scorecard_json:anchor_order_drift"]
        if failures != expected:
            raise AssertionError(f"unexpected anchor-drift failure: {failures}")

        missing_path_root = root / "missing_path"
        _seed_repo(missing_path_root)
        (missing_path_root / SCORECARD_ZIG_PATH).unlink()
        failures = collect_failures(missing_path_root)
        expected = [f"repo:missing_required_path:{SCORECARD_ZIG_PATH}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-path failure: {failures}")

        posture_root = root / "posture_drift"
        _seed_repo(posture_root)
        drifted = json.loads(_sample_scorecard_json())
        drifted["posture"]["scorecard_role"] = "port_readiness"
        _write(posture_root / SCORECARD_JSON_PATH, json.dumps(drifted, indent=2) + "\n")
        failures = collect_failures(posture_root)
        expected = ["scorecard_json:posture_role_drift"]
        if failures != expected:
            raise AssertionError(f"unexpected posture-drift failure: {failures}")

    print("PHASE15_PARITY_SCORECARD_SURVEY_SELF_TEST=pass")
    print("PHASE15_PARITY_SCORECARD_SURVEY_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 parity-scorecard survey stays aligned with the landed scorecard packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in synthetic self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE15_PARITY_SCORECARD_SURVEY=pass")
    print("PHASE15_PARITY_SCORECARD_SURVEY_REQUIRED_PATH_COUNT=4")
    print(f"PHASE15_PARITY_SCORECARD_SURVEY_ANCHOR_COUNT={len(EXPECTED_ANCHORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

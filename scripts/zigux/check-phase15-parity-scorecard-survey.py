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
READINESS_NOTE_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
SEQUENCING_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
BUILD_PATH = Path("zigux/tests/phase15_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-25"
EXPECTED_LANE_KEY = "P15-L09"
EXPECTED_SLICE = "parity-roadmap-readback-alignment"
EXPECTED_STATUS = "parity_scorecard_survey_landed"
EXPECTED_SCORECARD_LANE = "P15-L03"
EXPECTED_SCORECARD_SLICE = "parity-scorecard-baseline"
EXPECTED_POSTURE_ROLE = "blocked_posture_accounting_not_port_readiness"

EXPECTED_ANCHORS = (
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
)

EXPECTED_METRICS = (
    ("active freeze-in-C anchor count", "active_freeze_in_c_anchor_count", 4),
    ("blocked status-change anchor count", "blocked_status_change_anchor_count", 4),
    ("anchors blocked entirely within Phase 15 governance evidence", "phase15_governance_only_blocker_anchor_count", 2),
    ("Phase 14 coupled blocker anchor count", "phase14_coupled_blocker_anchor_count", 2),
    ("anchors still blocked on prior-phase bridge evidence", "anchors_still_blocked_on_prior_phase_bridge_evidence", 2),
    ("study-only anchors tracked outside the scorecard", "study_only_anchors_tracked_outside_scorecard", 2),
    ("Architecture Council approvals recorded for status change", "architecture_council_status_change_approval_count", 0),
)

REQUIRED_SURVEY_MARKERS = (
    f"PHASE15_LANE_KEY={EXPECTED_LANE_KEY}",
    f"PHASE15_STATUS={EXPECTED_STATUS}",
    f"PHASE15_SLICE={EXPECTED_SLICE}",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    f"survey rechecked against current `master` on 2026-05-25; the dedicated parity-scorecard packet now carries dated readback marker `{EXPECTED_SURVEYED_COMMIT}`",
    "The roadmap-required parity scorecard packet is still substantively present on current `master`.",
    "the roadmap-required parity scorecard is landed as a note plus machine-readable JSON plus dedicated Zig guard",
    "no Architecture Council approval is recorded for any freeze-map status change",
    "`scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig` are now present on current `master`",
    "the parked `make -C zigux phase15{,-validate,-test}` wrapper routes still remain broader repo-reality gaps",
    "the neighboring governance-lane-sequencing packet now needs its own separate truthfulness refresh if it is to stop treating the dedicated shared-build companion as missing",
    "landed `phase15-validator-first-route-materialized`",
    "landed `phase15-shared-build-route-materialized`",
)

FORBIDDEN_SURVEY_MARKERS = (
    "current-master-readback-2026-05-19",
    "current-master-readback-2026-05-21",
    "scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, and the parked `make -C zigux phase15{,-validate,-test}` routes actually return on current `master`",
    "still returned missing for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(_read_text(path))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _makefile_has_target(root: Path, target: str) -> bool:
    text = "\n" + _read_text(root / MAKEFILE_PATH)
    return f"\n{target}:" in text


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    required_paths = (
        SURVEY_PATH,
        SCORECARD_DOC_PATH,
        SCORECARD_JSON_PATH,
        SCORECARD_ZIG_PATH,
        READINESS_NOTE_PATH,
        SEQUENCING_PATH,
        VALIDATOR_PATH,
        BUILD_PATH,
        MAKEFILE_PATH,
    )
    for rel in required_paths:
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures

    survey = _read_text(root / SURVEY_PATH)
    scorecard_doc = _read_text(root / SCORECARD_DOC_PATH)
    scorecard_json = _read_json(root / SCORECARD_JSON_PATH)
    readiness = _read_text(root / READINESS_NOTE_PATH)
    sequencing = _read_text(root / SEQUENCING_PATH)

    for marker in REQUIRED_SURVEY_MARKERS:
        if marker not in survey:
            failures.append(f"survey:missing_marker:{marker}")

    for marker in FORBIDDEN_SURVEY_MARKERS:
        if marker in survey:
            failures.append(f"survey:forbidden_marker:{marker}")

    if scorecard_json.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        failures.append("scorecard_json:surveyed_commit_drift")
    if EXPECTED_SURVEYED_COMMIT not in scorecard_doc:
        failures.append("scorecard_doc:missing_surveyed_commit")
    if EXPECTED_SURVEYED_COMMIT not in survey:
        failures.append("survey:missing_surveyed_commit")

    if scorecard_json.get("lane_key") != EXPECTED_SCORECARD_LANE:
        failures.append("scorecard_json:lane_key_drift")
    if scorecard_json.get("slice") != EXPECTED_SCORECARD_SLICE:
        failures.append("scorecard_json:slice_drift")

    posture = scorecard_json.get("posture", {})
    if posture.get("scorecard_role") != EXPECTED_POSTURE_ROLE:
        failures.append("scorecard_json:posture_role_drift")
    if posture.get("architecture_council_status_change_approval_recorded") is not False:
        failures.append("scorecard_json:approval_flag_drift")

    metrics = scorecard_json.get("metrics", {})
    for label, key, value in EXPECTED_METRICS:
        line = f"{label}: `{value}`"
        if metrics.get(key) != value:
            failures.append(f"scorecard_json:metric_drift:{key}")
        if line not in survey:
            failures.append(f"survey:missing_metric_line:{line}")

    anchor_paths = [anchor.get("path") for anchor in scorecard_json.get("anchors", [])]
    if anchor_paths != list(EXPECTED_ANCHORS):
        failures.append("scorecard_json:anchor_order_drift")
    for anchor in EXPECTED_ANCHORS:
        marker = f"`{anchor}`"
        if marker not in survey:
            failures.append(f"survey:missing_anchor:{marker}")
        if anchor not in scorecard_doc:
            failures.append(f"scorecard_doc:missing_anchor:{anchor}")

    for rel in (SCORECARD_DOC_PATH, SCORECARD_JSON_PATH, SCORECARD_ZIG_PATH):
        marker = f"`{rel}`"
        if marker not in survey:
            failures.append(f"survey:missing_packet_path:{marker}")

    if "`scripts/zigux/validate-phase15.py`" not in readiness:
        failures.append("readiness:missing_validator_marker")
    if "`zigux/tests/phase15_build.zig`" not in readiness:
        failures.append("readiness:missing_build_marker")
    if "`zigux/tests/phase15_build.zig`" not in sequencing:
        failures.append("sequencing:missing_build_marker")

    if _makefile_has_target(root, "phase15-validate"):
        failures.append("makefile:unexpected_phase15_validate_target")
    if _makefile_has_target(root, "phase15-test"):
        failures.append("makefile:unexpected_phase15_test_target")
    if _makefile_has_target(root, "phase15"):
        failures.append("makefile:unexpected_phase15_target")

    return failures


def _sample_survey() -> str:
    metric_lines = "\n".join(f"- {label}: `{value}`" for label, _key, value in EXPECTED_METRICS)
    anchor_lines = "\n".join(f"- `{anchor}`" for anchor in EXPECTED_ANCHORS)
    return f"""# Phase 15 Parity Scorecard Survey

## Status

- `PHASE15_LANE_KEY={EXPECTED_LANE_KEY}`
- `PHASE15_STATUS={EXPECTED_STATUS}`
- `PHASE15_SLICE={EXPECTED_SLICE}`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- survey rechecked against current `master` on 2026-05-25; the dedicated parity-scorecard packet now carries dated readback marker `{EXPECTED_SURVEYED_COMMIT}`

## Current master readback

The roadmap-required parity scorecard packet is still substantively present on current `master`.
the roadmap-required parity scorecard is landed as a note plus machine-readable JSON plus dedicated Zig guard
no Architecture Council approval is recorded for any freeze-map status change

- `{SCORECARD_DOC_PATH}`
- `{SCORECARD_JSON_PATH}`
- `{SCORECARD_ZIG_PATH}`

{metric_lines}

{anchor_lines}

The exact handoff reread now shows the dedicated parity-scorecard packet itself aligned on current `master`:
- `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig` are now present on current `master`
- the parked `make -C zigux phase15{{,-validate,-test}}` wrapper routes still remain broader repo-reality gaps
- the neighboring governance-lane-sequencing packet now needs its own separate truthfulness refresh if it is to stop treating the dedicated shared-build companion as missing

## Recorded gaps

- landed `phase15-validator-first-route-materialized`
- landed `phase15-shared-build-route-materialized`
"""


def _sample_scorecard_doc() -> str:
    anchors = "\n".join(f"- `{anchor}`" for anchor in EXPECTED_ANCHORS)
    return f"""# Phase 15 Parity Scorecard

- surveyed against dated current-master readback marker `{EXPECTED_SURVEYED_COMMIT}`
{anchors}
"""


def _sample_scorecard_json() -> str:
    payload = {
        "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
        "lane_key": EXPECTED_SCORECARD_LANE,
        "slice": EXPECTED_SCORECARD_SLICE,
        "posture": {
            "architecture_council_status_change_approval_recorded": False,
            "scorecard_role": EXPECTED_POSTURE_ROLE,
        },
        "metrics": {key: value for _label, key, value in EXPECTED_METRICS},
        "anchors": [{"path": anchor} for anchor in EXPECTED_ANCHORS],
    }
    return json.dumps(payload, indent=2) + "\n"


def _sample_readiness() -> str:
    return """# Phase 15 Readiness Gate Survey

- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
"""


def _sample_sequencing() -> str:
    return """# Phase 15 Governance Lane Sequencing

- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
"""


def _seed_repo(root: Path) -> None:
    _write(root / SURVEY_PATH, _sample_survey())
    _write(root / SCORECARD_DOC_PATH, _sample_scorecard_doc())
    _write(root / SCORECARD_JSON_PATH, _sample_scorecard_json())
    _write(root / SCORECARD_ZIG_PATH, 'const std = @import("std");\n\ntest "placeholder" {\n    try std.testing.expect(true);\n}\n')
    _write(root / READINESS_NOTE_PATH, _sample_readiness())
    _write(root / SEQUENCING_PATH, _sample_sequencing())
    _write(root / VALIDATOR_PATH, "#!/usr/bin/env python3\n")
    _write(root / BUILD_PATH, 'const std = @import("std");\n')
    _write(root / MAKEFILE_PATH, "phase14-validate:\n\t@true\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_parity_scorecard_survey_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_metric_root = root / "missing_metric"
        _seed_repo(missing_metric_root)
        _write(
            missing_metric_root / SURVEY_PATH,
            _sample_survey().replace("- Architecture Council approvals recorded for status change: `0`\n", "", 1),
        )
        failures = collect_failures(missing_metric_root)
        expected = ["survey:missing_metric_line:Architecture Council approvals recorded for status change: `0`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-metric failure: {failures}")
        case_count += 1

        stale_marker_root = root / "stale_marker"
        _seed_repo(stale_marker_root)
        _write(
            stale_marker_root / SURVEY_PATH,
            _sample_survey().replace(EXPECTED_SURVEYED_COMMIT, "current-master-readback-2026-05-21", 1),
        )
        failures = collect_failures(stale_marker_root)
        expected = [
            f"survey:missing_marker:survey rechecked against current `master` on 2026-05-25; the dedicated parity-scorecard packet now carries dated readback marker `{EXPECTED_SURVEYED_COMMIT}`",
            "survey:forbidden_marker:current-master-readback-2026-05-21",
            "survey:missing_surveyed_commit",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-marker failure: {failures}")
        case_count += 1

        anchor_drift_root = root / "anchor_drift"
        _seed_repo(anchor_drift_root)
        drifted = json.loads(_sample_scorecard_json())
        drifted["anchors"] = drifted["anchors"][:-1]
        _write(anchor_drift_root / SCORECARD_JSON_PATH, json.dumps(drifted, indent=2) + "\n")
        failures = collect_failures(anchor_drift_root)
        expected = ["scorecard_json:anchor_order_drift"]
        if failures != expected:
            raise AssertionError(f"unexpected anchor-drift failure: {failures}")
        case_count += 1

        missing_path_root = root / "missing_path"
        _seed_repo(missing_path_root)
        (missing_path_root / SCORECARD_ZIG_PATH).unlink()
        failures = collect_failures(missing_path_root)
        expected = [f"missing_required_path:{SCORECARD_ZIG_PATH}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-path failure: {failures}")
        case_count += 1

        target_root = root / "target_drift"
        _seed_repo(target_root)
        _write(target_root / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(target_root)
        expected = ["makefile:unexpected_phase15_validate_target"]
        if failures != expected:
            raise AssertionError(f"unexpected target-drift failure: {failures}")
        case_count += 1

    print("PHASE15_PARITY_SCORECARD_SURVEY_SELF_TEST=pass")
    print(f"PHASE15_PARITY_SCORECARD_SURVEY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 parity-scorecard survey stays aligned with the landed parity packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in synthetic self-test")
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

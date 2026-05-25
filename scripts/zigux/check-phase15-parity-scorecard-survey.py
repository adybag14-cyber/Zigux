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
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
BUILD_PATH = Path("zigux/tests/phase15_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

EXPECTED_SURVEY_REREAD_DATE = "2026-05-23"
EXPECTED_SCORECARD_COMMIT = "current-master-readback-2026-05-22"
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
DOC_METRIC_OVERRIDES = {
    "study-only anchors tracked outside the scorecard": "study-only anchors tracked outside this scorecard",
}
JSON_METRIC_KEYS = {
    "active freeze-in-C anchor count": "active_freeze_in_c_anchor_count",
    "blocked status-change anchor count": "blocked_status_change_anchor_count",
    "anchors blocked entirely within Phase 15 governance evidence": "phase15_governance_only_blocker_anchor_count",
    "Phase 14 coupled blocker anchor count": "phase14_coupled_blocker_anchor_count",
    "anchors still blocked on prior-phase bridge evidence": "anchors_still_blocked_on_prior_phase_bridge_evidence",
    "study-only anchors tracked outside the scorecard": "study_only_anchors_tracked_outside_scorecard",
    "Architecture Council approvals recorded for status change": "architecture_council_status_change_approval_count",
}
REQUIRED_SURVEY_MARKERS = (
    "PHASE15_LANE_KEY=P15-L09",
    "PHASE15_STATUS=parity_scorecard_survey_landed",
    "PHASE15_SLICE=parity-roadmap-readback-alignment",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "the dedicated parity-scorecard packet now carries dated readback marker `current-master-readback-2026-05-22`",
    "The roadmap-required parity scorecard packet is still substantively present on current `master`.",
    "The dedicated scorecard note and JSON still agree on the core packet shape:",
    "The exact handoff reread now shows the dedicated parity-scorecard packet itself aligned on current `master`:",
    "`Documentation/zigux/phase15-parity-scorecard.md` now records the validator-first reminder route as directly readable through `python3 scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_parity_scorecard.zig` now expects that same directly-readable validator wording inside the dedicated scorecard note",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md` now keeps only `zigux/tests/phase15_build.zig` in the broader dedicated-build gap bucket",
    "the live drift has moved out of the owner packet and into this stale survey note",
    "`scripts/zigux/validate-phase15.py` is now present on current `master`",
    "`zigux/tests/phase15_build.zig` and the parked `make -C zigux phase15{,-validate,-test}` wrapper routes still remain broader repo-reality gaps",
    "the current same-lane parity-tracking drift was the stale survey wording itself",
    "landed `phase15-validator-first-route-materialized`",
    "landed `phase15-parity-scorecard-reminder-route-wording-sync`",
    "blocked `phase15-shared-build-route-materialization`",
    "blocked `phase15-deep-core-status-change-blocker`",
)
FORBIDDEN_SURVEY_MARKERS = (
    "survey rechecked against current `master` on 2026-05-22;",
    "current-master-readback-2026-05-21",
    "the current same-lane drift has narrowed to reminder-route wording that still treats `scripts/zigux/validate-phase15.py` as missing",
    "the current same-lane parity-tracking drift is that the dedicated scorecard note and dedicated Zig guard still underreport the validator's arrival",
    "current direct-`master` readback still returned missing for `scripts/zigux/validate-phase15.py`",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(_read_text(path))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _metric_line(label: str, value: int) -> str:
    return f"{label}: `{value}`"


def _makefile_has_target(root: Path, target: str) -> bool:
    makefile_path = root / MAKEFILE_PATH
    if not makefile_path.exists():
        return False
    return f"\n{target}:" in ("\n" + _read_text(makefile_path))


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    required_paths = (
        SURVEY_PATH,
        SCORECARD_DOC_PATH,
        SCORECARD_JSON_PATH,
        SCORECARD_ZIG_PATH,
        SEQUENCING_PATH,
        VALIDATOR_PATH,
        MAKEFILE_PATH,
    )
    for rel in required_paths:
        if not (root / rel).exists():
            failures.append(f"repo:missing_required_path:{rel}")
    if failures:
        return failures

    if (root / BUILD_PATH).exists():
        failures.append(f"repo:unexpected_materialized_path:{BUILD_PATH}")
    for target in ("phase15-validate", "phase15-test", "phase15"):
        if _makefile_has_target(root, target):
            failures.append(f"makefile:unexpected_target:{target}")

    survey = _read_text(root / SURVEY_PATH)
    scorecard_doc = _read_text(root / SCORECARD_DOC_PATH)
    scorecard_json = _read_json(root / SCORECARD_JSON_PATH)
    scorecard_zig = _read_text(root / SCORECARD_ZIG_PATH)
    sequencing = _read_text(root / SEQUENCING_PATH)

    if f"survey rechecked against current `master` on {EXPECTED_SURVEY_REREAD_DATE};" not in survey:
        failures.append("survey:missing_reread_date")

    for marker in REQUIRED_SURVEY_MARKERS:
        if marker not in survey:
            failures.append(f"survey:missing_marker:{marker}")
    for marker in FORBIDDEN_SURVEY_MARKERS:
        if marker in survey:
            failures.append(f"survey:forbidden_marker_present:{marker}")

    if scorecard_json.get("surveyed_commit") != EXPECTED_SCORECARD_COMMIT:
        failures.append("scorecard_json:surveyed_commit_drift")
    if EXPECTED_SCORECARD_COMMIT not in scorecard_doc:
        failures.append("scorecard_doc:missing_surveyed_commit")
    if EXPECTED_SCORECARD_COMMIT not in scorecard_zig:
        failures.append("scorecard_zig:missing_surveyed_commit")
    if EXPECTED_SCORECARD_COMMIT not in survey:
        failures.append("survey:missing_scorecard_commit_marker")

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
        survey_line = _metric_line(label, value)
        if survey_line not in survey:
            failures.append(f"survey:missing_metric_line:{survey_line}")
        doc_label = DOC_METRIC_OVERRIDES.get(label, label)
        doc_line = _metric_line(doc_label, value)
        if doc_line not in scorecard_doc:
            failures.append(f"scorecard_doc:missing_metric_line:{doc_line}")

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
        if anchor not in scorecard_zig:
            failures.append(f"scorecard_zig:missing_anchor:{anchor}")

    for path_marker in (
        f"`{SCORECARD_DOC_PATH}`",
        f"`{SCORECARD_JSON_PATH}`",
        f"`{SCORECARD_ZIG_PATH}`",
        f"`{SURVEY_PATH}`",
    ):
        if path_marker not in survey:
            failures.append(f"survey:missing_packet_path:{path_marker}")

    if "`scripts/zigux/validate-phase15.py`" not in sequencing:
        failures.append("sequencing:missing_validate_phase15_path")
    if "`zigux/tests/phase15_build.zig`" not in sequencing:
        failures.append("sequencing:missing_phase15_build_path")
    if "validator-first reminder route is directly readable on current `master` through `python3 scripts/zigux/validate-phase15.py`" not in scorecard_doc:
        failures.append("scorecard_doc:missing_validator_present_route")
    if "shared replay build route remains a repo-reality gap on current `master` through `zigux/tests/phase15_build.zig` and `zig build test --build-file zigux/tests/phase15_build.zig`" not in scorecard_doc:
        failures.append("scorecard_doc:missing_build_gap_route")
    if "current `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15` targets" not in scorecard_doc:
        failures.append("scorecard_doc:missing_wrapper_gap_route")

    return failures


def _sample_survey() -> str:
    metric_lines = "\n".join(f"- {_metric_line(label, value)}" for label, value in EXPECTED_METRICS)
    anchor_lines = "\n".join(f"- `{anchor}`" for anchor in EXPECTED_ANCHORS)
    return f"""# Phase 15 Parity Scorecard Survey

## Status

- `PHASE15_LANE_KEY=P15-L09`
- `PHASE15_STATUS=parity_scorecard_survey_landed`
- `PHASE15_SLICE=parity-roadmap-readback-alignment`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- survey rechecked against current `master` on {EXPECTED_SURVEY_REREAD_DATE}; the dedicated parity-scorecard packet now carries dated readback marker `{EXPECTED_SCORECARD_COMMIT}`, and the remaining reminder-route gap is no longer inside the dedicated parity-scorecard packet itself

## Current master readback

The roadmap-required parity scorecard packet is still substantively present on current `master`.
The dedicated scorecard note and JSON still agree on the core packet shape:

- `{SCORECARD_DOC_PATH}`
- `{SCORECARD_JSON_PATH}`
- `{SCORECARD_ZIG_PATH}`
- `{SURVEY_PATH}`

{metric_lines}

{anchor_lines}

The exact handoff reread now shows the dedicated parity-scorecard packet itself aligned on current `master`:

- `Documentation/zigux/phase15-parity-scorecard.md` now records the validator-first reminder route as directly readable through `python3 scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_parity_scorecard.zig` now expects that same directly-readable validator wording inside the dedicated scorecard note
- `Documentation/zigux/phase15-governance-lane-sequencing.md` now keeps only `zigux/tests/phase15_build.zig` in the broader dedicated-build gap bucket

## Honest current posture

- `scripts/zigux/validate-phase15.py` is now present on current `master`
- `zigux/tests/phase15_build.zig` and the parked `make -C zigux phase15{{,-validate,-test}}` wrapper routes still remain broader repo-reality gaps
- the live drift has moved out of the owner packet and into this stale survey note
- the current same-lane parity-tracking drift was the stale survey wording itself

## Recorded gaps

- landed `phase15-validator-first-route-materialized`
- landed `phase15-parity-scorecard-reminder-route-wording-sync`
- blocked `phase15-shared-build-route-materialization`
- blocked `phase15-deep-core-status-change-blocker`
"""


def _sample_scorecard_doc() -> str:
    metric_lines = "\n".join(
        f"- {_metric_line(DOC_METRIC_OVERRIDES.get(label, label), value)}"
        for label, value in EXPECTED_METRICS
    )
    anchor_lines = "\n".join(f"- `{anchor}`" for anchor in EXPECTED_ANCHORS)
    return f"""# Phase 15 Parity Scorecard

- surveyed against dated current-master readback marker `{EXPECTED_SCORECARD_COMMIT}`
- validator-first reminder route is directly readable on current `master` through `python3 scripts/zigux/validate-phase15.py`
- shared replay build route remains a repo-reality gap on current `master` through `zigux/tests/phase15_build.zig` and `zig build test --build-file zigux/tests/phase15_build.zig`
- current `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15` targets
{metric_lines}
{anchor_lines}
"""


def _sample_scorecard_json() -> str:
    return json.dumps(
        {
            "surveyed_commit": EXPECTED_SCORECARD_COMMIT,
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


def _sample_scorecard_zig() -> str:
    return f"""test \"phase15 parity scorecard\" {{
    _ = \"{EXPECTED_SCORECARD_COMMIT}\";
    _ = \"validator-first reminder route is directly readable on current `master` through `python3 scripts/zigux/validate-phase15.py`\";
    _ = \"shared replay build route remains a repo-reality gap on current `master` through `zigux/tests/phase15_build.zig` and `zig build test --build-file zigux/tests/phase15_build.zig`\";
    _ = \"current `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15` targets\";
    _ = \"{EXPECTED_ANCHORS[0]}\";
    _ = \"{EXPECTED_ANCHORS[1]}\";
    _ = \"{EXPECTED_ANCHORS[2]}\";
    _ = \"{EXPECTED_ANCHORS[3]}\";
}}
"""


def _sample_sequencing() -> str:
    return """# Phase 15 Governance Lane Sequencing

- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
"""


def _sample_makefile() -> str:
    return """phase12-validate:
	@true
"""


def _seed_repo(root: Path) -> None:
    _write(root / SURVEY_PATH, _sample_survey())
    _write(root / SCORECARD_DOC_PATH, _sample_scorecard_doc())
    _write(root / SCORECARD_JSON_PATH, _sample_scorecard_json())
    _write(root / SCORECARD_ZIG_PATH, _sample_scorecard_zig())
    _write(root / SEQUENCING_PATH, _sample_sequencing())
    _write(root / VALIDATOR_PATH, "#!/usr/bin/env python3\n")
    _write(root / MAKEFILE_PATH, _sample_makefile())


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_parity_scorecard_survey_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_marker_root = root / "missing_marker"
        _seed_repo(missing_marker_root)
        _write(
            missing_marker_root / SURVEY_PATH,
            _sample_survey().replace("the live drift has moved out of the owner packet and into this stale survey note\n", "", 1),
        )
        failures = collect_failures(missing_marker_root)
        expected = ["survey:missing_marker:the live drift has moved out of the owner packet and into this stale survey note"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")

        stale_root = root / "stale_marker"
        _seed_repo(stale_root)
        _write(
            stale_root / SURVEY_PATH,
            _sample_survey().replace(
                f"survey rechecked against current `master` on {EXPECTED_SURVEY_REREAD_DATE};",
                "survey rechecked against current `master` on 2026-05-22;",
                1,
            ).replace(
                "the live drift has moved out of the owner packet and into this stale survey note",
                "the current same-lane drift has narrowed to reminder-route wording that still treats `scripts/zigux/validate-phase15.py` as missing",
                1,
            ),
        )
        failures = collect_failures(stale_root)
        expected = [
            "survey:missing_reread_date",
            "survey:missing_marker:the live drift has moved out of the owner packet and into this stale survey note",
            "survey:forbidden_marker_present:survey rechecked against current `master` on 2026-05-22;",
            "survey:forbidden_marker_present:the current same-lane drift has narrowed to reminder-route wording that still treats `scripts/zigux/validate-phase15.py` as missing",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-marker failure: {failures}")

        build_root = root / "build_materialized"
        _seed_repo(build_root)
        _write(build_root / BUILD_PATH, 'const std = @import("std");\n')
        failures = collect_failures(build_root)
        expected = [f"repo:unexpected_materialized_path:{BUILD_PATH}"]
        if failures != expected:
            raise AssertionError(f"unexpected build-path failure: {failures}")

        target_root = root / "make_target"
        _seed_repo(target_root)
        _write(target_root / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(target_root)
        expected = ["makefile:unexpected_target:phase15-validate"]
        if failures != expected:
            raise AssertionError(f"unexpected make-target failure: {failures}")

        json_root = root / "json_drift"
        _seed_repo(json_root)
        drifted = json.loads(_sample_scorecard_json())
        drifted["surveyed_commit"] = "current-master-readback-2026-05-21"
        _write(json_root / SCORECARD_JSON_PATH, json.dumps(drifted, indent=2) + "\n")
        failures = collect_failures(json_root)
        expected = ["scorecard_json:surveyed_commit_drift"]
        if failures != expected:
            raise AssertionError(f"unexpected json-drift failure: {failures}")

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
    print("PHASE15_PARITY_SCORECARD_SURVEY_REQUIRED_PATH_COUNT=7")
    print(f"PHASE15_PARITY_SCORECARD_SURVEY_ANCHOR_COUNT={len(EXPECTED_ANCHORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

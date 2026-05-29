#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

READINESS_NOTE = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
GAP_MATRIX = Path("zigux/tests/phase15_readiness_gap_matrix.json")
VALIDATOR = Path("scripts/zigux/validate-phase15.py")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")

BLOCKED_MAKE_TARGETS = ("phase15-validate", "phase15-test", "phase15")
EXPECTED_GAPS = {
    "missing_make_routes",
    "missing_workflow_route",
    "no_architecture_council_status_change_approval",
}

NOTE_MARKERS = (
    "PHASE15_STATUS=readiness_gate_survey_landed",
    "PHASE15_LANE_KEY=P15-L04",
    "broader route and workflow companions still remain blocked on current `master`",
    "`make -C zigux phase15-validate` remains blocked route vocabulary",
    "`make -C zigux phase15-test` remains blocked route vocabulary",
    "`make -C zigux phase15` remains blocked route vocabulary",
    "shared CI coverage for the broader Phase 15 replay packet remains absent",
)

VALIDATOR_MARKERS = (
    '"missing_make_targets": ["phase15-validate", "phase15-test", "phase15"]',
    '"missing_workflow_phase15_route": True',
    '"phase15_validate_target_present": False',
    '"phase15_test_target_present": False',
    '"phase15_aggregate_target_present": False',
    '"shared_ci_phase15_present": False',
)


def read_text(root: Path, rel_path: Path) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def has_make_target(makefile_text: str, target: str) -> bool:
    prefix = f"{target}:"
    return any(line.strip().startswith(prefix) for line in makefile_text.splitlines())


def workflow_has_dedicated_phase15_route(workflow_text: str) -> bool:
    route_markers = (
        "make -C zigux phase15-validate",
        "make -C zigux phase15-test",
        "make -C zigux phase15",
        "scripts/zigux/validate-phase15.py",
    )
    return any(marker in workflow_text for marker in route_markers)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in (READINESS_NOTE, GAP_MATRIX, VALIDATOR, MAKEFILE, WORKFLOW):
        if not (root / rel_path).is_file():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    note_text = read_text(root, READINESS_NOTE)
    for marker in NOTE_MARKERS:
        if marker not in note_text:
            failures.append(f"missing_readiness_marker:{marker}")

    validator_text = read_text(root, VALIDATOR)
    compact_validator = " ".join(validator_text.split())
    for marker in VALIDATOR_MARKERS:
        if marker not in compact_validator:
            failures.append(f"missing_validator_marker:{marker}")

    try:
        gap_matrix = json.loads(read_text(root, GAP_MATRIX))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid_gap_matrix_json:{exc.msg}")
        gap_matrix = {}

    remaining_gaps = gap_matrix.get("remaining_readiness_gaps", [])
    if not isinstance(remaining_gaps, list):
        failures.append("gap_matrix_remaining_readiness_gaps:not_list")
        remaining_gaps = []
    gaps_by_name = {
        item.get("gap"): item for item in remaining_gaps if isinstance(item, dict)
    }
    for gap in sorted(EXPECTED_GAPS):
        item = gaps_by_name.get(gap)
        if item is None:
            failures.append(f"missing_gap_matrix_gap:{gap}")
        elif item.get("status") != "blocked":
            failures.append(f"gap_matrix_gap_not_blocked:{gap}:{item.get('status')!r}")

    make_gap = gaps_by_name.get("missing_make_routes", {})
    if isinstance(make_gap, dict):
        blocked_routes = make_gap.get("blocked_routes")
        if blocked_routes != list(BLOCKED_MAKE_TARGETS):
            failures.append(f"gap_matrix_blocked_routes:{blocked_routes!r}")

    makefile_text = read_text(root, MAKEFILE)
    for target in BLOCKED_MAKE_TARGETS:
        if has_make_target(makefile_text, target):
            failures.append(f"unexpected_make_target:{target}")

    workflow_text = read_text(root, WORKFLOW)
    if workflow_has_dedicated_phase15_route(workflow_text):
        failures.append("unexpected_workflow_phase15_route")

    return failures


def write_text(root: Path, rel_path: Path, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sample_gap_matrix(status: str = "blocked") -> str:
    payload = {
        "remaining_readiness_gaps": [
            {
                "gap": "missing_make_routes",
                "status": status,
                "path": "zigux/Makefile",
                "blocked_routes": list(BLOCKED_MAKE_TARGETS),
            },
            {
                "gap": "missing_workflow_route",
                "status": "blocked",
                "path": ".github/workflows/zigux-bootstrap.yml",
            },
            {
                "gap": "no_architecture_council_status_change_approval",
                "status": "blocked",
            },
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def write_fixture(root: Path) -> None:
    write_text(root, READINESS_NOTE, "\n".join(NOTE_MARKERS) + "\n")
    write_text(root, GAP_MATRIX, sample_gap_matrix())
    write_text(root, MAKEFILE, "phase14-validate:\n\t@true\n")
    write_text(root, WORKFLOW, "name: zigux-bootstrap\n")
    write_text(root, VALIDATOR, "\n".join(VALIDATOR_MARKERS) + "\n")


def expect_failure(root: Path, expected: str) -> None:
    failures = collect_failures(root)
    if expected not in failures:
        raise AssertionError(f"expected {expected!r}, got {failures!r}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_blocked_route_recovery_") as tmp:
        base = Path(tmp)

        baseline = base / "baseline"
        write_fixture(baseline)
        failures = collect_failures(baseline)
        if failures:
            raise AssertionError(f"baseline should pass: {failures!r}")

        stale_note = base / "stale-note"
        write_fixture(stale_note)
        note = read_text(stale_note, READINESS_NOTE).replace(NOTE_MARKERS[2], "", 1)
        write_text(stale_note, READINESS_NOTE, note)
        expect_failure(stale_note, f"missing_readiness_marker:{NOTE_MARKERS[2]}")

        recovered_make = base / "recovered-make"
        write_fixture(recovered_make)
        write_text(recovered_make, MAKEFILE, "phase15-validate:\n\t@true\n")
        expect_failure(recovered_make, "unexpected_make_target:phase15-validate")

        recovered_workflow = base / "recovered-workflow"
        write_fixture(recovered_workflow)
        write_text(recovered_workflow, WORKFLOW, "run: make -C zigux phase15-validate\n")
        expect_failure(recovered_workflow, "unexpected_workflow_phase15_route")

        stale_gap = base / "stale-gap"
        write_fixture(stale_gap)
        write_text(stale_gap, GAP_MATRIX, sample_gap_matrix(status="landed"))
        expect_failure(stale_gap, "gap_matrix_gap_not_blocked:missing_make_routes:'landed'")

        stale_validator = base / "stale-validator"
        write_fixture(stale_validator)
        validator = read_text(stale_validator, VALIDATOR).replace(VALIDATOR_MARKERS[1], "", 1)
        write_text(stale_validator, VALIDATOR, validator)
        expect_failure(stale_validator, f"missing_validator_marker:{VALIDATOR_MARKERS[1]}")

    print("PHASE15_BLOCKED_ROUTE_RECOVERY_SELF_TEST=pass")
    print("PHASE15_BLOCKED_ROUTE_RECOVERY_SELF_TEST_CASES=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Phase 15 blocked route recovery evidence stays synchronized."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run synthetic checker tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        print("PHASE15_BLOCKED_ROUTE_RECOVERY=fail")
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_BLOCKED_ROUTE_RECOVERY=pass")
    print(f"PHASE15_BLOCKED_ROUTE_RECOVERY_MAKE_TARGET_COUNT={len(BLOCKED_MAKE_TARGETS)}")
    print(f"PHASE15_BLOCKED_ROUTE_RECOVERY_GAP_COUNT={len(EXPECTED_GAPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

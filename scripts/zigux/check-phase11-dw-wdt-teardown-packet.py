#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

REQUIRED_FILES = {
    "alignment_note": Path("Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md"),
    "gap_note": Path("Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md"),
    "clock_plan": Path("Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md"),
    "platform_plan": Path("Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md"),
    "provenance": Path("Documentation/zigux/phase11-dw-wdt-provenance-readback.md"),
    "validation_matrix": Path("Documentation/zigux/phase11-dw-wdt-validation-matrix.md"),
    "survey": Path("Documentation/zigux/phase11-dw-wdt-survey.md"),
    "manifest": Path("zigux/tests/phase11_dw_wdt_manifest.json"),
    "registration_scaffold": Path("zigux/tests/phase11_dw_wdt_registration_scaffold.zig"),
    "restart": Path("drivers/watchdog/dw_wdt_restart.zig"),
    "verify": Path("drivers/watchdog/dw_wdt_verify.zig"),
    "pm": Path("drivers/watchdog/dw_wdt_pm.zig"),
    "pm_scaffold": Path("drivers/watchdog/dw_wdt_pm_scaffold.zig"),
}

ALIGNMENT_NOTE_MARKERS = [
    "# Phase 11 DesignWare Verify Alignment Gap",
    "- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` now records that the direct driver-and-test pair has returned on the authenticated contents bridge while the slice note, teardown note, and older packet checker still remain outside the same narrower packet",
]

GAP_NOTE_MARKERS = [
    "current authenticated contents rereads keep `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`",
    "`drivers/watchdog/dw_wdt.zig`",
    "`zigux/tests/phase11_dw_wdt.zig`",
    "still do not rematerialize `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, or the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle",
]

CLOCK_PLAN_MARKERS = [
    "current direct contents rereads now materialize `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`",
    "`drivers/watchdog/dw_wdt.zig`",
    "`zigux/tests/phase11_dw_wdt.zig`",
    "keep the returned validation matrix, survey note, survey gate, registration scaffold, direct driver-and-test pair, restart helper, returned verify helper, bounded PM helper pair, and paired DesignWare checkers explicit while the slice-note, teardown-note, and older packet-checker reminder stack stays outside this direct contents bridge",
]

PLATFORM_PLAN_MARKERS = [
    "Current authenticated contents rereads on `master` now keep this owner note,",
    "`drivers/watchdog/dw_wdt.zig`,",
    "`zigux/tests/phase11_dw_wdt.zig`,",
    "The live DesignWare packet is therefore no longer just a docs-only owner stack, and it is no longer missing the direct driver or direct replay.",
]

PROVENANCE_MARKERS = [
    "# Phase 11 DesignWare Watchdog Provenance Readback",
    "current authenticated contents reads now materialize `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
    "`drivers/watchdog/dw_wdt.zig`",
    "`zigux/tests/phase11_dw_wdt.zig`",
    "still do not rematerialize `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, or the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle",
    "now records `dw_wdt_zig_present` and `dw_wdt_test_present` as true",
]

VALIDATION_MATRIX_MARKERS = [
    "# Phase 11 DesignWare Watchdog Validation Matrix",
    "`drivers/watchdog/dw_wdt.zig` and `zigux/tests/phase11_dw_wdt.zig` now rematerialize on current `master`",
    "`zigux/tests/phase11_build.zig` is still a shared current-head gap rather than live lane evidence here.",
]

SURVEY_MARKERS = [
    "# Phase 11 DesignWare Watchdog Survey",
    "`drivers/watchdog/dw_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`,",
    "Those same authenticated contents rereads still do not rematerialize",
]

REGISTRATION_SCAFFOLD_MARKERS = [
    'test "platform registration scaffold summary keeps imported-running resetless registration explicit" {',
    'test "platform registration scaffold summary keeps optional reset-control absence explicit" {',
]

RESTART_MARKERS = [
    'test "phase11 dw_wdt restart summary keeps missing drvdata explicit" {',
    'test "phase11 dw_wdt restart summary keeps restart register writes explicit" {',
]

VERIFY_MARKERS = [
    'test "dw_wdt verify keeps restart blockers and register-write readiness aligned" {',
    'test "dw_wdt verify keeps PM helper ordering and blocker branches explicit" {',
]

PM_MARKERS = [
    'test "phase11 dw_wdt pm suspend keeps missing drvdata explicit" {',
    'test "phase11 dw_wdt pm resume keeps imported-running handoff explicit" {',
    'test "phase11 dw_wdt pm shutdown keeps running pretimeout mask explicit" {',
]

PM_SCAFFOLD_MARKERS = [
    'test "phase11 dw_wdt pm scaffold keeps idle suspend and resume explicit" {',
    'test "phase11 dw_wdt pm scaffold keeps live-mmio blocker explicit for running hardware" {',
]

EXPECTED_MANIFEST_LANE = "P11-L10"
EXPECTED_MANIFEST_PIN = "75f8336c4305beed127d7abfae37d3999b7cc57c"
VERIFY_GAP_ID = "phase11-dw-wdt-teardown-parity"
VERIFY_DESTINATION = "drivers/watchdog/dw_wdt_verify.zig"
RESTART_GAP_ID = "phase11-dw-wdt-restart-summary"
RESTART_DESTINATION = "drivers/watchdog/dw_wdt_restart.zig"
PM_GAP_ID = "phase11-dw-wdt-live-platform-pm"
PM_DESTINATION = "drivers/watchdog/dw_wdt_pm.zig"
NEXT_GAP_ID = "phase11-dw-wdt-live-mmio-validation"
NEXT_DESTINATION = "zigux/tests/phase11_dw_wdt.zig"

MARKERS_BY_LABEL = {
    "alignment_note": ALIGNMENT_NOTE_MARKERS,
    "gap_note": GAP_NOTE_MARKERS,
    "clock_plan": CLOCK_PLAN_MARKERS,
    "platform_plan": PLATFORM_PLAN_MARKERS,
    "provenance": PROVENANCE_MARKERS,
    "validation_matrix": VALIDATION_MATRIX_MARKERS,
    "survey": SURVEY_MARKERS,
    "registration_scaffold": REGISTRATION_SCAFFOLD_MARKERS,
    "restart": RESTART_MARKERS,
    "verify": VERIFY_MARKERS,
    "pm": PM_MARKERS,
    "pm_scaffold": PM_SCAFFOLD_MARKERS,
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_manifest(root: Path) -> list[str]:
    failures: list[str] = []
    manifest_path = root / REQUIRED_FILES["manifest"]
    if not manifest_path.is_file():
        return [f"missing_file:{REQUIRED_FILES['manifest'].as_posix()}"]

    try:
        manifest = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        return [f"invalid_json:{manifest_path.as_posix()}:{exc}"]

    if manifest.get("lane_key") != EXPECTED_MANIFEST_LANE:
        failures.append(f"manifest_lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("surveyed_commit") != EXPECTED_MANIFEST_PIN:
        failures.append(f"manifest_surveyed_commit:{manifest.get('surveyed_commit')!r}")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        failures.append("manifest_survey_summary:missing_or_not_object")
    else:
        expected_flags = {
            "dw_wdt_zig_present": True,
            "dw_wdt_test_present": True,
            "dw_wdt_registration_scaffold_present": True,
            "dw_wdt_registration_order_present": True,
            "dw_wdt_slice_note_present": False,
            "dw_wdt_survey_gate_present": True,
            "dw_wdt_survey_note_present": True,
            "dw_wdt_pm_helper_present": True,
            "dw_wdt_restart_helper_present": True,
            "dw_wdt_verify_helper_present": True,
        }
        for flag, expected in expected_flags.items():
            if summary.get(flag) is not expected:
                failures.append(f"manifest_flag:{flag}:{summary.get(flag)!r}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        failures.append("manifest_gaps:missing_or_not_list")
        return failures

    gap_map = {gap.get("id"): gap for gap in gaps if isinstance(gap, dict)}
    restart_gap = gap_map.get(RESTART_GAP_ID)
    if not restart_gap or restart_gap.get("zigux_destination") != RESTART_DESTINATION or restart_gap.get("status") != "starter_landed":
        failures.append("manifest_restart_gap:mismatch")
    verify_gap = gap_map.get(VERIFY_GAP_ID)
    if not verify_gap or verify_gap.get("zigux_destination") != VERIFY_DESTINATION or verify_gap.get("status") != "starter_landed":
        failures.append("manifest_verify_gap:mismatch")
    pm_gap = gap_map.get(PM_GAP_ID)
    if not pm_gap or pm_gap.get("zigux_destination") != PM_DESTINATION or pm_gap.get("status") != "starter_landed":
        failures.append("manifest_pm_gap:mismatch")
    next_gap = gap_map.get(NEXT_GAP_ID)
    if not next_gap or next_gap.get("zigux_destination") != NEXT_DESTINATION or next_gap.get("status") != "ready_next":
        failures.append("manifest_next_gap:mismatch")

    return failures


def check_repo(root: Path) -> list[str]:
    failures: list[str] = []
    for label, rel_path in REQUIRED_FILES.items():
        if label == "manifest":
            continue
        path = root / rel_path
        if not path.is_file():
            failures.append(f"missing_file:{rel_path.as_posix()}")
            continue
        text = read_text(path)
        for marker in MARKERS_BY_LABEL[label]:
            if marker not in text:
                failures.append(f"missing_marker:{label}:{marker}")
    failures.extend(check_manifest(root))
    return failures


def seed_fixture(root: Path) -> None:
    for rel_path in REQUIRED_FILES.values():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

    for label, markers in MARKERS_BY_LABEL.items():
        (root / REQUIRED_FILES[label]).write_text("\n".join(markers) + "\n", encoding="utf-8")

    manifest = {
        "lane_key": EXPECTED_MANIFEST_LANE,
        "surveyed_commit": EXPECTED_MANIFEST_PIN,
        "survey_summary": {
            "dw_wdt_zig_present": True,
            "dw_wdt_test_present": True,
            "dw_wdt_registration_scaffold_present": True,
            "dw_wdt_registration_order_present": True,
            "dw_wdt_slice_note_present": False,
            "dw_wdt_survey_gate_present": True,
            "dw_wdt_survey_note_present": True,
            "dw_wdt_pm_helper_present": True,
            "dw_wdt_restart_helper_present": True,
            "dw_wdt_verify_helper_present": True,
        },
        "gaps": [
            {"id": VERIFY_GAP_ID, "status": "starter_landed", "zigux_destination": VERIFY_DESTINATION},
            {"id": RESTART_GAP_ID, "status": "starter_landed", "zigux_destination": RESTART_DESTINATION},
            {"id": PM_GAP_ID, "status": "starter_landed", "zigux_destination": PM_DESTINATION},
            {"id": NEXT_GAP_ID, "status": "ready_next", "zigux_destination": NEXT_DESTINATION},
        ],
    }
    (root / REQUIRED_FILES["manifest"]).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def expect_failure(root: Path, expected: str) -> None:
    failures = check_repo(root)
    if expected not in failures:
        raise SystemExit(f"expected {expected!r}, got {failures}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase11-dw-wdt-teardown-") as tmpdir:
        root = Path(tmpdir)
        fixture = root / "fixture"
        seed_fixture(fixture)

        baseline = check_repo(fixture)
        if baseline:
            raise SystemExit("baseline self-test fixture failed: " + ", ".join(baseline))

        case_count = 1

        marker_cases = [
            ("alignment_note", ALIGNMENT_NOTE_MARKERS[1]),
            ("gap_note", GAP_NOTE_MARKERS[3]),
            ("platform_plan", PLATFORM_PLAN_MARKERS[3]),
            ("provenance", PROVENANCE_MARKERS[5]),
            ("validation_matrix", VALIDATION_MATRIX_MARKERS[1]),
            ("survey", SURVEY_MARKERS[1]),
            ("registration_scaffold", REGISTRATION_SCAFFOLD_MARKERS[1]),
            ("restart", RESTART_MARKERS[1]),
            ("verify", VERIFY_MARKERS[1]),
            ("pm", PM_MARKERS[1]),
            ("pm_scaffold", PM_SCAFFOLD_MARKERS[1]),
        ]
        for index, (label, marker) in enumerate(marker_cases, start=1):
            case_root = root / f"marker_case_{index}"
            shutil.copytree(fixture, case_root)
            target = case_root / REQUIRED_FILES[label]
            target.write_text(read_text(target).replace(marker, "", 1), encoding="utf-8")
            expect_failure(case_root, f"missing_marker:{label}:{marker}")
            case_count += 1

        manifest_flag_case = root / "manifest_flag_case"
        shutil.copytree(fixture, manifest_flag_case)
        manifest_path = manifest_flag_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["survey_summary"]["dw_wdt_zig_present"] = False
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_flag_case, "manifest_flag:dw_wdt_zig_present:False")
        case_count += 1

        print("PHASE11_DW_WDT_TEARDOWN_PACKET_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_TEARDOWN_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fail-close the current returned Phase 11 DesignWare watchdog teardown packet.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    failures = check_repo(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE11_DW_WDT_TEARDOWN_PACKET=pass")
    print(f"PHASE11_DW_WDT_TEARDOWN_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    print("PHASE11_DW_WDT_TEARDOWN_PACKET_MARKER_COUNT=" f"{sum(len(markers) for markers in MARKERS_BY_LABEL.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
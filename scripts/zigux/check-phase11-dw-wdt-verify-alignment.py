#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 DesignWare verify-alignment packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

FILES = {
    "note": "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
    "matrix": "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "platform_plan": "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "manifest": "zigux/tests/phase11_dw_wdt_manifest.json",
    "verify": "drivers/watchdog/dw_wdt_verify.zig",
    "pm": "drivers/watchdog/dw_wdt_pm.zig",
}

EXPECTED_MANIFEST_LANE = "P11-L10"
EXPECTED_MANIFEST_PIN = "75f8336c4305beed127d7abfae37d3999b7cc57c"
VERIFY_DESTINATION = "drivers/watchdog/dw_wdt_verify.zig"
VERIFY_GAP_ID = "phase11-dw-wdt-teardown-parity"
VERIFY_STATUS = "starter_landed"
PM_DESTINATION = "drivers/watchdog/dw_wdt_pm.zig"
PM_GAP_ID = "phase11-dw-wdt-live-platform-pm"
NEXT_DESTINATION = "zigux/tests/phase11_dw_wdt.zig"
NEXT_GAP_ID = "phase11-dw-wdt-live-mmio-validation"

NOTE_MARKERS = [
    "# Phase 11 DesignWare Verify Alignment Gap",
    "- current authenticated contents now keep the returned validation matrix directly readable through the same bridge that serves the rest of this narrower packet",
    "- the directly checkable current-head packet in this environment is `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/watchdog/dw_wdt_pm.zig`, and this companion note",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` now records deeper platform-registration scaffold continuity `P11-L10` at surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`",
    "- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` now records that the direct driver-and-test pair has returned on the authenticated contents bridge while the slice note, teardown note, and older packet checker still remain outside the same narrower packet",
    "- `drivers/watchdog/dw_wdt_pm.zig` still keeps bounded suspend, resume, and shutdown handoff summaries explicit across missing-drvdata blocks, idle suspend without teardown hooks, running-hardware suspend stop intent, missing suspend hook teardown during running stop, imported-running resume recovery, timeout-reprogram blocks, running shutdown stop intent, pretimeout-mask teardown, and idle shutdown cleanup while still keeping live PM execution out of scope",
]

MATRIX_MARKERS = [
    "- `PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`",
    "- current surveyed packet pin: `75f8336c4305beed127d7abfae37d3999b7cc57c`",
    "- `drivers/watchdog/dw_wdt.zig` and `zigux/tests/phase11_dw_wdt.zig` now rematerialize on current `master`",
    "- The next bounded same-lane follow-up remains the manifest-marked ready-next step: hardware-backed MMIO validation around suspend, resume, and platform-backed probe or remove execution, without widening into unrelated driver behavior.",
]

PLATFORM_PLAN_MARKERS = [
    "Current authenticated contents rereads on `master` now keep this owner note,",
    "`drivers/watchdog/dw_wdt.zig`,",
    "`zigux/tests/phase11_dw_wdt.zig`,",
    "The live DesignWare packet is therefore no longer just a docs-only owner stack, and it is no longer missing the direct driver or direct replay.",
    "- the returned direct driver-and-test pair in `drivers/watchdog/dw_wdt.zig` and `zigux/tests/phase11_dw_wdt.zig`",
]

VERIFY_MARKERS = [
    'const dw_wdt_pm = @import("dw_wdt_pm.zig");',
    'const dw_wdt_restart = @import("dw_wdt_restart.zig");',
    'test "dw_wdt verify keeps restart blockers and register-write readiness aligned" {',
    'test "dw_wdt verify keeps PM helper ordering and blocker branches explicit" {',
    'test "dw_wdt verify keeps PM scaffold dispositions aligned with the stronger helper packet" {',
]

PM_MARKERS = [
    'pub const anchor_path = "drivers/watchdog/dw_wdt.c";',
    'test "phase11 dw_wdt pm suspend keeps missing drvdata explicit" {',
    'test "phase11 dw_wdt pm resume keeps imported-running handoff explicit" {',
    'test "phase11 dw_wdt pm shutdown keeps running pretimeout mask explicit" {',
]

class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {label}: {marker}")


def read_manifest(root: Path) -> dict[str, object]:
    try:
        value = json.loads(read_text(root, FILES["manifest"]))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {FILES['manifest']}: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckError("manifest root must be an object")
    return value


def expect_manifest_state(manifest: dict[str, object]) -> None:
    if manifest.get("lane_key") != EXPECTED_MANIFEST_LANE:
        raise CheckError("manifest lane_key mismatch")
    if manifest.get("surveyed_commit") != EXPECTED_MANIFEST_PIN:
        raise CheckError("manifest surveyed_commit mismatch")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        raise CheckError("manifest survey_summary must be an object")
    if summary.get("dw_wdt_zig_present") is not True:
        raise CheckError("manifest dw_wdt_zig_present mismatch")
    if summary.get("dw_wdt_test_present") is not True:
        raise CheckError("manifest dw_wdt_test_present mismatch")
    if summary.get("dw_wdt_pm_helper_present") is not True:
        raise CheckError("manifest dw_wdt_pm_helper_present mismatch")
    if summary.get("dw_wdt_verify_helper_present") is not True:
        raise CheckError("manifest dw_wdt_verify_helper_present mismatch")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        raise CheckError("manifest gaps must be a list")

    gap_map = {entry.get("id"): entry for entry in gaps if isinstance(entry, dict)}
    verify_gap = gap_map.get(VERIFY_GAP_ID)
    if not verify_gap or verify_gap.get("zigux_destination") != VERIFY_DESTINATION or verify_gap.get("status") != VERIFY_STATUS:
        raise CheckError("manifest verify gap mismatch")
    pm_gap = gap_map.get(PM_GAP_ID)
    if not pm_gap or pm_gap.get("zigux_destination") != PM_DESTINATION or pm_gap.get("status") != "starter_landed":
        raise CheckError("manifest pm gap mismatch")
    next_gap = gap_map.get(NEXT_GAP_ID)
    if not next_gap or next_gap.get("zigux_destination") != NEXT_DESTINATION or next_gap.get("status") != "ready_next":
        raise CheckError("manifest next gap mismatch")


def run_check(root: Path) -> None:
    expect_markers("note", read_text(root, FILES["note"]), NOTE_MARKERS)
    expect_markers("matrix", read_text(root, FILES["matrix"]), MATRIX_MARKERS)
    expect_markers("platform_plan", read_text(root, FILES["platform_plan"]), PLATFORM_PLAN_MARKERS)
    expect_markers("verify", read_text(root, FILES["verify"]), VERIFY_MARKERS)
    expect_markers("pm", read_text(root, FILES["pm"]), PM_MARKERS)
    expect_manifest_state(read_manifest(root))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / FILES["note"], "\n".join(NOTE_MARKERS) + "\n")
    write(root / FILES["matrix"], "\n".join(MATRIX_MARKERS) + "\n")
    write(root / FILES["platform_plan"], "\n".join(PLATFORM_PLAN_MARKERS) + "\n")
    write(root / FILES["verify"], "\n".join(VERIFY_MARKERS) + "\n")
    write(root / FILES["pm"], "\n".join(PM_MARKERS) + "\n")
    write(
        root / FILES["manifest"],
        json.dumps(
            {
                "lane_key": EXPECTED_MANIFEST_LANE,
                "surveyed_commit": EXPECTED_MANIFEST_PIN,
                "survey_summary": {
                    "dw_wdt_zig_present": True,
                    "dw_wdt_test_present": True,
                    "dw_wdt_pm_helper_present": True,
                    "dw_wdt_verify_helper_present": True,
                },
                "gaps": [
                    {"id": VERIFY_GAP_ID, "status": VERIFY_STATUS, "zigux_destination": VERIFY_DESTINATION},
                    {"id": PM_GAP_ID, "status": "starter_landed", "zigux_destination": PM_DESTINATION},
                    {"id": NEXT_GAP_ID, "status": "ready_next", "zigux_destination": NEXT_DESTINATION},
                ],
            },
            indent=2,
        ) + "\n",
    )


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected self-test failure containing {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase11-dw-wdt-verify-alignment-") as tmpdir:
        root = Path(tmpdir)
        fixture = root / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        bad_lane = root / "bad-lane"
        shutil.copytree(fixture, bad_lane)
        manifest_path = bad_lane / FILES["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["lane_key"] = "P11-L05"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(bad_lane, "manifest lane_key mismatch")
        case_count += 1

        bad_driver_flag = root / "bad-driver-flag"
        shutil.copytree(fixture, bad_driver_flag)
        manifest_path = bad_driver_flag / FILES["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_summary"]["dw_wdt_zig_present"] = False
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(bad_driver_flag, "manifest dw_wdt_zig_present mismatch")
        case_count += 1

        missing_marker = root / "missing-marker"
        shutil.copytree(fixture, missing_marker)
        note_path = missing_marker / FILES["note"]
        note_path.write_text("# Phase 11 DesignWare Verify Alignment Gap\n", encoding="utf-8")
        expect_failure(missing_marker, "missing marker in note")
        case_count += 1

        print("PHASE11_DW_WDT_VERIFY_ALIGNMENT_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_VERIFY_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            run_self_test()
        else:
            run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_DW_WDT_VERIFY_ALIGNMENT=fail: {exc}")
        return 1
    except AssertionError as exc:
        print(str(exc))
        return 1

    if not args.self_test:
        print("PHASE11_DW_WDT_VERIFY_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

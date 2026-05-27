#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 DesignWare live-MMIO gap packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


FILES = {
    "matrix": Path("Documentation/zigux/phase11-dw-wdt-validation-matrix.md"),
    "survey": Path("Documentation/zigux/phase11-dw-wdt-survey.md"),
    "platform_plan": Path("Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md"),
    "manifest": Path("zigux/tests/phase11_dw_wdt_manifest.json"),
    "registration_scaffold": Path("zigux/tests/phase11_dw_wdt_registration_scaffold.zig"),
    "driver": Path("drivers/watchdog/dw_wdt.zig"),
    "pm": Path("drivers/watchdog/dw_wdt_pm.zig"),
}

EXPECTED_LANE = "P11-L10"
EXPECTED_PIN = "75f8336c4305beed127d7abfae37d3999b7cc57c"
NEXT_GAP_ID = "phase11-dw-wdt-live-mmio-validation"
NEXT_DESTINATION = "zigux/tests/phase11_dw_wdt.zig"
NEXT_KIND = "validation"
NEXT_STATUS = "ready_next"
NEXT_WHY_NOW = (
    "With the PM handoff helper, direct restart summary, and returned verify helper "
    "parked in-tree, the next real gap is hardware-backed MMIO validation around "
    "suspend, resume, and platform-backed probe or remove execution, still without "
    "widening into unrelated driver behavior."
)

MATRIX_MARKERS = [
    "# Phase 11 DesignWare Watchdog Validation Matrix",
    "- `PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`",
    "- active watchdog continuity for this matrix and its coupled survey packet is",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` and",
    "- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` keeps timer-clock",
    "- `drivers/watchdog/dw_wdt.zig` now rematerializes on current `master` and",
    "- The next bounded same-lane follow-up remains the manifest-marked ready-next",
    "hardware-backed MMIO validation around suspend, resume, and",
]

SURVEY_MARKERS = [
    "# Phase 11 DesignWare Watchdog Survey",
    "The current lane-local packet is `P11-L10`.",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`,",
    "`drivers/watchdog/dw_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`,",
    "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`,",
    "`drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_pm.zig`,",
    "The next bounded same-lane step is still the ready-next manifest gap:",
]

PLATFORM_PLAN_MARKERS = [
    "# Phase 11 DesignWare Watchdog Platform Registration Plan",
    "The preferred next packet is:",
    "keep timer-clock acquisition and optional APB clock acquisition explicit as outcome-bearing scaffold steps",
    "keep reset-control availability and reset-release intent explicit as outcome-bearing scaffold steps while preserving the already-readable ready-to-register branch when reset control is absent",
    "leave imported-running-state handoff reviewable inside the scaffold without widening into live platform registration, MMIO execution, or survey-only overclaiming",
]

REGISTRATION_SCAFFOLD_MARKERS = [
    'test "platform registration scaffold summary keeps blocked timeout-programming branch explicit" {',
    "dw_wdt.RegistrationScaffoldState.blocked_on_live_mmio,",
    "dw_wdt.ProbeTimeoutOrigin.blocked_on_live_mmio,",
    'test "platform registration scaffold summary keeps optional reset-control absence explicit" {',
    "dw_wdt.RegistrationScaffoldState.ready_to_register,",
]

DRIVER_MARKERS = [
    "pub const ProbeTimeoutOrigin = enum {",
    "blocked_on_live_mmio,",
    "pub const RegistrationScaffoldState = enum {",
    "pub fn platformHandoffSummary(request: PlatformHandoffRequest) PlatformHandoffSummary {",
    "const blocked_on_live_mmio = !missing_timer_clock and",
    "else\n            .blocked_on_live_mmio,",
    'test "dw_wdt registration scaffold keeps optional reset absence ready when timeout image is already programmed" {',
]

PM_MARKERS = [
    'test "phase11 dw_wdt pm resume keeps timeout reprogram block explicit before idle restore" {',
    "PmResumeState.blocked_live_mmio_timeout_reprogram,",
    'test "phase11 dw_wdt pm shutdown keeps running teardown stop and hook removal explicit" {',
    'test "phase11 dw_wdt pm shutdown keeps running pretimeout mask explicit" {',
]

MARKERS = {
    "matrix": MATRIX_MARKERS,
    "survey": SURVEY_MARKERS,
    "platform_plan": PLATFORM_PLAN_MARKERS,
    "registration_scaffold": REGISTRATION_SCAFFOLD_MARKERS,
    "driver": DRIVER_MARKERS,
    "pm": PM_MARKERS,
}


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path.as_posix()}")
    return path.read_text(encoding="utf-8")


def expect_markers(path: Path, markers: list[str]) -> None:
    text = read_text(path)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {path.as_posix()}: {marker}")


def expect_manifest(path: Path) -> None:
    try:
        manifest = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {path.as_posix()}: {exc}") from exc
    if manifest.get("lane_key") != EXPECTED_LANE:
        raise CheckError(
            f"manifest lane_key mismatch: expected {EXPECTED_LANE}, got {manifest.get('lane_key')!r}"
        )
    if manifest.get("surveyed_commit") != EXPECTED_PIN:
        raise CheckError(
            "manifest surveyed_commit mismatch: "
            f"expected {EXPECTED_PIN}, got {manifest.get('surveyed_commit')!r}"
        )

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        raise CheckError("manifest survey_summary must be an object")

    expected_flags = {
        "dw_wdt_zig_present": False,
        "dw_wdt_test_present": False,
        "dw_wdt_registration_scaffold_present": True,
        "dw_wdt_registration_order_present": True,
        "dw_wdt_pm_helper_present": True,
        "dw_wdt_restart_helper_present": True,
        "dw_wdt_verify_helper_present": True,
    }
    for key, expected in expected_flags.items():
        if summary.get(key) is not expected:
            raise CheckError(
                f"manifest survey flag mismatch for {key}: expected {expected!r}, got {summary.get(key)!r}"
            )

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        raise CheckError("manifest gaps must be a list")

    next_gap = None
    for gap in gaps:
        if isinstance(gap, dict) and gap.get("id") == NEXT_GAP_ID:
            next_gap = gap
            break
    if next_gap is None:
        raise CheckError(f"manifest missing gap entry: {NEXT_GAP_ID}")
    if next_gap.get("status") != NEXT_STATUS:
        raise CheckError(
            f"manifest next-step status mismatch: expected {NEXT_STATUS!r}, got {next_gap.get('status')!r}"
        )
    if next_gap.get("kind") != NEXT_KIND:
        raise CheckError(
            f"manifest next-step kind mismatch: expected {NEXT_KIND!r}, got {next_gap.get('kind')!r}"
        )
    if next_gap.get("zigux_destination") != NEXT_DESTINATION:
        raise CheckError(
            "manifest next-step destination mismatch: "
            f"expected {NEXT_DESTINATION}, got {next_gap.get('zigux_destination')!r}"
        )
    if next_gap.get("why_now") != NEXT_WHY_NOW:
        raise CheckError("manifest next-step why_now drifted from the current live-MMIO packet")


def run_check(root: Path) -> None:
    for label, markers in MARKERS.items():
        expect_markers(root / FILES[label], markers)
    expect_manifest(root / FILES["manifest"])


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    for label, path in FILES.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if label == "manifest":
            manifest = {
                "lane_key": EXPECTED_LANE,
                "surveyed_commit": EXPECTED_PIN,
                "survey_summary": {
                    "dw_wdt_zig_present": False,
                    "dw_wdt_test_present": False,
                    "dw_wdt_registration_scaffold_present": True,
                    "dw_wdt_registration_order_present": True,
                    "dw_wdt_pm_helper_present": True,
                    "dw_wdt_restart_helper_present": True,
                    "dw_wdt_verify_helper_present": True,
                },
                "gaps": [
                    {
                        "id": NEXT_GAP_ID,
                        "status": NEXT_STATUS,
                        "kind": NEXT_KIND,
                        "zigux_destination": NEXT_DESTINATION,
                        "why_now": NEXT_WHY_NOW,
                    }
                ],
            }
            write_text(root / path, json.dumps(manifest, indent=2) + "\n")
        else:
            write_text(root / path, "\n".join(MARKERS[label]) + "\n")


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected failure containing {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase11-dw-wdt-live-mmio-gap-") as tmpdir:
        tmp = Path(tmpdir)
        fixture = tmp / "fixture"
        write_sample_root(fixture)
        run_check(fixture)
        case_count = 1

        missing_matrix = tmp / "missing-matrix"
        shutil.copytree(fixture, missing_matrix)
        (missing_matrix / FILES["matrix"]).unlink()
        expect_failure(missing_matrix, FILES["matrix"].as_posix())
        case_count += 1

        missing_mmio_marker = tmp / "missing-mmio-marker"
        shutil.copytree(fixture, missing_mmio_marker)
        path = missing_mmio_marker / FILES["registration_scaffold"]
        path.write_text(path.read_text(encoding="utf-8").replace("dw_wdt.ProbeTimeoutOrigin.blocked_on_live_mmio,", "", 1), encoding="utf-8")
        expect_failure(missing_mmio_marker, "dw_wdt.ProbeTimeoutOrigin.blocked_on_live_mmio,")
        case_count += 1

        wrong_lane = tmp / "wrong-lane"
        shutil.copytree(fixture, wrong_lane)
        manifest_path = wrong_lane / FILES["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["lane_key"] = "P11-L05"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(wrong_lane, "manifest lane_key mismatch")
        case_count += 1

        wrong_flag = tmp / "wrong-flag"
        shutil.copytree(fixture, wrong_flag)
        manifest_path = wrong_flag / FILES["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_summary"]["dw_wdt_pm_helper_present"] = False
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(wrong_flag, "dw_wdt_pm_helper_present")
        case_count += 1

        wrong_kind = tmp / "wrong-kind"
        shutil.copytree(fixture, wrong_kind)
        manifest_path = wrong_kind / FILES["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["gaps"][0]["kind"] = "documentation"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(wrong_kind, "manifest next-step kind mismatch")
        case_count += 1

        wrong_why_now = tmp / "wrong-why-now"
        shutil.copytree(fixture, wrong_why_now)
        manifest_path = wrong_why_now / FILES["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["gaps"][0]["why_now"] = "stale"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(wrong_why_now, "manifest next-step why_now drifted")
        case_count += 1

        wrong_driver_marker = tmp / "wrong-driver-marker"
        shutil.copytree(fixture, wrong_driver_marker)
        path = wrong_driver_marker / FILES["driver"]
        path.write_text(path.read_text(encoding="utf-8").replace("const blocked_on_live_mmio = !missing_timer_clock and", "", 1), encoding="utf-8")
        expect_failure(wrong_driver_marker, "const blocked_on_live_mmio = !missing_timer_clock and")
        case_count += 1

        print("PHASE11_DW_WDT_LIVE_MMIO_GAP_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_LIVE_MMIO_GAP_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail-close the current Phase 11 DesignWare live-MMIO next-step packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    try:
        if args.self_test:
            run_self_test()
        elif args.write_sample_root is not None:
            write_sample_root(args.write_sample_root)
        else:
            run_check(args.root.resolve())
    except (CheckError, AssertionError) as exc:
        print(str(exc))
        return 1

    if not args.self_test and args.write_sample_root is None:
        print("PHASE11_DW_WDT_LIVE_MMIO_GAP=pass")
        print(f"PHASE11_DW_WDT_LIVE_MMIO_GAP_FILE_COUNT={len(FILES)}")
        print(
            "PHASE11_DW_WDT_LIVE_MMIO_GAP_MARKER_COUNT="
            f"{sum(len(markers) for markers in MARKERS.values())}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

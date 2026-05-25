#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 DesignWare PM helper packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path("/workspace/current-like")

SURVEY_PATH = Path("Documentation/zigux/phase11-dw-wdt-survey.md")
MATRIX_PATH = Path("Documentation/zigux/phase11-dw-wdt-validation-matrix.md")
PLAN_PATH = Path("Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md")
MANIFEST_PATH = Path("zigux/tests/phase11_dw_wdt_manifest.json")
PM_PATH = Path("drivers/watchdog/dw_wdt_pm.zig")
PM_SCAFFOLD_PATH = Path("drivers/watchdog/dw_wdt_pm_scaffold.zig")
PM_BUILD_PATH = Path("zigux/tests/phase11_dw_wdt_pm_build.zig")
VALIDATE_PATH = Path("scripts/zigux/validate-phase11.py")
FIXTURE_PATH = Path("zigux/tests/fixtures/phase11_validate_checks.json")

EXPECTED_MANIFEST_LANE = "P11-L10"
EXPECTED_MANIFEST_PHASE = "Phase 11"
EXPECTED_SURVEYED_COMMIT = "75f8336c4305beed127d7abfae37d3999b7cc57c"
PM_GAP_ID = "phase11-dw-wdt-live-platform-pm"
PM_DESTINATION = "drivers/watchdog/dw_wdt_pm.zig"
PM_STATUS = "starter_landed"
NEXT_GAP_ID = "phase11-dw-wdt-live-mmio-validation"
NEXT_DESTINATION = "zigux/tests/phase11_dw_wdt.zig"
NEXT_STATUS = "ready_next"

PM_WHY_NOW = (
    "The bounded PM helper now keeps suspend, resume, and shutdown handoff "
    "reviewable across missing-drvdata blocks, running-hardware suspend stop "
    "intent with stop-on-reboot unregister and restart-priority clear, idle "
    "suspend without teardown hooks, imported-running resume recovery plus "
    "stop-on-reboot and restart-priority restore, idle restore hooks, "
    "timeout-reprogram blocks, running shutdown stop intent with "
    "pretimeout-mask teardown, and idle shutdown cleanup before live "
    "MMIO-backed PM work lands."
)

SURVEY_MARKERS = (
    "`drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_pm.zig`,",
    "`drivers/watchdog/dw_wdt_pm_scaffold.zig`,",
    "the bounded PM-helper pair reviewable",
    "hardware-backed MMIO validation around",
    "suspend, resume, and platform-backed probe or remove execution",
)

MATRIX_MARKERS = (
    "`drivers/watchdog/dw_wdt_pm.zig` keeps the bounded PM-helper handoff",
    "hardware-backed MMIO validation around suspend, resume, and",
)

PLAN_MARKERS = (
    "- the bounded PM helper pair `drivers/watchdog/dw_wdt_pm.zig` and `drivers/watchdog/dw_wdt_pm_scaffold.zig`",
    "- suspend or resume behavior beyond the already-readable PM helper summaries",
)

PM_MARKERS = (
    'pub const anchor_path = "drivers/watchdog/dw_wdt.c";',
    'test "phase11 dw_wdt pm suspend keeps missing drvdata explicit" {',
    "try std.testing.expectEqual(PmSuspendState.blocked_missing_drvdata, summary.state);",
    'test "phase11 dw_wdt pm suspend keeps running-hardware stop handoff explicit" {',
    "try std.testing.expectEqual(PmSuspendState.running_suspend_requires_stop, summary.state);",
    'test "phase11 dw_wdt pm resume keeps imported-running handoff explicit" {',
    "PmResumeState.import_running_state_then_restore_hooks,",
    'test "phase11 dw_wdt pm resume keeps timeout reprogram block explicit before idle restore" {',
    "PmResumeState.blocked_live_mmio_timeout_reprogram,",
    'test "phase11 dw_wdt pm shutdown keeps running pretimeout mask explicit" {',
    "try std.testing.expect(summary.pretimeout_mask_requested);",
)

PM_SCAFFOLD_MARKERS = (
    'pub const anchor_path = "drivers/watchdog/dw_wdt.c";',
    'test "phase11 dw_wdt pm scaffold keeps idle suspend and resume explicit" {',
    "try std.testing.expectEqual(SuspendDisposition.idle_noop, suspend_report.disposition);",
    'test "phase11 dw_wdt pm scaffold quiesces a stoppable watchdog before suspend" {',
    "try std.testing.expectEqual(SuspendDisposition.quiesce_before_suspend, suspend_report.disposition);",
    'test "phase11 dw_wdt pm scaffold keeps no-way-out hardware running across suspend and resume" {',
    "try std.testing.expectEqual(ResumeDisposition.keep_running_without_restore, resume_report.disposition);",
    'test "phase11 dw_wdt pm scaffold keeps live-mmio blocker explicit for running hardware" {',
    "try std.testing.expectEqual(ResumeDisposition.blocked_on_live_mmio, resume_report.disposition);",
)

PM_BUILD_MARKERS = (
    '.root_source_file = b.path("../../drivers/watchdog/dw_wdt_pm.zig"),',
    '.root_source_file = b.path("../../drivers/watchdog/dw_wdt_pm_scaffold.zig"),',
    '.name = "phase11-dw-wdt-pm-tests",',
    '.name = "phase11-dw-wdt-pm-scaffold-tests",',
    'const test_step = b.step(',
    '"Run the focused Phase 11 DesignWare watchdog PM helper pair replay"',
    '"phase11-dw-wdt-pm-test"',
)

VALIDATE_MARKERS = (
    '"scripts/zigux/check-phase11-dw-wdt-pm-helper-packet.py",',
    '"phase11-dw-wdt-pm-helper-packet-self-test",',
    '("python", "scripts/zigux/check-phase11-dw-wdt-pm-helper-packet.py", "--self-test")',
    '"phase11-dw-wdt-pm-helper-packet",',
    '("python", "scripts/zigux/check-phase11-dw-wdt-pm-helper-packet.py")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_dw_wdt_pm_build.zig")',
)

FIXTURE_CHECK_NAMES = (
    "phase11-dw-wdt-pm-helper-packet-self-test",
    "phase11-dw-wdt-pm-helper-packet",
)


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def require_markers(root: Path, rel: Path, label: str, markers: tuple[str, ...]) -> None:
    text = read_text(root / rel)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing {label} marker: {marker}")


def read_manifest(root: Path) -> dict[str, object]:
    path = root / MANIFEST_PATH
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckError("manifest root must be an object")
    return payload


def check_manifest(root: Path) -> None:
    manifest = read_manifest(root)
    if manifest.get("lane_key") != EXPECTED_MANIFEST_LANE:
        raise CheckError(
            f"manifest lane_key mismatch: expected {EXPECTED_MANIFEST_LANE}, "
            f"got {manifest.get('lane_key')!r}"
        )
    if manifest.get("phase") != EXPECTED_MANIFEST_PHASE:
        raise CheckError(
            f"manifest phase mismatch: expected {EXPECTED_MANIFEST_PHASE!r}, "
            f"got {manifest.get('phase')!r}"
        )
    if manifest.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        raise CheckError(
            "manifest surveyed_commit mismatch: expected "
            f"{EXPECTED_SURVEYED_COMMIT}, got {manifest.get('surveyed_commit')!r}"
        )

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        raise CheckError("manifest survey_summary must be an object")
    if summary.get("dw_wdt_pm_helper_present") is not True:
        raise CheckError(
            "manifest pm helper survey flag mismatch: expected True, "
            f"got {summary.get('dw_wdt_pm_helper_present')!r}"
        )

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        raise CheckError("manifest gaps must be a list")

    gap_map = {
        gap.get("id"): gap for gap in gaps if isinstance(gap, dict) and isinstance(gap.get("id"), str)
    }

    pm_gap = gap_map.get(PM_GAP_ID)
    if pm_gap is None:
        raise CheckError(f"manifest missing gap entry: {PM_GAP_ID}")
    if pm_gap.get("zigux_destination") != PM_DESTINATION:
        raise CheckError(
            "manifest pm destination mismatch: expected "
            f"{PM_DESTINATION}, got {pm_gap.get('zigux_destination')!r}"
        )
    if pm_gap.get("status") != PM_STATUS:
        raise CheckError(
            f"manifest pm status mismatch: expected {PM_STATUS!r}, got {pm_gap.get('status')!r}"
        )
    if pm_gap.get("why_now") != PM_WHY_NOW:
        raise CheckError("manifest pm why_now mismatch")

    next_gap = gap_map.get(NEXT_GAP_ID)
    if next_gap is None:
        raise CheckError(f"manifest missing gap entry: {NEXT_GAP_ID}")
    if next_gap.get("zigux_destination") != NEXT_DESTINATION:
        raise CheckError(
            "manifest next destination mismatch: expected "
            f"{NEXT_DESTINATION}, got {next_gap.get('zigux_destination')!r}"
        )
    if next_gap.get("status") != NEXT_STATUS:
        raise CheckError(
            f"manifest next status mismatch: expected {NEXT_STATUS!r}, got {next_gap.get('status')!r}"
        )


def check_validate_fixture(root: Path) -> None:
    path = root / FIXTURE_PATH
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {path}: {exc}") from exc
    checks = payload.get("exact_checks")
    if not isinstance(checks, list):
        raise CheckError("phase11 validate fixture exact_checks must be a list")
    names = [item.get("name") for item in checks if isinstance(item, dict)]
    for name in FIXTURE_CHECK_NAMES:
        if name not in names:
            raise CheckError(f"phase11 validate fixture missing check: {name}")


def run_check(root: Path) -> None:
    require_markers(root, SURVEY_PATH, "survey", SURVEY_MARKERS)
    require_markers(root, MATRIX_PATH, "matrix", MATRIX_MARKERS)
    require_markers(root, PLAN_PATH, "platform plan", PLAN_MARKERS)
    require_markers(root, PM_PATH, "pm helper", PM_MARKERS)
    require_markers(root, PM_SCAFFOLD_PATH, "pm scaffold", PM_SCAFFOLD_MARKERS)
    require_markers(root, PM_BUILD_PATH, "pm build", PM_BUILD_MARKERS)
    require_markers(root, VALIDATE_PATH, "validate-phase11", VALIDATE_MARKERS)
    check_manifest(root)
    check_validate_fixture(root)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / SURVEY_PATH, "\n".join(SURVEY_MARKERS) + "\n")
    write(root / MATRIX_PATH, "\n".join(MATRIX_MARKERS) + "\n")
    write(root / PLAN_PATH, "\n".join(PLAN_MARKERS) + "\n")
    write(root / PM_PATH, "\n".join(PM_MARKERS) + "\n")
    write(root / PM_SCAFFOLD_PATH, "\n".join(PM_SCAFFOLD_MARKERS) + "\n")
    write(root / PM_BUILD_PATH, "\n".join(PM_BUILD_MARKERS) + "\n")
    write(root / VALIDATE_PATH, "\n".join(VALIDATE_MARKERS) + "\n")
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": EXPECTED_MANIFEST_LANE,
                "phase": EXPECTED_MANIFEST_PHASE,
                "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
                "survey_summary": {
                    "dw_wdt_pm_helper_present": True,
                },
                "gaps": [
                    {
                        "id": PM_GAP_ID,
                        "status": PM_STATUS,
                        "zigux_destination": PM_DESTINATION,
                        "why_now": PM_WHY_NOW,
                    },
                    {
                        "id": NEXT_GAP_ID,
                        "status": NEXT_STATUS,
                        "zigux_destination": NEXT_DESTINATION,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / FIXTURE_PATH,
        json.dumps(
            {
                "exact_checks": [
                    {
                        "name": "phase11-dw-wdt-pm-helper-packet-self-test",
                        "command": [
                            "python",
                            "scripts/zigux/check-phase11-dw-wdt-pm-helper-packet.py",
                            "--self-test",
                        ],
                    },
                    {
                        "name": "phase11-dw-wdt-pm-helper-packet",
                        "command": [
                            "python",
                            "scripts/zigux/check-phase11-dw-wdt-pm-helper-packet.py",
                        ],
                    },
                ]
            },
            indent=2,
        )
        + "\n",
    )


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected failure containing {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_dw_wdt_pm_helper_packet_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        missing_survey_marker = tmpdir / "missing_survey_marker"
        shutil.copytree(fixture, missing_survey_marker)
        write(
            missing_survey_marker / SURVEY_PATH,
            read_text(missing_survey_marker / SURVEY_PATH).replace(SURVEY_MARKERS[2], "", 1),
        )
        expect_failure(missing_survey_marker, SURVEY_MARKERS[2])
        case_count += 1

        missing_matrix_marker = tmpdir / "missing_matrix_marker"
        shutil.copytree(fixture, missing_matrix_marker)
        write(
            missing_matrix_marker / MATRIX_PATH,
            read_text(missing_matrix_marker / MATRIX_PATH).replace(MATRIX_MARKERS[0], "", 1),
        )
        expect_failure(missing_matrix_marker, MATRIX_MARKERS[0])
        case_count += 1

        bad_manifest_why_now = tmpdir / "bad_manifest_why_now"
        shutil.copytree(fixture, bad_manifest_why_now)
        manifest = json.loads(read_text(bad_manifest_why_now / MANIFEST_PATH))
        manifest["gaps"][0]["why_now"] = "drift"
        write(bad_manifest_why_now / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(bad_manifest_why_now, "manifest pm why_now mismatch")
        case_count += 1

        bad_manifest_lane = tmpdir / "bad_manifest_lane"
        shutil.copytree(fixture, bad_manifest_lane)
        manifest = json.loads(read_text(bad_manifest_lane / MANIFEST_PATH))
        manifest["lane_key"] = "P11-L99"
        write(bad_manifest_lane / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(bad_manifest_lane, "manifest lane_key mismatch")
        case_count += 1

        missing_fixture_check = tmpdir / "missing_fixture_check"
        shutil.copytree(fixture, missing_fixture_check)
        payload = json.loads(read_text(missing_fixture_check / FIXTURE_PATH))
        payload["exact_checks"] = payload["exact_checks"][:-1]
        write(missing_fixture_check / FIXTURE_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(missing_fixture_check, FIXTURE_CHECK_NAMES[1])
        case_count += 1

        missing_validate_marker = tmpdir / "missing_validate_marker"
        shutil.copytree(fixture, missing_validate_marker)
        write(
            missing_validate_marker / VALIDATE_PATH,
            read_text(missing_validate_marker / VALIDATE_PATH).replace(VALIDATE_MARKERS[2], "", 1),
        )
        expect_failure(missing_validate_marker, VALIDATE_MARKERS[2])
        case_count += 1

        print("PHASE11_DW_WDT_PM_HELPER_PACKET_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_PM_HELPER_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_DW_WDT_PM_HELPER_PACKET=fail: {exc}")
        return 1

    print("PHASE11_DW_WDT_PM_HELPER_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

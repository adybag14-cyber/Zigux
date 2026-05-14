#!/usr/bin/env python3
"""Fail-closed checker for the surviving Phase 11 DesignWare watchdog packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase11-dw-wdt-packet.py"

FILES = {
    "plan_note": "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "lane_sequencing": "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "tests_companion": "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "driver_file": "drivers/watchdog/dw_wdt.zig",
    "verify_file": "drivers/watchdog/dw_wdt_verify.zig",
    "registration_scaffold": "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
}

MARKERS = {
    "plan_note": [
        "# Phase 11 DesignWare Watchdog Platform Registration Plan",
        "This note records the next bounded follow-up for the surviving Phase 11 DesignWare watchdog packet on current `master`.",
        "The live repository still keeps the DesignWare lane reviewable through:",
        "`drivers/watchdog/dw_wdt.zig` for bounded TOP timeout windows, reset-versus-IRQ timeout selection, register-image transitions, probe-time bookkeeping, optional pretimeout-IRQ preflight, registration-facing handoff summaries, teardown-adjacent remove summaries, and an explicit missing timer-clock block",
        "`drivers/watchdog/dw_wdt_verify.zig` for direct teardown ownership and restart failure-mode parity that stays compile-local and host-free beside the bounded driver packet",
        "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig` for the bounded acquisition-facing scaffold that keeps timer-clock, APB-clock, reset-release, optional pretimeout-IRQ acquisition, imported-running handoff, and the missing timer-clock failure path reviewable without widening into live platform behavior",
        "`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` for the surviving owner-lane continuity packet, pinned to `P11-L10`",
        "That means the honest next step is to keep the surviving `P11-L10` platform-registration follow-through aligned with the still-shipped direct DesignWare reminder packet pinned to `P11-L05` through `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_survey.zig`, `Documentation/zigux/phase11-dw-wdt-survey.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` instead of describing those reminder surfaces as removed.",
        "The next bounded follow-up is still to keep `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` aligned with one acquisition-facing platform-registration scaffold without widening into live platform behavior.",
        "- keep missing timer-clock acquisition blocked as a distinct scaffold state so the bounded packet does not imply registration is ready before timer-clock acquisition succeeds",
        "- update this plan note, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` together when the DesignWare packet meaning changes",
        "- keep `drivers/watchdog/dw_wdt_verify.zig` compile-local and host-free so teardown ownership and restart failure-mode parity stay explicit while platform-backed acquisition remains the next bounded follow-through",
        "If clock acquisition lands first, leave reset wiring for the next bounded step. If reset acquisition lands first, leave clock-path execution for the next bounded step. Keep the missing timer-clock failure path explicit until live acquisition exists.",
    ],
    "lane_sequencing": [
        "* DesignWare lane `P11-L10` owns `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` as the surviving bounded platform-registration follow-through packet; keep that scaffold packet explicit beside the still-shipped direct DesignWare reminder packet pinned to `P11-L05` through `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_survey.zig`, `Documentation/zigux/phase11-dw-wdt-survey.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, without recasting those reminder surfaces as removed or treating them as the active scaffold anchor",
        "8. Keep the DesignWare lane honest: on current `master` the surviving `P11-L10` platform-registration follow-through still lives in `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, but the still-shipped direct DesignWare reminder packet also remains pinned to `P11-L05` through `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_survey.zig`, `Documentation/zigux/phase11-dw-wdt-survey.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`; keep those reminder surfaces explicit without recasting them as removed, without treating them as the active scaffold anchor, and without widening the compile-local teardown or restart proofs into hardware-backed closure or treating a missing timer clock as registration-ready.",
    ],
    "tests_companion": [
        "## Phase 11 tests-root packet",
        "- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
        "- `scripts/zigux/check-phase11-dw-wdt-packet.py`",
        "- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
        "- `drivers/watchdog/dw_wdt.zig`",
        "- `drivers/watchdog/dw_wdt_verify.zig`",
        "surviving DesignWare platform-registration continuity packet through `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
        "- `zigux/tests/phase11_dw_wdt.zig`",
        "- `zigux/tests/phase11_dw_wdt_survey.zig`",
    ],
    "driver_file": [
        "pub const RegistrationScaffoldState",
        "blocked_missing_timer_clock",
        "pub const TimerClockPath",
        "pub const ProbeTimeoutOrigin",
        "ProbeTimeoutOrigin = enum",
        "pub const default_restart_priority",
        "pub fn platformHandoffSummary",
        "pub fn registrationOrderSummary",
        "pub fn platformRegistrationScaffoldSummary",
        "ProbeTimeoutOrigin.blocked_missing_timer_clock",
        "blocked_on_live_platform_registration",
        "blocked_on_live_mmio",
        'test "phase11 dw_wdt platform handoff keeps missing timer-clock acquisition explicit"',
        "pub const PlatformResourcePreflightSummary = struct {",
        "pub fn platformResourcePreflightSummary",
        "pub const RemoveSummary = struct {",
        "pub fn removeSummary",
        'test "phase11 dw_wdt remove summary clears interrupts while distinguishing reset-backed shutdown"',
    ],
    "verify_file": [
        "pub fn summarizeStopTeardown",
        "pub fn summarizeRestartFailureMode",
        'test "phase11 dw_wdt verify keeps stop teardown ownership explicit"',
        'test "phase11 dw_wdt verify keeps inactive and missing-drvdata teardown paths distinct"',
        'test "phase11 dw_wdt verify keeps restart failure modes explicit"',
        'test "phase11 dw_wdt verify keeps missing-drvdata restart failures explicit"',
        '"watchdog_unregister_device"',
        '"watchdog_stop_on_reboot"',
        '"watchdog_set_restart_priority"',
        '"dw_wdt_restart"',
        '"WDOG_TIMEOUT_RANGE_REG_OFFSET"',
        '"WDOG_CONTROL_REG_OFFSET"',
        'test "phase11 dw_wdt verify keeps unregistered teardown hooks distinct from watchdog unregister"',
        'test "phase11 dw_wdt verify keeps inactive registered teardown hooks explicit"',
    ],
    "registration_scaffold": [
        'test "platform handoff stays blocked when drvdata publication is missing"',
        'test "platform handoff keeps timeout-programming registration state explicit when resources are ready"',
        'test "registration order summary keeps blocked registration explicit when drvdata is missing"',
        'test "platform registration scaffold summary keeps ready imported-state probe anchors explicit"',
        'test "platform registration scaffold summary keeps blocked timeout-programming branch explicit"',
        'test "platform registration scaffold summary keeps missing timer clock block explicit"',
        "platformHandoffSummary",
        "registrationOrderSummary",
        "platformRegistrationScaffoldSummary",
        "RegistrationScaffoldState.import_running_state_then_register",
        "RegistrationScaffoldState.blocked_missing_drvdata",
        "RegistrationScaffoldState.blocked_missing_timer_clock",
        "ProbeTimeoutOrigin.blocked_missing_timer_clock",
        "blocked_on_live_platform_registration",
        "blocked_on_live_mmio",
        'test "platform resource preflight keeps named acquisition surfaces explicit"',
        'test "platform resource preflight keeps shared fallback and missing-clock block explicit"',
        "platformResourcePreflightSummary",
    ],
}


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


def run_check(root: Path) -> None:
    for label, relative_path in FILES.items():
        text = read_text(root, relative_path)
        expect_markers(label, text, MARKERS[label])


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    for label, relative_path in FILES.items():
        write(root / relative_path, "\n".join(MARKERS[label]) + "\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(
                f"expected self-test failure containing {expected_fragment!r}, got {exc!r}"
            ) from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_dw_wdt_packet_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_self_test_fixture(fixture_root)
        run_check(fixture_root)

        cases = [
            ("plan_note", 1),
            ("plan_note", 3),
            ("plan_note", 5),
            ("plan_note", 7),
            ("plan_note", 8),
            ("plan_note", 9),
            ("plan_note", 11),
            ("lane_sequencing", 0),
            ("lane_sequencing", 1),
            ("tests_companion", 1),
            ("tests_companion", 3),
            ("tests_companion", 4),
            ("tests_companion", 5),
            ("tests_companion", 6),
            ("tests_companion", 7),
            ("tests_companion", 8),
            ("driver_file", 0),
            ("driver_file", 8),
            ("driver_file", 9),
            ("driver_file", 12),
            ("driver_file", 13),
            ("driver_file", 14),
            ("driver_file", 15),
            ("driver_file", 16),
            ("driver_file", 17),
            ("verify_file", 0),
            ("verify_file", 4),
            ("verify_file", 5),
            ("verify_file", 11),
            ("verify_file", 12),
            ("verify_file", 13),
            ("registration_scaffold", 0),
            ("registration_scaffold", 2),
            ("registration_scaffold", 3),
            ("registration_scaffold", 5),
            ("registration_scaffold", 12),
            ("registration_scaffold", 13),
            ("registration_scaffold", 15),
            ("registration_scaffold", 16),
            ("registration_scaffold", 17),
        ]

        for idx, (label, marker_index) in enumerate(cases, start=1):
            case_root = tmpdir / f"case_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            relative_path = FILES[label]
            marker = MARKERS[label][marker_index]
            path = case_root / relative_path
            path.write_text(
                path.read_text(encoding="utf-8").replace(marker + "\n", "", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        missing_driver_root = tmpdir / "missing_driver_file"
        shutil.copytree(fixture_root, missing_driver_root, dirs_exist_ok=True)
        (missing_driver_root / FILES["driver_file"]).unlink()
        expect_failure(missing_driver_root, FILES["driver_file"])

        missing_verify_root = tmpdir / "missing_verify_file"
        shutil.copytree(fixture_root, missing_verify_root, dirs_exist_ok=True)
        (missing_verify_root / FILES["verify_file"]).unlink()
        expect_failure(missing_verify_root, FILES["verify_file"])

        missing_scaffold_root = tmpdir / "missing_registration_scaffold"
        shutil.copytree(fixture_root, missing_scaffold_root, dirs_exist_ok=True)
        (missing_scaffold_root / FILES["registration_scaffold"]).unlink()
        expect_failure(missing_scaffold_root, FILES["registration_scaffold"])

        missing_companion_root = tmpdir / "missing_tests_companion"
        shutil.copytree(fixture_root, missing_companion_root, dirs_exist_ok=True)
        (missing_companion_root / FILES["tests_companion"]).unlink()
        expect_failure(missing_companion_root, FILES["tests_companion"])

        self_test_case_count = len(cases) + 4
        print("PHASE11_DW_WDT_PACKET_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_PACKET_SELF_TEST_CASE_COUNT={self_test_case_count}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE11_DW_WDT_PACKET=fail: {exc}")
        return 1

    print("PHASE11_DW_WDT_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
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
        "`drivers/watchdog/dw_wdt.zig` for bounded TOP timeout windows, reset-versus-IRQ timeout selection, register-image transitions, probe-time bookkeeping, and registration-facing handoff summaries",
        "`drivers/watchdog/dw_wdt_verify.zig` for direct teardown ownership and restart failure-mode parity that stays compile-local and host-free beside the bounded driver packet",
        "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig` for the bounded acquisition-facing scaffold that keeps timer-clock, APB-clock, reset-release, and imported-running handoff reviewable without widening into live platform behavior",
        "`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` for the surviving owner-lane continuity packet, pinned to `P11-L10`",
        "That means the honest next step is no longer to pretend the older DesignWare manifest, survey, validation-matrix, or teardown packet is still shipped on current `master`.",
        "The next bounded follow-up is still to keep `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` aligned with one acquisition-facing platform-registration scaffold without widening into live platform behavior.",
        "- update this plan note, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` together when the DesignWare packet meaning changes",
        "- keep `drivers/watchdog/dw_wdt_verify.zig` compile-local and host-free so teardown ownership and restart failure-mode parity stay explicit while platform-backed acquisition remains the next bounded follow-through",
        "If no scaffold lands yet, keep these reminder surfaces aligned with the surviving DesignWare packet instead of reviving removed manifest-backed evidence.",
    ],
    "lane_sequencing": [
        "* DesignWare lane `P11-L10` owns `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, and `drivers/watchdog/dw_wdt_verify.zig` as the surviving bounded DesignWare packet; keep the landed direct DesignWare replay files and compile-local teardown or restart proofs explicit in shared summaries without widening them into broader platform-registration closure claims",
        "7. Keep the DesignWare lane honest: on current `master` the surviving DesignWare lane evidence is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, and `drivers/watchdog/dw_wdt_verify.zig`, pinned to `P11-L10`, while the next bounded step still remains platform-backed registration scaffolding rather than reviving removed manifest-backed reminder surfaces or widening the compile-local teardown or restart proofs into hardware-backed closure.",
    ],
    "tests_companion": [
        "## Phase 11 tests-root packet",
        "- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
        "- `scripts/zigux/check-phase11-dw-wdt-packet.py`",
        "- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
        "- `drivers/watchdog/dw_wdt.zig`",
        "- `drivers/watchdog/dw_wdt_verify.zig`",
        "surviving DesignWare platform-registration continuity packet through `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
    ],
    "driver_file": [
        "pub const RegistrationScaffoldState",
        "pub const TimerClockPath",
        "pub const ProbeTimeoutOrigin",
        "pub const default_restart_priority",
        "pub fn platformHandoffSummary",
        "pub fn registrationOrderSummary",
        "pub fn platformRegistrationScaffoldSummary",
        "blocked_on_live_platform_registration",
        "blocked_on_live_mmio",
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
    ],
    "registration_scaffold": [
        'test "platform handoff stays blocked when drvdata publication is missing"',
        'test "platform handoff keeps timeout-programming registration state explicit when resources are ready"',
        'test "registration order summary keeps blocked registration explicit when drvdata is missing"',
        'test "platform registration scaffold summary keeps ready imported-state probe anchors explicit"',
        'test "platform registration scaffold summary keeps blocked timeout-programming branch explicit"',
        "platformHandoffSummary",
        "registrationOrderSummary",
        "platformRegistrationScaffoldSummary",
        "RegistrationScaffoldState.import_running_state_then_register",
        "RegistrationScaffoldState.blocked_missing_drvdata",
        "blocked_on_live_platform_registration",
        "blocked_on_live_mmio",
    ],
}

SELF_TEST_CASE_COUNT = 28


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
            ("plan_note", 10),
            ("lane_sequencing", 0),
            ("lane_sequencing", 1),
            ("tests_companion", 1),
            ("tests_companion", 3),
            ("tests_companion", 4),
            ("tests_companion", 5),
            ("tests_companion", 6),
            ("driver_file", 0),
            ("driver_file", 6),
            ("verify_file", 0),
            ("verify_file", 4),
            ("verify_file", 5),
            ("verify_file", 11),
            ("verify_file", 12),
            ("registration_scaffold", 0),
            ("registration_scaffold", 2),
            ("registration_scaffold", 3),
            ("registration_scaffold", 10),
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

        print("PHASE11_DW_WDT_PACKET_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
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
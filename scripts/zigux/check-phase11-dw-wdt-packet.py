#!/usr/bin/env python3
"""Fail-closed checker for the live Phase 11 DesignWare watchdog packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase11-dw-wdt-packet.py"

FILES = {
    "plan_note": "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "tests_companion": "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "driver_file": "drivers/watchdog/dw_wdt.zig",
    "verify_file": "drivers/watchdog/dw_wdt_verify.zig",
    "registration_scaffold": "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
}

MARKERS = {
    "plan_note": [
        "# Phase 11 DesignWare Watchdog Platform Registration Plan",
        "This note records the next bounded follow-up for the live Phase 11 DesignWare watchdog packet on current `master`.",
        "The live repository still keeps the DesignWare lane reviewable through:",
        "`drivers/watchdog/dw_wdt.zig` for bounded TOP timeout windows, reset-versus-IRQ timeout selection, register-image transitions, probe-time bookkeeping, registration-facing handoff summaries, teardown-adjacent remove summaries, and an explicit missing timer-clock block",
        "`drivers/watchdog/dw_wdt_verify.zig` for direct teardown ownership and remove failure-mode parity that stays compile-local and host-free beside the bounded driver packet",
        "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig` for the bounded acquisition-facing scaffold that keeps timer-clock, APB-clock, reset-release, optional pretimeout-IRQ acquisition, imported-running handoff, and the missing timer-clock failure path reviewable without widening into live platform behavior",
        "`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` for the owner-lane continuity packet that keeps the next DesignWare platform-registration follow-through explicit without widening it into live platform-driver execution or broader hardware-backed closure",
        "Current `master` keeps that smaller DesignWare packet explicit through the live driver, verify file, registration scaffold, and owner-lane continuity surfaces, so this owner note should not reintroduce the older survey, slice, teardown, validation-matrix, manifest, survey-gate, or direct replay files as current evidence.",
        "That means the honest next step is to keep the DesignWare owner packet aligned with the already-landed driver, verify, registration scaffold, and owner-lane continuity surfaces current `master` actually materializes while still parking the next implementation step on platform-backed registration scaffolding instead of widening into live platform behavior.",
        "The next bounded follow-up is still to attach the existing registration-facing handoff to one acquisition-facing platform-registration scaffold without widening into live clock, reset, IRQ, or MMIO behavior.",
        "- keep missing timer-clock acquisition blocked as a distinct scaffold state so the bounded packet does not imply registration is ready before timer-clock acquisition succeeds",
        "- update this plan note and `scripts/zigux/check-phase11-dw-wdt-packet.py` together when the live DesignWare packet meaning changes; refresh the shared lane note or tests-root companion only when that shared owner map needs to change",
        "- keep proof bounded to the checker self-test plus the narrowest truthful Zig-side review available for the next scaffold change",
        "- keep `drivers/watchdog/dw_wdt_verify.zig` compile-local and host-free so teardown ownership and remove failure-mode parity stay explicit while platform-backed acquisition remains the next bounded follow-through",
        "- refresh the shared tests-root companion or the shared lane-sequencing note only when a future DesignWare owner-packet change materially changes the shared owner map, not just because the live driver, verify, and scaffold packet is still being restated",
        "Keep the live driver, verify, and scaffold packet explicit while the next implementation step stays inside `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` and `drivers/watchdog/dw_wdt.zig`.",
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
        'test "phase11 dw_wdt registration order summary keeps blocked registration explicit"',
        'test "phase11 dw_wdt platform handoff keeps reset-release intent explicit"',
        'test "phase11 dw_wdt platform handoff keeps missing timer-clock acquisition explicit"',
        'test "phase11 dw_wdt platform registration scaffold keeps shared-clock fallback and reset release explicit"',
        "pub const PlatformResourcePreflightSummary = struct {",
        "pub fn platformResourcePreflightSummary",
        "pub const RemoveSummary = struct {",
        "pub fn removeSummary",
        'test "phase11 dw_wdt teardown summary keeps idle, stoppable, and unstoppable paths distinct"',
        'test "phase11 dw_wdt remove summary clears interrupts while distinguishing reset-backed shutdown"',
        'test "phase11 dw_wdt remove summary keeps idle removal distinct from reset-backed shutdown"',
    ],
    "verify_file": [
        'test "phase11 dw_wdt verify keeps registration-blocking failure paths explicit" {',
        'test "phase11 dw_wdt verify keeps mmio-blocked registration handoff explicit" {',
        'test "phase11 dw_wdt verify keeps imported-running handoff and shared-clock fallback explicit" {',
        'test "phase11 dw_wdt verify keeps continued-heartbeat teardown and remove failure modes explicit" {',
        'test "phase11 dw_wdt verify keeps reset-backed teardown and remove cleanup distinct" {',
        'test "phase11 dw_wdt verify keeps idle no-op teardown and remove paths explicit" {',
        "dw_wdt.RegistrationScaffoldState.blocked_missing_drvdata",
        "dw_wdt.TimerClockPath.blocked_no_timer_clock",
        "dw_wdt.ProbeTimeoutOrigin.blocked_missing_timer_clock",
        "dw_wdt.RegistrationScaffoldState.import_running_state_then_register",
        "dw_wdt.TimerClockPath.unnamed_shared_fallback",
        "dw_wdt.ProbeTimeoutOrigin.imported_running_counter",
        "dw_wdt.TeardownOutcome.continued_heartbeat",
        "dw_wdt.TeardownOutcome.reset_control_stop",
        "remove_summary.remove_leaves_hardware_running",
        "remove_summary.reset_assert_requested",
        "var idle_remove_without_reset = try dw_wdt.DwWdtLab.initFixedTops(9, false);",
        "try testing.expect(!idle_remove_without_reset_summary.reset_control_available);",
        "try testing.expect(!idle_remove_without_reset_summary.reset_assert_requested);",
    ],
    "registration_scaffold": [
        'test "platform handoff stays blocked when drvdata publication is missing"',
        'test "platform handoff keeps timeout-programming registration state explicit when resources are ready"',
        'test "platform handoff keeps imported-running registration state explicit"',
        'test "registration order summary keeps blocked registration explicit when drvdata is missing"',
        'test "registration order summary keeps imported-running registration distinct from timeout programming"',
        'test "platform registration scaffold summary keeps ready imported-state probe anchors explicit"',
        'test "platform registration scaffold summary keeps blocked timeout-programming branch explicit"',
        'test "platform registration scaffold summary keeps optional reset-control absence explicit"',
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

FORBIDDEN_MARKERS = {
    "plan_note": [
        "Current `master` keeps that broader DesignWare packet explicit through the live driver, verify file, direct replay, manifest, survey, slice, validation matrix, teardown note, registration scaffold, and owner-lane continuity surfaces, so this owner note should keep those landed review surfaces explicit instead of retelling them as absent or collapsing the lane back to scaffold-only continuity.",
        "That means the honest next step is to keep the DesignWare owner packet aligned with the already-landed driver, verify, direct replay, manifest, survey, slice, validation matrix, teardown note, registration scaffold, and owner-lane continuity surfaces current `master` actually materializes while still parking the next implementation step on platform-backed registration scaffolding instead of widening into live platform behavior.",
        "- refresh the shared tests-root companion or the shared lane-sequencing note only when a future DesignWare owner-packet change materially changes the shared owner map, not just because the live driver, verify, direct replay, manifest, survey, slice, validation matrix, teardown note, and scaffold packet is still being restated",
        "Keep the live driver, verify, direct replay, manifest, survey, slice, validation-matrix, teardown-note, and scaffold packet explicit while the next implementation step stays inside `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` and `drivers/watchdog/dw_wdt.zig`.",
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


def expect_forbidden_markers_absent(label: str, text: str) -> None:
    for marker in FORBIDDEN_MARKERS.get(label, []):
        if marker in text:
            raise CheckError(f"forbidden marker in {label}: {marker}")


def run_check(root: Path) -> None:
    for label, relative_path in FILES.items():
        text = read_text(root, relative_path)
        expect_markers(label, text, MARKERS[label])
        expect_forbidden_markers_absent(label, text)


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
            (label, marker_index)
            for label, markers in MARKERS.items()
            for marker_index in range(len(markers))
        ]

        for idx, (label, marker_index) in enumerate(cases, start=1):
            case_root = tmpdir / f"case_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            relative_path = FILES[label]
            marker = MARKERS[label][marker_index]
            path = case_root / relative_path
            path.write_text(
                path.read_text(encoding="utf-8").replace(marker, "__mutated__"),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        forbidden_case_index = 1
        for label, markers in FORBIDDEN_MARKERS.items():
            for marker in markers:
                case_root = tmpdir / f"forbidden_{label}_{forbidden_case_index}"
                shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
                path = case_root / FILES[label]
                path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
                expect_failure(case_root, marker)
                forbidden_case_index += 1

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

        self_test_case_count = len(cases) + sum(len(markers) for markers in FORBIDDEN_MARKERS.values()) + 4
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

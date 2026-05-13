#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 DesignWare watchdog review packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase11-dw-wdt-packet.py"

FILES = {
    "plan_note": "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "lane_sequencing": "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "survey_note": "Documentation/zigux/phase11-dw-wdt-survey.md",
    "validation_matrix": "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "manifest_file": "zigux/tests/phase11_dw_wdt_manifest.json",
    "survey_gate": "zigux/tests/phase11_dw_wdt_survey.zig",
    "registration_scaffold": "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
    "build_file": "zigux/tests/phase11_build.zig",
    "verify_file": "drivers/watchdog/dw_wdt_verify.zig",
}

MARKERS = {
    "plan_note": [
        "# Phase 11 DesignWare Watchdog Platform Registration Plan",
        "This note records the next bounded follow-up for the surviving Phase 11 DesignWare watchdog packet on current `master`.",
        "The live repository still keeps the DesignWare lane reviewable through:",
        "`drivers/watchdog/dw_wdt.zig` for bounded TOP timeout windows, reset-versus-IRQ timeout selection, register-image transitions, probe-time bookkeeping, and registration-facing handoff summaries",
        "`drivers/watchdog/dw_wdt_verify.zig` for direct teardown ownership and restart failure-mode parity that stays compile-local and host-free beside the bounded driver packet",
        "`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` for the surviving owner-lane continuity packet, pinned to `P11-L10`",
        "That means the honest next step is no longer to pretend the older DesignWare manifest, survey, validation-matrix, or teardown packet is still shipped on current `master`.",
        "The next bounded follow-up is still to attach the registration-facing handoff to one acquisition-facing platform-registration scaffold without widening into live platform behavior.",
        "- shared Phase 11 reminder-surface churn outside the DesignWare packet",
        "- update this plan note, `Documentation/zigux/phase11-driver-lane-sequencing.md`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` together when the DesignWare packet meaning changes",
        "- keep `drivers/watchdog/dw_wdt_verify.zig` compile-local and host-free so teardown ownership and restart failure-mode parity stay explicit while platform-backed acquisition remains the next bounded follow-through",
        "- create a new DesignWare manifest, survey, validation-matrix, or teardown surface only if a future scaffold lands enough new lane evidence to justify reviving it",
        "- `Documentation/zigux/phase11-driver-lane-sequencing.md`",
        "- `drivers/watchdog/dw_wdt_verify.zig`",
        "If no scaffold lands yet, keep these reminder surfaces aligned with the surviving DesignWare packet instead of reviving removed manifest-backed evidence.",
    ],
    "lane_sequencing": [
        "* DesignWare lane `P11-L10` owns `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, and `drivers/watchdog/dw_wdt_verify.zig` as the surviving bounded DesignWare packet; keep the landed direct DesignWare replay files and compile-local teardown or restart proofs explicit in shared summaries without widening them into broader platform-registration closure claims",
        "7. Keep the DesignWare lane honest: on current `master` the surviving DesignWare lane evidence is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, and `drivers/watchdog/dw_wdt_verify.zig`, pinned to `P11-L10`, while the next bounded step still remains platform-backed registration scaffolding rather than reviving removed manifest-backed reminder surfaces or widening the compile-local teardown or restart proofs into hardware-backed closure.",
    ],
    "survey_note": [
        "# Phase 11 DesignWare Watchdog Survey",
        "This survey note tracks the Phase 11 gap around `drivers/watchdog/dw_wdt.c` after re-reading `master` `75f8336c4305beed127d7abfae37d3999b7cc57c`.",
        "`drivers/watchdog/dw_wdt.zig` now ships the bounded DesignWare starter for fixed TOP timeout windows, reset-mode versus IRQ-mode timeout selection, pretimeout bookkeeping, register-image transitions, non-stoppable stop semantics, a tiny probe-time summary for fixed-versus-custom TOP sourcing plus already-running watchdog metadata, a small registration-facing handoff around watchdog info selection, parent linkage, timeout-programming intent, and `watchdog_register_device`, a bounded registration-order summary for timer-clock path choice, optional APB clock presence, reset-release posture, `platform_set_drvdata` publication, restart-priority sequencing, stop-on-reboot intent, and register-device request ordering, and a dedicated platform-registration scaffold summary that names `module_platform_driver` plus `dw_wdt_drv_probe`, `dw_wdt_drv_remove`, and `dw_wdt_drv_shutdown` without claiming live probe execution",
        "`drivers/watchdog/dw_wdt_verify.zig` keeps the teardown and failure-mode parity packet reviewable by replaying the split between reset-controlled remove, unstoppable running remove, idle remove without a fabricated heartbeat, idle remove with reset-backed quiesce, idle stop outcomes across reset-controlled and non-stoppable hardware, idle IRQ-configured teardown without a fabricated stop path or continued heartbeat, IRQ-mode teardown outcomes, the imported-running no-IRQ pretimeout-flattening handoff, the missing-`drvdata` platform handoff, and the blocked-but-reviewable no-IRQ plus no-`drvdata` handoff while also keeping the custom TOP ordering explicit",
        "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md` now records the bounded hardware-validation posture for the current starter so the shared replay path and deferred ownership boundaries stay reviewable in one place",
        "`scripts/zigux/check-phase11-dw-wdt-packet.py` now fail-closes the DesignWare-local review packet across this survey note, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and the shared `zigux/tests/phase11_build.zig` wiring; run `python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test` for the synthetic packet and `python3 scripts/zigux/check-phase11-dw-wdt-packet.py` for the live repo packet",
        "`zigux/tests/phase11_build.zig` now runs the gpio starter checks, bcm2835 starter and survey checks, the `phase11-dw-wdt-tests` starter replay, the `phase11-dw-wdt-registration-scaffold-tests` scaffold replay, the `phase11-dw-wdt-verify-tests` verify replay, and the `phase11-dw-wdt-survey-tests` survey replay together so watchdog-lane drift is visible in one place",
    ],
    "validation_matrix": [
        "# Phase 11 DesignWare Watchdog Validation Matrix",
        "This document records the first bounded hardware-validation matrix for the Zigux `dw_wdt` lane.",
        "`PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`",
        "current surveyed packet pin: `75f8336c4305beed127d7abfae37d3999b7cc57c`",
        "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
        "a bounded platform-resource preflight summary that keeps named `tclk` versus shared-clock fallback, optional APB clock presence, optional reset-control availability, optional pretimeout-IRQ wiring, and the explicit no-timer-clock block reviewable before any live `devm_*` acquisition",
        "a dedicated platform-registration scaffold summary that names `module_platform_driver` plus the bounded `dw_wdt_drv_probe`, `dw_wdt_drv_remove`, and `dw_wdt_drv_shutdown` anchors without claiming live platform execution.",
        "The dedicated `scripts/zigux/check-phase11-dw-wdt-packet.py` guard now keeps this matrix, the survey note, the manifest-backed survey gate, the registration-scaffold replay, the verify replay, and the shared Phase 11 build wiring fail-closed together instead of relying on prose alone.",
    ],
    "manifest_file": [
        "\"lane_key\": \"P11-L05\"",
        "\"phase\": \"Phase 11\"",
        "\"surveyed_commit\": \"75f8336c4305beed127d7abfae37d3999b7cc57c\"",
        "\"anchor\": \"drivers/watchdog/dw_wdt.c\"",
        "\"dw_wdt_registration_scaffold_present\": true",
        "\"id\": \"phase11-dw-wdt-registration-order-scaffold\"",
        "\"zigux_destination\": \"zigux/tests/phase11_dw_wdt_registration_scaffold.zig\"",
        "\"zigux_destination\": \"drivers/watchdog/dw_wdt_verify.zig\"",
        "\"id\": \"phase11-dw-wdt-live-platform-pm\"",
    ],
    "survey_gate": [
        "test \"phase11 dw_wdt survey manifest records the landed registration handoff and remaining platform gap\"",
        "\"zigux/tests/phase11_dw_wdt_manifest.json\"",
        "try std.testing.expectEqualStrings(\"P11-L05\", manifest.lane_key);",
        "try std.testing.expect(manifest.survey_summary.dw_wdt_registration_scaffold_present);",
    ],
    "registration_scaffold": [
        "test \"platform handoff stays blocked when drvdata publication is missing\"",
        "test \"registration order summary keeps blocked registration explicit when drvdata is missing\"",
        "test \"platform registration scaffold summary keeps ready imported-state probe anchors explicit\"",
        "test \"platform registration scaffold summary keeps blocked timeout-programming branch explicit\"",
        "try std.testing.expectEqualStrings(\"module_platform_driver\", summary.platform_driver_anchor);",
        "try std.testing.expectEqualStrings(\"dw_wdt_drv_probe\", summary.probe_anchor);",
        "try std.testing.expectEqualStrings(\"dw_wdt_drv_remove\", summary.remove_anchor);",
        "try std.testing.expectEqualStrings(\"dw_wdt_drv_shutdown\", summary.shutdown_anchor);",
        "try std.testing.expect(summary.blocked_on_live_platform_registration);",
        "try std.testing.expect(summary.blocked_on_live_mmio);",
    ],
    "build_file": [
        '.name = "phase11-dw-wdt-tests",',
        '.name = "phase11-dw-wdt-verify-tests",',
        '.name = "phase11-dw-wdt-survey-tests",',
        "test_step.dependOn(&run_phase11_dw_wdt_tests.step);",
        "test_step.dependOn(&run_dw_wdt_verify_tests.step);",
        "test_step.dependOn(&run_phase11_dw_wdt_survey_tests.step);",
    ],
    "verify_file": [
        "pub fn summarizeStopTeardown",
        "pub fn summarizeRestartFailureMode",
        'test "phase11 dw_wdt verify keeps stop teardown ownership explicit"',
        'test "phase11 dw_wdt verify keeps inactive and missing-drvdata teardown paths distinct"',
        'test "phase11 dw_wdt verify keeps restart failure modes explicit"',
        '"drivers/watchdog/dw_wdt.c"',
        '"watchdog_unregister_device"',
        '"watchdog_stop_on_reboot"',
        '"watchdog_set_restart_priority"',
        '"dw_wdt_restart"',
        '"WDOG_TIMEOUT_RANGE_REG_OFFSET"',
        '"WDOG_CONTROL_REG_OFFSET"',
    ],
}

SELF_TEST_CASE_COUNT = 21


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
        expect_markers(label, read_text(root, relative_path), MARKERS[label])


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
            ("plan_note", 4),
            ("plan_note", 7),
            ("lane_sequencing", 0),
            ("lane_sequencing", 1),
            ("survey_note", 3),
            ("survey_note", 5),
            ("validation_matrix", 4),
            ("validation_matrix", 7),
            ("manifest_file", 4),
            ("manifest_file", 6),
            ("survey_gate", 0),
            ("survey_gate", 3),
            ("registration_scaffold", 0),
            ("registration_scaffold", 2),
            ("registration_scaffold", 7),
            ("build_file", 0),
            ("build_file", 5),
            ("verify_file", 0),
            ("verify_file", 4),
            ("verify_file", 10),
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

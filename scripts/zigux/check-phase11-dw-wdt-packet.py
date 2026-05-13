#!/usr/bin/env python3
"""Fail-closed checker for the surviving Phase 11 DesignWare watchdog ownership packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase11-dw-wdt-packet.py"

FILES = {
    "plan_note": "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "lane_sequencing": "Documentation/zigux/phase11-driver-lane-sequencing.md",
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

SELF_TEST_CASE_COUNT = 12


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
            (FILES["plan_note"], MARKERS["plan_note"][1]),
            (FILES["plan_note"], MARKERS["plan_note"][4]),
            (FILES["plan_note"], MARKERS["plan_note"][7]),
            (FILES["plan_note"], MARKERS["plan_note"][10]),
            (FILES["lane_sequencing"], MARKERS["lane_sequencing"][0]),
            (FILES["lane_sequencing"], MARKERS["lane_sequencing"][1]),
            (FILES["verify_file"], MARKERS["verify_file"][0]),
            (FILES["verify_file"], MARKERS["verify_file"][1]),
            (FILES["verify_file"], MARKERS["verify_file"][2]),
            (FILES["verify_file"], MARKERS["verify_file"][4]),
            (FILES["verify_file"], MARKERS["verify_file"][10]),
            (FILES["verify_file"], MARKERS["verify_file"][11]),
        ]

        for idx, (relative_path, marker) in enumerate(cases, start=1):
            case_root = tmpdir / f"case_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
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

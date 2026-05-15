#!/usr/bin/env python3
"""Fail-closed checker for the live Phase 11 DesignWare watchdog failure packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase11-dw-wdt-failure-matrix.py"

FILES = {
    "survey_note": "Documentation/zigux/phase11-dw-wdt-survey.md",
    "validation_matrix": "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "teardown_note": "Documentation/zigux/phase11-dw-wdt-teardown-note.md",
    "slice_note": "Documentation/zigux/phase11-dw-wdt-slice.md",
    "manifest": "zigux/tests/phase11_dw_wdt_manifest.json",
    "survey_gate": "zigux/tests/phase11_dw_wdt_survey.zig",
    "verify_file": "drivers/watchdog/dw_wdt_verify.zig",
}

MARKERS = {
    "survey_note": [
        "# Phase 11 DesignWare Watchdog Survey",
        "`drivers/watchdog/dw_wdt_verify.zig` keeps the teardown and failure-mode parity packet reviewable",
        "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md` now records the bounded hardware-validation posture",
        "`phase11-dw-wdt-verify-tests`",
        "`phase11-dw-wdt-registration-scaffold-tests`",
        "hardware validation matrix is present",
        "teardown and failure-mode parity is reviewable",
        "`P11-L05`",
    ],
    "validation_matrix": [
        "# Phase 11 DesignWare Watchdog Validation Matrix",
        "PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed",
        "active watchdog continuity for this matrix and its coupled survey packet is `P11-L05`",
        "`drivers/watchdog/dw_wdt_verify.zig`",
        "`zigux/tests/phase11_dw_wdt_manifest.json`",
        "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
        "`zigux/tests/phase11_dw_wdt_survey.zig`",
        "`Documentation/zigux/phase11-dw-wdt-survey.md`",
        "`Documentation/zigux/phase11-dw-wdt-teardown-note.md`",
    ],
    "teardown_note": [
        "# Phase 11 DesignWare Watchdog Teardown Note",
        "`stop()` owns the reset-control split",
        "`teardownSummary()` owns the stop-backed handoff",
        "`removeSummary()` owns the unregister-side cleanup",
        "`zigux/tests/phase11_dw_wdt.zig`",
        "`drivers/watchdog/dw_wdt_verify.zig`",
        "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    ],
    "slice_note": [
        "# Phase 11 DesignWare Watchdog Slice",
        "With the paired validation matrix and dedicated teardown note now landed beside the starter",
        "platform-backed registration scaffolding",
        "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
        "`Documentation/zigux/phase11-dw-wdt-teardown-note.md`",
    ],
    "manifest": [
        '"lane_key": "P11-L05"',
        '"id": "phase11-dw-wdt-survey-note"',
        '"zigux_destination": "Documentation/zigux/phase11-dw-wdt-survey.md"',
        '"id": "phase11-dw-wdt-teardown-parity"',
        '"zigux_destination": "drivers/watchdog/dw_wdt_verify.zig"',
        '"id": "phase11-dw-wdt-platform-registration-scaffold"',
        '"status": "ready_next"',
        '"id": "phase11-dw-wdt-live-platform-pm"',
        '"status": "blocked_on_driver_scaffold"',
    ],
    "survey_gate": [
        'test "phase11 dw_wdt survey manifest records the landed registration handoff and remaining platform gap"',
        'test "phase11 dw_wdt survey note, slice note, and validation matrix stay aligned"',
        '"phase11-dw-wdt-survey-note"',
        '"phase11-dw-wdt-teardown-parity"',
        '"phase11-dw-wdt-platform-registration-scaffold"',
        '"PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed"',
        '"phase11-dw-wdt-verify-tests"',
        '"Documentation/zigux/phase11-dw-wdt-slice.md"',
    ],
    "verify_file": [
        'test "phase11 dw_wdt verify keeps stop teardown ownership explicit"',
        'test "phase11 dw_wdt verify keeps inactive and missing-drvdata teardown paths distinct"',
        'test "phase11 dw_wdt verify keeps inactive registered teardown hooks explicit"',
        'test "phase11 dw_wdt verify keeps unregistered teardown hooks distinct from watchdog unregister"',
        'test "phase11 dw_wdt verify keeps restart failure modes explicit"',
        'test "phase11 dw_wdt verify keeps missing-drvdata restart failures explicit"',
        '"watchdog_unregister_device"',
        '"watchdog_stop_on_reboot"',
        '"watchdog_set_restart_priority"',
        '"dw_wdt_restart"',
    ],
}

FORBIDDEN_MARKERS = {
    "survey_note": ["`P11-L10`", "`P11-L11`", "`P11-L12`"],
    "validation_matrix": ["`P11-L10`", "`P11-L12`", "current tree does not carry a landed DesignWare watchdog packet yet."],
    "manifest": ['"lane_key": "P11-L10"'],
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
            raise CheckError(f"unexpected stale marker in {label}: {marker}")


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
        markers = list(MARKERS[label])
        text = "\n".join(markers) + "\n"
        write(root / relative_path, text)


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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_dw_wdt_failure_matrix_"))
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
                path.read_text(encoding="utf-8").replace(marker, "__mutated__", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        forbidden_cases = [
            (label, marker)
            for label, markers in FORBIDDEN_MARKERS.items()
            for marker in markers
        ]
        for idx, (label, marker) in enumerate(forbidden_cases, start=1):
            case_root = tmpdir / f"forbidden_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            relative_path = FILES[label]
            path = case_root / relative_path
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            expect_failure(case_root, marker)

        missing_manifest_root = tmpdir / "missing_manifest"
        shutil.copytree(fixture_root, missing_manifest_root, dirs_exist_ok=True)
        (missing_manifest_root / FILES["manifest"]).unlink()
        expect_failure(missing_manifest_root, FILES["manifest"])

        self_test_case_count = len(cases) + len(forbidden_cases) + 1
        print("PHASE11_DW_WDT_FAILURE_MATRIX_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_FAILURE_MATRIX_SELF_TEST_CASE_COUNT={self_test_case_count}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the live Phase 11 dw_wdt teardown and failure packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(args.root)
    except CheckError as exc:
        print(f"PHASE11_DW_WDT_FAILURE_MATRIX=fail: {exc}")
        return 1

    print("PHASE11_DW_WDT_FAILURE_MATRIX=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

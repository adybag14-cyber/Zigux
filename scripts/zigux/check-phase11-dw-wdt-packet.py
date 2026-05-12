#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 11 DesignWare watchdog planning packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase11-dw-wdt-packet.py"

FILES = {
    "plan_note": "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "shared_contract": "Documentation/zigux/phase11-shared-replay-contract.md",
    "closure_note": "Documentation/zigux/phase11-closure-note.md",
    "lane_note": "Documentation/zigux/phase11-driver-lane-sequencing.md",
}

MARKERS = {
    "plan_note": [
        "# Phase 11 DesignWare Watchdog Platform Registration Plan",
        "The live repository does not currently ship a `dw_wdt` test packet, manifest, or driver-local replay surface under `zigux/tests/` or `drivers/watchdog/`.",
        "Keep the next implementation bounded to a single scaffolding surface that makes clock or reset acquisition reviewable without claiming a full probe path.",
        "1. model timer-clock acquisition and optional APB clock acquisition as explicit outcome-bearing steps",
        "2. model reset-control availability and reset-release intent as explicit outcome-bearing steps",
        "3. preserve the intended ordering around `platform_set_drvdata`, timeout-programming intent, stop-on-reboot intent, restart-priority sequencing, and `watchdog_register_device`",
        "4. keep imported-running-state handoff reviewable when the timer starts hot",
        "- focused Zig tests for the new acquisition-order summary or summaries",
        "- survey or manifest update only if the new scaffold actually lands",
        "- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
        "- `Documentation/zigux/phase11-driver-lane-sequencing.md`",
        "- `zigux/tests/README.md`",
        "If clock acquisition lands first, leave reset wiring for the next bounded step. If reset acquisition lands first, leave clock-path execution for the next bounded step.",
    ],
    "shared_contract": [
        "The DesignWare watchdog lane is still parked on a planning checkpoint beside that shared route:",
        "* `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
        "* `scripts/zigux/check-phase11-dw-wdt-packet.py`",
        "Treat that plan note together with the dedicated packet checker as the current DesignWare lane evidence on `master`: they keep the next bounded platform-registration scaffold explicit while the repository still does not materialize `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, or `drivers/watchdog/dw_wdt_verify.zig`.",
    ],
    "closure_note": [
        "* DesignWare watchdog continuity stays with `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` and `scripts/zigux/check-phase11-dw-wdt-packet.py`, while `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, and `drivers/watchdog/dw_wdt_verify.zig` stay recorded as remaining repo-reality gaps rather than shared closure evidence",
    ],
    "lane_note": [
        "- DesignWare lane `P11-L05` currently owns `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` and `scripts/zigux/check-phase11-dw-wdt-packet.py`; `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, and `drivers/watchdog/dw_wdt_verify.zig` stay recorded as the intended first scaffold packet rather than shipped current-`master` evidence",
        "- DesignWare packet review stays parked on `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` and `scripts/zigux/check-phase11-dw-wdt-packet.py`; `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, and `drivers/watchdog/dw_wdt_verify.zig` stay recorded as repo-reality gaps until the first scaffold lands",
        "Keep the DesignWare lane honest: on current `master` the landed DesignWare lane evidence is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` plus `scripts/zigux/check-phase11-dw-wdt-packet.py`, while `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, and `drivers/watchdog/dw_wdt_verify.zig` remain repo-reality gaps rather than a landed packet.",
    ],
}

SELF_TEST_CASE_COUNT = 10


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
            (FILES["plan_note"], MARKERS["plan_note"][5]),
            (FILES["shared_contract"], MARKERS["shared_contract"][0]),
            (FILES["shared_contract"], MARKERS["shared_contract"][3]),
            (FILES["closure_note"], MARKERS["closure_note"][0]),
            (FILES["lane_note"], MARKERS["lane_note"][0]),
            (FILES["lane_note"], MARKERS["lane_note"][1]),
            (FILES["lane_note"], MARKERS["lane_note"][2]),
            (FILES["plan_note"], MARKERS["plan_note"][12]),
            (FILES["plan_note"], "- `zigux/tests/README.md`"),
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

        missing_file_root = tmpdir / "missing_file"
        shutil.copytree(fixture_root, missing_file_root, dirs_exist_ok=True)
        (missing_file_root / FILES["shared_contract"]).unlink()
        expect_failure(missing_file_root, FILES["shared_contract"])

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

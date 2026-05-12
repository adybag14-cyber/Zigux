#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 11 DesignWare watchdog ownership packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase11-dw-wdt-packet.py"

FILES = {
    "plan_note": "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "validation_matrix": "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "survey_note": "Documentation/zigux/phase11-dw-wdt-survey.md",
    "teardown_note": "Documentation/zigux/phase11-dw-wdt-teardown-note.md",
    "manifest": "zigux/tests/phase11_dw_wdt_manifest.json",
}

MARKERS = {
    "plan_note": [
        "# Phase 11 DesignWare Watchdog Platform Registration Plan",
        "This note records the next bounded follow-up for the landed Phase 11 DesignWare watchdog packet on current `master`.",
        "The live repository already ships a bounded `dw_wdt` packet under the DesignWare lane:",
        "`drivers/watchdog/dw_wdt.zig` keeps fixed and custom TOP timeout windows, reset-versus-IRQ timeout selection, register-image transitions, probe-time bookkeeping, and the registration-facing handoff reviewable",
        "That means the honest next step is no longer to invent a first DesignWare packet.",
        "Keep the next implementation bounded to one acquisition-facing scaffold inside the existing DesignWare packet without claiming a full probe path.",
        "3. reuse the existing ordering around `platform_set_drvdata`, timeout-programming intent, stop-on-reboot intent, restart-priority sequencing, and `watchdog_register_device`",
        "- `drivers/watchdog/dw_wdt.zig`",
        "- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
        "If neither acquisition branch lands yet, keep this note aligned with the already-landed DesignWare packet instead of reopening shared Phase 11 reminder surfaces.",
    ],
    "validation_matrix": [
        "# Phase 11 DesignWare Watchdog Validation Matrix",
        "active watchdog continuity for this matrix and its coupled survey packet is `P11-L05`",
        "registration-facing and pre-registration platform handoff",
        "keep this handoff truthful while the next step stays limited to one platform-backed registration scaffold that reuses this matrix as the hardware-validation plan",
    ],
    "survey_note": [
        "# Phase 11 DesignWare Watchdog Survey",
        "The remaining simple-driver gap is the next ready step already hinted at by the starter: attach the bounded registration-facing handoff and its already-recorded registration-order scaffold to platform-backed registration scaffolding",
        "This cleanup packet now carries lane identity `P11-L05`",
    ],
    "teardown_note": [
        "# Phase 11 DesignWare Watchdog Teardown Note",
        "`stop()` owns the reset-control split",
        "keep this note tied only to `drivers/watchdog/dw_wdt.zig` and its directly coupled remove or teardown checks in `zigux/tests/phase11_dw_wdt.zig` and `drivers/watchdog/dw_wdt_verify.zig`",
    ],
    "manifest": [
        '"lane_key": "P11-L05"',
        '"id": "phase11-dw-wdt-platform-registration-scaffold"',
        '"status": "ready_next"',
        '"zigux_destination": "drivers/watchdog/dw_wdt.zig"',
    ],
}

SELF_TEST_CASE_COUNT = 8


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
            (FILES["plan_note"], MARKERS["plan_note"][6]),
            (FILES["validation_matrix"], MARKERS["validation_matrix"][3]),
            (FILES["survey_note"], MARKERS["survey_note"][1]),
            (FILES["teardown_note"], MARKERS["teardown_note"][2]),
            (FILES["manifest"], MARKERS["manifest"][0]),
            (FILES["manifest"], MARKERS["manifest"][1]),
            (FILES["manifest"], MARKERS["manifest"][2]),
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
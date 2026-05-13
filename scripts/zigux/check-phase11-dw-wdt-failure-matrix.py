#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

PLAN_NOTE_PATH = Path("Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md")
VALIDATION_MATRIX_PATH = Path("Documentation/zigux/phase11-dw-wdt-validation-matrix.md")
TEARDOWN_NOTE_PATH = Path("Documentation/zigux/phase11-dw-wdt-teardown-note.md")
VERIFY_REPLAY_PATH = Path("drivers/watchdog/dw_wdt_verify.zig")

REQUIRED_PLAN_MARKERS = (
    "# Phase 11 DesignWare Watchdog Platform Registration Plan",
    "The current tree does not carry a landed DesignWare watchdog packet yet.",
    "failure-mode parity should stay paired with `drivers/watchdog/dw_wdt_verify.zig`",
    "focused Zig tests for the new acquisition-order summary or summaries only after a real scaffold lands",
    "a survey, teardown note, validation matrix, manifest, or replay update only if that new scaffold actually lands",
    "Phase 11 shared validation replay only as a truthfulness check",
)

PARKED_MATRIX_PATHS = (
    VALIDATION_MATRIX_PATH,
    TEARDOWN_NOTE_PATH,
    VERIFY_REPLAY_PATH,
)

SELF_TEST_CASE_COUNT = len(REQUIRED_PLAN_MARKERS) + len(PARKED_MATRIX_PATHS) + 1


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path.as_posix()}")
    return path.read_text(encoding="utf-8")


def check_plan_note(root: Path) -> None:
    note = read_text(root, PLAN_NOTE_PATH)
    for marker in REQUIRED_PLAN_MARKERS:
        if marker not in note:
            raise CheckError(
                f"missing marker in {PLAN_NOTE_PATH.as_posix()}: {marker}"
            )


def check_parked_absence(root: Path) -> None:
    for relative_path in PARKED_MATRIX_PATHS:
        if (root / relative_path).exists():
            raise CheckError(
                "parked DesignWare matrix artifact unexpectedly present: "
                f"{relative_path.as_posix()}"
            )


def run_check(root: Path) -> None:
    check_plan_note(root)
    check_parked_absence(root)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / PLAN_NOTE_PATH, "\n".join(REQUIRED_PLAN_MARKERS) + "\n")


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


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_dw_wdt_failure_matrix_"))
    try:
        build_self_test_fixture(tmpdir)
        run_check(tmpdir)

        for marker in REQUIRED_PLAN_MARKERS:
            plan_path = tmpdir / PLAN_NOTE_PATH
            plan_path.write_text(
                plan_path.read_text(encoding="utf-8").replace(marker + "\n", "", 1),
                encoding="utf-8",
            )
            expect_failure(tmpdir, marker)
            build_self_test_fixture(tmpdir)

        for relative_path in PARKED_MATRIX_PATHS:
            write(tmpdir / relative_path, "stale parked artifact\n")
            expect_failure(tmpdir, relative_path.as_posix())
            build_self_test_fixture(tmpdir)
            (tmpdir / relative_path).unlink()

        shutil.rmtree(tmpdir / PLAN_NOTE_PATH.parent, ignore_errors=True)
        expect_failure(tmpdir, PLAN_NOTE_PATH.as_posix())

        print("PHASE11_DW_WDT_FAILURE_MATRIX_SELF_TEST=pass")
        print(
            f"PHASE11_DW_WDT_FAILURE_MATRIX_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}"
        )
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the parked Phase 11 dw_wdt matrix and teardown continuity surface."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root)
    except CheckError as exc:
        print(f"PHASE11_DW_WDT_FAILURE_MATRIX=fail: {exc}")
        return 1

    print("PHASE11_DW_WDT_FAILURE_MATRIX=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

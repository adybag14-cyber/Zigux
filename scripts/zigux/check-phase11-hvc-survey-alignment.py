#!/usr/bin/env python3
"""Fail-closed checker for the focused Phase 11 HVC survey alignment markers."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SURVEY_NOTE = "Documentation/zigux/phase11-hvc-console-survey.md"
SURVEY_PACKET_CHECKER = "scripts/zigux/check-phase11-hvc-survey-packet.py"

SURVEY_NOTE_MARKERS = [
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "exported hvc helper signature proof",
    "dedicated HVC survey packet",
    "scripts-root sync",
]

SURVEY_PACKET_CHECKER_MARKERS = [
    '"survey_note": "Documentation/zigux/phase11-hvc-console-survey.md"',
    '"sysrq_helper": "drivers/tty/hvc/hvc_console_sysrq.zig"',
    "exported hvc helper signature proof",
    "make -C zigux phase11-hvc-survey",
]

SELF_TEST_CASE_COUNT = 7


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(relative_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {relative_path}: {marker}")


def run_check(root: Path) -> None:
    expect_markers(SURVEY_NOTE, read_text(root, SURVEY_NOTE), SURVEY_NOTE_MARKERS)
    expect_markers(
        SURVEY_PACKET_CHECKER,
        read_text(root, SURVEY_PACKET_CHECKER),
        SURVEY_PACKET_CHECKER_MARKERS,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SURVEY_NOTE, "\n".join(SURVEY_NOTE_MARKERS) + "\n")
    write(root / SURVEY_PACKET_CHECKER, "\n".join(SURVEY_PACKET_CHECKER_MARKERS) + "\n")


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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_survey_alignment_"))
    try:
        build_self_test_fixture(tmpdir)
        run_check(tmpdir)

        note = tmpdir / SURVEY_NOTE
        note.write_text(
            note.read_text(encoding="utf-8").replace("scripts-root sync\n", ""),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "scripts-root sync")
        build_self_test_fixture(tmpdir)

        checker = tmpdir / SURVEY_PACKET_CHECKER
        checker.write_text(
            checker.read_text(encoding="utf-8").replace(
                "exported hvc helper signature proof\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "exported hvc helper signature proof")
        build_self_test_fixture(tmpdir)

        checker.write_text(
            checker.read_text(encoding="utf-8").replace(
                "make -C zigux phase11-hvc-survey\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "make -C zigux phase11-hvc-survey")
        build_self_test_fixture(tmpdir)

        note.unlink()
        expect_failure(tmpdir, SURVEY_NOTE)

        print("PHASE11_HVC_SURVEY_ALIGNMENT_SELF_TEST=pass")
        print(
            f"PHASE11_HVC_SURVEY_ALIGNMENT_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}"
        )
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
        print(f"PHASE11_HVC_SURVEY_ALIGNMENT=fail: {exc}")
        return 1

    print("PHASE11_HVC_SURVEY_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

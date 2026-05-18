#!/usr/bin/env python3
"""Fail-close guard for the Phase 11 broad shared-summary gap note."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
DOC_PATH = Path("Documentation/zigux/phase11-shared-summary-gap.md")

REQUIRED_MARKERS = (
    "`PHASE11_SHARED_SUMMARY_GAP=phase11_broad_reminders_missing`",
    "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
    "`Documentation/zigux/phase11-hvc-console-survey.md`",
    "`Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`",
    "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "Current broad shared reminders do not currently materialize",
    "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
    "`zigux/tests/phase11_build.zig`",
    "`make -C zigux phase11-contract`",
    "`drivers/tty/hvc/hvc_console_verify.zig`",
    "`zigux/tests/phase11_hvc_console_manifest.json`",
    "Do not use the broad shared reminders listed above as Phase 11 authority",
)

FORBIDDEN_MARKERS = (
    "whole simple-driver tranche is closed",
    "shipped Phase 11 shared-summary checker",
)


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def run_check(root: Path) -> None:
    text = read_text(root / DOC_PATH)
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            raise CheckError(f"missing required marker: {marker}")
    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            raise CheckError(f"forbidden marker present: {marker}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(
        root / DOC_PATH,
        "\n".join(
            [
                "# Phase 11 Shared Summary Gap",
                "",
                "`PHASE11_SHARED_SUMMARY_GAP=phase11_broad_reminders_missing`",
                "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
                "`Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
                "`Documentation/zigux/phase11-hvc-console-survey.md`",
                "`Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`",
                "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
                "`Documentation/zigux/README.md`",
                "`Documentation/zigux/review-checklist.md`",
                "`scripts/zigux/README.md`",
                "`zigux/tests/README.md`",
                "Current broad shared reminders do not currently materialize",
                "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
                "`zigux/tests/phase11_build.zig`",
                "`make -C zigux phase11-contract`",
                "`drivers/tty/hvc/hvc_console_verify.zig`",
                "`zigux/tests/phase11_hvc_console_manifest.json`",
                "Do not use the broad shared reminders listed above as Phase 11 authority until they are refreshed in a bounded same-lane pass.",
                "",
            ]
        ),
    )


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_shared_summary_gap_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        missing_marker = tmpdir / "missing_marker"
        shutil.copytree(fixture, missing_marker, dirs_exist_ok=True)
        write(
            missing_marker / DOC_PATH,
            read_text(missing_marker / DOC_PATH).replace(
                "`scripts/zigux/check-phase11-shared-summary-surfaces.py`\n",
                "",
            ),
        )
        expect_failure(missing_marker, "check-phase11-shared-summary-surfaces.py")

        forbidden = tmpdir / "forbidden"
        shutil.copytree(fixture, forbidden, dirs_exist_ok=True)
        write(
            forbidden / DOC_PATH,
            read_text(forbidden / DOC_PATH)
            + "This note says the whole simple-driver tranche is closed.\n",
        )
        expect_failure(forbidden, "whole simple-driver tranche is closed")

        missing_file = tmpdir / "missing_file"
        shutil.copytree(fixture, missing_file, dirs_exist_ok=True)
        (missing_file / DOC_PATH).unlink()
        expect_failure(missing_file, str(DOC_PATH))

        print("PHASE11_SHARED_SUMMARY_GAP_SELF_TEST=pass")
        print("PHASE11_SHARED_SUMMARY_GAP_SELF_TEST_CASE_COUNT=4")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root)
    except CheckError as exc:
        print(f"PHASE11_SHARED_SUMMARY_GAP=fail: {exc}")
        return 1

    print("PHASE11_SHARED_SUMMARY_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

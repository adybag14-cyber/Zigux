#!/usr/bin/env python3
"""Fail-close guard for the Phase 11 ABI layout assertion suite survey."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
DOC_PATH = Path("Documentation/zigux/phase11-abi-layout-assertion-suite-survey.md")

REQUIRED_MARKERS = (
    "`PHASE11_ABI_LAYOUT_ASSERTION_SUITE_STATUS=returned_layout_assert_suite_broad_reminders_still_missing`",
    "`P11-L13`",
    "`zigux/helpers/layout_assert.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
    "`drivers/tty/hvc/hvc_console.h`",
    "`drivers/tty/hvc/hvc_console.zig`",
    "`Documentation/zigux/phase11-uapi-header-parity-survey.md`",
    "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`",
    "`Documentation/zigux/phase11-uapi-header-parity-hv-ops-followup.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`zigux/tests/phase11_uapi_header_parity_survey.zig`",
    "`zigux/tests/phase11_uapi_header_parity_manifest.json`",
    "`zigux/tests/phase11_build.zig`",
    "machine-checked ABI evidence",
    "broader reminder layer still under-describes",
    "missing HVC ABI proof code",
)

FORBIDDEN_MARKERS = (
    "whole-Phase-11 closure",
    "the older shared replay family has returned",
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
                "# Phase 11 ABI Layout Assertion Suite Survey",
                "",
                "`PHASE11_ABI_LAYOUT_ASSERTION_SUITE_STATUS=returned_layout_assert_suite_broad_reminders_still_missing`",
                "`P11-L13`",
                "`zigux/helpers/layout_assert.zig`",
                "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
                "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
                "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
                "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
                "`drivers/tty/hvc/hvc_console.h`",
                "`drivers/tty/hvc/hvc_console.zig`",
                "`Documentation/zigux/phase11-uapi-header-parity-survey.md`",
                "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`",
                "`Documentation/zigux/phase11-uapi-header-parity-hv-ops-followup.md`",
                "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
                "`Documentation/zigux/README.md`",
                "`Documentation/zigux/review-checklist.md`",
                "`scripts/zigux/README.md`",
                "`zigux/tests/README.md`",
                "`zigux/tests/phase11_uapi_header_parity_survey.zig`",
                "`zigux/tests/phase11_uapi_header_parity_manifest.json`",
                "`zigux/tests/phase11_build.zig`",
                "machine-checked ABI evidence",
                "broader reminder layer still under-describes",
                "missing HVC ABI proof code",
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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_abi_layout_assertion_suite_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        missing_marker = tmpdir / "missing_marker"
        shutil.copytree(fixture, missing_marker, dirs_exist_ok=True)
        write(
            missing_marker / DOC_PATH,
            read_text(missing_marker / DOC_PATH).replace(
                "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`\n",
                "",
            ),
        )
        expect_failure(missing_marker, "phase11_hvc_hv_ops_layout_proof.zig")

        forbidden = tmpdir / "forbidden"
        shutil.copytree(fixture, forbidden, dirs_exist_ok=True)
        write(
            forbidden / DOC_PATH,
            read_text(forbidden / DOC_PATH)
            + "This note claims the older shared replay family has returned.\n",
        )
        expect_failure(forbidden, "the older shared replay family has returned")

        missing_file = tmpdir / "missing_file"
        shutil.copytree(fixture, missing_file, dirs_exist_ok=True)
        (missing_file / DOC_PATH).unlink()
        expect_failure(missing_file, str(DOC_PATH))

        print("PHASE11_ABI_LAYOUT_ASSERTION_SUITE_SURVEY_SELF_TEST=pass")
        print("PHASE11_ABI_LAYOUT_ASSERTION_SUITE_SURVEY_SELF_TEST_CASE_COUNT=4")
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
        print(f"PHASE11_ABI_LAYOUT_ASSERTION_SUITE_SURVEY=fail: {exc}")
        return 1

    print("PHASE11_ABI_LAYOUT_ASSERTION_SUITE_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

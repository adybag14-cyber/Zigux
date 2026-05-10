#!/usr/bin/env python3
"""Fail-closed checker for Phase 9 trace-events module-slice/build alignment."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MODULE_SLICE = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"
PHASE9_BUILD = "zigux/tests/phase9_build.zig"

MODULE_SLICE_REQUIRED_MARKERS = [
    "samples/zigux/runtime_trace_events_loader.zig",
    "phase9-runtime-trace-events-tests",
    "phase9-runtime-trace-events-loader-tests",
    "zig build test --build-file zigux/tests/phase9_build.zig --summary all",
]

MODULE_SLICE_FORBIDDEN_MARKERS = [
    "no trace-events loader target",
    "without claiming a shared runtime-loader binding or a trace-events loader target in the shared build packet",
    "phase9-runtime-trace-events-survey-tests` while still carrying no trace-events loader target",
]

PHASE9_BUILD_REQUIRED_MARKERS = [
    "runtime_trace_events_loader_module",
    "phase9-runtime-trace-events-loader-tests",
    "run_runtime_trace_events_loader_tests.step",
    '"phase9-runtime-trace-events-tests"',
]

SELF_TEST_CASE_COUNT = 6


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


def expect_forbidden_markers_absent(relative_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            raise CheckError(f"stale marker still present in {relative_path}: {marker}")


def run_check(root: Path) -> None:
    module_slice = read_text(root, MODULE_SLICE)
    phase9_build = read_text(root, PHASE9_BUILD)

    expect_markers(MODULE_SLICE, module_slice, MODULE_SLICE_REQUIRED_MARKERS)
    expect_forbidden_markers_absent(MODULE_SLICE, module_slice, MODULE_SLICE_FORBIDDEN_MARKERS)
    expect_markers(PHASE9_BUILD, phase9_build, PHASE9_BUILD_REQUIRED_MARKERS)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(
        root / MODULE_SLICE,
        "\n".join(MODULE_SLICE_REQUIRED_MARKERS)
        + "\nthis shared build includes `phase9-runtime-trace-events-sample-tests`, "
        + "`phase9-runtime-trace-events-module-tests`, `phase9-runtime-trace-events-diff-tests`, "
        + "`phase9-runtime-trace-events-loader-tests`, and `phase9-runtime-trace-events-survey-tests`\n",
    )
    write(root / PHASE9_BUILD, "\n".join(PHASE9_BUILD_REQUIRED_MARKERS) + "\n")


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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase9_trace_events_build_alignment_"))
    try:
        build_self_test_fixture(tmpdir)
        run_check(tmpdir)

        module_slice = tmpdir / MODULE_SLICE
        module_slice.write_text(
            module_slice.read_text(encoding="utf-8").replace(
                "phase9-runtime-trace-events-loader-tests", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "phase9-runtime-trace-events-loader-tests")
        build_self_test_fixture(tmpdir)

        module_slice.write_text(
            module_slice.read_text(encoding="utf-8")
            + "phase9-runtime-trace-events-survey-tests` while still carrying no trace-events loader target\n",
            encoding="utf-8",
        )
        expect_failure(tmpdir, "stale marker still present")
        build_self_test_fixture(tmpdir)

        phase9_build = tmpdir / PHASE9_BUILD
        phase9_build.write_text(
            phase9_build.read_text(encoding="utf-8").replace(
                "run_runtime_trace_events_loader_tests.step\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "run_runtime_trace_events_loader_tests.step")
        build_self_test_fixture(tmpdir)

        module_slice.unlink()
        expect_failure(tmpdir, MODULE_SLICE)
        build_self_test_fixture(tmpdir)

        phase9_build.unlink()
        expect_failure(tmpdir, PHASE9_BUILD)

        print("PHASE9_TRACE_EVENTS_BUILD_ALIGNMENT_SELF_TEST=pass")
        print(
            f"PHASE9_TRACE_EVENTS_BUILD_ALIGNMENT_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}"
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
        print(f"PHASE9_TRACE_EVENTS_BUILD_ALIGNMENT=fail: {exc}")
        return 1

    print("PHASE9_TRACE_EVENTS_BUILD_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

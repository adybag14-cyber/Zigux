#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 HVC poll/sysrq boundary packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = (
    Path(__file__).resolve().parents[3]
    if len(Path(__file__).resolve().parents) > 3
    else Path.cwd()
)

DRIVER_PATH = Path("drivers/tty/hvc/hvc_console.zig")
SURVEY_PATH = Path("Documentation/zigux/phase11-hvc-console-survey.md")
MATRIX_PATH = Path("Documentation/zigux/phase11-hvc-console-validation-matrix.md")
VERIFY_BOUNDARY_PATH = Path("Documentation/zigux/phase11-hvc-verify-helper-boundary.md")

DRIVER_MARKERS = (
    "pub const PollDrainOrderSummary = struct {",
    "pending_sysrq_dispatch_separate: bool,",
    "tty_wakeup_precedes_flip_push: bool,",
    "read_activity_resets_timeout: bool,",
    "pub fn summarizePollDrainOrder(request: PollDrainOrderRequest) PollDrainOrderSummary {",
    'test "phase11 hvc console keeps __hvc_poll drain-order summary reviewable" {',
    'test "phase11 hvc console keeps wakeup-only poll retries distinct from read-driven timeout reset" {',
)

SURVEY_MARKERS = (
    "live sysrq dispatch",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "standalone targetless-unregister witness pair",
)

MATRIX_MARKERS = (
    "`__hvc_poll` drain-order",
    "live sysrq dispatch",
    "targetless-unregister witness explicitly separate",
)

VERIFY_BOUNDARY_MARKERS = (
    "error.NotifierDispatchRequiresTtyRegistration",
    "targetless_dispatch_without_notifier",
    "sanitized targetless sysrq path",
)


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def require_markers(path: Path, markers: tuple[str, ...]) -> None:
    text = read_text(path)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {path}: {marker}")


def run_check(root: Path) -> None:
    require_markers(root / DRIVER_PATH, DRIVER_MARKERS)
    require_markers(root / SURVEY_PATH, SURVEY_MARKERS)
    require_markers(root / MATRIX_PATH, MATRIX_MARKERS)
    require_markers(root / VERIFY_BOUNDARY_PATH, VERIFY_BOUNDARY_MARKERS)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


FIXTURE_DRIVER_TEXT = """pub const PollDrainOrderSummary = struct {
    pending_sysrq_dispatch_separate: bool,
    tty_wakeup_precedes_flip_push: bool,
    read_activity_resets_timeout: bool,
};

pub fn summarizePollDrainOrder(request: PollDrainOrderRequest) PollDrainOrderSummary {
    _ = request;
    return undefined;
}

test \"phase11 hvc console keeps __hvc_poll drain-order summary reviewable\" {}
test \"phase11 hvc console keeps wakeup-only poll retries distinct from read-driven timeout reset\" {}
"""

FIXTURE_SURVEY_TEXT = """live sysrq dispatch
`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
standalone targetless-unregister witness pair
"""

FIXTURE_MATRIX_TEXT = """`__hvc_poll` drain-order
live sysrq dispatch
targetless-unregister witness explicitly separate
"""

FIXTURE_VERIFY_BOUNDARY_TEXT = """error.NotifierDispatchRequiresTtyRegistration
targetless_dispatch_without_notifier
sanitized targetless sysrq path
"""


def build_fixture(root: Path) -> None:
    write(root / DRIVER_PATH, FIXTURE_DRIVER_TEXT)
    write(root / SURVEY_PATH, FIXTURE_SURVEY_TEXT)
    write(root / MATRIX_PATH, FIXTURE_MATRIX_TEXT)
    write(root / VERIFY_BOUNDARY_PATH, FIXTURE_VERIFY_BOUNDARY_TEXT)


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_poll_sysrq_boundary_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        missing_driver = tmpdir / "missing_driver"
        shutil.copytree(fixture, missing_driver, dirs_exist_ok=True)
        write(
            missing_driver / DRIVER_PATH,
            read_text(missing_driver / DRIVER_PATH).replace(
                "pending_sysrq_dispatch_separate: bool,\n",
                "",
                1,
            ),
        )
        expect_failure(missing_driver, "pending_sysrq_dispatch_separate: bool,")
        case_count += 1

        missing_matrix = tmpdir / "missing_matrix"
        shutil.copytree(fixture, missing_matrix, dirs_exist_ok=True)
        write(
            missing_matrix / MATRIX_PATH,
            read_text(missing_matrix / MATRIX_PATH).replace(
                "targetless-unregister witness explicitly separate\n",
                "",
                1,
            ),
        )
        expect_failure(missing_matrix, "targetless-unregister witness explicitly separate")
        case_count += 1

        missing_boundary = tmpdir / "missing_boundary"
        shutil.copytree(fixture, missing_boundary, dirs_exist_ok=True)
        write(
            missing_boundary / VERIFY_BOUNDARY_PATH,
            read_text(missing_boundary / VERIFY_BOUNDARY_PATH).replace(
                "targetless_dispatch_without_notifier\n",
                "",
                1,
            ),
        )
        expect_failure(missing_boundary, "targetless_dispatch_without_notifier")
        case_count += 1

        print("PHASE11_HVC_POLL_SYSRQ_BOUNDARY_SELF_TEST=pass")
        print(f"PHASE11_HVC_POLL_SYSRQ_BOUNDARY_SELF_TEST_CASE_COUNT={case_count}")
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
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_HVC_POLL_SYSRQ_BOUNDARY=fail: {exc}")
        return 1

    print("PHASE11_HVC_POLL_SYSRQ_BOUNDARY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

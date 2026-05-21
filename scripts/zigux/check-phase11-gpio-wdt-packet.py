#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 gpio watchdog packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SURVEY_PATH = Path("Documentation/zigux/phase11-gpio-wdt-survey.md")
MODULE_SLICE_PATH = Path("Documentation/zigux/phase11-gpio-wdt-module-slice.md")
TEARDOWN_NOTE_PATH = Path("Documentation/zigux/phase11-gpio-wdt-teardown-note.md")
REMOVE_HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md")
VALIDATION_MATRIX_PATH = Path("Documentation/zigux/phase11-gpio-wdt-validation-matrix.md")
DRIVER_PATH = Path("drivers/watchdog/gpio_wdt.zig")
PROOF_PATH = Path("zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig")

SURVEY_MARKERS = (
    "`PHASE11_GPIO_WDT_SURVEY_STATUS=current_head_driver_docs_and_proof_packet_truthful`",
    "current authenticated contents readback keeps the bounded gpio watchdog packet",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
    "That current packet now also keeps the bounded remove-handoff packet explicit",
    "focused replay recovery or another equally small truthfulness repair",
)

MODULE_SLICE_MARKERS = (
    "`registerDeviceCallSummary()` keeps the first bounded",
    "`registerDeviceFailureSummary()` keeps the bounded register-device failure",
    "`summarizeTeardown()` keeps the host-free teardown summary visible",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` keeps the current remove-handoff packet explicit",
    "one equally small gpio watchdog replay, manifest, checker, or validation-truthfulness repair",
)

TEARDOWN_MARKERS = (
    "`PHASE11_GPIO_WDT_TEARDOWN_STATUS=teardown_handoff_driver_docs_and_proof_packet`",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
    "as the companion surface that keeps the bounded remove-handoff packet explicit",
    "The returned driver-backed packet also keeps the stop-transition",
)

REMOVE_HANDOFF_MARKERS = (
    "`PHASE11_GPIO_WDT_REMOVE_HANDOFF_STATUS=driver_docs_and_proof_remove_handoff_truthful`",
    "The current remove-handoff-facing gpio packet on `master` is:",
    "`registerDeviceFailureSummary()` keeps register-device failure cues reviewable",
    "`requestStop()` keeps the bounded nowayout, stopped, and kept-running stop",
    "`summarizeTeardown()` keeps the stop-request, register-device-failure, and",
)

VALIDATION_MATRIX_MARKERS = (
    "`PHASE11_GPIO_WDT_STATUS=driver_docs_and_proof_packet_truthful`",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
    "remove-handoff note: `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
    "The next honest gpio-only follow-up is still one equally small replay,",
)

DRIVER_MARKERS = (
    "pub const WatchdogDrvdataCheckpointSummary = struct {",
    "pub const RegisterDeviceFailureSummary = struct {",
    "pub const RebootGlueCheckpointSummary = struct {",
    "pub const TeardownSummary = struct {",
    "pub fn watchdogDrvdataCheckpointSummary(self: *const Self) WatchdogDrvdataCheckpointSummary {",
    "pub fn registerDeviceFailureSummary(self: *const Self, nowayout: bool) RegisterDeviceFailureSummary {",
    "pub fn rebootGlueCheckpointSummary(self: *const Self) RebootGlueCheckpointSummary {",
    "pub fn summarizeTeardown(self: *Self, nowayout: bool) TeardownSummary {",
    'test "phase11 gpio watchdog keeps remove-handoff teardown reviewable without live unregister behavior" {',
)

PROOF_MARKERS = (
    'test "phase11 gpio watchdog keeps register-device call glued to reboot boundary" {',
    'test "phase11 gpio watchdog keeps remove-handoff teardown reviewable without live unregister behavior" {',
)

FORBIDDEN_SURVEY_MARKERS = (
    "`zigux/tests/phase11_gpio_wdt.zig` is directly readable on current `master`",
    "`zigux/Makefile` now exposes `make -C zigux phase11-gpio-wdt`",
)


class CheckError(RuntimeError):
    pass


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path.as_posix()}")
    return path.read_text(encoding="utf-8")


def require_markers(root: Path, relative_path: Path, label: str, markers: tuple[str, ...]) -> None:
    text = normalize_whitespace(read_text(root, relative_path))
    for marker in markers:
        if normalize_whitespace(marker) not in text:
            raise CheckError(f"missing {label} marker: {marker}")


def require_forbidden_absent(root: Path, relative_path: Path, label: str, markers: tuple[str, ...]) -> None:
    text = normalize_whitespace(read_text(root, relative_path))
    for marker in markers:
        if normalize_whitespace(marker) in text:
            raise CheckError(f"forbidden {label} marker: {marker}")


def run_check(root: Path) -> None:
    require_markers(root, SURVEY_PATH, "survey", SURVEY_MARKERS)
    require_forbidden_absent(root, SURVEY_PATH, "survey", FORBIDDEN_SURVEY_MARKERS)
    require_markers(root, MODULE_SLICE_PATH, "module slice", MODULE_SLICE_MARKERS)
    require_markers(root, TEARDOWN_NOTE_PATH, "teardown note", TEARDOWN_MARKERS)
    require_markers(root, REMOVE_HANDOFF_NOTE_PATH, "remove handoff note", REMOVE_HANDOFF_MARKERS)
    require_markers(root, VALIDATION_MATRIX_PATH, "validation matrix", VALIDATION_MATRIX_MARKERS)
    require_markers(root, DRIVER_PATH, "driver", DRIVER_MARKERS)
    require_markers(root, PROOF_PATH, "proof", PROOF_MARKERS)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(
        root / SURVEY_PATH,
        """# Phase 11 GPIO Watchdog Survey

- `PHASE11_GPIO_WDT_SURVEY_STATUS=current_head_driver_docs_and_proof_packet_truthful`
- current authenticated contents readback keeps the bounded gpio watchdog packet reviewable through:
  - `drivers/watchdog/gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
  - `Documentation/zigux/phase11-gpio-wdt-survey.md`
  - `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  - `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
  - `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
  - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- current authenticated contents readback still does not rematerialize the older wider replay and manifest route surfaces
- That current packet now also keeps the bounded remove-handoff packet explicit beside the existing watchdog-drvdata ownership handoff and reboot-glue checkpoint without overstating live unregister or shutdown behavior.
- If the current smaller packet needs one more driver-local follow-up first, keep it to focused replay recovery or another equally small truthfulness repair.
""",
    )
    write(
        root / MODULE_SLICE_PATH,
        """# Phase 11 GPIO Watchdog Module Slice

- `registerDeviceCallSummary()` keeps the first bounded `devm_watchdog_register_device()` request surface visible without claiming live watchdog-core registration.
- `registerDeviceFailureSummary()` keeps the bounded register-device failure cues explicit without promoting them into live watchdog-core behavior.
- `summarizeTeardown()` keeps the host-free teardown summary visible without claiming reboot-backed shutdown execution.
- The same review packet also keeps teardown and failure-mode parity explicit in bounded form while the paired `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` keeps the current remove-handoff packet explicit without claiming live platform cleanup callbacks, platform-driver removal, watchdog-core unregister side effects, or host-backed shutdown behavior.
- The next honest bounded step remains one equally small gpio watchdog replay, manifest, checker, or validation-truthfulness repair inside this returned driver-plus-docs-plus-proof packet, rather than new runtime behavior.
""",
    )
    write(
        root / TEARDOWN_NOTE_PATH,
        """# Phase 11 GPIO Watchdog Teardown Note

- `PHASE11_GPIO_WDT_TEARDOWN_STATUS=teardown_handoff_driver_docs_and_proof_packet`
- The current teardown-facing GPIO packet on `master` is:
  - `drivers/watchdog/gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
  - `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  - `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
  - `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
  - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` as the companion surface that keeps the bounded remove-handoff packet explicit without claiming live platform cleanup callbacks, platform-driver removal, watchdog-core unregister side effects, or host-backed shutdown execution
- The returned driver-backed packet also keeps the stop-transition, reboot-glue handoff, remove-handoff boundary, and teardown-ownership boundaries visible without claiming live execution.
""",
    )
    write(
        root / REMOVE_HANDOFF_NOTE_PATH,
        """# Phase 11 GPIO Watchdog Remove Handoff Note

- `PHASE11_GPIO_WDT_REMOVE_HANDOFF_STATUS=driver_docs_and_proof_remove_handoff_truthful`
- The current remove-handoff-facing gpio packet on `master` is:
  - `drivers/watchdog/gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
  - `Documentation/zigux/phase11-gpio-wdt-survey.md`
  - `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  - `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
  - `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
  - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `registerDeviceFailureSummary()` keeps register-device failure cues reviewable before any later remove-hook execution claim.
- `requestStop()` keeps the bounded nowayout, stopped, and kept-running stop split explicit before any platform cleanup callback claim.
- `summarizeTeardown()` keeps the stop-request, register-device-failure, and reboot-glue checkpoint cues reviewable as a host-free remove-handoff packet.
""",
    )
    write(
        root / VALIDATION_MATRIX_PATH,
        """# Phase 11 GPIO Watchdog Validation Matrix

- `PHASE11_GPIO_WDT_STATUS=driver_docs_and_proof_packet_truthful`
- The current gpio watchdog matrix packet on `master` is:
  - `drivers/watchdog/gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
  - `Documentation/zigux/phase11-gpio-wdt-survey.md`
  - `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  - `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
  - `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
  - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- remove-handoff note: `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` keeps the bounded remove-handoff packet explicit without claiming live platform cleanup callbacks, platform-driver removal, watchdog-core unregister, or host-backed shutdown execution.
- The next honest gpio-only follow-up is still one equally small replay, manifest, checker, or validation-truthfulness repair, rather than new runtime behavior.
""",
    )
    write(
        root / DRIVER_PATH,
        """pub const WatchdogDrvdataCheckpointSummary = struct {};
pub const RegisterDeviceFailureSummary = struct {};
pub const RebootGlueCheckpointSummary = struct {};
pub const TeardownSummary = struct {};
pub fn watchdogDrvdataCheckpointSummary(self: *const Self) WatchdogDrvdataCheckpointSummary {}
pub fn registerDeviceFailureSummary(self: *const Self, nowayout: bool) RegisterDeviceFailureSummary {}
pub fn rebootGlueCheckpointSummary(self: *const Self) RebootGlueCheckpointSummary {}
pub fn summarizeTeardown(self: *Self, nowayout: bool) TeardownSummary {}
test "phase11 gpio watchdog keeps remove-handoff teardown reviewable without live unregister behavior" {}
""",
    )
    write(
        root / PROOF_PATH,
        """const std = @import("std");
test "phase11 gpio watchdog keeps register-device call glued to reboot boundary" {}
test "phase11 gpio watchdog keeps remove-handoff teardown reviewable without live unregister behavior" {}
""",
    )


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected {expected_fragment!r}, got {str(exc)!r}") from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_gpio_wdt_packet_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_fixture(fixture_root)
        run_check(fixture_root)

        survey_text = read_text(fixture_root, SURVEY_PATH)
        write(
            fixture_root / SURVEY_PATH,
            survey_text.replace("`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`", "", 1),
        )
        expect_failure(fixture_root, "missing survey marker")
        build_fixture(fixture_root)

        module_text = read_text(fixture_root, MODULE_SLICE_PATH)
        write(
            fixture_root / MODULE_SLICE_PATH,
            module_text.replace(
                "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` keeps the current remove-handoff packet explicit",
                "",
                1,
            ),
        )
        expect_failure(fixture_root, "missing module slice marker")
        build_fixture(fixture_root)

        teardown_text = read_text(fixture_root, TEARDOWN_NOTE_PATH)
        write(
            fixture_root / TEARDOWN_NOTE_PATH,
            teardown_text.replace(
                "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` as the companion surface that keeps the bounded remove-handoff packet explicit",
                "",
                1,
            ),
        )
        expect_failure(fixture_root, "missing teardown note marker")
        build_fixture(fixture_root)

        remove_text = read_text(fixture_root, REMOVE_HANDOFF_NOTE_PATH)
        write(
            fixture_root / REMOVE_HANDOFF_NOTE_PATH,
            remove_text.replace("`requestStop()` keeps the bounded nowayout, stopped, and kept-running stop", "", 1),
        )
        expect_failure(fixture_root, "missing remove handoff note marker")
        build_fixture(fixture_root)

        matrix_text = read_text(fixture_root, VALIDATION_MATRIX_PATH)
        write(
            fixture_root / VALIDATION_MATRIX_PATH,
            matrix_text.replace(
                "remove-handoff note: `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
                "",
                1,
            ),
        )
        expect_failure(fixture_root, "missing validation matrix marker")
        build_fixture(fixture_root)

        driver_text = read_text(fixture_root, DRIVER_PATH)
        write(
            fixture_root / DRIVER_PATH,
            driver_text.replace(
                "pub fn summarizeTeardown(self: *Self, nowayout: bool) TeardownSummary {}",
                "",
                1,
            ),
        )
        expect_failure(fixture_root, "missing driver marker")
        build_fixture(fixture_root)

        write(
            fixture_root / SURVEY_PATH,
            survey_text + "\n`zigux/tests/phase11_gpio_wdt.zig` is directly readable on current `master`\n",
        )
        expect_failure(fixture_root, "forbidden survey marker")
        build_fixture(fixture_root)

        print("PHASE11_GPIO_WDT_PACKET_SELF_TEST=pass")
        print("PHASE11_GPIO_WDT_PACKET_SELF_TEST_CASES=8")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root to check")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-test cases")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root)
    except CheckError as exc:
        print(f"PHASE11_GPIO_WDT_PACKET=fail: {exc}")
        return 1

    print("PHASE11_GPIO_WDT_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
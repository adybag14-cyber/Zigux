#!/usr/bin/env python3
"""Fail-closed checker for the current-head Phase 11 gpio watchdog packet."""

from __future__ import annotations

import argparse
import tempfile
import shutil
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

SURVEY_PATH = Path("Documentation/zigux/phase11-gpio-wdt-survey.md")
MODULE_SLICE_PATH = Path("Documentation/zigux/phase11-gpio-wdt-module-slice.md")
TEARDOWN_NOTE_PATH = Path("Documentation/zigux/phase11-gpio-wdt-teardown-note.md")
REMOVE_NOTE_PATH = Path("Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md")
VALIDATION_MATRIX_PATH = Path("Documentation/zigux/phase11-gpio-wdt-validation-matrix.md")
DRIVER_PATH = Path("drivers/watchdog/gpio_wdt.zig")
PROOF_PATH = Path("zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig")
BUILD_PATH = Path("zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig")

REQUIRED_PATHS = (
    SURVEY_PATH,
    MODULE_SLICE_PATH,
    TEARDOWN_NOTE_PATH,
    REMOVE_NOTE_PATH,
    VALIDATION_MATRIX_PATH,
    DRIVER_PATH,
    PROOF_PATH,
    BUILD_PATH,
)

SURVEY_MARKERS = (
    "`PHASE11_GPIO_WDT_SURVEY_STATUS=current_head_driver_docs_and_proof_packet_truthful`",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`nowayoutPolicySummary()`",
    "`requestStop()`",
    "`summarizeTeardown()`",
)

MODULE_SLICE_MARKERS = (
    "`watchdogDrvdataCheckpointSummary()` keeps the bounded",
    "`rebootGlueCheckpointSummary()` keeps the bounded",
    "`registerDeviceCallSummary()` keeps the first bounded",
    "`registerDeviceFailureSummary()` keeps the bounded register-device failure",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig` keeps the",
    "`summarizeTeardown()` keeps the host-free teardown summary visible",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` keeps the current",
    "one equally small gpio watchdog replay, manifest, checker, or validation-truthfulness repair",
)

TEARDOWN_NOTE_MARKERS = (
    "`PHASE11_GPIO_WDT_TEARDOWN_STATUS=teardown_handoff_driver_docs_and_proof_packet`",
    "`requestStop()` and the split between watchdog-core stop policy and hardware",
    "`nowayoutPolicySummary()` as a driver-local checkpoint",
    "`registerDeviceFailureSummary()` and the teardown-facing failure-mode cues",
    "`watchdogDrvdataCheckpointSummary()` and `rebootGlueCheckpointSummary()` as",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` as the",
    "teardown handoff after descriptor preflight and the first bounded",
)

REMOVE_NOTE_MARKERS = (
    "`PHASE11_GPIO_WDT_REMOVE_HANDOFF_STATUS=driver_docs_and_proof_remove_handoff_truthful`",
    "`registerDeviceFailureSummary()` keeps register-device failure cues reviewable",
    "`requestStop()` keeps the bounded nowayout, stopped, and kept-running stop",
    "`rebootGlueCheckpointSummary()` keeps the stop-on-reboot handoff visible",
    "`summarizeTeardown()` keeps the stop-request, register-device-failure, and",
    "`summarizeRemoveHandoff()` keeps the dedicated remove-handoff summary itself",
)

VALIDATION_MATRIX_MARKERS = (
    "`PHASE11_GPIO_WDT_STATUS=driver_docs_and_proof_packet_truthful`",
    "`drivers/watchdog/gpio_wdt.zig`",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
    "`watchdogDrvdataCheckpointSummary()`",
    "`rebootGlueCheckpointSummary()`",
    "`registerDeviceCallSummary()`",
    "`registerDeviceFailureSummary()`",
    "`requestStop()`",
    "`summarizeTeardown()`",
    "focused `zig build phase11-gpio-wdt-register-device-glue-review-test`",
)

DRIVER_MARKERS = (
    "pub const WatchdogDrvdataCheckpointSummary = struct {",
    "pub const RebootGlueCheckpointSummary = struct {",
    "pub const TeardownCheckpointSummary = struct {",
    "pub const TeardownSummary = struct {",
    "pub const RemoveHandoffSummary = struct {",
    "pub fn watchdogDrvdataCheckpointSummary(self: *const Self) WatchdogDrvdataCheckpointSummary {",
    "pub fn rebootGlueCheckpointSummary(self: *const Self) RebootGlueCheckpointSummary {",
    "pub fn teardownCheckpointSummary(self: *Self, nowayout: bool) TeardownCheckpointSummary {",
    "pub fn summarizeTeardown(self: *Self, nowayout: bool) TeardownSummary {",
    "pub fn summarizeRemoveHandoff(self: *Self, nowayout: bool) RemoveHandoffSummary {",
)

PROOF_MARKERS = (
    'test "phase11 gpio watchdog keeps register-device call glued to reboot boundary" {',
    'test "phase11 gpio watchdog keeps teardown checkpoint glued to register-device failure and reboot handoff" {',
    'test "phase11 gpio watchdog keeps register-device failure summary tied to the same reboot-glue checkpoint" {',
    'test "phase11 gpio watchdog keeps remove-handoff teardown reviewable without live unregister behavior" {',
    'test "phase11 gpio watchdog keeps a dedicated remove-handoff summary reviewable" {',
    "stoppable_teardown.reboot_glue_precedes_register_device_request",
    "guarded_teardown.blocked_on_host_shutdown_execution",
    "stoppable_handoff.blocked_on_watchdog_core_unregister",
)

BUILD_MARKERS = (
    '.root_source_file = b.path("../../drivers/watchdog/gpio_wdt.zig"),',
    '.root_source_file = b.path("phase11_gpio_wdt_register_device_glue_review.zig"),',
    '"phase11-gpio-wdt-register-device-glue-review-test"',
    '"Run the bounded gpio_wdt register-device glue review packet"',
)


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def require_markers(root: Path, rel: Path, label: str, markers: tuple[str, ...]) -> None:
    text = read_text(root / rel)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing {label} marker: {marker}")


def run_check(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        if not (root / rel).is_file():
            raise CheckError(f"missing required file: {rel}")

    require_markers(root, SURVEY_PATH, "survey", SURVEY_MARKERS)
    require_markers(root, MODULE_SLICE_PATH, "module slice", MODULE_SLICE_MARKERS)
    require_markers(root, TEARDOWN_NOTE_PATH, "teardown note", TEARDOWN_NOTE_MARKERS)
    require_markers(root, REMOVE_NOTE_PATH, "remove note", REMOVE_NOTE_MARKERS)
    require_markers(root, VALIDATION_MATRIX_PATH, "validation matrix", VALIDATION_MATRIX_MARKERS)
    require_markers(root, DRIVER_PATH, "driver", DRIVER_MARKERS)
    require_markers(root, PROOF_PATH, "proof", PROOF_MARKERS)
    require_markers(root, BUILD_PATH, "build", BUILD_MARKERS)


FIXTURE_CONTENT = {
    SURVEY_PATH: """# Phase 11 GPIO Watchdog Survey

- `PHASE11_GPIO_WDT_SURVEY_STATUS=current_head_driver_docs_and_proof_packet_truthful`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `nowayoutPolicySummary()`
- `requestStop()`
- `summarizeTeardown()`
""",
    MODULE_SLICE_PATH: """# Phase 11 GPIO Watchdog Module Slice

- `watchdogDrvdataCheckpointSummary()` keeps the bounded
- `rebootGlueCheckpointSummary()` keeps the bounded
- `registerDeviceCallSummary()` keeps the first bounded
- `registerDeviceFailureSummary()` keeps the bounded register-device failure
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig` keeps the
- `summarizeTeardown()` keeps the host-free teardown summary visible
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` keeps the current
- one equally small gpio watchdog replay, manifest, checker, or validation-truthfulness repair
""",
    TEARDOWN_NOTE_PATH: """# Phase 11 GPIO Watchdog Teardown Note

- `PHASE11_GPIO_WDT_TEARDOWN_STATUS=teardown_handoff_driver_docs_and_proof_packet`
- `requestStop()` and the split between watchdog-core stop policy and hardware
- `nowayoutPolicySummary()` as a driver-local checkpoint
- `registerDeviceFailureSummary()` and the teardown-facing failure-mode cues
- `watchdogDrvdataCheckpointSummary()` and `rebootGlueCheckpointSummary()` as
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` as the
- teardown handoff after descriptor preflight and the first bounded
""",
    REMOVE_NOTE_PATH: """# Phase 11 GPIO Watchdog Remove Handoff Note

- `PHASE11_GPIO_WDT_REMOVE_HANDOFF_STATUS=driver_docs_and_proof_remove_handoff_truthful`
- `registerDeviceFailureSummary()` keeps register-device failure cues reviewable
- `requestStop()` keeps the bounded nowayout, stopped, and kept-running stop
- `rebootGlueCheckpointSummary()` keeps the stop-on-reboot handoff visible
- `summarizeTeardown()` keeps the stop-request, register-device-failure, and
- `summarizeRemoveHandoff()` keeps the dedicated remove-handoff summary itself
""",
    VALIDATION_MATRIX_PATH: """# Phase 11 GPIO Watchdog Validation Matrix

- `PHASE11_GPIO_WDT_STATUS=driver_docs_and_proof_packet_truthful`
- `drivers/watchdog/gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
- `watchdogDrvdataCheckpointSummary()`
- `rebootGlueCheckpointSummary()`
- `registerDeviceCallSummary()`
- `registerDeviceFailureSummary()`
- `requestStop()`
- `summarizeTeardown()`
- focused `zig build phase11-gpio-wdt-register-device-glue-review-test`
""",
    DRIVER_PATH: """pub const WatchdogDrvdataCheckpointSummary = struct {};
pub const RebootGlueCheckpointSummary = struct {};
pub const TeardownCheckpointSummary = struct {};
pub const TeardownSummary = struct {};
pub const RemoveHandoffSummary = struct {};
pub fn watchdogDrvdataCheckpointSummary(self: *const Self) WatchdogDrvdataCheckpointSummary { _ = self; return undefined; }
pub fn rebootGlueCheckpointSummary(self: *const Self) RebootGlueCheckpointSummary { _ = self; return undefined; }
pub fn teardownCheckpointSummary(self: *Self, nowayout: bool) TeardownCheckpointSummary { _ = self; _ = nowayout; return undefined; }
pub fn summarizeTeardown(self: *Self, nowayout: bool) TeardownSummary { _ = self; _ = nowayout; return undefined; }
pub fn summarizeRemoveHandoff(self: *Self, nowayout: bool) RemoveHandoffSummary { _ = self; _ = nowayout; return undefined; }
""",
    PROOF_PATH: """test "phase11 gpio watchdog keeps register-device call glued to reboot boundary" {}
test "phase11 gpio watchdog keeps teardown checkpoint glued to register-device failure and reboot handoff" {}
test "phase11 gpio watchdog keeps register-device failure summary tied to the same reboot-glue checkpoint" {}
test "phase11 gpio watchdog keeps remove-handoff teardown reviewable without live unregister behavior" {}
test "phase11 gpio watchdog keeps a dedicated remove-handoff summary reviewable" {}
stoppable_teardown.reboot_glue_precedes_register_device_request
guarded_teardown.blocked_on_host_shutdown_execution
stoppable_handoff.blocked_on_watchdog_core_unregister
""",
    BUILD_PATH: """const gpio_wdt = b.createModule(.{
    .root_source_file = b.path("../../drivers/watchdog/gpio_wdt.zig"),
});
const test_root = b.createModule(.{
    .root_source_file = b.path("phase11_gpio_wdt_register_device_glue_review.zig"),
});
const test_step = b.step(
    "phase11-gpio-wdt-register-device-glue-review-test",
    "Run the bounded gpio_wdt register-device glue review packet",
);
""",
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    for rel, text in FIXTURE_CONTENT.items():
        write(root / rel, text)


def expect_failure(root: Path, rel: Path, needle: str) -> None:
    write(root / rel, read_text(root / rel).replace(needle, "", 1))
    try:
        run_check(root)
    except CheckError as exc:
        if needle not in str(exc):
            raise AssertionError(f"expected {needle!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {needle!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_gpio_wdt_packet_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        cases = (
            (SURVEY_PATH, "`requestStop()`"),
            (MODULE_SLICE_PATH, "`registerDeviceFailureSummary()` keeps the bounded register-device failure"),
            (TEARDOWN_NOTE_PATH, "`nowayoutPolicySummary()` as a driver-local checkpoint"),
            (REMOVE_NOTE_PATH, "`summarizeRemoveHandoff()` keeps the dedicated remove-handoff summary itself"),
            (VALIDATION_MATRIX_PATH, "`summarizeTeardown()`"),
            (DRIVER_PATH, "pub fn summarizeRemoveHandoff(self: *Self, nowayout: bool) RemoveHandoffSummary {"),
            (PROOF_PATH, 'test "phase11 gpio watchdog keeps a dedicated remove-handoff summary reviewable" {'),
            (BUILD_PATH, '"phase11-gpio-wdt-register-device-glue-review-test"'),
        )

        for index, (rel, needle) in enumerate(cases, start=1):
            broken = tmpdir / f"broken_{index:02d}"
            shutil.copytree(fixture, broken, dirs_exist_ok=True)
            expect_failure(broken, rel, needle)

        missing = tmpdir / "missing"
        shutil.copytree(fixture, missing, dirs_exist_ok=True)
        (missing / PROOF_PATH).unlink()
        try:
            run_check(missing)
        except CheckError as exc:
            if "missing required file" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing file failure")

        print("PHASE11_GPIO_WDT_REMOVE_HANDOFF_PACKET_SELF_TEST=pass")
        print(f"PHASE11_GPIO_WDT_REMOVE_HANDOFF_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 1}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current-head Phase 11 gpio watchdog remove-handoff packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_GPIO_WDT_REMOVE_HANDOFF_PACKET=fail: {exc}")
        return 1

    print("PHASE11_GPIO_WDT_REMOVE_HANDOFF_PACKET=pass")
    print(f"PHASE11_GPIO_WDT_REMOVE_HANDOFF_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

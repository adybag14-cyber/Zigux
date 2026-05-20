#!/usr/bin/env python3
"""Fail-closed checker for the current-head Phase 11 gpio watchdog packet."""

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = (
    Path(__file__).resolve().parents[3]
    if len(Path(__file__).resolve().parents) > 3
    else Path.cwd()
)

SURVEY_PATH = Path("Documentation/zigux/phase11-gpio-wdt-survey.md")
MODULE_SLICE_PATH = Path("Documentation/zigux/phase11-gpio-wdt-module-slice.md")
TEARDOWN_NOTE_PATH = Path("Documentation/zigux/phase11-gpio-wdt-teardown-note.md")
VALIDATION_MATRIX_PATH = Path("Documentation/zigux/phase11-gpio-wdt-validation-matrix.md")
DRIVER_PATH = Path("drivers/watchdog/gpio_wdt.zig")

SURVEY_MARKERS = (
    "`PHASE11_GPIO_WDT_SURVEY_STATUS=current_head_driver_docs_and_proof_packet_truthful`",
    "current authenticated contents readback keeps the bounded gpio watchdog packet",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "current authenticated contents readback still does not rematerialize",
    "`zigux/tests/phase11_gpio_wdt.zig`,",
    "`zigux/Makefile` still exposes no dedicated `make -C zigux phase11-gpio-wdt` route",
    "`platformDriverIdentitySummary()`, `watchdogMetadataSummary()`,",
    "`watchdogDrvdataCheckpointSummary()`,",
    "`rebootGlueCheckpointSummary()`",
    "focused replay recovery or another equally small truthfulness repair",
)

MODULE_SLICE_MARKERS = (
    "`platformDriverIdentitySummary()` keeps the Linux anchor",
    "`watchdogMetadataSummary()` keeps the watchdog metadata packet visible",
    "`descriptorRequestSummary()` keeps the `devm_gpiod_get()` flag choice reviewable",
    "`platformDrvdataCheckpointSummary()` keeps the early `platform_set_drvdata()` ordering explicit",
    "`watchdogDrvdataCheckpointSummary()` keeps the bounded `watchdog_set_drvdata()` ownership handoff explicit",
    "`rebootGlueCheckpointSummary()` keeps the bounded `watchdog_stop_on_reboot()` handoff explicit",
    "`registerDeviceCallSummary()` keeps the first bounded `devm_watchdog_register_device()` request surface visible",
    "one equally small gpio watchdog replay, manifest, checker, or validation-truthfulness repair",
)

TEARDOWN_MARKERS = (
    "`PHASE11_GPIO_WDT_TEARDOWN_STATUS=teardown_handoff_driver_docs_and_proof_packet`",
    "The current teardown-facing GPIO packet on `master` is:",
    "`drivers/watchdog/gpio_wdt.zig`",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`summarizeTeardown()` and the bounded stop-request outcomes it records",
    "`requestStop()` and the split between watchdog-core stop policy and hardware",
    "`registerDeviceFailureSummary()` and the teardown-facing failure-mode cues",
    "`watchdogDrvdataCheckpointSummary()` and `rebootGlueCheckpointSummary()`",
    "It does not claim live GPIO descriptor acquisition",
)

VALIDATION_MATRIX_MARKERS = (
    "`PHASE11_GPIO_WDT_STATUS=driver_docs_and_proof_packet_truthful`",
    "The directly readable gpio watchdog matrix packet on current `master` is:",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`",
    "`Documentation/zigux/phase11-gpio-wdt-survey.md`",
    "`Documentation/zigux/phase11-gpio-wdt-module-slice.md`",
    "`Documentation/zigux/phase11-gpio-wdt-teardown-note.md`",
    "`zigux/tests/phase11_gpio_wdt.zig`,",
    "Treat the current gpio watchdog matrix packet as the driver-plus-docs-plus-proof packet",
    "`descriptorRequestSummary()`, `timeoutPropertyCheckpointSummary()`,",
    "`registerDeviceFailureSummary()`, `requestStop()`,",
    "The next honest gpio-only follow-up is still one equally small replay,",
    "manifest, checker, or validation-truthfulness repair, rather than new runtime behavior.",
)

DRIVER_MARKERS = (
    "pub const DescriptorRequestSummary = struct {",
    "pub const PlatformDrvdataCheckpointSummary = struct {",
    "pub const WatchdogDrvdataCheckpointSummary = struct {",
    "pub const RebootGlueCheckpointSummary = struct {",
    "pub const RegistrationPlanSummary = struct {",
    "pub const RegisterDeviceCallSummary = struct {",
    "pub const RegisterDeviceFailureSummary = struct {",
    "pub const TeardownSummary = struct {",
    "pub fn platformDriverIdentitySummary(self: *const Self) PlatformDriverIdentitySummary {",
    "pub fn watchdogMetadataSummary(self: *const Self) WatchdogMetadataSummary {",
    "pub fn descriptorRequestSummary(self: *const Self) DescriptorRequestSummary {",
    "pub fn platformDrvdataCheckpointSummary(self: *const Self) PlatformDrvdataCheckpointSummary {",
    "pub fn watchdogDrvdataCheckpointSummary(self: *const Self) WatchdogDrvdataCheckpointSummary {",
    "pub fn rebootGlueCheckpointSummary(self: *const Self) RebootGlueCheckpointSummary {",
    "pub fn registrationPlanSummary(self: *const Self, nowayout: bool) RegistrationPlanSummary {",
    "pub fn registerDeviceCallSummary(self: *const Self, nowayout: bool) RegisterDeviceCallSummary {",
    "pub fn registerDeviceFailureSummary(self: *const Self, nowayout: bool) RegisterDeviceFailureSummary {",
    "pub fn requestStop(self: *Self, nowayout: bool) StopSummary {",
    "pub fn summarizeTeardown(self: Self, nowayout: bool) TeardownSummary {",
)

FORBIDDEN_MARKERS = {
    "survey": (
        "`zigux/tests/phase11_gpio_wdt.zig` is directly readable on current `master`",
        "`zigux/tests/phase11_gpio_wdt_platform_drvdata.zig` is directly readable on current `master`",
        "`zigux/Makefile` now exposes `make -C zigux phase11-gpio-wdt`",
    ),
    "validation_matrix": (
        "`zigux/tests/phase11_gpio_wdt.zig` is directly readable on current `master`",
        "`zigux/tests/phase11_gpio_wdt_platform_drvdata.zig` is directly readable on current `master`",
        "hardware-validated parity is complete",
    ),
}


class CheckError(RuntimeError):
    pass


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path.as_posix()}")
    return path.read_text(encoding="utf-8")


def expect_markers(root: Path, relative_path: Path, markers: tuple[str, ...], label: str) -> None:
    text = normalize_whitespace(read_text(root, relative_path))
    for marker in markers:
        if normalize_whitespace(marker) not in text:
            raise CheckError(f"missing {label} marker: {marker}")


def expect_forbidden_markers_absent(root: Path, relative_path: Path, label: str) -> None:
    text = normalize_whitespace(read_text(root, relative_path))
    for marker in FORBIDDEN_MARKERS.get(label, ()):
        if normalize_whitespace(marker) in text:
            raise CheckError(f"forbidden {label} marker: {marker}")


def run_check(root: Path) -> None:
    expect_markers(root, SURVEY_PATH, SURVEY_MARKERS, "survey")
    expect_forbidden_markers_absent(root, SURVEY_PATH, "survey")
    expect_markers(root, MODULE_SLICE_PATH, MODULE_SLICE_MARKERS, "module slice")
    expect_markers(root, TEARDOWN_NOTE_PATH, TEARDOWN_MARKERS, "teardown note")
    expect_markers(root, VALIDATION_MATRIX_PATH, VALIDATION_MATRIX_MARKERS, "validation matrix")
    expect_forbidden_markers_absent(root, VALIDATION_MATRIX_PATH, "validation_matrix")
    expect_markers(root, DRIVER_PATH, DRIVER_MARKERS, "driver")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(
        root / SURVEY_PATH,
        """# Phase 11 GPIO Watchdog Survey

- `PHASE11_GPIO_WDT_SURVEY_STATUS=current_head_driver_docs_and_proof_packet_truthful`
- current authenticated contents readback keeps the bounded gpio watchdog packet reviewable through:
  - `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
  - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- current authenticated contents readback still does not rematerialize `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_gpio_wdt_survey.zig`, `Documentation/zigux/phase11-shared-replay-contract.md`, or `zigux/tests/phase11_build.zig`
- `zigux/Makefile` still exposes no dedicated `make -C zigux phase11-gpio-wdt` route
- `platformDriverIdentitySummary()`, `watchdogMetadataSummary()`, `descriptorRequestSummary()`, `platformDrvdataCheckpointSummary()`, `watchdogDrvdataCheckpointSummary()`, `rebootGlueCheckpointSummary()`, `nowayoutPolicySummary()`, `registrationHandoffSummary()`, `registrationPlanSummary()`, `registerDeviceCallSummary()`, `registerDeviceFailureSummary()`, `requestStop()`, and `summarizeTeardown()` stay reviewable
- If the current smaller packet needs one more driver-local follow-up first, keep it to focused replay recovery or another equally small truthfulness repair.
""",
    )
    write(
        root / MODULE_SLICE_PATH,
        """# Phase 11 GPIO Watchdog Module Slice

- `platformDriverIdentitySummary()` keeps the Linux anchor and bounded starter identity explicit.
- `watchdogMetadataSummary()` keeps the watchdog metadata packet visible before later live registration work.
- `descriptorRequestSummary()` keeps the `devm_gpiod_get()` flag choice reviewable without claiming live descriptor acquisition.
- `platformDrvdataCheckpointSummary()` keeps the early `platform_set_drvdata()` ordering explicit before later GPIO and watchdog bookkeeping.
- `watchdogDrvdataCheckpointSummary()` keeps the bounded `watchdog_set_drvdata()` ownership handoff explicit before later reboot glue or registration execution.
- `rebootGlueCheckpointSummary()` keeps the bounded `watchdog_stop_on_reboot()` handoff explicit between watchdog drvdata ownership and the first register-device request without claiming live shutdown execution.
- `registerDeviceCallSummary()` keeps the first bounded `devm_watchdog_register_device()` request surface visible without claiming live watchdog-core registration.
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
  - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `summarizeTeardown()` and the bounded stop-request outcomes it records
- `requestStop()` and the split between watchdog-core stop policy and hardware `always-running` behavior
- `registerDeviceFailureSummary()` and the teardown-facing failure-mode cues that stay reviewable without claiming live remove-hook or reboot-backed shutdown execution
- `watchdogDrvdataCheckpointSummary()` and `rebootGlueCheckpointSummary()` as the bounded ownership-to-reboot-glue handoff before the first `watchdog_stop_on_reboot()` request surface
- It does not claim live GPIO descriptor acquisition.
""",
    )
    write(
        root / VALIDATION_MATRIX_PATH,
        """# Phase 11 GPIO Watchdog Validation Matrix

- `PHASE11_GPIO_WDT_STATUS=driver_docs_and_proof_packet_truthful`
- The directly readable gpio watchdog matrix packet on current `master` is:
  - `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
  - `Documentation/zigux/phase11-gpio-wdt-survey.md`
  - `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  - `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- Current direct contents reads in this run do not rematerialize `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_gpio_wdt_survey.zig`, `Documentation/zigux/phase11-shared-replay-contract.md`, or `zigux/tests/phase11_build.zig`
- Treat the current gpio watchdog matrix packet as the driver-plus-docs-plus-proof packet below.
- The returned driver plus the paired module slice and teardown note keep the bounded `descriptorRequestSummary()`, `timeoutPropertyCheckpointSummary()`, `platformDrvdataCheckpointSummary()`, `watchdogDrvdataCheckpointSummary()`, `rebootGlueCheckpointSummary()`, `nowayoutPolicySummary()`, `registrationHandoffSummary()`, `registrationPlanSummary()`, `registerDeviceCallSummary()`, `registerDeviceFailureSummary()`, `requestStop()`, and `summarizeTeardown()` checkpoint names reviewable.
- The next honest gpio-only follow-up is still one equally small replay, manifest, checker, or validation-truthfulness repair, rather than new runtime behavior.
""",
    )
    write(
        root / DRIVER_PATH,
        """pub const DescriptorRequestSummary = struct {};
pub const PlatformDrvdataCheckpointSummary = struct {};
pub const WatchdogDrvdataCheckpointSummary = struct {};
pub const RebootGlueCheckpointSummary = struct {};
pub const RegistrationPlanSummary = struct {};
pub const RegisterDeviceCallSummary = struct {};
pub const RegisterDeviceFailureSummary = struct {};
pub const TeardownSummary = struct {};

pub fn platformDriverIdentitySummary(self: *const Self) PlatformDriverIdentitySummary {}
pub fn watchdogMetadataSummary(self: *const Self) WatchdogMetadataSummary {}
pub fn descriptorRequestSummary(self: *const Self) DescriptorRequestSummary {}
pub fn platformDrvdataCheckpointSummary(self: *const Self) PlatformDrvdataCheckpointSummary {}
pub fn watchdogDrvdataCheckpointSummary(self: *const Self) WatchdogDrvdataCheckpointSummary {}
pub fn rebootGlueCheckpointSummary(self: *const Self) RebootGlueCheckpointSummary {}
pub fn registrationPlanSummary(self: *const Self, nowayout: bool) RegistrationPlanSummary {}
pub fn registerDeviceCallSummary(self: *const Self, nowayout: bool) RegisterDeviceCallSummary {}
pub fn registerDeviceFailureSummary(self: *const Self, nowayout: bool) RegisterDeviceFailureSummary {}
pub fn requestStop(self: *Self, nowayout: bool) StopSummary {}
pub fn summarizeTeardown(self: Self, nowayout: bool) TeardownSummary {}
""",
    )


def replace_once(text: str, marker: str, replacement: str) -> str:
    pattern = re.compile(re.escape(marker))
    updated_text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise AssertionError(f"expected to replace marker exactly once: {marker!r}")
    return updated_text


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(
                f"expected {expected_fragment!r}, got {str(exc)!r}"
            ) from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_gpio_wdt_packet_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_fixture(fixture_root)
        run_check(fixture_root)

        survey_text = read_text(fixture_root, SURVEY_PATH)
        write(
            fixture_root / SURVEY_PATH,
            replace_once(
                survey_text,
                "`PHASE11_GPIO_WDT_SURVEY_STATUS=current_head_driver_docs_and_proof_packet_truthful`",
                "`PHASE11_GPIO_WDT_SURVEY_STATUS=broken`",
            ),
        )
        expect_failure(fixture_root, "missing survey marker")
        build_fixture(fixture_root)

        matrix_text = read_text(fixture_root, VALIDATION_MATRIX_PATH)
        write(
            fixture_root / VALIDATION_MATRIX_PATH,
            replace_once(
                matrix_text,
                "manifest, checker, or validation-truthfulness repair, rather than new runtime behavior.",
                "new runtime behavior",
            ),
        )
        expect_failure(fixture_root, "missing validation matrix marker")
        build_fixture(fixture_root)

        write(
            fixture_root / SURVEY_PATH,
            survey_text
            + "\n`zigux/tests/phase11_gpio_wdt.zig` is directly readable on current `master`\n",
        )
        expect_failure(fixture_root, "forbidden survey marker")
        build_fixture(fixture_root)

        driver_text = read_text(fixture_root, DRIVER_PATH)
        write(
            fixture_root / DRIVER_PATH,
            replace_once(
                driver_text,
                "pub fn rebootGlueCheckpointSummary(self: *const Self) RebootGlueCheckpointSummary {}",
                "",
            ),
        )
        expect_failure(fixture_root, "missing driver marker")
        build_fixture(fixture_root)

        print("PHASE11_GPIO_WDT_PACKET_SELF_TEST=pass")
        print("PHASE11_GPIO_WDT_PACKET_SELF_TEST_CASES=5")
    finally:
        shutil.rmtree(tmpdir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="Repository root to check",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in self-test cases",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(args.root)
    except CheckError as exc:
        print(f"PHASE11_GPIO_WDT_PACKET=fail: {exc}")
        return 1

    print("PHASE11_GPIO_WDT_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

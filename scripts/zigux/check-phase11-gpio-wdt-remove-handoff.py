#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 gpio watchdog remove-handoff note."""

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
from pathlib import Path

NOTE_PATH = "Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md"

REQUIRED_MARKERS = [
    "# Phase 11 GPIO Watchdog Remove Handoff Note",
    "`PHASE11_GPIO_WDT_REMOVE_HANDOFF_STATUS=driver_plus_docs_remove_handoff_truthful`",
    "`drivers/watchdog/gpio_wdt.zig`",
    "`Documentation/zigux/phase11-gpio-wdt-survey.md`",
    "`Documentation/zigux/phase11-gpio-wdt-module-slice.md`",
    "`Documentation/zigux/phase11-gpio-wdt-teardown-note.md`",
    "`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "do not rematerialize `zigux/tests/phase11_gpio_wdt.zig`",
    "`registerDeviceFailureSummary()` keeps register-device failure cues reviewable before any later remove-hook execution claim",
    "`requestStop()` keeps the bounded nowayout, stopped, and kept-running stop split explicit before any platform cleanup callback claim",
    "`rebootGlueCheckpointSummary()` keeps the stop-on-reboot handoff visible before any later remove-hook execution claim",
    "`summarizeTeardown()` keeps the stop-request, register-device-failure, and reboot-glue checkpoint cues reviewable as a host-free remove-handoff packet",
    "does not claim live platform cleanup callbacks, platform-driver removal, watchdog-core unregister side effects, reboot-backed teardown execution, or hardware-backed validation",
    "focused replay or manifest recovery, or another equally small gpio watchdog truthfulness repair",
]

FORBIDDEN_MARKERS = [
    "`PHASE11_GPIO_WDT_REMOVE_HANDOFF_STATUS=remove_hook_runtime_validated`",
    "claims live platform cleanup callbacks",
    "claims live platform-driver removal",
    "claims watchdog-core unregister side effects",
]

FIXTURE_TEXT = """# Phase 11 GPIO Watchdog Remove Handoff Note

## Status

- `PHASE11_GPIO_WDT_REMOVE_HANDOFF_STATUS=driver_plus_docs_remove_handoff_truthful`
- scope: keep the bounded gpio watchdog remove-handoff packet truthful without widening into live platform cleanup callbacks, platform-driver removal, watchdog-core unregister side effects, reboot-backed teardown execution, or hardware-backed validation

## Current Repo Reality

- `drivers/watchdog/gpio_wdt.zig`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`

Current direct contents reads in this run do not rematerialize `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, or `zigux/tests/phase11_build.zig`, so keep the remove-handoff packet bounded to the returned driver-plus-docs surfaces instead of treating absent replay, manifest, or shared-build files as current-head evidence.

## Returned Remove-Handoff Surface

- `registerDeviceFailureSummary()` keeps register-device failure cues reviewable before any later remove-hook execution claim.
- `requestStop()` keeps the bounded nowayout, stopped, and kept-running stop split explicit before any platform cleanup callback claim.
- `rebootGlueCheckpointSummary()` keeps the stop-on-reboot handoff visible before any later remove-hook execution claim.
- `summarizeTeardown()` keeps the stop-request, register-device-failure, and reboot-glue checkpoint cues reviewable as a host-free remove-handoff packet.

## Guardrails

This note does not claim live platform cleanup callbacks, platform-driver removal, watchdog-core unregister side effects, reboot-backed teardown execution, or hardware-backed validation.

## Next Blocked Step

The next honest gpio-only follow-through remains focused replay or manifest recovery, or another equally small gpio watchdog truthfulness repair, rather than new runtime behavior.
"""

class CheckError(RuntimeError):
    pass


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def run_check(root: Path) -> None:
    note = read_text(root, NOTE_PATH)
    normalized = normalize_whitespace(note)
    for marker in REQUIRED_MARKERS:
        if normalize_whitespace(marker) not in normalized:
            raise CheckError(f"missing marker in {NOTE_PATH}: {marker}")
    for marker in FORBIDDEN_MARKERS:
        if normalize_whitespace(marker) in normalized:
            raise CheckError(f"forbidden marker in {NOTE_PATH}: {marker}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / NOTE_PATH, FIXTURE_TEXT)


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def remove_marker(text: str, marker: str) -> str:
    pattern = r"\s+".join(re.escape(part) for part in marker.split())
    updated, count = re.subn(pattern, "", text, flags=re.MULTILINE)
    if count < 1:
        raise AssertionError(f"expected to remove marker from fixture: {marker!r}")
    return updated


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_gpio_remove_handoff_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        required_cases = [
            REQUIRED_MARKERS[1],
            REQUIRED_MARKERS[7],
            REQUIRED_MARKERS[9],
            REQUIRED_MARKERS[12],
        ]
        for idx, marker in enumerate(required_cases, start=1):
            case_root = tmpdir / f"required_{idx}"
            shutil.copytree(fixture, case_root, dirs_exist_ok=True)
            path = case_root / NOTE_PATH
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            expect_failure(case_root, marker)

        for idx, marker in enumerate(FORBIDDEN_MARKERS, start=1):
            case_root = tmpdir / f"forbidden_{idx}"
            shutil.copytree(fixture, case_root, dirs_exist_ok=True)
            path = case_root / NOTE_PATH
            path.write_text(path.read_text(encoding="utf-8") + "\n" + marker + "\n", encoding="utf-8")
            expect_failure(case_root, marker)

        missing_file_root = tmpdir / "missing_file"
        shutil.copytree(fixture, missing_file_root, dirs_exist_ok=True)
        (missing_file_root / NOTE_PATH).unlink()
        expect_failure(missing_file_root, NOTE_PATH)

        print("PHASE11_GPIO_WDT_REMOVE_HANDOFF_SELF_TEST=pass")
        print("PHASE11_GPIO_WDT_REMOVE_HANDOFF_SELF_TEST_CASE_COUNT=9")
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
        print(f"PHASE11_GPIO_WDT_REMOVE_HANDOFF=fail: {exc}")
        return 1

    print("PHASE11_GPIO_WDT_REMOVE_HANDOFF=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

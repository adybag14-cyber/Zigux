#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

NOTE = "Documentation/zigux/phase11-validation-matrix-gap-survey.md"

REQUIRED_MARKERS = [
    "# Phase 11 Validation Matrix Gap Survey",
    "`PHASE11_MATRIX_GAP_STATUS=dw_matrix_gap_only`",
    "lane: `P11-L01`",
    "Phase 11 still names `drivers/watchdog/gpio_wdt.c`, `drivers/watchdog/bcm2835_wdt.c`, `drivers/watchdog/dw_wdt.c`, and `drivers/tty/hvc/hvc_console.c` as the simple-production-driver anchors.",
    "Phase 11 still requires a hardware validation matrix together with teardown or failure-mode parity.",
    "Current `master` does not ship `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, or `zigux/tests/phase11_dw_wdt_survey.zig`.",
    "the live matrix count is three, with DesignWare currently represented by the surviving platform-registration continuity packet instead.",
]

PRESENT_PATHS = [
    "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "scripts/zigux/check-phase11-dw-wdt-packet.py",
    "drivers/watchdog/dw_wdt.zig",
    "drivers/watchdog/dw_wdt_verify.zig",
    "zigux/tests/phase11_dw_wdt.zig",
    "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
]

ABSENT_PATHS = [
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-dw-wdt-survey.md",
    "Documentation/zigux/phase11-dw-wdt-teardown-note.md",
    "zigux/tests/phase11_dw_wdt_manifest.json",
    "zigux/tests/phase11_dw_wdt_survey.zig",
]

NOTE_TEXT = """# Phase 11 Validation Matrix Gap Survey

This note records the roadmap-facing validation-matrix coverage for the current Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=dw_matrix_gap_only`
- lane: `P11-L01`
- reviewed against live `master`
- scope: compare the Phase 11 roadmap anchors against the current validation-matrix packet without reopening driver-local implementation, shared replay-contract wording, or removed DesignWare matrix-era files

## Roadmap Anchor

- Phase 11 still names `drivers/watchdog/gpio_wdt.c`, `drivers/watchdog/bcm2835_wdt.c`, `drivers/watchdog/dw_wdt.c`, and `drivers/tty/hvc/hvc_console.c` as the simple-production-driver anchors.
- Phase 11 still requires a hardware validation matrix together with teardown or failure-mode parity.

## Current Repo Reality

- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `drivers/watchdog/dw_wdt.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`

Current `master` does not ship `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, or `zigux/tests/phase11_dw_wdt_survey.zig`.

## Gap Survey

- `bcm2835_wdt`: validation matrix present through `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, and the bounded bcm2835 packet still keeps teardown, ownership, lifecycle, and register-model evidence reviewable.
- `gpio_wdt`: validation matrix present through `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, and the bounded gpio packet still keeps descriptor, drvdata, registration-handoff, and teardown checkpoints reviewable without overclaiming live platform behavior.
- `hvc_console`: validation matrix present through `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and the bounded archival packet still keeps teardown, sysrq-helper, notifier-edge, and direct companion evidence reviewable without widening into tty or hypervisor execution.
- `dw_wdt`: no current `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` is shipped on `master`; the surviving same-lane evidence stays in `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, so the roadmap-facing validation-matrix gap is explicit rather than silently treated as closed.

## Review Rules

- Treat this survey as shared matrix truthfulness only, not as proof that the DesignWare starter is absent.
- Do not claim four live driver-local validation matrices on current `master`; the live matrix count is three, with DesignWare currently represented by the surviving platform-registration continuity packet instead.
- If a future DesignWare lane lands enough same-family evidence to justify a bounded validation matrix again, update this survey in the same patch so the roadmap-facing matrix count stays honest.
"""


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def run_check(root: Path) -> None:
    note = read_text(root, NOTE)
    for marker in REQUIRED_MARKERS:
        if marker not in note:
            raise CheckError(f"missing marker: {marker}")

    for relative_path in PRESENT_PATHS:
        if not (root / relative_path).is_file():
            raise CheckError(f"missing present path: {relative_path}")

    for relative_path in ABSENT_PATHS:
        if (root / relative_path).exists():
            raise CheckError(f"expected absent path to stay absent: {relative_path}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / NOTE, NOTE_TEXT)
    for relative_path in PRESENT_PATHS:
        write(root / relative_path, "present\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_matrix_gap_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_fixture(fixture_root)
        run_check(fixture_root)

        marker_cases = [
            ("- lane: `P11-L01`\n", "lane: `P11-L01`"),
            (
                "Current `master` does not ship `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, or `zigux/tests/phase11_dw_wdt_survey.zig`.\n",
                "Current `master` does not ship `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, or `zigux/tests/phase11_dw_wdt_survey.zig`.",
            ),
            (
                "- Do not claim four live driver-local validation matrices on current `master`; the live matrix count is three, with DesignWare currently represented by the surviving platform-registration continuity packet instead.\n",
                "the live matrix count is three, with DesignWare currently represented by the surviving platform-registration continuity packet instead.",
            ),
        ]

        for idx, (line_text, expected_fragment) in enumerate(marker_cases, start=1):
            case_root = tmpdir / f"marker_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            note_path = case_root / NOTE
            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(line_text, "", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, expected_fragment)

        for idx, relative_path in enumerate(PRESENT_PATHS[:2], start=1):
            case_root = tmpdir / f"present_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            (case_root / relative_path).unlink()
            expect_failure(case_root, relative_path)

        for idx, relative_path in enumerate(ABSENT_PATHS[:2], start=1):
            case_root = tmpdir / f"absent_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            write(case_root / relative_path, "unexpected\n")
            expect_failure(case_root, relative_path)

        print("PHASE11_MATRIX_GAP_SURVEY_SELF_TEST=pass")
        print("PHASE11_MATRIX_GAP_SURVEY_SELF_TEST_CASE_COUNT=7")
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
        print(f"PHASE11_MATRIX_GAP_SURVEY=fail: {exc}")
        return 1

    print("PHASE11_MATRIX_GAP_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 validation-matrix gap survey."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SURVEY_PATH = "Documentation/zigux/phase11-validation-matrix-gap-survey.md"

REQUIRED_MARKERS = [
    "`PHASE11_MATRIX_GAP_STATUS=direct_readback_matrix_drift_recorded`",
    "lane: `P11-L05`",
    "`Documentation/zigux/phase11-hvc-console-survey.md`",
    "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`",
    "`Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "shared matrix packet is no longer an honest four-matrix direct-readback claim",
    "inventory-backed rather than direct-readback current-head evidence",
    "`scripts/zigux/check-phase11-matrix-gap-survey.py`",
    "`python3 scripts/zigux/check-phase11-matrix-gap-survey.py`",
]

SELF_TEST_CASES = [
    (
        "`PHASE11_MATRIX_GAP_STATUS=direct_readback_matrix_drift_recorded`",
        "`PHASE11_MATRIX_GAP_STATUS=direct_readback_matrix_drift_recorded`",
    ),
    ("lane: `P11-L05`", "lane: `P11-L05`"),
]

FIXTURE_TEXT = """# Phase 11 Validation Matrix Gap Survey

This note records the roadmap-facing validation-matrix coverage for the current
Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=direct_readback_matrix_drift_recorded`
- lane: `P11-L05`
- reviewed against live `master`
- scope: compare the Phase 11 roadmap anchors against the current validation-matrix
  packet without reopening driver-local implementation, DesignWare
  platform-registration follow-through, or HVC cleanup-alignment checker repair

## Roadmap Anchor

- Phase 11 still names `drivers/watchdog/gpio_wdt.c`,
  `drivers/watchdog/bcm2835_wdt.c`, `drivers/watchdog/dw_wdt.c`, and
  `drivers/tty/hvc/hvc_console.c` as the simple-production-driver anchors.
- Phase 11 still requires a hardware validation matrix together with teardown or
  failure-mode parity.

## Current Repo Reality

- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`
- `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`

Current direct contents reads in this run did not rematerialize
`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-hvc-console-validation-matrix.md`, or
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so the shared matrix
packet is no longer an honest four-matrix direct-readback claim.

The current HVC survey note already keeps the HVC archival packet inventory-backed
when those direct matrix and companion surfaces do not rematerialize in the same
readback pass.

## Validation Gate

- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`

## Gap Survey

- `bcm2835_wdt`: the validation matrix did not rematerialize by current direct
  contents readback in this run, so keep older bcm2835 matrix claims archival
  rather than presenting them as live direct-readback evidence.
- `gpio_wdt`: the validation matrix did not rematerialize by current direct
  contents readback in this run, so keep the gpio matrix packet inventory-backed
  until a future reread confirms the file again.
- `hvc_console`: `Documentation/zigux/phase11-hvc-console-survey.md` already
  records that direct contents reads did not rematerialize
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md` or the direct
  companion packet, so HVC matrix continuity is inventory-backed rather than
  direct-readback current-head evidence.
- `dw_wdt`: current continuity notes still keep DesignWare follow-through explicit
  through `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md` and
  `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, but the
  validation matrix itself did not rematerialize by direct contents readback in
  this run and should not be counted as a live direct-readback matrix until a
  future reread confirms it again.

## Review Rules

- Treat this survey as current-head matrix truthfulness only, not as proof that
  the missing matrix files are gone forever or that any driver-local packet has
  been reopened.
- Do not claim four live driver-local validation matrices on current `master`
  while current direct readback still fails to rematerialize those matrix files.
- If future direct contents reads confirm any Phase 11 matrix again, update this
  survey and `scripts/zigux/check-phase11-matrix-gap-survey.py` in the same patch
  so the direct-readback count stays honest.
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
    survey_text = read_text(root, SURVEY_PATH)
    normalized_survey_text = normalize_whitespace(survey_text)
    for marker in REQUIRED_MARKERS:
        if normalize_whitespace(marker) not in normalized_survey_text:
            raise CheckError(f"missing marker in {SURVEY_PATH}: {marker}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / SURVEY_PATH, FIXTURE_TEXT)


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_matrix_gap_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        for index, (needle, fragment) in enumerate(SELF_TEST_CASES, start=1):
            case_root = tmpdir / f"missing_marker_{index}"
            shutil.copytree(fixture, case_root, dirs_exist_ok=True)
            survey_path = case_root / SURVEY_PATH
            survey_text = survey_path.read_text(encoding="utf-8")
            survey_path.write_text(survey_text.replace(needle, "", 1), encoding="utf-8")
            expect_failure(case_root, fragment)

        missing_file_root = tmpdir / "missing_file"
        shutil.copytree(fixture, missing_file_root, dirs_exist_ok=True)
        (missing_file_root / SURVEY_PATH).unlink()
        expect_failure(missing_file_root, SURVEY_PATH)

        print("PHASE11_MATRIX_GAP_SURVEY_SELF_TEST=pass")
        print(f"PHASE11_MATRIX_GAP_SURVEY_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + 1}")
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

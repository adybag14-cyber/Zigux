#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 validation-matrix gap survey."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SURVEY_PATH = "Documentation/zigux/phase11-validation-matrix-gap-survey.md"

REQUIRED_MARKERS = [
    "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
    "lane: `P11-L05`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "shared matrix count is four rather than three",
    "`scripts/zigux/check-phase11-matrix-gap-survey.py`",
    "`python3 scripts/zigux/check-phase11-matrix-gap-survey.py`",
]

SELF_TEST_CASES = [
    (
        "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
        "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
    ),
    ("lane: `P11-L05`", "lane: `P11-L05`"),
    (
        "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
        "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    ),
    (
        "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
        "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    ),
    (
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    ),
    (
        "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
        "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    ),
    ("four rather\nthan three", "shared matrix count is four rather than three"),
    (
        "- `scripts/zigux/check-phase11-matrix-gap-survey.py`\n",
        "`scripts/zigux/check-phase11-matrix-gap-survey.py`",
    ),
    (
        "- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`\n",
        "`python3 scripts/zigux/check-phase11-matrix-gap-survey.py`",
    ),
]


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
    write(
        root / SURVEY_PATH,
        """# Phase 11 Validation Matrix Gap Survey

This note records the roadmap-facing validation-matrix coverage for the current
Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`
- lane: `P11-L05`
- reviewed against live `master`
- scope: compare the Phase 11 roadmap anchors against the current validation-matrix
  packet without reopening driver-local implementation, DesignWare
  platform-registration follow-through, or driver-local provenance cleanup

## Roadmap Anchor

- Phase 11 still names `drivers/watchdog/gpio_wdt.c`,
  `drivers/watchdog/bcm2835_wdt.c`, `drivers/watchdog/dw_wdt.c`, and
  `drivers/tty/hvc/hvc_console.c` as the simple-production-driver anchors.
- Phase 11 still requires a hardware validation matrix together with teardown or
  failure-mode parity.

## Current Repo Reality

- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `zigux/tests/phase11_build.zig`

Current `master` ships the bounded DesignWare validation-matrix packet beside the
surviving owner-plan continuity note, so the shared matrix count is four rather
than three.

## Validation Gate

- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`

## Gap Survey

- `bcm2835_wdt`: validation matrix present through
  `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, and the bounded
  bcm2835 packet still keeps teardown, ownership, lifecycle, and register-model
  evidence reviewable.
- `gpio_wdt`: validation matrix present through
  `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, and the bounded
  gpio packet still keeps descriptor, drvdata, registration-handoff, and teardown
  checkpoints reviewable without overclaiming live platform behavior.
- `hvc_console`: validation matrix present through
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and the bounded
  archival packet still keeps teardown, sysrq-helper, notifier-edge, and direct
  companion evidence reviewable without widening into tty or hypervisor
  execution.
- `dw_wdt`: validation matrix present through
  `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, and the bounded
  DesignWare packet now keeps the survey note, teardown note, manifest-backed
  survey evidence, and shared `phase11_build.zig` replay route reviewable beside
  the surviving owner-plan continuity packet without overclaiming live
  platform-registration or MMIO behavior.

## Review Rules

- Treat this survey as shared matrix truthfulness only, not as proof that the
  DesignWare starter or its next platform-registration step is complete.
- Claim four live driver-local validation matrices on current `master`, with
  DesignWare now represented by the landed validation matrix plus the
  still-separate owner-plan continuity packet.
- If a future simple-driver matrix is removed or materially reframed, update this
  survey in the same patch so the roadmap-facing matrix count stays honest.
""",
    )


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
            survey_path.write_text(survey_text.replace(needle, ""), encoding="utf-8")
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

#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 matrix-gap survey."""

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
from pathlib import Path


SURVEY_PATH = "Documentation/zigux/phase11-validation-matrix-gap-survey.md"

REQUIRED_MARKERS = [
    "`PHASE11_MATRIX_GAP_STATUS=hvc_matrix_direct_readback_only`",
    "lane: `P11-L03`",
    "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`",
    "`scripts/zigux/check-phase11-matrix-gap-survey.py`",
    "`python3 scripts/zigux/check-phase11-matrix-gap-survey.py`",
    "`scripts/zigux/check-phase11-validation-matrix-gap-survey.py`",
    "`python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "no longer an honest four-matrix direct-readback claim",
    "The only directly readable driver-local Phase 11 matrix note on current `master` is `Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains useful adjacent shared evidence, but it is not one of the driver-local Phase 11 validation matrices named by the roadmap",
    "`zigux/tests/fixtures/phase11_build_inventory.json` still records the narrower current-head HVC continuity packet",
    "4 HVC archival build test names, 3 shared depend steps, 1 dedicated survey replay, and 2 proof adjunct replays",
    "does not stand in for a whole-Phase-11 replay roster",
    "`phase11-hvc-console-tests`",
    "`phase11-hvc-console-verify-tests`",
    "`phase11-hvc-cleanup-tests`",
    "`phase11-hvc-console-survey-tests`",
    "`bcm2835_wdt`: `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`gpio_wdt`: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`hvc_console`: `Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`dw_wdt`: `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
    "`zigux/tests/phase11_dw_wdt_manifest.json`",
    "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
]

FORBIDDEN_MARKERS = [
    "`PHASE11_MATRIX_GAP_STATUS=four_matrix_direct_readback_restored`",
    "shared matrix packet is once again an honest four-matrix direct-readback claim",
    "is directly readable on current `master`, so the bcm2835 matrix remains live reminder evidence",
    "is directly readable on current `master`, so the gpio matrix remains live reminder evidence",
    "the DesignWare matrix remains live reminder evidence",
]

FIXTURE_TEXT = """# Phase 11 Validation Matrix Gap Survey

- `PHASE11_MATRIX_GAP_STATUS=hvc_matrix_direct_readback_only`
- lane: `P11-L03`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`
- current direct contents reads in this run do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, or `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so the shared matrix packet is no longer an honest four-matrix direct-readback claim
- The only directly readable driver-local Phase 11 matrix note on current `master` is `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains useful adjacent shared evidence, but it is not one of the driver-local Phase 11 validation matrices named by the roadmap
- `zigux/tests/fixtures/phase11_build_inventory.json` still records the narrower current-head HVC continuity packet
- 4 HVC archival build test names, 3 shared depend steps, 1 dedicated survey replay, and 2 proof adjunct replays
- the shared build inventory does not stand in for a whole-Phase-11 replay roster
- `phase11-hvc-console-tests`
- `phase11-hvc-console-verify-tests`
- `phase11-hvc-cleanup-tests`
- `phase11-hvc-console-survey-tests`
- `bcm2835_wdt`: `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `gpio_wdt`: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `hvc_console`: `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `dw_wdt`: `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
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
    normalized = normalize_whitespace(survey_text)
    for marker in REQUIRED_MARKERS:
        if normalize_whitespace(marker) not in normalized:
            raise CheckError(f"missing marker in {SURVEY_PATH}: {marker}")
    for marker in FORBIDDEN_MARKERS:
        if normalize_whitespace(marker) in normalized:
            raise CheckError(f"forbidden marker in {SURVEY_PATH}: {marker}")


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


def remove_marker(text: str, marker: str) -> str:
    pattern = r"\s+".join(re.escape(part) for part in marker.split())
    updated_text, count = re.subn(pattern, "", text, flags=re.MULTILINE)
    if count < 1:
        raise AssertionError(f"expected to remove marker from fixture: {marker!r}")
    return updated_text


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_matrix_gap_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        for index, marker in enumerate(REQUIRED_MARKERS[:6], start=1):
            case_root = tmpdir / f"missing_marker_{index}"
            shutil.copytree(fixture, case_root, dirs_exist_ok=True)
            survey_path = case_root / SURVEY_PATH
            survey_text = survey_path.read_text(encoding="utf-8")
            survey_path.write_text(remove_marker(survey_text, marker), encoding="utf-8")
            expect_failure(case_root, marker)

        for index, marker in enumerate(FORBIDDEN_MARKERS, start=1):
            case_root = tmpdir / f"forbidden_marker_{index}"
            shutil.copytree(fixture, case_root, dirs_exist_ok=True)
            survey_path = case_root / SURVEY_PATH
            survey_path.write_text(
                survey_path.read_text(encoding="utf-8") + "\n" + marker + "\n",
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        missing_file_root = tmpdir / "missing_file"
        shutil.copytree(fixture, missing_file_root, dirs_exist_ok=True)
        (missing_file_root / SURVEY_PATH).unlink()
        expect_failure(missing_file_root, SURVEY_PATH)

        print("PHASE11_MATRIX_GAP_SURVEY_SELF_TEST=pass")
        print("PHASE11_MATRIX_GAP_SURVEY_SELF_TEST_CASE_COUNT=12")
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

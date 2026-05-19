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
    "`PHASE11_MATRIX_GAP_STATUS=gpio_hvc_and_dw_reread_with_bcm_gap`",
    "lane: `P11-L03`",
    "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`",
    "`scripts/zigux/check-phase11-matrix-gap-survey.py`",
    "Current Repo Reality - `Documentation/zigux/phase11-validation-matrix-gap-survey.md` - `Documentation/zigux/phase11-driver-lane-sequencing.md` - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` - `Documentation/zigux/phase11-hvc-console-validation-matrix.md` - `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`python3 scripts/zigux/check-phase11-matrix-gap-survey.py`",
    "`scripts/zigux/check-phase11-validation-matrix-gap-survey.py`",
    "`python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "Current repo rereads in this run rematerialize the gpio watchdog, HVC, and DesignWare matrix notes",
    "do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "The reread driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains useful adjacent shared evidence, but it is not one of the driver-local Phase 11 validation matrices named by the roadmap",
    "`zigux/tests/fixtures/phase11_build_inventory.json` still records the narrower current-head HVC continuity packet",
    "3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays",
    "does not stand in for a whole-Phase-11 replay roster while the current reread expansion is limited to the gpio, HVC, and DesignWare matrix notes plus the existing HVC continuity packet",
    "`bcm2835_wdt`: current repo rereads do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`gpio_wdt`: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` is directly readable on current `master`",
    "`hvc_console`: `Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`dw_wdt`: `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` is reread on current `master` through the returned DesignWare owner packet",
]

FORBIDDEN_MARKERS = [
    "`PHASE11_MATRIX_GAP_STATUS=gpio_and_hvc_matrices_direct_readback_only`",
    "do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` or `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "Current Repo Reality - `Documentation/zigux/phase11-validation-matrix-gap-survey.md` - `Documentation/zigux/phase11-driver-lane-sequencing.md` - `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "The directly readable driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` and `Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "does not stand in for a whole-Phase-11 replay roster while the current direct-readback expansion is limited to the gpio and HVC matrix notes plus the existing HVC continuity packet",
    "`PHASE11_MATRIX_GAP_STATUS=all_phase11_driver_matrices_direct_readback_only`",
    "Current direct contents reads in this run now rematerialize all four driver-local Phase 11 matrix notes named by the roadmap",
    "The directly readable driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "does not stand in for a whole-Phase-11 replay roster while the current direct-readback expansion is limited to the four driver-local matrix notes plus the existing HVC continuity packet",
]

FIXTURE_TEXT = """# Phase 11 Validation Matrix Gap Survey

- `PHASE11_MATRIX_GAP_STATUS=gpio_hvc_and_dw_reread_with_bcm_gap`
- lane: `P11-L03`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- Current Repo Reality
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`
- Current repo rereads in this run rematerialize the gpio watchdog, HVC, and DesignWare matrix notes, but do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, so the shared matrix packet should treat gpio, HVC, and DesignWare as current reread matrix evidence while keeping bcm2835 in repo-reality-gap vocabulary.
- The reread driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`.
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains useful adjacent shared evidence, but it is not one of the driver-local Phase 11 validation matrices named by the roadmap.
- `zigux/tests/fixtures/phase11_build_inventory.json` still records the narrower current-head HVC continuity packet.
- 3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.
- the shared build inventory does not stand in for a whole-Phase-11 replay roster while the current reread expansion is limited to the gpio, HVC, and DesignWare matrix notes plus the existing HVC continuity packet.
- `bcm2835_wdt`: current repo rereads do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `gpio_wdt`: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` is directly readable on current `master`
- `hvc_console`: `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `dw_wdt`: `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` is reread on current `master` through the returned DesignWare owner packet
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

        required_self_test_markers = (
            REQUIRED_MARKERS[:9]
            + [
                REQUIRED_MARKERS[15],
                REQUIRED_MARKERS[18],
                REQUIRED_MARKERS[23],
            ]
        )
        for index, marker in enumerate(required_self_test_markers, start=1):
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
        print("PHASE11_MATRIX_GAP_SURVEY_SELF_TEST_CASE_COUNT=22")
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

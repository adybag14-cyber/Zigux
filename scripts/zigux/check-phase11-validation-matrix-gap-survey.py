#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase11-validation-matrix-gap-survey.py"

FILES = {
    "matrix_gap_note": "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
    "dw_matrix": "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "dw_survey": "Documentation/zigux/phase11-dw-wdt-survey.md",
    "dw_manifest": "zigux/tests/phase11_dw_wdt_manifest.json",
    "shared_build": "zigux/tests/phase11_build.zig",
}

MARKERS = {
    "matrix_gap_note": [
        "# Phase 11 Validation Matrix Gap Survey",
        "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
        "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
        "`Documentation/zigux/phase11-dw-wdt-survey.md`",
        "`Documentation/zigux/phase11-dw-wdt-slice.md`",
        "`Documentation/zigux/phase11-dw-wdt-teardown-note.md`",
        "`zigux/tests/phase11_dw_wdt_manifest.json`",
        "`zigux/tests/phase11_dw_wdt_survey.zig`",
        "`zigux/tests/phase11_build.zig`",
        "Current `master` now ships the bounded DesignWare review packet beside the surviving platform-registration continuity note",
        "`dw_wdt`: validation matrix present through `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
        "It is now accurate to claim four live driver-local validation matrices on current `master`",
    ],
    "dw_matrix": [
        "`PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`",
        "`zigux/tests/phase11_dw_wdt_manifest.json`",
        "`zigux/tests/phase11_dw_wdt_survey.zig`",
        "phase11-dw-wdt-survey-tests",
    ],
    "dw_survey": [
        "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md` now records the bounded hardware-validation posture",
        "`phase11-dw-wdt-survey-tests`",
    ],
    "dw_manifest": [
        '"phase11-dw-wdt-live-platform-acquisition"',
        '"status": "ready_next"',
    ],
    "shared_build": [
        '"phase11-dw-wdt-tests"',
        '"phase11-dw-wdt-registration-scaffold-tests"',
        '"phase11-dw-wdt-verify-tests"',
        '"phase11-dw-wdt-survey-tests"',
    ],
}

FORBIDDEN_MARKERS = {
    "matrix_gap_note": [
        "`PHASE11_MATRIX_GAP_STATUS=dw_matrix_gap_only`",
        "Current `master` does not ship `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
        "`dw_wdt`: no current `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` is shipped on `master`",
        "the live matrix count is three",
        "with DesignWare currently represented by the surviving platform-registration continuity packet instead",
    ],
}


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {label}: {marker}")


def expect_forbidden_markers_absent(label: str, text: str) -> None:
    for marker in FORBIDDEN_MARKERS.get(label, []):
        if marker in text:
            raise CheckError(f"forbidden marker in {label}: {marker}")


def run_check(root: Path) -> None:
    texts = {label: read_text(root, path) for label, path in FILES.items()}
    for label, markers in MARKERS.items():
        expect_markers(label, texts[label], markers)
    for label, text in texts.items():
        expect_forbidden_markers_absent(label, text)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    for label, relative_path in FILES.items():
        lines = list(MARKERS.get(label, [])) or [f"placeholder for {label}"]
        write(root / relative_path, "\n".join(lines) + "\n")


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
        build_self_test_fixture(fixture_root)
        run_check(fixture_root)

        required_cases = [
            (label, marker)
            for label, markers in MARKERS.items()
            for marker in markers
        ]
        for idx, (label, marker) in enumerate(required_cases, start=1):
            case_root = tmpdir / f"required_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(
                path.read_text(encoding="utf-8").replace(marker + "\n", "", 1).replace(marker, "", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        forbidden_cases = [
            (label, marker)
            for label, markers in FORBIDDEN_MARKERS.items()
            for marker in markers
        ]
        for idx, (label, marker) in enumerate(forbidden_cases, start=1):
            case_root = tmpdir / f"forbidden_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            expect_failure(case_root, marker)

        missing_file_cases = list(FILES.values())
        for idx, relative_path in enumerate(missing_file_cases, start=1):
            case_root = tmpdir / f"missing_file_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            (case_root / relative_path).unlink()
            expect_failure(case_root, relative_path)

        print("PHASE11_MATRIX_GAP_SURVEY_CHECK=pass")
        print(
            "PHASE11_MATRIX_GAP_SURVEY_SELF_TEST_CASE_COUNT="
            f"{len(required_cases) + len(forbidden_cases) + len(missing_file_cases)}"
        )
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
        print(f"PHASE11_MATRIX_GAP_SURVEY_CHECK=fail: {exc}")
        return 1

    print("PHASE11_MATRIX_GAP_SURVEY_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase11-uapi-header-parity-survey.md")
COVERAGE_NOTE_PATH = Path(
    "Documentation/zigux/phase11-uapi-header-parity-checker-coverage-note.md"
)
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")

SURVEY_MARKERS = (
    "`phase11-shared-reminder-surface-gap`",
    "`scripts/zigux/README.md` and `zigux/tests/README.md` still omit a Phase 11 packet entry",
    "narrower validator-backed packet is landed",
)

COVERAGE_MARKERS = (
    "the shared reminder surfaces outside this note stack still lag the roadmap",
    "`scripts/zigux/README.md` and `zigux/tests/README.md` currently skip Phase 11",
    "`Documentation/zigux/phase11-uapi-header-parity-survey.md`",
    "`scripts/zigux/validate-phase11.py`",
    "`make -C zigux phase11-validate`",
)

README_FORBIDDEN_MARKERS = (
    "## Phase 11",
    "phase11-validate",
    "check-phase11-header-boundary-packet.py",
)


class CheckError(RuntimeError):
    pass


def read(root: Path, path: Path) -> str:
    candidate = root / path
    try:
        return candidate.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckError(f"missing {path}") from exc


def require_markers(text: str, path: Path, markers: tuple[str, ...]) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise CheckError(f"{path} missing marker: {missing[0]}")


def require_absent(text: str, path: Path, markers: tuple[str, ...]) -> None:
    present = [marker for marker in markers if marker in text]
    if present:
        raise CheckError(f"{path} unexpectedly contains marker: {present[0]}")


def run_check(root: Path) -> None:
    survey = read(root, SURVEY_PATH)
    coverage = read(root, COVERAGE_NOTE_PATH)
    scripts_readme = read(root, SCRIPTS_README_PATH)
    tests_readme = read(root, TESTS_README_PATH)

    require_markers(survey, SURVEY_PATH, SURVEY_MARKERS)
    require_markers(coverage, COVERAGE_NOTE_PATH, COVERAGE_MARKERS)
    require_absent(scripts_readme, SCRIPTS_README_PATH, README_FORBIDDEN_MARKERS)
    require_absent(tests_readme, TESTS_README_PATH, README_FORBIDDEN_MARKERS)


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"fixture missing marker {marker!r}")
    return text.replace(marker, "", 1)


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def write_fixture(root: Path) -> None:
    files = {
        SURVEY_PATH: "\n".join(SURVEY_MARKERS) + "\n",
        COVERAGE_NOTE_PATH: "\n".join(COVERAGE_MARKERS) + "\n",
        SCRIPTS_README_PATH: "# scripts/zigux\n\n## Phase 12\n",
        TESTS_README_PATH: "# zigux/tests\n\n## Phase 10\n",
    }
    for path, content in files.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_reminder_surface_gap_"))
    try:
        fixture = tmpdir / "fixture"
        write_fixture(fixture)
        run_check(fixture)
        case_count = 1

        survey_missing = tmpdir / "survey_missing"
        shutil.copytree(fixture, survey_missing)
        path = survey_missing / SURVEY_PATH
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), SURVEY_MARKERS[0]), encoding="utf-8")
        expect_failure(survey_missing, SURVEY_MARKERS[0])
        case_count += 1

        coverage_missing = tmpdir / "coverage_missing"
        shutil.copytree(fixture, coverage_missing)
        path = coverage_missing / COVERAGE_NOTE_PATH
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), COVERAGE_MARKERS[-1]), encoding="utf-8")
        expect_failure(coverage_missing, COVERAGE_MARKERS[-1])
        case_count += 1

        scripts_fixed = tmpdir / "scripts_fixed"
        shutil.copytree(fixture, scripts_fixed)
        path = scripts_fixed / SCRIPTS_README_PATH
        path.write_text(path.read_text(encoding="utf-8") + "\n## Phase 11\n", encoding="utf-8")
        expect_failure(scripts_fixed, "unexpectedly contains marker: ## Phase 11")
        case_count += 1

        tests_fixed = tmpdir / "tests_fixed"
        shutil.copytree(fixture, tests_fixed)
        path = tests_fixed / TESTS_README_PATH
        path.write_text(path.read_text(encoding="utf-8") + "\nphase11-validate\n", encoding="utf-8")
        expect_failure(tests_fixed, "unexpectedly contains marker: phase11-validate")
        case_count += 1

        print("PHASE11_REMINDER_SURFACE_GAP_SELF_TEST=pass")
        print(f"PHASE11_REMINDER_SURFACE_GAP_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    try:
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_REMINDER_SURFACE_GAP=fail: {exc}")
        return 1
    print("PHASE11_REMINDER_SURFACE_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

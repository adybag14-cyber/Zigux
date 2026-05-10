#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

SURVEY_NOTE_PATH = Path("Documentation/zigux/phase11-hvc-console-survey.md")
VALIDATION_MATRIX_PATH = Path("Documentation/zigux/phase11-hvc-console-validation-matrix.md")

REQUIRED_SURVEY_MARKERS = (
    "archival checkpoint",
    "`ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839` as the archived landing review",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
)

FORBIDDEN_SURVEY_MARKERS = (
    "The live repo state is now:",
    "reviewed against live `master` `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`",
)

REQUIRED_MATRIX_MARKERS = (
    "archival landing checkpoint",
    "not as a rolling promise about the current `master` head",
    "keep `Documentation/zigux/phase11-hvc-console-survey.md` aligned with this matrix",
)


def collect_missing_markers(label: str, path: Path, markers: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:missing:{marker}")
    return failures


def collect_forbidden_markers(label: str, path: Path, markers: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for marker in markers:
        if marker in text:
            failures.append(f"{label}:forbidden:{marker}")
    return failures


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in (SURVEY_NOTE_PATH, VALIDATION_MATRIX_PATH):
        path = root / rel_path
        if not path.is_file():
            failures.append(f"missing_file:{rel_path.as_posix()}")
            return failures

    failures.extend(
        collect_missing_markers(
            SURVEY_NOTE_PATH.as_posix(),
            root / SURVEY_NOTE_PATH,
            REQUIRED_SURVEY_MARKERS,
        )
    )
    failures.extend(
        collect_forbidden_markers(
            SURVEY_NOTE_PATH.as_posix(),
            root / SURVEY_NOTE_PATH,
            FORBIDDEN_SURVEY_MARKERS,
        )
    )
    failures.extend(
        collect_missing_markers(
            VALIDATION_MATRIX_PATH.as_posix(),
            root / VALIDATION_MATRIX_PATH,
            REQUIRED_MATRIX_MARKERS,
        )
    )
    return failures


def write_fixture_tree(root: Path) -> None:
    (root / SURVEY_NOTE_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / VALIDATION_MATRIX_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / SURVEY_NOTE_PATH).write_text(
        "# Phase 11 HVC Console Survey\n"
        "\n"
        "This survey note now serves as the archival checkpoint for the original Phase 11 roadmap gap around `drivers/tty/hvc/hvc_console.c`.\n"
        "\n"
        "Treat `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839` as the archived landing review for the bounded starter instead of a rolling live-head claim.\n"
        "\n"
        "Keep `Documentation/zigux/phase11-hvc-console-validation-matrix.md` and `Documentation/zigux/phase11-shared-replay-contract.md` aligned with this archival note whenever the shared HVC review packet moves.\n",
        encoding="utf-8",
    )
    (root / VALIDATION_MATRIX_PATH).write_text(
        "## Status\n"
        "- treat `zigux/tests/phase11_hvc_console_manifest.json` and `Documentation/zigux/phase11-hvc-console-survey.md` as the archival landing checkpoint for the bounded starter, not as a rolling promise about the current `master` head\n"
        "- keep `Documentation/zigux/phase11-hvc-console-survey.md` aligned with this matrix whenever the dedicated HVC packet moves\n",
        encoding="utf-8",
    )


def expect_failure(root: Path, rel_path: Path, marker: str, expected: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(marker, "", 1), encoding="utf-8")
    failures = validate(root)
    if expected not in failures:
        raise AssertionError(f"missing expected failure {expected!r}; got {failures!r}")


def expect_forbidden_failure(root: Path, marker: str) -> None:
    path = root / SURVEY_NOTE_PATH
    original = path.read_text(encoding="utf-8")
    path.write_text(original + marker + "\n", encoding="utf-8")
    failures = validate(root)
    expected = f"{SURVEY_NOTE_PATH.as_posix()}:forbidden:{marker}"
    if expected not in failures:
        raise AssertionError(f"missing expected failure {expected!r}; got {failures!r}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase11_hvc_archival_continuity_") as tmpdir:
        root = Path(tmpdir)
        write_fixture_tree(root)
        failures = validate(root)
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            return 1

        for marker in REQUIRED_SURVEY_MARKERS:
            expect_failure(root, SURVEY_NOTE_PATH, marker, f"{SURVEY_NOTE_PATH.as_posix()}:missing:{marker}")
            write_fixture_tree(root)
            case_count += 1

        for marker in FORBIDDEN_SURVEY_MARKERS:
            expect_forbidden_failure(root, marker)
            write_fixture_tree(root)
            case_count += 1

        for marker in REQUIRED_MATRIX_MARKERS:
            expect_failure(root, VALIDATION_MATRIX_PATH, marker, f"{VALIDATION_MATRIX_PATH.as_posix()}:missing:{marker}")
            write_fixture_tree(root)
            case_count += 1

        (root / VALIDATION_MATRIX_PATH).unlink()
        failures = validate(root)
        expected_missing = f"missing_file:{VALIDATION_MATRIX_PATH.as_posix()}"
        if expected_missing not in failures:
            raise AssertionError(f"missing expected failure {expected_missing!r}; got {failures!r}")
        case_count += 1

    print(f"PHASE11_HVC_ARCHIVAL_CONTINUITY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the Phase 11 HVC archival survey continuity packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("PHASE11_HVC_ARCHIVAL_CONTINUITY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

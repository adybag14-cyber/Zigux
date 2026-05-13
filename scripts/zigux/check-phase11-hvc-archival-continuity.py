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
    "This note restores the compact archival survey",
    "archival landing checkpoint:",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "the paired teardown checkpoint readable together",
)

FORBIDDEN_SURVEY_MARKERS = (
    "The live repo state is now:",
    "reviewed against live `master` `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`",
)

REQUIRED_MATRIX_MARKERS = (
    "archival landing checkpoint",
    "not as a rolling promise about runtime parity",
    "keep `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-slice.md`, and this matrix aligned",
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
        "This note restores the compact archival survey for the bounded Phase 11 `hvc_console` packet on current `master`.\n"
        "\n"
        "* archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`\n"
        "* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`\n"
        "\n"
        "The survey note exists to keep those surfaces, the direct `drivers/tty/hvc/hvc_console.zig` starter, the paired validation matrix, and the paired teardown checkpoint readable together without overstating runtime parity or widening the Phase 11 claim beyond the landed starter.\n",
        encoding="utf-8",
    )
    (root / VALIDATION_MATRIX_PATH).write_text(
        "## Status\n"
        "- archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`\n"
        "\n"
        "## Review Rules\n"
        "- treat `zigux/tests/phase11_hvc_console_manifest.json` and `Documentation/zigux/phase11-hvc-console-survey.md` as the landing checkpoint for the archived packet at `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`, not as a rolling promise about runtime parity\n"
        "- keep `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-slice.md`, and this matrix aligned whenever the close, remove, notifier-add, khvcd polling-contract, or hangup-disconnect ownership story changes\n",
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

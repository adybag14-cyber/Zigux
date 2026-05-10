#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

SURVEY_NOTE_PATH = Path("Documentation/zigux/phase11-bcm2835-wdt-survey.md")
VALIDATION_MATRIX_PATH = Path("Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md")

REQUIRED_SURVEY_MARKERS = (
    "archival survey now carries `P11-L08` packet identity",
    "tracked through `P11-L10`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
)

REQUIRED_MATRIX_MARKERS = (
    "`PHASE11_BCM2835_WDT_STATUS=platform_handoff_landed`",
    "archival packet identity remains `P11-L08`",
    "current lane-sequencing note still keeps this bounded bcm2835 watchdog packet on the bcm2835 lane",
)


def collect_missing_markers(label: str, path: Path, markers: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:{marker}")
    return failures


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path, markers in (
        (SURVEY_NOTE_PATH, REQUIRED_SURVEY_MARKERS),
        (VALIDATION_MATRIX_PATH, REQUIRED_MATRIX_MARKERS),
    ):
        path = root / rel_path
        if not path.is_file():
            failures.append(f"missing_file:{rel_path.as_posix()}")
            continue
        failures.extend(collect_missing_markers(rel_path.as_posix(), path, markers))
    return failures


def write_fixture_tree(root: Path) -> None:
    (root / SURVEY_NOTE_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / VALIDATION_MATRIX_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / SURVEY_NOTE_PATH).write_text(
        "# Phase 11 BCM2835 Watchdog Survey\n"
        "This lane is archived.\n"
        "The archival survey now carries `P11-L08` packet identity for traceability while current scheduled watchdog-family continuity remains tracked through `P11-L10`.\n"
        "The packet still references `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` and `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`.\n",
        encoding="utf-8",
    )
    (root / VALIDATION_MATRIX_PATH).write_text(
        "## Status\n"
        "- `PHASE11_BCM2835_WDT_STATUS=platform_handoff_landed`\n"
        "- archival packet identity remains `P11-L08`\n"
        "- current lane-sequencing note still keeps this bounded bcm2835 watchdog packet on the bcm2835 lane\n",
        encoding="utf-8",
    )


def expect_failure(root: Path, rel_path: Path, marker: str, expected: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(marker, "", 1), encoding="utf-8")
    failures = validate(root)
    if expected not in failures:
        raise AssertionError(f"missing expected failure {expected!r}; got {failures!r}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase11_bcm2835_archival_continuity_") as tmpdir:
        root = Path(tmpdir)
        write_fixture_tree(root)
        failures = validate(root)
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            return 1

        for rel_path, markers in (
            (SURVEY_NOTE_PATH, REQUIRED_SURVEY_MARKERS),
            (VALIDATION_MATRIX_PATH, REQUIRED_MATRIX_MARKERS),
        ):
            for marker in markers:
                expect_failure(root, rel_path, marker, f"{rel_path.as_posix()}:{marker}")
                write_fixture_tree(root)
                case_count += 1

        shutil.rmtree(root / VALIDATION_MATRIX_PATH.parent)
        failures = validate(root)
        expected_missing = f"missing_file:{VALIDATION_MATRIX_PATH.as_posix()}"
        if expected_missing not in failures:
            raise AssertionError(f"missing expected failure {expected_missing!r}; got {failures!r}")
        case_count += 1

    print(f"PHASE11_BCM2835_ARCHIVAL_CONTINUITY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the bcm2835 watchdog archival continuity packet."
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

    print("PHASE11_BCM2835_ARCHIVAL_CONTINUITY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

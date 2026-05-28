#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

TESTS_README = "zigux/tests/README.md"
SURVEY_DOC = "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md"
SURVEY_CHECKER = "scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py"
GENKSYMS_BRIDGE_CHECKER = "scripts/zigux/check-genksyms-bridge.py"
GENKSYMS_HELPER = "scripts/zigux/genksyms.zig"

REQUIRED_TESTS_README_MARKERS = [
    SURVEY_DOC,
    SURVEY_CHECKER,
    GENKSYMS_BRIDGE_CHECKER,
    GENKSYMS_HELPER,
    "survey-backed genksyms packet",
]

REQUIRED_SURVEY_MARKERS = [
    "# Phase 2 genksyms dual-implementation survey",
    GENKSYMS_BRIDGE_CHECKER,
    GENKSYMS_HELPER,
]

REQUIRED_CHECKER_MARKERS = [
    SURVEY_DOC,
    "PHASE2_GENKSYMS_DUAL_IMPLEMENTATION_SURVEY_SELF_TEST=pass",
]


def read_text(root: Path, rel_path: str, failures: list[str]) -> str | None:
    path = root / rel_path
    if not path.exists():
        failures.append(f"missing_file:{rel_path}")
        return None
    return path.read_text(encoding="utf-8")


def require_markers(text: str | None, rel_path: str, markers: list[str], failures: list[str]) -> None:
    if text is None:
        return
    for marker in markers:
        if marker not in text:
            failures.append(f"missing_marker:{rel_path}:{marker}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    tests_readme = read_text(root, TESTS_README, failures)
    survey_doc = read_text(root, SURVEY_DOC, failures)
    survey_checker = read_text(root, SURVEY_CHECKER, failures)

    require_markers(tests_readme, TESTS_README, REQUIRED_TESTS_README_MARKERS, failures)
    require_markers(survey_doc, SURVEY_DOC, REQUIRED_SURVEY_MARKERS, failures)
    require_markers(survey_checker, SURVEY_CHECKER, REQUIRED_CHECKER_MARKERS, failures)
    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(
        root / TESTS_README,
        "\n".join(
            [
                "# zigux/tests",
                "",
                "## Phase 2 review packet",
                f"  * `{SURVEY_DOC}`",
                f"  * `{SURVEY_CHECKER}`",
                f"  * `{GENKSYMS_BRIDGE_CHECKER}`",
                f"  * `{GENKSYMS_HELPER}`",
                "  * keep the survey-backed genksyms packet visible from the tests root",
                "",
            ]
        ),
    )
    write_text(
        root / SURVEY_DOC,
        "\n".join(
            [
                "# Phase 2 genksyms dual-implementation survey",
                f"- {GENKSYMS_BRIDGE_CHECKER}",
                f"- {GENKSYMS_HELPER}",
                "",
            ]
        ),
    )
    write_text(
        root / SURVEY_CHECKER,
        "\n".join(
            [
                f'SURVEY = ROOT / "{SURVEY_DOC}"',
                'print("PHASE2_GENKSYMS_DUAL_IMPLEMENTATION_SURVEY_SELF_TEST=pass")',
                "",
            ]
        ),
    )


def mutate_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(marker, "__REMOVED_PHASE2_GENKSYMS_SURVEY_MARKER__", 1)
    if updated == text:
        raise SystemExit(f"fixture marker was not present: {marker}")
    path.write_text(updated, encoding="utf-8")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase2-tests-readme-genksyms-survey-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path in [TESTS_README, SURVEY_DOC, SURVEY_CHECKER]:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (TESTS_README, marker) for marker in REQUIRED_TESTS_README_MARKERS
        ] + [
            (SURVEY_DOC, marker) for marker in REQUIRED_SURVEY_MARKERS
        ] + [
            (SURVEY_CHECKER, marker) for marker in REQUIRED_CHECKER_MARKERS
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            mutate_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        case_count = 3 + len(marker_cases)
        print("PHASE2_TESTS_README_GENKSYMS_SURVEY_REMINDER_SELF_TEST=pass")
        print(f"PHASE2_TESTS_README_GENKSYMS_SURVEY_REMINDER_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that the tests-root Phase 2 reminder keeps the genksyms "
            "dual-implementation survey and its dedicated checker visible together."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE2_TESTS_README_GENKSYMS_SURVEY_REMINDER=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE2_TESTS_README_GENKSYMS_SURVEY_REMINDER=pass")
    print(
        "PHASE2_TESTS_README_GENKSYMS_SURVEY_REMINDER_TESTS_MARKER_COUNT="
        f"{len(REQUIRED_TESTS_README_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

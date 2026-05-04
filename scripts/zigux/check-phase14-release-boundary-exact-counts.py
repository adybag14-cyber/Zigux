#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

VALIDATOR_SNIPPETS = [
    "RELEASE_BOUNDARY_EXACT_COUNT_MARKERS = RELEASE_BOUNDARY_MARKERS",
    '"PHASE14_RELEASE_BOUNDARY=present"',
    '"PHASE14_SHARED_REPLAY_PRESENT=yes"',
    '"PHASE14_RELEASE_CLOSED=no"',
    'release_boundary_text = text("Documentation/zigux/phase14-release-boundary-survey.md")',
    "for marker in RELEASE_BOUNDARY_EXACT_COUNT_MARKERS:",
    'expect_exact_count("release_boundary", release_boundary_text, marker, 1, missing)',
]

DOCS_ROOT_CHECKER_SNIPPETS = [
    "RELEASE_BOUNDARY_LINES = [",
    '"PHASE14_RELEASE_BOUNDARY=present"',
    '"PHASE14_SHARED_REPLAY_PRESENT=yes"',
    '"PHASE14_RELEASE_CLOSED=no"',
    "require_exact_count(",
    '"release_boundary", release_boundary_text, RELEASE_BOUNDARY_LINES, 1',
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_exact_count(label: str, text: str, snippets: list[str], expected_count: int) -> list[str]:
    issues: list[str] = []
    for snippet in snippets:
        actual_count = text.count(snippet)
        if actual_count != expected_count:
            issues.append(f"{label}:{actual_count}:{snippet}")
    return issues


def validate_validator_alignment(validator_text: str, docs_root_checker_text: str) -> list[str]:
    issues = require_exact_count("validator", validator_text, VALIDATOR_SNIPPETS, 1)
    issues.extend(
        require_exact_count(
            "docs_root_checker",
            docs_root_checker_text,
            DOCS_ROOT_CHECKER_SNIPPETS,
            1,
        )
    )
    return issues


def run_self_test() -> int:
    validator_text = """
RELEASE_BOUNDARY_MARKERS = [
    "PHASE14_RELEASE_BOUNDARY=present",
    "PHASE14_SHARED_REPLAY_PRESENT=yes",
    "PHASE14_RELEASE_CLOSED=no",
]
RELEASE_BOUNDARY_EXACT_COUNT_MARKERS = RELEASE_BOUNDARY_MARKERS
release_boundary_text = text("Documentation/zigux/phase14-release-boundary-survey.md")
for marker in RELEASE_BOUNDARY_EXACT_COUNT_MARKERS:
    expect_exact_count("release_boundary", release_boundary_text, marker, 1, missing)
""".strip()

    docs_root_checker_text = """
RELEASE_BOUNDARY_LINES = [
    "PHASE14_RELEASE_BOUNDARY=present",
    "PHASE14_SHARED_REPLAY_PRESENT=yes",
    "PHASE14_RELEASE_CLOSED=no",
]
missing.extend(
    require_exact_count(
        "release_boundary", release_boundary_text, RELEASE_BOUNDARY_LINES, 1
    )
)
""".strip()

    cases = [
        ("happy_path", validator_text, docs_root_checker_text, False),
        (
            "missing_validator_shared_replay_marker",
            validator_text.replace('"PHASE14_SHARED_REPLAY_PRESENT=yes"', "", 1),
            docs_root_checker_text,
            True,
        ),
        (
            "duplicate_validator_exact_count_alias",
            validator_text + "\nRELEASE_BOUNDARY_EXACT_COUNT_MARKERS = RELEASE_BOUNDARY_MARKERS",
            docs_root_checker_text,
            True,
        ),
        (
            "missing_docs_root_shared_replay_marker",
            validator_text,
            docs_root_checker_text.replace('"PHASE14_SHARED_REPLAY_PRESENT=yes"', "", 1),
            True,
        ),
        (
            "duplicate_docs_root_release_closed_marker",
            validator_text,
            docs_root_checker_text + '\n"PHASE14_RELEASE_CLOSED=no"',
            True,
        ),
    ]

    for name, validator_value, docs_root_checker_value, should_fail in cases:
        issues = validate_validator_alignment(validator_value, docs_root_checker_value)
        failed = bool(issues)
        if failed != should_fail:
            print(f"PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST={name}:fail")
            if issues:
                print("ISSUES_START")
                for issue in issues:
                    print(issue)
                print("ISSUES_END")
            return 1

    print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass")
    print(f"PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        return run_self_test()

    validator_path = ROOT / "scripts/zigux/validate-phase14.py"
    docs_root_checker_path = ROOT / "scripts/zigux/check-phase14-docs-root-smoke-summary.py"
    required_paths = [validator_path, docs_root_checker_path]
    missing_files = [str(path) for path in required_paths if not path.exists()]
    if missing_files:
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS=fail")
        print("MISSING_FILES_START")
        for path in missing_files:
            print(path)
        print("MISSING_FILES_END")
        return 1

    issues = validate_validator_alignment(read(validator_path), read(docs_root_checker_path))
    if issues:
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS=fail")
        print("ISSUES_START")
        for issue in issues:
            print(issue)
        print("ISSUES_END")
        return 1

    print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS=pass")
    print(f"PHASE14_VALIDATOR_SNIPPET_COUNT={len(VALIDATOR_SNIPPETS)}")
    print(f"PHASE14_DOCS_ROOT_CHECKER_SNIPPET_COUNT={len(DOCS_ROOT_CHECKER_SNIPPETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

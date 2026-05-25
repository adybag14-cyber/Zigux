#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
DOCS_README = Path("Documentation/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")

SUMMARY_CHECKER = "`scripts/zigux/check-phase2-tests-root-summary.py`"
ROUTE_GAP_CHECKER = "`scripts/zigux/check-phase2-tests-root-summary-route-gap.py`"
VALIDATOR_GAP_CHECKER = "`scripts/zigux/check-phase2-closure-validator-gap.py`"

TRIO_MARKERS = (
    SUMMARY_CHECKER,
    ROUTE_GAP_CHECKER,
    VALIDATOR_GAP_CHECKER,
)

DOCS_REQUIRED_MARKERS = (
    SUMMARY_CHECKER,
    ROUTE_GAP_CHECKER,
    VALIDATOR_GAP_CHECKER,
)

TESTS_REQUIRED_MARKERS = (
    SUMMARY_CHECKER,
    ROUTE_GAP_CHECKER,
    VALIDATOR_GAP_CHECKER,
)


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    closure_text = read_text(root, PHASE2_CLOSURE)
    docs_text = read_text(root, DOCS_README)
    tests_text = read_text(root, TESTS_README)

    for marker in TRIO_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in DOCS_REQUIRED_MARKERS:
        if marker not in docs_text:
            issues.append(("MISSING_DOCS_MARKER", marker))

    for marker in TESTS_REQUIRED_MARKERS:
        if marker not in tests_text:
            issues.append(("MISSING_TESTS_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_SHARED_REMINDER_GAP_TRIO=fail")
    for code, value in issues:
        print(f"{code}:{value}")
    return 1


def build_self_test_root(root: Path) -> None:
    closure_text = "\n".join(
        (
            "# Phase 2 Closure",
            "",
            SUMMARY_CHECKER,
            ROUTE_GAP_CHECKER,
            VALIDATOR_GAP_CHECKER,
            "",
        )
    )
    docs_text = "\n".join(
        (
            "# Zigux Documentation",
            "",
            "Phase 2 notes",
            SUMMARY_CHECKER,
            ROUTE_GAP_CHECKER,
            VALIDATOR_GAP_CHECKER,
            "",
        )
    )
    tests_text = "\n".join(
        (
            "# zigux/tests",
            "",
            "## Phase 2 review packet",
            SUMMARY_CHECKER,
            ROUTE_GAP_CHECKER,
            VALIDATOR_GAP_CHECKER,
            "",
        )
    )

    write_text(root, PHASE2_CLOSURE, closure_text)
    write_text(root, DOCS_README, docs_text)
    write_text(root, TESTS_README, tests_text)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="lane22_shared_reminder_gap_trio_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in TRIO_MARKERS:
            build_self_test_root(root)
            write_text(
                root,
                PHASE2_CLOSURE,
                read_text(root, PHASE2_CLOSURE).replace(marker, "", 1),
            )
            assert ("MISSING_CLOSURE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in DOCS_REQUIRED_MARKERS:
            build_self_test_root(root)
            write_text(
                root,
                DOCS_README,
                read_text(root, DOCS_README).replace(marker, "", 1),
            )
            assert ("MISSING_DOCS_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in TESTS_REQUIRED_MARKERS:
            build_self_test_root(root)
            write_text(
                root,
                TESTS_README,
                read_text(root, TESTS_README).replace(marker, "", 1),
            )
            assert ("MISSING_TESTS_MARKER", marker) in collect_issues(root)
            checks_run += 1

    print("PHASE2_SHARED_REMINDER_GAP_TRIO_SELF_TEST=pass")
    print(f"PHASE2_SHARED_REMINDER_GAP_TRIO_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed when the docs-root and tests-root Phase 2 reminder "
            "surfaces stop carrying the closure-side summary and gap guard trio."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_SHARED_REMINDER_GAP_TRIO=pass")
    print(
        "PHASE2_SHARED_REMINDER_GAP_TRIO_PACKET="
        "docs_root_tests_root_closure_side_summary_gap_guards"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

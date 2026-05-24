#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SUMMARY_CHECKER = Path("scripts/zigux/check-phase2-tests-root-summary.py")
VALIDATE_PHASE2 = Path("scripts/zigux/validate-phase2.py")
VALIDATE_PHASE2_CLOSURE = Path("scripts/zigux/validate-phase2-closure.py")
MAKEFILE = Path("zigux/Makefile")

REQUIRED_SUMMARY_MARKERS = (
    "PHASE2_TESTS_ROOT_SUMMARY=pass",
    "PHASE2_TESTS_ROOT_SUMMARY_GAP=",
)

REQUIRED_VALIDATE_PHASE2_MARKERS = (
    '"scripts/zigux/check-phase2-tests-root-summary.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-root-summary.py",',
)

REQUIRED_VALIDATE_PHASE2_CLOSURE_MARKERS = (
    '"`scripts/zigux/check-phase2-tests-root-summary.py`",',
    '"`python3 scripts/zigux/check-phase2-tests-root-summary.py --self-test`",',
    '"`python3 scripts/zigux/check-phase2-tests-root-summary.py`",',
)

REQUIRED_MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-root-summary.py",
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

    summary_text = read_text(root, SUMMARY_CHECKER)
    for marker in REQUIRED_SUMMARY_MARKERS:
        if marker not in summary_text:
            issues.append(("MISSING_SUMMARY_CHECKER_MARKER", marker))

    validate_phase2_text = read_text(root, VALIDATE_PHASE2)
    for marker in REQUIRED_VALIDATE_PHASE2_MARKERS:
        if marker not in validate_phase2_text:
            issues.append(("MISSING_VALIDATE_PHASE2_MARKER", marker))

    validate_phase2_closure_text = read_text(root, VALIDATE_PHASE2_CLOSURE)
    for marker in REQUIRED_VALIDATE_PHASE2_CLOSURE_MARKERS:
        if marker not in validate_phase2_closure_text:
            issues.append(("MISSING_VALIDATE_PHASE2_CLOSURE_MARKER", marker))

    makefile_text = read_text(root, MAKEFILE)
    for marker in REQUIRED_MAKEFILE_LINES:
        count = makefile_text.count(marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{count}::{marker}"))

    return issues


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        SUMMARY_CHECKER,
        "\n".join(
            (
                "PHASE2_TESTS_ROOT_SUMMARY=pass",
                "PHASE2_TESTS_ROOT_SUMMARY_GAP=third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
            )
        )
        + "\n",
    )
    write_text(
        root,
        VALIDATE_PHASE2,
        "\n".join(
            (
                "REQUIRED_PATHS = (",
                '    "scripts/zigux/check-phase2-tests-root-summary.py",',
                ")",
                "REQUIRED_MAKEFILE_LINES = (",
                '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-root-summary.py",',
                ")",
            )
        )
        + "\n",
    )
    write_text(
        root,
        VALIDATE_PHASE2_CLOSURE,
        "\n".join(
            (
                "REQUIRED_CLOSURE_MARKERS = (",
                '    "`scripts/zigux/check-phase2-tests-root-summary.py`",',
                '    "`python3 scripts/zigux/check-phase2-tests-root-summary.py --self-test`",',
                '    "`python3 scripts/zigux/check-phase2-tests-root-summary.py`",',
                ")",
            )
        )
        + "\n",
    )
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
                "phase2-validate:",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-root-summary.py",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="lane22_tests_root_summary_route_gap_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        write_text(root, SUMMARY_CHECKER, "broken\n")
        assert any(code == "MISSING_SUMMARY_CHECKER_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(root, VALIDATE_PHASE2, "broken\n")
        assert any(code == "MISSING_VALIDATE_PHASE2_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(root, VALIDATE_PHASE2_CLOSURE, "broken\n")
        assert any(code == "MISSING_VALIDATE_PHASE2_CLOSURE_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE, "phase2-validate:\n")
        assert any(code == "MISSING_MAKEFILE_LINE" for code, _ in collect_issues(root))
        checks_run += 1

    print("PHASE2_TESTS_ROOT_SUMMARY_ROUTE_GAP_SELF_TEST=pass")
    print(f"PHASE2_TESTS_ROOT_SUMMARY_ROUTE_GAP_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the tests-root summary checker is not wired through the remaining Lane 22 routes."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE2_TESTS_ROOT_SUMMARY_ROUTE_GAP=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_TESTS_ROOT_SUMMARY_ROUTE_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

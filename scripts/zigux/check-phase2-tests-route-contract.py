#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATE = "scripts/zigux/validate-phase2.py"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"

REQUIRED_PATHS = (
    "Documentation/zigux/README.md",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
)

REQUIRED_VALIDATE_SNIPPETS = (
    '"Documentation/zigux/README.md",',
    '"scripts/zigux/check-phase2-tests-readme-alignment.py",',
    '"zigux/tests/README.md",',
    '"zigux/tests/fixtures/phase2_tool_manifest.json",',
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
)


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    validate_text = read_text(root, VALIDATE)
    workflow_text = read_text(root, WORKFLOW)
    makefile_text = read_text(root, MAKEFILE)

    for marker in REQUIRED_VALIDATE_SNIPPETS:
        count = validate_text.count(marker)
        if count == 0:
            issues.append(("MISSING_VALIDATE_SNIPPET", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATE_SNIPPET", f"{marker}:count={count}"))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TESTS_ROUTE_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(root, VALIDATE, "\n".join(REQUIRED_VALIDATE_SNIPPETS) + "\n")
    write_text(root, WORKFLOW, "\n".join(("name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES)) + "\n")
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
                "PYTHON ?= python3",
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "",
                *REQUIRED_MAKEFILE_LINES,
            )
        )
        + "\n",
    )
    for rel in REQUIRED_PATHS:
        write_text(root, rel, "present\n")


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(REQUIRED_VALIDATE_SNIPPETS)
        + len(REQUIRED_VALIDATE_SNIPPETS)
        + len(REQUIRED_WORKFLOW_LINES)
        + len(REQUIRED_WORKFLOW_LINES)
        + len(REQUIRED_MAKEFILE_LINES)
        + len(REQUIRED_MAKEFILE_LINES)
        + len(REQUIRED_PATHS)
        + 3
    )
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tests_route_contract_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in REQUIRED_VALIDATE_SNIPPETS:
            build_self_test_root(root)
            write_text(root, VALIDATE, read_text(root, VALIDATE).replace(marker, "", 1))
            expect_issue(root, ("MISSING_VALIDATE_SNIPPET", marker))
            checks += 1

        for marker in REQUIRED_VALIDATE_SNIPPETS:
            build_self_test_root(root)
            write_text(root, VALIDATE, read_text(root, VALIDATE) + marker + "\n")
            expect_issue(root, ("DUPLICATE_VALIDATE_SNIPPET", f"{marker}:count=2"))
            checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            write_text(root, WORKFLOW, replace_line(read_text(root, WORKFLOW), marker, "run: python3 scripts/zigux/other.py"))
            expect_issue(root, ("MISSING_WORKFLOW_LINE", marker))
            checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            write_text(root, WORKFLOW, duplicate_line(read_text(root, WORKFLOW), marker))
            expect_issue(root, ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2"))
            checks += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            write_text(root, MAKEFILE, replace_line(read_text(root, MAKEFILE), marker, "# removed"))
            expect_issue(root, ("MISSING_MAKEFILE_LINE", marker))
            checks += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            write_text(root, MAKEFILE, duplicate_line(read_text(root, MAKEFILE), marker))
            expect_issue(root, ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2"))
            checks += 1

        for rel in REQUIRED_PATHS:
            build_self_test_root(root)
            (root / rel).unlink()
            expect_issue(root, ("MISSING_REQUIRED_PATH", rel))
            checks += 1

        for rel in (VALIDATE, WORKFLOW, MAKEFILE):
            build_self_test_root(root)
            (root / rel).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel}")

    assert checks == expected_case_count
    print("PHASE2_TESTS_ROUTE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_TESTS_ROUTE_CONTRACT_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-close the live Phase 2 tests-root route contract.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TESTS_ROUTE_CONTRACT=pass")
    print(f"PHASE2_TESTS_ROUTE_CONTRACT_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_TESTS_ROUTE_CONTRACT_VALIDATE_SNIPPET_COUNT={len(REQUIRED_VALIDATE_SNIPPETS)}")
    print(f"PHASE2_TESTS_ROUTE_CONTRACT_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_TESTS_ROUTE_CONTRACT_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = "scripts/zigux/validate-phase2.py"
CLOSURE_MATRIX_CHECKER = "scripts/zigux/check-phase2-closure-matrix.py"

REQUIRED_LINES = (
    'CLOSURE_MATRIX_CHECKER = "scripts/zigux/check-phase2-closure-matrix.py"',
    '    CLOSURE_MATRIX_CHECKER,',
)
REQUIRED_SNIPPETS = (
    "Validate the current Phase 2 toolchain, kbuild, kconfig, closure-matrix, genksyms, and fixdep packet.",
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
    return sum(1 for line in text.splitlines() if line == marker)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker text not found: {marker}")
    return text.replace(marker, replacement, 1)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    validator_text = read_text(root, VALIDATOR)
    issues: list[tuple[str, str]] = []

    if not (root / CLOSURE_MATRIX_CHECKER).exists():
        issues.append(("MISSING_REQUIRED_PATH", CLOSURE_MATRIX_CHECKER))

    for marker in REQUIRED_LINES:
        count = count_exact_lines(validator_text, marker)
        if count == 0:
            issues.append(("MISSING_VALIDATOR_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATOR_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_SNIPPETS:
        count = validator_text.count(marker)
        if count == 0:
            issues.append(("MISSING_VALIDATOR_SNIPPET", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATOR_SNIPPET", f"{marker}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_SHARED_VALIDATOR_CLOSURE_MATRIX=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    validator_text = "\n".join(
        (
            "#!/usr/bin/env python3",
            'CLOSURE_MATRIX_CHECKER = "scripts/zigux/check-phase2-closure-matrix.py"',
            "REQUIRED_PATHS = (",
            "    CLOSURE_MATRIX_CHECKER,",
            ")",
            'parser_description = "Validate the current Phase 2 toolchain, kbuild, kconfig, closure-matrix, genksyms, and fixdep packet."',
            "",
        )
    )
    write_text(root, VALIDATOR, validator_text)
    write_text(root, CLOSURE_MATRIX_CHECKER, "present\n")


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_shared_validator_closure_matrix_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        (root / CLOSURE_MATRIX_CHECKER).unlink()
        expect_issue(root, ("MISSING_REQUIRED_PATH", CLOSURE_MATRIX_CHECKER))
        checks += 1

        for marker in REQUIRED_LINES:
            build_self_test_root(root)
            write_text(root, VALIDATOR, replace_exact_line(read_text(root, VALIDATOR), marker, "# removed"))
            expect_issue(root, ("MISSING_VALIDATOR_LINE", marker))
            checks += 1

            build_self_test_root(root)
            write_text(root, VALIDATOR, duplicate_exact_line(read_text(root, VALIDATOR), marker))
            expect_issue(root, ("DUPLICATE_VALIDATOR_LINE", f"{marker}:count=2"))
            checks += 1

        for marker in REQUIRED_SNIPPETS:
            build_self_test_root(root)
            write_text(root, VALIDATOR, replace_once(read_text(root, VALIDATOR), marker, "drifted"))
            expect_issue(root, ("MISSING_VALIDATOR_SNIPPET", marker))
            checks += 1

            build_self_test_root(root)
            write_text(root, VALIDATOR, read_text(root, VALIDATOR) + marker)
            expect_issue(root, ("DUPLICATE_VALIDATOR_SNIPPET", f"{marker}:count=2"))
            checks += 1

    print("PHASE2_SHARED_VALIDATOR_CLOSURE_MATRIX_SELF_TEST=pass")
    print(f"PHASE2_SHARED_VALIDATOR_CLOSURE_MATRIX_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when validate-phase2.py stops naming the shipped closure-matrix checker."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a passing sample repository root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        print(f"PHASE2_SHARED_VALIDATOR_CLOSURE_MATRIX_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_SHARED_VALIDATOR_CLOSURE_MATRIX=pass")
    print(f"PHASE2_SHARED_VALIDATOR_CLOSURE_MATRIX_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    print(f"PHASE2_SHARED_VALIDATOR_CLOSURE_MATRIX_REQUIRED_SNIPPET_COUNT={len(REQUIRED_SNIPPETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

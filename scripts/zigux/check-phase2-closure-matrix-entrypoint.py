#!/usr/bin/env python3
"""Guard the shared Phase 2 validator entrypoint for the closure-matrix checker."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VALIDATE_PHASE2_REL = Path("scripts/zigux/validate-phase2.py")
CLOSURE_MATRIX_REL = "scripts/zigux/check-phase2-closure-matrix.py"
REQUIRED_PATH_MARKER = f'"{CLOSURE_MATRIX_REL}",' 
DESCRIPTION_MARKER = "Validate the current Phase 2 toolchain, kbuild, closure-matrix, kconfig, genksyms, and fixdep packet."
LEGACY_DESCRIPTION_MARKER = "Validate the current Phase 2 toolchain, kbuild, kconfig, genksyms, and fixdep packet."


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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    text = read_text(root, VALIDATE_PHASE2_REL)
    issues: list[tuple[str, str]] = []

    path_count = count_exact_lines(text, REQUIRED_PATH_MARKER)
    if path_count == 0:
        issues.append(("MISSING_REQUIRED_PATH_MARKER", REQUIRED_PATH_MARKER))
    elif path_count != 1:
        issues.append(("DUPLICATE_REQUIRED_PATH_MARKER", f"{REQUIRED_PATH_MARKER}:count={path_count}"))

    description_count = text.count(DESCRIPTION_MARKER)
    if description_count == 0:
        issues.append(("MISSING_DESCRIPTION_MARKER", DESCRIPTION_MARKER))
    elif description_count != 1:
        issues.append(("DUPLICATE_DESCRIPTION_MARKER", f"{DESCRIPTION_MARKER}:count={description_count}"))

    legacy_count = text.count(LEGACY_DESCRIPTION_MARKER)
    if legacy_count != 0:
        issues.append(("UNEXPECTED_LEGACY_DESCRIPTION_MARKER", f"{LEGACY_DESCRIPTION_MARKER}:count={legacy_count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_MATRIX_ENTRYPOINT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    for child in root.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    write_text(
        root,
        VALIDATE_PHASE2_REL,
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "REQUIRED_PATHS = (",
                f"    {REQUIRED_PATH_MARKER}",
                "    \"scripts/zigux/validate-phase2-closure.py\",",
                ")",
                "",
                "def main() -> int:",
                f"    parser_description = \"{DESCRIPTION_MARKER}\"",
                "    return 0",
                "",
            )
        ),
    )


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def run_self_test() -> int:
    checks = 0
    expected_case_count = 7
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_matrix_entrypoint_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            VALIDATE_PHASE2_REL,
            replace_exact_line(read_text(root, VALIDATE_PHASE2_REL), REQUIRED_PATH_MARKER, '    "scripts/zigux/other.py",'),
        )
        expect_issue(root, ("MISSING_REQUIRED_PATH_MARKER", REQUIRED_PATH_MARKER))
        checks += 1

        build_sample_root(root)
        write_text(root, VALIDATE_PHASE2_REL, duplicate_exact_line(read_text(root, VALIDATE_PHASE2_REL), REQUIRED_PATH_MARKER))
        expect_issue(root, ("DUPLICATE_REQUIRED_PATH_MARKER", f"{REQUIRED_PATH_MARKER}:count=2"))
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            VALIDATE_PHASE2_REL,
            read_text(root, VALIDATE_PHASE2_REL).replace(DESCRIPTION_MARKER, "Validate the current Phase 2 packet."),
        )
        expect_issue(root, ("MISSING_DESCRIPTION_MARKER", DESCRIPTION_MARKER))
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            VALIDATE_PHASE2_REL,
            read_text(root, VALIDATE_PHASE2_REL).replace(DESCRIPTION_MARKER, f"{DESCRIPTION_MARKER} {DESCRIPTION_MARKER}"),
        )
        expect_issue(root, ("DUPLICATE_DESCRIPTION_MARKER", f"{DESCRIPTION_MARKER}:count=2"))
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            VALIDATE_PHASE2_REL,
            read_text(root, VALIDATE_PHASE2_REL).replace(DESCRIPTION_MARKER, LEGACY_DESCRIPTION_MARKER),
        )
        expect_issue(root, ("UNEXPECTED_LEGACY_DESCRIPTION_MARKER", f"{LEGACY_DESCRIPTION_MARKER}:count=1"))
        checks += 1

        build_sample_root(root)
        (root / VALIDATE_PHASE2_REL).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks += 1
        else:
            raise AssertionError("missing validate-phase2.py did not abort")

    assert checks == expected_case_count
    print("PHASE2_CLOSURE_MATRIX_ENTRYPOINT_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_MATRIX_ENTRYPOINT_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the shared Phase 2 validator explicitly names the closure-matrix checker.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        args.write_sample_root.mkdir(parents=True, exist_ok=True)
        build_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_MATRIX_ENTRYPOINT=pass")
    print("PHASE2_CLOSURE_MATRIX_ENTRYPOINT_MARKER_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
INSTALL_ZIG = "scripts/zigux/install-zig.py"
TOOLCHAIN_POLICY = "scripts/zigux/zig-toolchain-policy.json"
ARCHIVE_VERIFICATION_CHECKER = "scripts/zigux/check-lane05-install-zig-archive-verification.py"

REQUIRED_PATHS = (
    INSTALL_ZIG,
    TOOLCHAIN_POLICY,
    ARCHIVE_VERIFICATION_CHECKER,
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
)

REQUIRED_CHECKER_MARKERS = (
    'INSTALL_ZIG = Path("scripts/zigux/install-zig.py")',
    'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
    'print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass")',
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


def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(root, WORKFLOW)
    makefile_text = read_text(root, MAKEFILE)

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    if issues:
        return issues

    checker_text = read_text(root, ARCHIVE_VERIFICATION_CHECKER)

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

    for marker in REQUIRED_CHECKER_MARKERS:
        if marker not in checker_text:
            issues.append(("MISSING_CHECKER_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_INSTALL_ZIG_ARCHIVE_VERIFICATION_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
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
    write_text(root, INSTALL_ZIG, "present\n")
    write_text(root, TOOLCHAIN_POLICY, "present\n")
    write_text(
        root,
        ARCHIVE_VERIFICATION_CHECKER,
        "\n".join(
            (
                "from pathlib import Path",
                "",
                'INSTALL_ZIG = Path("scripts/zigux/install-zig.py")',
                'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
                "",
                'print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass")',
            )
        )
        + "\n",
    )


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def run_self_test() -> int:
    checks = 0
    expected_case_count = 8

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_install_archive_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), REQUIRED_WORKFLOW_LINES[0], "run: python3 scripts/zigux/other.py"))
        expect_issue(root, ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[0]))
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), REQUIRED_WORKFLOW_LINES[1]))
        expect_issue(root, ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_LINES[1]}:count=2"))
        checks += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE, replace_exact_line(read_text(root, MAKEFILE), REQUIRED_MAKEFILE_LINES[1], "# removed"))
        expect_issue(root, ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[1]))
        checks += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE, duplicate_exact_line(read_text(root, MAKEFILE), REQUIRED_MAKEFILE_LINES[2]))
        expect_issue(root, ("DUPLICATE_MAKEFILE_LINE", f"{REQUIRED_MAKEFILE_LINES[2]}:count=2"))
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            ARCHIVE_VERIFICATION_CHECKER,
            replace_once(
                read_text(root, ARCHIVE_VERIFICATION_CHECKER),
                REQUIRED_CHECKER_MARKERS[0],
                "",
            ),
        )
        expect_issue(root, ("MISSING_CHECKER_MARKER", REQUIRED_CHECKER_MARKERS[0]))
        checks += 1

        build_self_test_root(root)
        (root / INSTALL_ZIG).unlink()
        expect_issue(root, ("MISSING_REQUIRED_PATH", INSTALL_ZIG))
        checks += 1

        build_self_test_root(root)
        (root / ARCHIVE_VERIFICATION_CHECKER).unlink()
        expect_issue(root, ("MISSING_REQUIRED_PATH", ARCHIVE_VERIFICATION_CHECKER))
        checks += 1

    assert checks == expected_case_count
    print("PHASE2_INSTALL_ZIG_ARCHIVE_VERIFICATION_PACKET_SELF_TEST=pass")
    print(f"PHASE2_INSTALL_ZIG_ARCHIVE_VERIFICATION_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shipped Phase 2 install-zig archive verification packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_INSTALL_ZIG_ARCHIVE_VERIFICATION_PACKET=pass")
    print(f"PHASE2_INSTALL_ZIG_ARCHIVE_VERIFICATION_PACKET_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_INSTALL_ZIG_ARCHIVE_VERIFICATION_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

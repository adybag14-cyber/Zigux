#!/usr/bin/env python3
"""Guard the Lane 03 bootstrap toolchain verification packet."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
TOOLCHAIN_CHECKER = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"
MAKEFILE = ROOT / "zigux" / "Makefile"

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-validate",
)

CHECKER_MARKERS = (
    'parser.add_argument("--allow-missing", action="store_true", help="Return success when zig is unavailable.")',
    'parser.add_argument("--policy-only", action="store_true", help="Validate and summarize the pinned Zig policy without probing a zig executable.")',
    'parser.add_argument("--archive-only", action="store_true", help="Validate the pinned Zig archive artifact without probing a zig executable.")',
    'parser.add_argument("--zig", help="Explicit zig executable path.")',
    'parser.add_argument("--self-test", action="store_true", help="Run built-in parser and ordering checks.")',
    'print("ZIG_TOOLCHAIN_POLICY_STATUS=present")',
    'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=present")',
    'print("ZIG_TOOLCHAIN_STATUS=present")',
    'print("ZIG_TOOLCHAIN_PIN_POLICY=exact")',
)

MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

WORKFLOW_ORDER = (
    WORKFLOW_LINES[0],
    WORKFLOW_LINES[1],
    WORKFLOW_LINES[2],
    WORKFLOW_LINES[3],
    WORKFLOW_LINES[4],
    WORKFLOW_LINES[5],
    WORKFLOW_LINES[6],
)

MAKEFILE_ORDER = (
    MAKEFILE_MARKERS[1],
    MAKEFILE_MARKERS[2],
    MAKEFILE_MARKERS[3],
    MAKEFILE_MARKERS[4],
    MAKEFILE_MARKERS[5],
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(WORKFLOW_LINES)
    + len(WORKFLOW_LINES)
    + len(CHECKER_MARKERS)
    + len(MAKEFILE_MARKERS)
    + 1
    + 1
    + 1
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def find_index(text: str, marker: str) -> int:
    index = text.find(marker)
    if index < 0:
        raise ValueError(f"missing marker: {marker}")
    return index


def collect_order_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    previous = -1
    for marker in markers:
        try:
            index = find_index(text, marker)
        except ValueError:
            return issues
        if index <= previous:
            issues.append((code, marker))
            break
        previous = index
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
    issues.extend(collect_order_issues(workflow_text, WORKFLOW_ORDER, "WORKFLOW_ORDER_DRIFT"))

    checker_text = read_text(resolve_path(root, TOOLCHAIN_CHECKER))
    for marker in CHECKER_MARKERS:
        if marker not in checker_text:
            issues.append(("MISSING_TOOLCHAIN_CHECKER_MARKER", marker))

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    for marker in MAKEFILE_MARKERS:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_MARKER", f"{marker}:count={count}"))
    issues.extend(collect_order_issues(makefile_text, MAKEFILE_ORDER, "MAKEFILE_ORDER_DRIFT"))

    return issues


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, TOOLCHAIN_CHECKER), "\n".join(CHECKER_MARKERS) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_MARKERS) + "\n")


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
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


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_verification_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(
                duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in CHECKER_MARKERS:
            build_self_test_root(root)
            checker_path = resolve_path(root, TOOLCHAIN_CHECKER)
            checker_path.write_text(
                checker_path.read_text(encoding="utf-8").replace(marker, "", 1),
                encoding="utf-8",
            )
            assert ("MISSING_TOOLCHAIN_CHECKER_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_MARKERS:
            build_self_test_root(root)
            makefile_path = resolve_path(root, MAKEFILE)
            makefile_path.write_text(
                replace_exact_line(makefile_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_MAKEFILE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(
                workflow_path.read_text(encoding="utf-8"),
                WORKFLOW_LINES[1],
                WORKFLOW_LINES[2],
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_LINES[2]}:count=2") in issues
        assert ("WORKFLOW_ORDER_DRIFT", WORKFLOW_LINES[2]) not in issues
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_text = workflow_text.replace(
            WORKFLOW_LINES[2] + "\n" + WORKFLOW_LINES[3],
            WORKFLOW_LINES[3] + "\n" + WORKFLOW_LINES[2],
            1,
        )
        workflow_path.write_text(workflow_text, encoding="utf-8")
        assert ("WORKFLOW_ORDER_DRIFT", WORKFLOW_LINES[3]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_text = makefile_path.read_text(encoding="utf-8")
        makefile_text = makefile_text.replace(
            MAKEFILE_MARKERS[2] + "\n" + MAKEFILE_MARKERS[3],
            MAKEFILE_MARKERS[3] + "\n" + MAKEFILE_MARKERS[2],
            1,
        )
        makefile_path.write_text(makefile_text, encoding="utf-8")
        assert ("MAKEFILE_ORDER_DRIFT", MAKEFILE_MARKERS[3]) in collect_issues(root)
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOLCHAIN_VERIFICATION_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_VERIFICATION_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 03 bootstrap toolchain verification packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        print("PHASE2_TOOLCHAIN_VERIFICATION_PACKET=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_TOOLCHAIN_VERIFICATION_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_VERIFICATION_WORKFLOW_PATH={resolve_path(root, WORKFLOW)}")
    print(f"PHASE2_TOOLCHAIN_VERIFICATION_CHECKER_PATH={resolve_path(root, TOOLCHAIN_CHECKER)}")
    print(f"PHASE2_TOOLCHAIN_VERIFICATION_MAKEFILE_PATH={resolve_path(root, MAKEFILE)}")
    print(f"PHASE2_TOOLCHAIN_VERIFICATION_WORKFLOW_STEP_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_TOOLCHAIN_VERIFICATION_CHECKER_MARKER_COUNT={len(CHECKER_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_VERIFICATION_MAKEFILE_MARKER_COUNT={len(MAKEFILE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

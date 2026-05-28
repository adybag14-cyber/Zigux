#!/usr/bin/env python3
"""Guard the exact current-master Phase 2 toolchain wrapper sequence."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")

WORKFLOW_ROUTE_LINES = (
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-cross",
)

MAKEFILE_TOOLCHAIN_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
)

DEPENDENT_TARGET_HEADERS = (
    "phase2-kconfig: phase2-toolchain",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
)

EXPECTED_SELF_TEST_CASE_COUNT = 10


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
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


def move_exact_line_after(text: str, marker: str, after_marker: str) -> str:
    lines = text.splitlines()
    source_index = next((i for i, line in enumerate(lines) if line.strip() == marker), None)
    after_index = next((i for i, line in enumerate(lines) if line.strip() == after_marker), None)
    if source_index is None or after_index is None:
        raise AssertionError("marker line not found")
    line = lines.pop(source_index)
    if source_index < after_index:
        after_index -= 1
    lines.insert(after_index + 1, line)
    return "\n".join(lines) + "\n"


def extract_target_block(makefile_text: str, header: str) -> list[str] | None:
    lines = makefile_text.splitlines()
    start_index = None
    for index, line in enumerate(lines):
        if line.strip() == header:
            start_index = index + 1
            break
    if start_index is None:
        return None

    block: list[str] = []
    for line in lines[start_index:]:
        stripped = line.strip()
        if stripped and not line.startswith(("\t", " ")):
            break
        if stripped:
            block.append(stripped)
    return block


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    workflow_text = read_text(root / WORKFLOW)
    makefile_text = read_text(root / MAKEFILE)

    workflow_positions: list[int] = []
    for line in WORKFLOW_ROUTE_LINES:
        count = count_exact_lines(workflow_text, line)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_ROUTE_LINE", line))
            continue
        if count != 1:
            issues.append(("DUPLICATE_WORKFLOW_ROUTE_LINE", f"{line}:count={count}"))
            continue
        workflow_positions.append(
            next(index for index, current in enumerate(workflow_text.splitlines()) if current.strip() == line)
        )

    if len(workflow_positions) == len(WORKFLOW_ROUTE_LINES):
        if workflow_positions != sorted(workflow_positions):
            issues.append(("WORKFLOW_ROUTE_ORDER_MISMATCH", "phase2-toolchain route order"))

    target_block = extract_target_block(makefile_text, "phase2-toolchain:")
    if target_block is None:
        issues.append(("MISSING_MAKEFILE_TARGET", "phase2-toolchain:"))
    else:
        makefile_positions: list[int] = []
        for line in MAKEFILE_TOOLCHAIN_LINES:
            count = sum(1 for current in target_block if current == line)
            if count == 0:
                issues.append(("MISSING_MAKEFILE_TOOLCHAIN_LINE", line))
                continue
            if count != 1:
                issues.append(("DUPLICATE_MAKEFILE_TOOLCHAIN_LINE", f"{line}:count={count}"))
                continue
            makefile_positions.append(target_block.index(line))
        if len(makefile_positions) == len(MAKEFILE_TOOLCHAIN_LINES):
            if makefile_positions != sorted(makefile_positions):
                issues.append(("MAKEFILE_TOOLCHAIN_ORDER_MISMATCH", "phase2-toolchain helper order"))
        if len(target_block) != len(MAKEFILE_TOOLCHAIN_LINES):
            issues.append(("UNEXPECTED_MAKEFILE_TOOLCHAIN_LINE_COUNT", str(len(target_block))))

    for header in DEPENDENT_TARGET_HEADERS:
        count = count_exact_lines(makefile_text, header)
        if count == 0:
            issues.append(("MISSING_DEPENDENT_TARGET_HEADER", header))
        elif count != 1:
            issues.append(("DUPLICATE_DEPENDENT_TARGET_HEADER", f"{header}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOLCHAIN_WRAPPER_SEQUENCE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root / WORKFLOW,
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Run current Phase 2 toolchain make route",
                "        run: make -C zigux phase2-toolchain",
                "      - name: Run current Phase 2 tools make route",
                "        run: make -C zigux phase2-tools",
                "      - name: Run current Phase 2 kconfig make route",
                "        run: make -C zigux phase2-kconfig",
                "      - name: Run current Phase 2 fixdep make route",
                "        run: make -C zigux phase2-fixdep",
                "      - name: Run current Phase 2 cross make route",
                "        run: make -C zigux phase2-cross",
            )
        )
        + "\n",
    )
    write_text(
        root / MAKEFILE,
        "\n".join(
            (
                "phase2-toolchain:",
                *[f"\t{line}" for line in MAKEFILE_TOOLCHAIN_LINES],
                "",
                "phase2-tools:",
                "\t@true",
                "",
                "phase2-kconfig: phase2-toolchain",
                "\t@true",
                "",
                "phase2-genksyms: phase2-toolchain",
                "\t@true",
                "",
                "phase2-fixdep: phase2-toolchain",
                "\t@true",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        build_self_test_root(root)

        def expect_pass() -> None:
            nonlocal case_count
            case_count += 1
            assert collect_issues(root) == []

        def expect_issue(code: str, mutate) -> None:
            nonlocal case_count
            case_count += 1
            build_self_test_root(root)
            mutate()
            codes = {issue_code for issue_code, _ in collect_issues(root)}
            assert code in codes, (code, codes)

        expect_pass()
        expect_issue(
            "MISSING_WORKFLOW_ROUTE_LINE",
            lambda: write_text(
                root / WORKFLOW,
                replace_exact_line(read_text(root / WORKFLOW), WORKFLOW_ROUTE_LINES[0], "        run: make -C zigux phase2-tools"),
            ),
        )
        expect_issue(
            "DUPLICATE_WORKFLOW_ROUTE_LINE",
            lambda: write_text(root / WORKFLOW, duplicate_exact_line(read_text(root / WORKFLOW), WORKFLOW_ROUTE_LINES[0])),
        )
        expect_issue(
            "WORKFLOW_ROUTE_ORDER_MISMATCH",
            lambda: write_text(
                root / WORKFLOW,
                move_exact_line_after(read_text(root / WORKFLOW), WORKFLOW_ROUTE_LINES[0], WORKFLOW_ROUTE_LINES[1]),
            ),
        )
        expect_issue(
            "MISSING_MAKEFILE_TARGET",
            lambda: write_text(root / MAKEFILE, replace_exact_line(read_text(root / MAKEFILE), "phase2-toolchain:", "phase2-toolchain-disabled:")),
        )
        expect_issue(
            "MISSING_MAKEFILE_TOOLCHAIN_LINE",
            lambda: write_text(
                root / MAKEFILE,
                replace_exact_line(read_text(root / MAKEFILE), MAKEFILE_TOOLCHAIN_LINES[0], "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --version-only"),
            ),
        )
        expect_issue(
            "DUPLICATE_MAKEFILE_TOOLCHAIN_LINE",
            lambda: write_text(root / MAKEFILE, duplicate_exact_line(read_text(root / MAKEFILE), MAKEFILE_TOOLCHAIN_LINES[0])),
        )
        expect_issue(
            "MAKEFILE_TOOLCHAIN_ORDER_MISMATCH",
            lambda: write_text(
                root / MAKEFILE,
                move_exact_line_after(read_text(root / MAKEFILE), MAKEFILE_TOOLCHAIN_LINES[0], MAKEFILE_TOOLCHAIN_LINES[1]),
            ),
        )
        expect_issue(
            "UNEXPECTED_MAKEFILE_TOOLCHAIN_LINE_COUNT",
            lambda: write_text(
                root / MAKEFILE,
                replace_exact_line(
                    read_text(root / MAKEFILE),
                    MAKEFILE_TOOLCHAIN_LINES[-1],
                    MAKEFILE_TOOLCHAIN_LINES[-1] + "\n\t@echo extra",
                ),
            ),
        )
        expect_issue(
            "MISSING_DEPENDENT_TARGET_HEADER",
            lambda: write_text(
                root / MAKEFILE,
                replace_exact_line(read_text(root / MAKEFILE), DEPENDENT_TARGET_HEADERS[0], "phase2-kconfig:"),
            ),
        )

    assert case_count == EXPECTED_SELF_TEST_CASE_COUNT, case_count
    print("PHASE2_TOOLCHAIN_WRAPPER_SEQUENCE_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_WRAPPER_SEQUENCE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repo root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    workflow_text = read_text(args.root / WORKFLOW)
    makefile_text = read_text(args.root / MAKEFILE)
    target_block = extract_target_block(makefile_text, "phase2-toolchain:")
    assert target_block is not None

    print("PHASE2_TOOLCHAIN_WRAPPER_SEQUENCE=pass")
    print(f"PHASE2_TOOLCHAIN_WRAPPER_SEQUENCE_WORKFLOW_ROUTE_COUNT={len(WORKFLOW_ROUTE_LINES)}")
    print(f"PHASE2_TOOLCHAIN_WRAPPER_SEQUENCE_TOOLCHAIN_LINE_COUNT={len(target_block)}")
    print(f"PHASE2_TOOLCHAIN_WRAPPER_SEQUENCE_DEPENDENT_TARGET_COUNT={len(DEPENDENT_TARGET_HEADERS)}")
    print(f"PHASE2_TOOLCHAIN_WRAPPER_SEQUENCE_WORKFLOW_LINE_TOTAL={len(workflow_text.splitlines())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

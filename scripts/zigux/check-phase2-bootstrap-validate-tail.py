#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
VALIDATOR = "scripts/zigux/validate-phase2.py"

REQUIRED_PATHS = (
    VALIDATOR,
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/validate-phase2-closure.py",
    "Documentation/zigux/phase2-closure.md",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    MAKEFILE,
    WORKFLOW,
)

REQUIRED_WORKFLOW_SEQUENCE = (
    "run: zig test scripts/zigux/genksyms.zig",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

REQUIRED_VALIDATOR_MARKERS = (
    '"run: make -C zigux phase2-validate",',
    '"run: python3 scripts/zigux/validate-phase2.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",',
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


def find_sequence_positions(text: str, markers: tuple[str, ...]) -> list[int]:
    positions: list[int] = []
    search_from = 0
    for marker in markers:
        pos = text.find(marker, search_from)
        if pos == -1:
            raise ValueError(marker)
        positions.append(pos)
        search_from = pos + len(marker)
    return positions


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
    try:
        marker_index = next(index for index, line in enumerate(lines) if line.strip() == marker)
        after_index = next(index for index, line in enumerate(lines) if line.strip() == after_marker)
    except StopIteration as exc:
        raise AssertionError("marker line not found for move") from exc

    moved_line = lines.pop(marker_index)
    if marker_index < after_index:
        after_index -= 1
    lines.insert(after_index + 1, moved_line)
    return "\n".join(lines) + "\n"


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    workflow_text = read_text(root, WORKFLOW)
    makefile_text = read_text(root, MAKEFILE)
    validator_text = read_text(root, VALIDATOR)

    for marker in REQUIRED_WORKFLOW_SEQUENCE:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    try:
        find_sequence_positions(workflow_text, REQUIRED_WORKFLOW_SEQUENCE)
    except ValueError as exc:
        issues.append(("WORKFLOW_ORDER_DRIFT", str(exc)))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_VALIDATOR_MARKERS:
        count = validator_text.count(marker)
        if count == 0:
            issues.append(("MISSING_VALIDATOR_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATOR_MARKER", f"{marker}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_VALIDATE_TAIL=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    workflow_lines = [
        "name: zigux-bootstrap",
        "- name: Run current Phase 2 genksyms unit replay",
        f"  {REQUIRED_WORKFLOW_SEQUENCE[0]}",
        "- name: Run current Phase 2 validate make route",
        f"  {REQUIRED_WORKFLOW_SEQUENCE[1]}",
        "- name: Validate current Phase 2 tool packet",
        f"  {REQUIRED_WORKFLOW_SEQUENCE[2]}",
        "- name: Self-test current Phase 1 direct-owner checker",
        f"  {REQUIRED_WORKFLOW_SEQUENCE[3]}",
    ]
    write_text(root, WORKFLOW, "\n".join(workflow_lines) + "\n")

    makefile_lines = [
        "PYTHON ?= python3",
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        "",
        REQUIRED_MAKEFILE_LINES[0],
        f"\t{REQUIRED_MAKEFILE_LINES[1]}",
        f"\t{REQUIRED_MAKEFILE_LINES[2]}",
        f"\t{REQUIRED_MAKEFILE_LINES[3]}",
        "",
        REQUIRED_MAKEFILE_LINES[4],
    ]
    write_text(root, MAKEFILE, "\n".join(makefile_lines) + "\n")

    validator_lines = [
        "REQUIRED_WORKFLOW_LINES = (",
        f"    {REQUIRED_VALIDATOR_MARKERS[0]}",
        f"    {REQUIRED_VALIDATOR_MARKERS[1]}",
        ")",
        "REQUIRED_MAKEFILE_LINES = (",
        f"    {REQUIRED_VALIDATOR_MARKERS[2]}",
        f"    {REQUIRED_VALIDATOR_MARKERS[3]}",
        f"    {REQUIRED_VALIDATOR_MARKERS[4]}",
        ")",
    ]
    write_text(root, VALIDATOR, "\n".join(validator_lines) + "\n")

    for rel in REQUIRED_PATHS:
        if rel in {WORKFLOW, MAKEFILE, VALIDATOR}:
            continue
        write_text(root, rel, "present\n")


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_validate_tail_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), REQUIRED_WORKFLOW_SEQUENCE[1], "run: make -C zigux phase2-tools"))
        expect_issue(root, ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_SEQUENCE[1]))
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), REQUIRED_WORKFLOW_SEQUENCE[2]))
        expect_issue(root, ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_SEQUENCE[2]}:count=2"))
        checks += 1

        build_sample_root(root)
        workflow_text = read_text(root, WORKFLOW)
        workflow_text = move_exact_line_after(
            workflow_text,
            REQUIRED_WORKFLOW_SEQUENCE[1],
            REQUIRED_WORKFLOW_SEQUENCE[2],
        )
        write_text(root, WORKFLOW, workflow_text)
        expect_issue(root, ("WORKFLOW_ORDER_DRIFT", REQUIRED_WORKFLOW_SEQUENCE[2]))
        checks += 1

        build_sample_root(root)
        write_text(root, MAKEFILE, replace_exact_line(read_text(root, MAKEFILE), REQUIRED_MAKEFILE_LINES[3], "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2.py"))
        expect_issue(root, ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[3]))
        checks += 1

        build_sample_root(root)
        write_text(root, VALIDATOR, read_text(root, VALIDATOR).replace(REQUIRED_VALIDATOR_MARKERS[1], '"run: python3 scripts/zigux/validate-bootstrap.py",'))
        expect_issue(root, ("MISSING_VALIDATOR_MARKER", REQUIRED_VALIDATOR_MARKERS[1]))
        checks += 1

        build_sample_root(root)
        (root / "zigux/tests/fixtures/phase2_tool_manifest.json").unlink()
        expect_issue(root, ("MISSING_REQUIRED_PATH", "zigux/tests/fixtures/phase2_tool_manifest.json"))
        checks += 1

    print("PHASE2_BOOTSTRAP_VALIDATE_TAIL_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_VALIDATE_TAIL_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current bootstrap tail packet that hands Phase 2 validation from workflow into Makefile and validate-phase2.py."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like sample root for focused checker replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_BOOTSTRAP_VALIDATE_TAIL_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_VALIDATE_TAIL=pass")
    print(f"PHASE2_BOOTSTRAP_VALIDATE_TAIL_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_BOOTSTRAP_VALIDATE_TAIL_WORKFLOW_STEP_COUNT={len(REQUIRED_WORKFLOW_SEQUENCE)}")
    print(f"PHASE2_BOOTSTRAP_VALIDATE_TAIL_MAKEFILE_MARKER_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_BOOTSTRAP_VALIDATE_TAIL_VALIDATOR_MARKER_COUNT={len(REQUIRED_VALIDATOR_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

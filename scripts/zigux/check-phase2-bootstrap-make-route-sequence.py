#!/usr/bin/env python3
"""Guard the Lane 03 Phase 2 bootstrap make-route sequence."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"

ORDERED_MARKERS = (
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

EXPECTED_SELF_TEST_CASE_COUNT = 10


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


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            if replacement:
                lines[index] = replacement
            else:
                del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def swap_exact_lines(text: str, first: str, second: str) -> str:
    lines = text.splitlines()
    first_index = next(index for index, line in enumerate(lines) if line.strip() == first)
    second_index = next(index for index, line in enumerate(lines) if line.strip() == second)
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def find_exact_line_indices(text: str, markers: tuple[str, ...]) -> list[int]:
    indices: list[int] = []
    lines = text.splitlines()
    for marker in markers:
        matches = [index for index, line in enumerate(lines) if line.strip() == marker]
        if len(matches) != 1:
            return []
        indices.append(matches[0])
    return indices


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(root, WORKFLOW)

    for marker in ORDERED_MARKERS:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_ROUTE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_ROUTE_LINE", f"{marker}:count={count}"))

    if not issues:
        indices = find_exact_line_indices(workflow_text, ORDERED_MARKERS)
        if indices != sorted(indices):
            issues.append(("OUT_OF_ORDER_WORKFLOW_ROUTE_LINE", " -> ".join(ORDERED_MARKERS)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_MAKE_ROUTE_SEQUENCE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Run current Phase 2 toolchain make route",
                f"        {ORDERED_MARKERS[0]}",
                "      - name: Run current Phase 2 tools make route",
                f"        {ORDERED_MARKERS[1]}",
                "      - name: Run current Phase 2 kconfig make route",
                f"        {ORDERED_MARKERS[2]}",
                "      - name: Run current Phase 2 fixdep make route",
                f"        {ORDERED_MARKERS[3]}",
                "      - name: Run current Phase 2 cross make route",
                f"        {ORDERED_MARKERS[4]}",
                "      - name: Run current Phase 2 genksyms make route",
                f"        {ORDERED_MARKERS[5]}",
                "      - name: Run current Phase 2 validate make route",
                f"        {ORDERED_MARKERS[6]}",
                "      - name: Validate current Phase 2 tool packet",
                f"        {ORDERED_MARKERS[7]}",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_make_route_sequence_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), ORDERED_MARKERS[0]))
        assert ("MISSING_WORKFLOW_ROUTE_LINE", ORDERED_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), ORDERED_MARKERS[1]))
        assert ("DUPLICATE_WORKFLOW_ROUTE_LINE", f"{ORDERED_MARKERS[1]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, swap_exact_lines(read_text(root, WORKFLOW), ORDERED_MARKERS[0], ORDERED_MARKERS[1]))
        assert any(code == "OUT_OF_ORDER_WORKFLOW_ROUTE_LINE" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, swap_exact_lines(read_text(root, WORKFLOW), ORDERED_MARKERS[2], ORDERED_MARKERS[3]))
        assert any(code == "OUT_OF_ORDER_WORKFLOW_ROUTE_LINE" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(read_text(root, WORKFLOW), ORDERED_MARKERS[4], "run: make -C zigux phase2"),
        )
        assert ("MISSING_WORKFLOW_ROUTE_LINE", ORDERED_MARKERS[4]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), ORDERED_MARKERS[6]))
        assert ("DUPLICATE_WORKFLOW_ROUTE_LINE", f"{ORDERED_MARKERS[6]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(read_text(root, WORKFLOW), ORDERED_MARKERS[7], "run: python3 scripts/zigux/validate-phase1-closure.py"),
        )
        assert ("MISSING_WORKFLOW_ROUTE_LINE", ORDERED_MARKERS[7]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, swap_exact_lines(read_text(root, WORKFLOW), ORDERED_MARKERS[5], ORDERED_MARKERS[6]))
        assert any(code == "OUT_OF_ORDER_WORKFLOW_ROUTE_LINE" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), ORDERED_MARKERS[7]))
        assert ("DUPLICATE_WORKFLOW_ROUTE_LINE", f"{ORDERED_MARKERS[7]}:count=2") in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT, checks
    print("PHASE2_BOOTSTRAP_MAKE_ROUTE_SEQUENCE_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_MAKE_ROUTE_SEQUENCE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the bootstrap workflow keeps the shipped Phase 2 make-route sequence and validator handoff."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--write-sample-root", type=Path, help="Write a current-like sample root and exit")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        print("PHASE2_BOOTSTRAP_MAKE_ROUTE_SEQUENCE_SAMPLE_ROOT=pass")
        print(f"PHASE2_BOOTSTRAP_MAKE_ROUTE_SEQUENCE_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_MAKE_ROUTE_SEQUENCE=pass")
    print(f"PHASE2_BOOTSTRAP_MAKE_ROUTE_SEQUENCE_MARKER_COUNT={len(ORDERED_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_MAKE_ROUTE_SEQUENCE_WORKFLOW_PATH={args.root.resolve() / WORKFLOW}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

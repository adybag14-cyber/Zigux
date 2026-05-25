#!/usr/bin/env python3
"""Guard the current Phase 2 validate-route tail packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
VALIDATOR = "scripts/zigux/validate-phase2.py"

WORKFLOW_TAIL_LINES = (
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

MAKEFILE_VALIDATE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

VALIDATOR_WORKFLOW_MARKERS = WORKFLOW_TAIL_LINES
VALIDATOR_MAKEFILE_MARKERS = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",',
)

EXPECTED_SELF_TEST_CASE_COUNT = 11


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


def find_exact_line_indices(text: str, markers: tuple[str, ...]) -> list[int]:
    indices: list[int] = []
    lines = text.splitlines()
    for marker in markers:
        matches = [index for index, line in enumerate(lines) if line.strip() == marker]
        if len(matches) != 1:
            return []
        indices.append(matches[0])
    return indices


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


def collect_ordered_line_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
    order_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    if not issues:
        indices = find_exact_line_indices(text, markers)
        if indices != sorted(indices):
            issues.append((order_code, " -> ".join(markers)))
    return issues


def collect_validator_marker_issues(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in VALIDATOR_WORKFLOW_MARKERS:
        count = text.count(marker)
        if count == 0:
            issues.append(("MISSING_VALIDATOR_WORKFLOW_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATOR_WORKFLOW_MARKER", f"{marker}:count={count}"))
    for marker in VALIDATOR_MAKEFILE_MARKERS:
        count = text.count(marker)
        if count == 0:
            issues.append(("MISSING_VALIDATOR_MAKEFILE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATOR_MAKEFILE_MARKER", f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    workflow_text = read_text(root, WORKFLOW)
    makefile_text = read_text(root, MAKEFILE)
    validator_text = read_text(root, VALIDATOR)

    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_ordered_line_issues(
            workflow_text,
            WORKFLOW_TAIL_LINES,
            "MISSING_WORKFLOW_TAIL_LINE",
            "DUPLICATE_WORKFLOW_TAIL_LINE",
            "OUT_OF_ORDER_WORKFLOW_TAIL_LINE",
        )
    )
    issues.extend(
        collect_ordered_line_issues(
            makefile_text,
            MAKEFILE_VALIDATE_LINES,
            "MISSING_MAKEFILE_VALIDATE_LINE",
            "DUPLICATE_MAKEFILE_VALIDATE_LINE",
            "OUT_OF_ORDER_MAKEFILE_VALIDATE_LINE",
        )
    )
    issues.extend(collect_validator_marker_issues(validator_text))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_VALIDATE_ROUTE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(root, WORKFLOW, "\n".join(("name: zigux-bootstrap", *WORKFLOW_TAIL_LINES)) + "\n")
    write_text(
        root,
        MAKEFILE,
        "\n".join(("PYTHON ?= python3", "PHASE2_SCRIPT_ROOT := ../scripts/zigux", "", *MAKEFILE_VALIDATE_LINES)) + "\n",
    )
    write_text(
        root,
        VALIDATOR,
        "\n".join(
            (
                "REQUIRED_WORKFLOW_LINES = (",
                *[f'    "{line}",' for line in VALIDATOR_WORKFLOW_MARKERS],
                ")",
                "",
                "REQUIRED_MAKEFILE_LINES = (",
                *[f"    {line}" if line.startswith('"') else f'    "{line}",' for line in VALIDATOR_MAKEFILE_MARKERS],
                ")",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validate_route_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), WORKFLOW_TAIL_LINES[0]))
        assert ("MISSING_WORKFLOW_TAIL_LINE", WORKFLOW_TAIL_LINES[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), WORKFLOW_TAIL_LINES[-1]))
        assert ("DUPLICATE_WORKFLOW_TAIL_LINE", f"{WORKFLOW_TAIL_LINES[-1]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, swap_exact_lines(read_text(root, WORKFLOW), WORKFLOW_TAIL_LINES[0], WORKFLOW_TAIL_LINES[1]))
        assert any(code == "OUT_OF_ORDER_WORKFLOW_TAIL_LINE" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE, replace_exact_line(read_text(root, MAKEFILE), MAKEFILE_VALIDATE_LINES[0]))
        assert ("MISSING_MAKEFILE_VALIDATE_LINE", MAKEFILE_VALIDATE_LINES[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE, duplicate_exact_line(read_text(root, MAKEFILE), MAKEFILE_VALIDATE_LINES[-1]))
        assert ("DUPLICATE_MAKEFILE_VALIDATE_LINE", f"{MAKEFILE_VALIDATE_LINES[-1]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE, swap_exact_lines(read_text(root, MAKEFILE), MAKEFILE_VALIDATE_LINES[1], MAKEFILE_VALIDATE_LINES[2]))
        assert any(code == "OUT_OF_ORDER_MAKEFILE_VALIDATE_LINE" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(root, VALIDATOR, read_text(root, VALIDATOR).replace(VALIDATOR_WORKFLOW_MARKERS[0], "", 1))
        assert ("MISSING_VALIDATOR_WORKFLOW_MARKER", VALIDATOR_WORKFLOW_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, VALIDATOR, read_text(root, VALIDATOR) + VALIDATOR_WORKFLOW_MARKERS[-1])
        assert ("DUPLICATE_VALIDATOR_WORKFLOW_MARKER", f"{VALIDATOR_WORKFLOW_MARKERS[-1]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, VALIDATOR, read_text(root, VALIDATOR).replace(VALIDATOR_MAKEFILE_MARKERS[0], "", 1))
        assert ("MISSING_VALIDATOR_MAKEFILE_MARKER", VALIDATOR_MAKEFILE_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, VALIDATOR, read_text(root, VALIDATOR) + VALIDATOR_MAKEFILE_MARKERS[-1])
        assert ("DUPLICATE_VALIDATOR_MAKEFILE_MARKER", f"{VALIDATOR_MAKEFILE_MARKERS[-1]}:count=2") in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_VALIDATE_ROUTE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_VALIDATE_ROUTE_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the current Phase 2 validate-route tail packet stays aligned.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_VALIDATE_ROUTE_PACKET=pass")
    print(f"PHASE2_VALIDATE_ROUTE_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_TAIL_LINES)}")
    print(f"PHASE2_VALIDATE_ROUTE_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_VALIDATE_LINES)}")
    print(
        "PHASE2_VALIDATE_ROUTE_PACKET_VALIDATOR_MARKER_COUNT="
        f"{len(VALIDATOR_WORKFLOW_MARKERS) + len(VALIDATOR_MAKEFILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

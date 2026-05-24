#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = (
    Path(__file__).resolve().parents[2]
    if len(Path(__file__).resolve().parents) >= 3
    else Path.cwd()
)
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"

WORKFLOW_STEPS = (
    (
        "- name: Self-test current Phase 2 cross checker",
        "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    ),
    (
        "- name: Check current Phase 2 direct cross-route packet",
        "run: python3 scripts/zigux/check-phase2-cross.py",
    ),
    (
        "- name: Self-test current Phase 2 cross selftest alignment checker",
        "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    ),
    (
        "- name: Check current Phase 2 cross alignment packet",
        "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    ),
    (
        "- name: Self-test current Phase 2 cross workflow checker",
        "run: python3 scripts/zigux/check-phase2-cross-workflow.py --self-test",
    ),
    (
        "- name: Check current Phase 2 cross workflow packet",
        "run: python3 scripts/zigux/check-phase2-cross-workflow.py",
    ),
)

ROUTE_STEP = (
    "- name: Run current Phase 2 cross make route",
    "run: make -C zigux phase2-cross",
)

EXPECTED_SELF_TEST_CASE_COUNT = 20


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


def find_exact_line_index(lines: list[str], marker: str) -> int | None:
    for index, line in enumerate(lines):
        if line.strip() == marker:
            return index
    return None


def collect_exact_line_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_workflow_order_issues(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    lines = text.splitlines()
    previous_name_index = -1
    previous_run_index = -1

    for name_line, run_line in WORKFLOW_STEPS:
        name_index = find_exact_line_index(lines, name_line)
        run_index = find_exact_line_index(lines, run_line)
        if name_index is None or run_index is None:
            continue
        if name_index <= previous_name_index:
            issues.append(("WORKFLOW_STEP_ORDER_MISMATCH", name_line))
        if run_index <= previous_run_index:
            issues.append(("WORKFLOW_RUN_ORDER_MISMATCH", run_line))
        if run_index <= name_index:
            issues.append(("WORKFLOW_STEP_PAIRING_MISMATCH", name_line))
        previous_name_index = name_index
        previous_run_index = run_index

    return issues


def collect_route_step_issues(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    route_name, route_run = ROUTE_STEP
    name_count = count_exact_lines(text, route_name)
    run_count = count_exact_lines(text, route_run)

    if name_count == 0:
        issues.append(("MISSING_ROUTE_STEP_NAME", route_name))
    elif name_count != 1:
        issues.append(("DUPLICATE_ROUTE_STEP_NAME", f"{route_name}:count={name_count}"))

    if run_count == 0:
        issues.append(("MISSING_ROUTE_STEP_RUN", route_run))
    elif run_count != 1:
        issues.append(("DUPLICATE_ROUTE_STEP_RUN", f"{route_run}:count={run_count}"))

    lines = text.splitlines()
    route_name_index = find_exact_line_index(lines, route_name)
    route_run_index = find_exact_line_index(lines, route_run)
    last_cross_run_index = find_exact_line_index(lines, WORKFLOW_STEPS[-1][1])

    if route_name_index is not None and route_run_index is not None:
        if route_run_index <= route_name_index:
            issues.append(("ROUTE_STEP_PAIRING_MISMATCH", route_name))
        if last_cross_run_index is not None and route_name_index <= last_cross_run_index:
            issues.append(("ROUTE_STEP_ORDER_MISMATCH", route_name))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    workflow_text = read_text(resolve_path(root, WORKFLOW))

    workflow_name_lines = tuple(name_line for name_line, _ in WORKFLOW_STEPS)
    workflow_run_lines = tuple(run_line for _, run_line in WORKFLOW_STEPS)

    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_exact_line_issues(
            workflow_text,
            workflow_name_lines,
            "MISSING_WORKFLOW_STEP_NAME",
            "DUPLICATE_WORKFLOW_STEP_NAME",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            workflow_text,
            workflow_run_lines,
            "MISSING_WORKFLOW_STEP_RUN",
            "DUPLICATE_WORKFLOW_STEP_RUN",
        )
    )
    issues.extend(collect_workflow_order_issues(workflow_text))
    issues.extend(collect_route_step_issues(workflow_text))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_WORKFLOW=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    workflow_lines = ["name: zigux-bootstrap", "", "jobs:", "  bootstrap:", "    steps:"]
    for name_line, run_line in WORKFLOW_STEPS:
        workflow_lines.extend((f"      {name_line}", f"        {run_line}"))
    workflow_lines.extend((f"      {ROUTE_STEP[0]}", f"        {ROUTE_STEP[1]}"))
    workflow_lines.append("")
    write_text(resolve_path(root, WORKFLOW), "\n".join(workflow_lines))


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


def swap_exact_lines(text: str, first: str, second: str) -> str:
    lines = text.splitlines()
    first_index = None
    second_index = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == first and first_index is None:
            first_index = index
        if stripped == second and second_index is None:
            second_index = index
    if first_index is None or second_index is None:
        raise AssertionError("marker lines not found for swap")
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_workflow_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for name_line, _ in WORKFLOW_STEPS:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), name_line, "# removed"),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_STEP_NAME", name_line) in collect_issues(root)
            checks_run += 1

        for _, run_line in WORKFLOW_STEPS:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(
                replace_exact_line(
                    path.read_text(encoding="utf-8"),
                    run_line,
                    "run: python3 missing.py",
                ),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_STEP_RUN", run_line) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, WORKFLOW)
        path.write_text(
            duplicate_exact_line(path.read_text(encoding="utf-8"), WORKFLOW_STEPS[0][0]),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_WORKFLOW_STEP_NAME",
            f"{WORKFLOW_STEPS[0][0]}:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, WORKFLOW)
        path.write_text(
            duplicate_exact_line(path.read_text(encoding="utf-8"), WORKFLOW_STEPS[0][1]),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_WORKFLOW_STEP_RUN",
            f"{WORKFLOW_STEPS[0][1]}:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, WORKFLOW)
        path.write_text(
            swap_exact_lines(
                path.read_text(encoding="utf-8"),
                WORKFLOW_STEPS[0][0],
                WORKFLOW_STEPS[1][0],
            ),
            encoding="utf-8",
        )
        assert (
            "WORKFLOW_STEP_ORDER_MISMATCH",
            WORKFLOW_STEPS[1][0],
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, WORKFLOW)
        path.write_text(
            swap_exact_lines(
                path.read_text(encoding="utf-8"),
                WORKFLOW_STEPS[0][0],
                WORKFLOW_STEPS[0][1],
            ),
            encoding="utf-8",
        )
        assert (
            "WORKFLOW_STEP_PAIRING_MISMATCH",
            WORKFLOW_STEPS[0][0],
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, WORKFLOW)
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), ROUTE_STEP[0], "# removed"),
            encoding="utf-8",
        )
        assert ("MISSING_ROUTE_STEP_NAME", ROUTE_STEP[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, WORKFLOW)
        path.write_text(
            replace_exact_line(
                path.read_text(encoding="utf-8"),
                ROUTE_STEP[1],
                "run: make -C zigux phase2-toolchain",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_ROUTE_STEP_RUN", ROUTE_STEP[1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, WORKFLOW)
        path.write_text(
            swap_exact_lines(
                path.read_text(encoding="utf-8"),
                ROUTE_STEP[0],
                WORKFLOW_STEPS[-1][0],
            ),
            encoding="utf-8",
        )
        assert ("ROUTE_STEP_ORDER_MISMATCH", ROUTE_STEP[0]) in collect_issues(root)
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_WORKFLOW_SELF_TEST=pass")
    print(f"PHASE2_CROSS_WORKFLOW_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 cross workflow packet stays wired into the live route surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self-test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_WORKFLOW=pass")
    print(f"PHASE2_CROSS_WORKFLOW_STEP_COUNT={len(WORKFLOW_STEPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

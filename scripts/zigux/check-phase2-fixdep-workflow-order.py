#!/usr/bin/env python3
"""Check that the Phase 2 fixdep workflow steps stay grouped and ordered."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FIXDEP_STEPS = (
    (
        "Self-test current Phase 2 fixdep gate checker",
        "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    ),
    (
        "Check current Phase 2 fixdep gate packet",
        "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    ),
    (
        "Self-test current fixdep parity checker",
        "python3 scripts/zigux/check-fixdep-diff.py --self-test",
    ),
    (
        "Check current fixdep parity packet",
        "python3 scripts/zigux/check-fixdep-diff.py",
    ),
    (
        "Run current Phase 2 fixdep unit tests",
        "zig test scripts/zigux/fixdep.zig",
    ),
    (
        "Run current Phase 2 fixdep make wrapper",
        "make -C zigux phase2-fixdep",
    ),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_workflow_steps(text: str) -> list[tuple[str, str]]:
    steps: list[tuple[str, str]] = []
    current_name: str | None = None

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("- name: "):
            current_name = stripped.removeprefix("- name: ").strip()
            continue
        if current_name is None or not stripped.startswith("run: "):
            continue

        run_value = stripped.removeprefix("run: ").strip()
        if run_value and run_value != "|":
            steps.append((current_name, run_value))
        current_name = None

    return steps


def collect_issues(root: Path) -> list[tuple[str, str]]:
    workflow_path = root / WORKFLOW_REL
    steps = parse_workflow_steps(read_text(workflow_path))
    issues: list[tuple[str, str]] = []

    for expected in REQUIRED_FIXDEP_STEPS:
        count = steps.count(expected)
        if count == 0:
            issues.append(("MISSING_FIXDEP_WORKFLOW_STEP", f"{expected[0]}:{expected[1]}"))
        elif count != 1:
            issues.append(("DUPLICATE_FIXDEP_WORKFLOW_STEP", f"{expected[0]}:{expected[1]}:count={count}"))

    filtered_steps = [step for step in steps if step in REQUIRED_FIXDEP_STEPS]
    expected_steps = list(REQUIRED_FIXDEP_STEPS)
    if filtered_steps != expected_steps:
        rendered = [f"{name}:{run}" for name, run in filtered_steps]
        expected = [f"{name}:{run}" for name, run in expected_steps]
        issues.append(("FIXDEP_WORKFLOW_STEP_ORDER_MISMATCH", f"actual={rendered!r}:expected={expected!r}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_FIXDEP_WORKFLOW_ORDER=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def render_workflow(steps: tuple[tuple[str, str], ...] = REQUIRED_FIXDEP_STEPS) -> str:
    lines = ["jobs:", "  bootstrap:", "    steps:"]
    for name, run in steps:
        lines.append(f"      - name: {name}")
        lines.append(f"        run: {run}")
    return "\n".join(lines) + "\n"


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_fixdep_workflow_order_") as tmp_dir:
        root = Path(tmp_dir)
        workflow_path = root / WORKFLOW_REL

        write_text(workflow_path, render_workflow())
        assert collect_issues(root) == []
        checks_run += 1

        write_text(workflow_path, render_workflow(REQUIRED_FIXDEP_STEPS[:-1]))
        assert any(code == "MISSING_FIXDEP_WORKFLOW_STEP" for code, _ in collect_issues(root))
        checks_run += 1

        write_text(workflow_path, render_workflow(REQUIRED_FIXDEP_STEPS + (REQUIRED_FIXDEP_STEPS[-1],)))
        assert any(code == "DUPLICATE_FIXDEP_WORKFLOW_STEP" for code, _ in collect_issues(root))
        checks_run += 1

        swapped = REQUIRED_FIXDEP_STEPS[:2] + (REQUIRED_FIXDEP_STEPS[3], REQUIRED_FIXDEP_STEPS[2]) + REQUIRED_FIXDEP_STEPS[4:]
        write_text(workflow_path, render_workflow(swapped))
        assert any(code == "FIXDEP_WORKFLOW_STEP_ORDER_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

    print("PHASE2_FIXDEP_WORKFLOW_ORDER_SELF_TEST=pass")
    print(f"PHASE2_FIXDEP_WORKFLOW_ORDER_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that Phase 2 fixdep workflow steps stay grouped and ordered.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_FIXDEP_WORKFLOW_ORDER=pass")
    print(f"PHASE2_FIXDEP_WORKFLOW_ORDER_REQUIRED_STEP_COUNT={len(REQUIRED_FIXDEP_STEPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

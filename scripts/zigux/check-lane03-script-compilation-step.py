#!/usr/bin/env python3
"""Guard the current Lane 03 bootstrap script-compilation step."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"

SETUP_STEP = "- name: Setup pinned Zig toolchain"
COMPILE_STEP = "- name: Compile current scripts"
NEXT_STEP = "- name: Self-test current Zig toolchain checker"

COMPILE_STEP_LINES = (
    "set -euxo pipefail",
    "mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)",
    'if [ "${#scripts[@]}" -eq 0 ]; then',
    "echo 'no Python scripts found under scripts/zigux' >&2",
    "exit 1",
    'python3 -m py_compile "${scripts[@]}"',
)

EXPECTED_SELF_TEST_CASE_COUNT = 9


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


def find_exact_line_index(text: str, marker: str) -> int:
    for index, line in enumerate(text.splitlines()):
        if line.strip() == marker:
            return index
    return -1


def extract_step_block(text: str, marker: str) -> list[str]:
    lines = text.splitlines()
    start_index = find_exact_line_index(text, marker)
    if start_index == -1:
        return []

    block: list[str] = []
    for line in lines[start_index + 1 :]:
        stripped = line.strip()
        if stripped.startswith("- name:"):
            break
        block.append(stripped)
    return block


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


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve_path(root, WORKFLOW),
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                f"      {SETUP_STEP}",
                "        run: echo setup",
                f"      {COMPILE_STEP}",
                "        run: |",
                "          set -euxo pipefail",
                "          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)",
                '          if [ "${#scripts[@]}" -eq 0 ]; then',
                "            echo 'no Python scripts found under scripts/zigux' >&2",
                "            exit 1",
                "          fi",
                '          python3 -m py_compile "${scripts[@]}"',
                f"      {NEXT_STEP}",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
            )
        )
        + "\n",
    )


def collect_issues(root: Path) -> list[tuple[str, str]]:
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    issues: list[tuple[str, str]] = []

    for marker in (SETUP_STEP, COMPILE_STEP, NEXT_STEP):
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_STEP", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_STEP", f"{marker}:count={count}"))

    compile_block = extract_step_block(workflow_text, COMPILE_STEP)
    compile_block_text = "\n".join(compile_block) + ("\n" if compile_block else "")
    for marker in COMPILE_STEP_LINES:
        count = count_exact_lines(compile_block_text, marker)
        if count == 0:
            issues.append(("MISSING_COMPILE_STEP_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_COMPILE_STEP_LINE", f"{marker}:count={count}"))

    setup_index = find_exact_line_index(workflow_text, SETUP_STEP)
    compile_index = find_exact_line_index(workflow_text, COMPILE_STEP)
    next_index = find_exact_line_index(workflow_text, NEXT_STEP)
    if setup_index != -1 and compile_index != -1 and setup_index > compile_index:
        issues.append(("INVALID_STEP_ORDER", f"{SETUP_STEP} must appear before {COMPILE_STEP}"))
    if compile_index != -1 and next_index != -1 and compile_index > next_index:
        issues.append(("INVALID_STEP_ORDER", f"{COMPILE_STEP} must appear before {NEXT_STEP}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("LANE03_SCRIPT_COMPILATION_STEP=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane03_script_compilation_step_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), COMPILE_STEP),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_STEP", COMPILE_STEP) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(
                workflow_path.read_text(encoding="utf-8"),
                COMPILE_STEP_LINES[1],
                "          mapfile -t scripts < <(find scripts -type f -name '*.py' | sort)",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_COMPILE_STEP_LINE", COMPILE_STEP_LINES[1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), COMPILE_STEP_LINES[-1]),
            encoding="utf-8",
        )
        assert ("MISSING_COMPILE_STEP_LINE", COMPILE_STEP_LINES[-1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), COMPILE_STEP_LINES[-1]),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_COMPILE_STEP_LINE",
            f'{COMPILE_STEP_LINES[-1]}:count=2',
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), COMPILE_STEP),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_WORKFLOW_STEP",
            f"{COMPILE_STEP}:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        text = workflow_path.read_text(encoding="utf-8")
        text = replace_exact_line(text, COMPILE_STEP)
        text = replace_exact_line(text, NEXT_STEP)
        text = text.rstrip("\n") + "\n" + f"      {NEXT_STEP}\n        run: python3 scripts/zigux/check-zig-toolchain.py --self-test\n"
        text = text.rstrip("\n") + "\n" + f"      {COMPILE_STEP}\n        run: |\n"
        for marker in COMPILE_STEP_LINES:
            text += f"          {marker}\n"
        workflow_path.write_text(text, encoding="utf-8")
        assert (
            "INVALID_STEP_ORDER",
            f"{COMPILE_STEP} must appear before {NEXT_STEP}",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        text = workflow_path.read_text(encoding="utf-8")
        text = replace_exact_line(text, SETUP_STEP)
        text = text.rstrip("\n") + "\n" + f"      {SETUP_STEP}\n        run: echo setup\n"
        workflow_path.write_text(text, encoding="utf-8")
        assert (
            "INVALID_STEP_ORDER",
            f"{SETUP_STEP} must appear before {COMPILE_STEP}",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, WORKFLOW).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing workflow did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("LANE03_SCRIPT_COMPILATION_STEP_SELF_TEST=pass")
    print(f"LANE03_SCRIPT_COMPILATION_STEP_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Lane 03 bootstrap script-compilation step stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("LANE03_SCRIPT_COMPILATION_STEP=pass")
    print(f"LANE03_SCRIPT_COMPILATION_STEP_REQUIRED_LINE_COUNT={len(COMPILE_STEP_LINES)}")
    print("LANE03_SCRIPT_COMPILATION_STEP_ORDER_STATUS=present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

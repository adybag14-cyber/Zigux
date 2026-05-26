#!/usr/bin/env python3
"""Guard the Lane 03 bootstrap workflow compile-current-scripts packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
SCRIPTS_DIR = "scripts/zigux"
STEP_HEADING = "- name: Compile current scripts"
EXPECTED_SELF_TEST_CASE_COUNT = 9

REQUIRED_STEP_LINES = (
    "set -euxo pipefail",
    "mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)",
    'if [ "${#scripts[@]}" -eq 0 ]; then',
    "echo 'no Python scripts found under scripts/zigux' >&2",
    "exit 1",
    "fi",
    'python3 -m py_compile "${scripts[@]}"',
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


def extract_step_body(workflow_text: str, heading: str) -> str:
    lines = workflow_text.splitlines()
    matches = [index for index, line in enumerate(lines) if line.strip() == heading]
    if len(matches) != 1:
        return ""

    start = matches[0] + 1
    end = len(lines)
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("- name:"):
            end = index
            break
    return "\n".join(lines[start:end]) + "\n"


def find_exact_line_indices(text: str, markers: tuple[str, ...]) -> list[int]:
    indices: list[int] = []
    lines = text.splitlines()
    for marker in markers:
        matches = [index for index, line in enumerate(lines) if line.strip() == marker]
        if len(matches) != 1:
            return []
        indices.append(matches[0])
    return indices


def list_top_level_python_files(root: Path) -> list[str]:
    scripts_root = root / SCRIPTS_DIR
    if not scripts_root.exists():
        return []
    return sorted(path.name for path in scripts_root.iterdir() if path.is_file() and path.suffix == ".py")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(root, WORKFLOW)

    heading_count = count_exact_lines(workflow_text, STEP_HEADING)
    if heading_count == 0:
        issues.append(("MISSING_COMPILE_STEP_HEADING", STEP_HEADING))
        return issues
    if heading_count != 1:
        issues.append(("DUPLICATE_COMPILE_STEP_HEADING", f"{STEP_HEADING}:count={heading_count}"))
        return issues

    step_body = extract_step_body(workflow_text, STEP_HEADING)
    if not step_body:
        issues.append(("INVALID_COMPILE_STEP_BODY", STEP_HEADING))
        return issues

    for marker in REQUIRED_STEP_LINES:
        count = count_exact_lines(step_body, marker)
        if count == 0:
            issues.append(("MISSING_COMPILE_STEP_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_COMPILE_STEP_LINE", f"{marker}:count={count}"))

    if not issues:
        indices = find_exact_line_indices(step_body, REQUIRED_STEP_LINES)
        if indices != sorted(indices):
            issues.append(("OUT_OF_ORDER_COMPILE_STEP_LINE", " -> ".join(REQUIRED_STEP_LINES)))

    scripts_root = root / SCRIPTS_DIR
    if not scripts_root.exists():
        issues.append(("MISSING_SCRIPTS_ROOT", SCRIPTS_DIR))
        return issues

    top_level_python_files = list_top_level_python_files(root)
    if not top_level_python_files:
        issues.append(("MISSING_TOP_LEVEL_PYTHON_SCRIPTS", SCRIPTS_DIR))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_COMPILE_PACKET=fail")
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
                f"      {STEP_HEADING}",
                "        run: |",
                "          set -euxo pipefail",
                "          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)",
                '          if [ "${#scripts[@]}" -eq 0 ]; then',
                "            echo 'no Python scripts found under scripts/zigux' >&2",
                "            exit 1",
                "          fi",
                '          python3 -m py_compile "${scripts[@]}"',
                "      - name: Next step",
                "        run: true",
            )
        )
        + "\n",
    )
    write_text(root, "scripts/zigux/alpha.py", "print('alpha')\n")
    write_text(root, "scripts/zigux/beta.py", "print('beta')\n")
    write_text(root, "scripts/zigux/nested/ignored.py", "print('nested')\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_compile_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), STEP_HEADING))
        assert ("MISSING_COMPILE_STEP_HEADING", STEP_HEADING) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), STEP_HEADING))
        assert ("DUPLICATE_COMPILE_STEP_HEADING", f"{STEP_HEADING}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        marker = REQUIRED_STEP_LINES[1]
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), marker))
        assert ("MISSING_COMPILE_STEP_LINE", marker) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        marker = REQUIRED_STEP_LINES[-1]
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), marker))
        assert ("DUPLICATE_COMPILE_STEP_LINE", f"{marker}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, swap_exact_lines(read_text(root, WORKFLOW), REQUIRED_STEP_LINES[0], REQUIRED_STEP_LINES[-1]))
        assert any(code == "OUT_OF_ORDER_COMPILE_STEP_LINE" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        (root / "scripts/zigux").rename(root / "scripts/zigux-moved")
        assert ("MISSING_SCRIPTS_ROOT", SCRIPTS_DIR) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        for path in (root / "scripts/zigux").glob("*.py"):
            path.unlink()
        assert ("MISSING_TOP_LEVEL_PYTHON_SCRIPTS", SCRIPTS_DIR) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                REQUIRED_STEP_LINES[1],
                "          mapfile -t scripts < <(find scripts/zigux -type f -name '*.py' | sort)",
            ),
        )
        assert ("MISSING_COMPILE_STEP_LINE", REQUIRED_STEP_LINES[1]) in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_BOOTSTRAP_COMPILE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_COMPILE_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 03 bootstrap workflow keeps compiling the current top-level scripts/zigux Python packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    top_level_python_files = list_top_level_python_files(args.root.resolve())
    print("PHASE2_BOOTSTRAP_COMPILE_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_COMPILE_PACKET_REQUIRED_LINE_COUNT={len(REQUIRED_STEP_LINES)}")
    print(f"PHASE2_BOOTSTRAP_COMPILE_PACKET_SCRIPT_COUNT={len(top_level_python_files)}")
    print("PHASE2_BOOTSTRAP_COMPILE_PACKET_SCRIPT_LIST=" + ",".join(top_level_python_files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
SCRIPTS_DIR = Path("scripts/zigux")

STEP_NAME = "Compile current scripts"
SETUP_STEP_NAME = "Setup pinned Zig toolchain"
NEXT_STEP_NAME = "Self-test current Zig toolchain checker"

REQUIRED_SCRIPT_FILES = [
    Path("scripts/zigux/check-zig-toolchain.py"),
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/validate-phase2.py"),
]

REQUIRED_STEP_LINES = [
    "mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)",
    'if [ "${#scripts[@]}" -eq 0 ]; then',
    "echo 'no Python scripts found under scripts/zigux' >&2",
    "exit 1",
    "fi",
    'python3 -m py_compile "${scripts[@]}"',
]


def normalized_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines()]


def count_line(text: str, needle: str) -> int:
    return sum(1 for line in normalized_lines(text) if line == needle)


def find_line_index(text: str, needle: str) -> int:
    for index, line in enumerate(normalized_lines(text)):
        if line == needle:
            return index
    return -1


def require_files(root: Path) -> list[str]:
    missing: list[str] = []
    required_paths = [WORKFLOW, *REQUIRED_SCRIPT_FILES]
    for rel_path in required_paths:
        if not (root / rel_path).is_file():
            missing.append(str(rel_path))

    scripts_dir = root / SCRIPTS_DIR
    if not scripts_dir.is_dir():
        missing.append(str(SCRIPTS_DIR))
    elif not any(scripts_dir.glob("*.py")):
        missing.append("scripts/zigux/*.py")
    return missing


def top_level_python_scripts(root: Path) -> list[str]:
    scripts_dir = root / SCRIPTS_DIR
    return sorted(path.name for path in scripts_dir.glob("*.py") if path.is_file())


def validate_workflow(text: str) -> list[str]:
    issues: list[str] = []

    expected_steps = {
        f"- name: {SETUP_STEP_NAME}": 1,
        f"- name: {STEP_NAME}": 1,
        f"- name: {NEXT_STEP_NAME}": 1,
    }
    for line, expected_count in expected_steps.items():
        actual_count = count_line(text, line)
        if actual_count != expected_count:
            issues.append(f"workflow:count:{line}:{actual_count}")

    for line in REQUIRED_STEP_LINES:
        actual_count = count_line(text, line)
        if actual_count != 1:
            issues.append(f"workflow:compile_line:{line}:{actual_count}")

    setup_pos = find_line_index(text, f"- name: {SETUP_STEP_NAME}")
    compile_pos = find_line_index(text, f"- name: {STEP_NAME}")
    next_pos = find_line_index(text, f"- name: {NEXT_STEP_NAME}")
    if not (setup_pos != -1 and compile_pos != -1 and next_pos != -1):
        issues.append("workflow:step_order:missing_boundary")
    elif not (setup_pos < compile_pos < next_pos):
        issues.append("workflow:step_order:out_of_order")

    return issues


def validate_root(root: Path) -> list[str]:
    issues = [f"missing:{rel_path}" for rel_path in require_files(root)]
    if issues:
        return issues

    workflow_text = (root / WORKFLOW).read_text(encoding="utf-8")
    issues.extend(validate_workflow(workflow_text))
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    workflow_text = """name: zigux-bootstrap

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Setup pinned Zig toolchain
        run: |
          echo setup

      - name: Compile current scripts
        run: |
          set -euxo pipefail
          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)
          if [ \"${#scripts[@]}\" -eq 0 ]; then
            echo 'no Python scripts found under scripts/zigux' >&2
            exit 1
          fi
          python3 -m py_compile \"${scripts[@]}\"

      - name: Self-test current Zig toolchain checker
        run: python3 scripts/zigux/check-zig-toolchain.py --self-test
"""
    write_text(root / WORKFLOW, workflow_text)
    write_text(root / "scripts/zigux/check-zig-toolchain.py", "print('ok')\n")
    write_text(root / "scripts/zigux/install-zig.py", "print('ok')\n")
    write_text(root / "scripts/zigux/validate-phase2.py", "print('ok')\n")
    write_text(root / "scripts/zigux/extra.py", "print('ok')\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_bootstrap_compile_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)

        assert require_files(root) == []
        assert validate_root(root) == []
        case_count += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                'python3 -m py_compile "${scripts[@]}"\n',
                "",
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert any(issue.startswith("workflow:compile_line:python3 -m py_compile") for issue in issues)
        case_count += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)\n",
                "",
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert any(issue.startswith("workflow:compile_line:mapfile -t scripts") for issue in issues)
        case_count += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "- name: Compile current scripts\n",
                "- name: Compile current scripts\n      - name: Compile current scripts\n",
            ),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert f"workflow:count:- name: {STEP_NAME}:2" in issues
        case_count += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW
        workflow_text = workflow_path.read_text(encoding="utf-8")
        compile_block = """      - name: Compile current scripts
        run: |
          set -euxo pipefail
          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)
          if [ \"${#scripts[@]}\" -eq 0 ]; then
            echo 'no Python scripts found under scripts/zigux' >&2
            exit 1
          fi
          python3 -m py_compile \"${scripts[@]}\"

"""
        setup_block = """      - name: Setup pinned Zig toolchain
        run: |
          echo setup

"""
        workflow_path.write_text(
            workflow_text.replace(setup_block + compile_block, compile_block + setup_block),
            encoding="utf-8",
        )
        issues = validate_root(root)
        assert "workflow:step_order:out_of_order" in issues
        case_count += 1

        build_sample_root(root)
        (root / "scripts/zigux/install-zig.py").unlink()
        issues = validate_root(root)
        assert "missing:scripts/zigux/install-zig.py" in issues
        case_count += 1

    print("PHASE2_BOOTSTRAP_COMPILE_STEP_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_COMPILE_STEP_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 2 bootstrap workflow compile-current-scripts packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the current checkout root.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for replay coverage.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_BOOTSTRAP_COMPILE_STEP_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = validate_root(args.root)
    if issues:
        print("PHASE2_BOOTSTRAP_COMPILE_STEP=fail")
        for issue in issues:
            print(f"PHASE2_BOOTSTRAP_COMPILE_STEP_ISSUE={issue}")
        return 1

    script_files = top_level_python_scripts(args.root)
    print("PHASE2_BOOTSTRAP_COMPILE_STEP=pass")
    print(f"PHASE2_BOOTSTRAP_COMPILE_STEP_REQUIRED_FILE_COUNT={1 + len(REQUIRED_SCRIPT_FILES)}")
    print(f"PHASE2_BOOTSTRAP_COMPILE_STEP_TOP_LEVEL_SCRIPT_COUNT={len(script_files)}")
    print("PHASE2_BOOTSTRAP_COMPILE_STEP_REQUIRED_BOUNDARY=" + ",".join([STEP_NAME, NEXT_STEP_NAME]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

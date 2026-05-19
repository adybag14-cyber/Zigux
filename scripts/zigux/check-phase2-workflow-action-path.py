#!/usr/bin/env python3
"""Guard the Lane 18 Phase 2 workflow action-path packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
INSTALLER = ROOT / "scripts" / "zigux" / "install-zig.py"
CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
CROSS_ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"
CROSS_FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

EXACT_WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/install-zig.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-phase2-cross.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross.py": 1,
}

ORDERED_STEP_MARKERS = (
    "- name: Compile current scripts",
    "- name: Self-test restored Zig installer helper",
    "- name: Self-test current Zig toolchain checker",
    "- name: Check current Phase 2 cross alignment packet",
    "- name: Self-test current Phase 2 direct cross-route checker",
    "- name: Check current Phase 2 direct cross-route packet",
    "- name: Self-test current Phase 2 toolchain pinning checker",
)

EXPECTED_SELF_TEST_CASE_COUNT = 13

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

def validate_exact_workflow_runs(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for command, expected_count in EXACT_WORKFLOW_RUN_COUNTS.items():
        count = count_exact_lines(text, f"run: {command}")
        if count == 0:
            issues.append(("MISSING_WORKFLOW_RUN", command))
        elif count != expected_count:
            issues.append(("DUPLICATE_WORKFLOW_RUN", f"{command}:count={count}"))
    return issues

def validate_required_files(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for path in (INSTALLER, CROSS_CHECKER, CROSS_ALIGNMENT_CHECKER, CROSS_FIXTURE):
        resolved = resolve_path(root, path)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_FILE", str(path.relative_to(ROOT))))
    return issues

def validate_step_order(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    positions: dict[str, int] = {}
    for marker in ORDERED_STEP_MARKERS:
        index = text.find(marker)
        if index < 0:
            issues.append(("MISSING_STEP_MARKER", marker))
            continue
        positions[marker] = index
    if issues:
        return issues
    for earlier, later in zip(ORDERED_STEP_MARKERS, ORDERED_STEP_MARKERS[1:]):
        if positions[earlier] >= positions[later]:
            issues.append(("STEP_ORDER", f"{earlier} -> {later}"))
    return issues

def collect_issues(root: Path) -> list[tuple[str, str]]:
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    issues: list[tuple[str, str]] = []
    issues.extend(validate_required_files(root))
    issues.extend(validate_exact_workflow_runs(workflow_text))
    issues.extend(validate_step_order(workflow_text))
    return issues

def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_WORKFLOW_ACTION_PATH=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1

def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, INSTALLER), "#!/usr/bin/env python3\n")
    write_text(resolve_path(root, CROSS_CHECKER), "#!/usr/bin/env python3\n")
    write_text(resolve_path(root, CROSS_ALIGNMENT_CHECKER), "#!/usr/bin/env python3\n")
    write_text(resolve_path(root, CROSS_FIXTURE), "{\n  \"phase\": \"Phase 2\"\n}\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(["jobs:","  bootstrap:","    steps:","      - name: Compile current scripts","        run: python3 -m py_compile scripts/zigux/*.py","      - name: Self-test restored Zig installer helper","        run: python3 scripts/zigux/install-zig.py --self-test","      - name: Self-test current Zig toolchain checker","        run: python3 scripts/zigux/check-zig-toolchain.py --self-test","      - name: Self-test current Phase 2 cross selftest alignment checker","        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test","      - name: Check current Phase 2 cross alignment packet","        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py","      - name: Self-test current Phase 2 direct cross-route checker","        run: python3 scripts/zigux/check-phase2-cross.py --self-test","      - name: Check current Phase 2 direct cross-route packet","        run: python3 scripts/zigux/check-phase2-cross.py","      - name: Self-test current Phase 2 toolchain pinning checker","        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",""]))

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

def swap_step_markers(text: str, first: str, second: str) -> str:
    first_line = f"      - name: {first}"
    second_line = f"      - name: {second}"
    placeholder = "__PHASE2_WORKFLOW_ACTION_PATH_PLACEHOLDER__"
    return text.replace(first_line, placeholder, 1).replace(second_line, first_line, 1).replace(placeholder, second_line, 1)

def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_workflow_action_path_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1
        for command in ("python3 scripts/zigux/install-zig.py --self-test","python3 scripts/zigux/check-phase2-cross.py --self-test","python3 scripts/zigux/check-phase2-cross.py",):
            build_self_test_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(replace_exact_line(workflow_path.read_text(encoding="utf-8"), f"run: {command}", "        run: true"), encoding="utf-8")
            assert ("MISSING_WORKFLOW_RUN", command) in collect_issues(root)
            checks_run += 1
        for command in ("python3 scripts/zigux/install-zig.py --self-test","python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test","python3 scripts/zigux/check-phase2-cross-selftest-alignment.py","python3 scripts/zigux/check-phase2-cross.py --self-test","python3 scripts/zigux/check-phase2-cross.py"):
            build_self_test_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), f"run: {command}"), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_RUN", f"{command}:count=2") in collect_issues(root)
            checks_run += 1
        build_self_test_root(root)
        resolve_path(root, INSTALLER).unlink()
        assert ("MISSING_REQUIRED_FILE", "scripts/zigux/install-zig.py") in collect_issues(root)
        checks_run += 1
        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(swap_step_markers(workflow_path.read_text(encoding="utf-8"),"Self-test restored Zig installer helper","Self-test current Zig toolchain checker"), encoding="utf-8")
        assert ("STEP_ORDER","- name: Self-test restored Zig installer helper -> - name: Self-test current Zig toolchain checker") in collect_issues(root)
        checks_run += 1
        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(swap_step_markers(workflow_path.read_text(encoding="utf-8"),"Check current Phase 2 cross alignment packet","Self-test current Phase 2 direct cross-route checker"), encoding="utf-8")
        assert ("STEP_ORDER","- name: Check current Phase 2 cross alignment packet -> - name: Self-test current Phase 2 direct cross-route checker") in collect_issues(root)
        checks_run += 1
        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(swap_step_markers(workflow_path.read_text(encoding="utf-8"),"Check current Phase 2 direct cross-route packet","Self-test current Phase 2 toolchain pinning checker"), encoding="utf-8")
        assert ("STEP_ORDER","- name: Check current Phase 2 direct cross-route packet -> - name: Self-test current Phase 2 toolchain pinning checker") in collect_issues(root)
        checks_run += 1
    print("PHASE2_WORKFLOW_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_WORKFLOW_ACTION_PATH_SELF_TEST_CASE_COUNT={checks_run}")
    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        raise SystemExit(f"unexpected self-test case count: {checks_run} != {EXPECTED_SELF_TEST_CASE_COUNT}")
    return 0

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Guard the Lane 18 Phase 2 workflow action-path packet.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("PHASE2_WORKFLOW_ACTION_PATH=pass")
    print("PHASE2_WORKFLOW_ACTION_PATH_REQUIRED_FILE_COUNT=4")
    print(f"PHASE2_WORKFLOW_ACTION_PATH_MARKER_COUNT={len(EXACT_WORKFLOW_RUN_COUNTS)}")
    print(f"PHASE2_WORKFLOW_ACTION_PATH_ORDER_CHECK_COUNT={len(ORDERED_STEP_MARKERS) - 1}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

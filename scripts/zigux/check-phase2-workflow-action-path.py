#!/usr/bin/env python3
"""Guard the current Lane 18 Phase 2 workflow action-path packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
INSTALLER = ROOT / "scripts" / "zigux" / "install-zig.py"
TESTS_ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
CROSS_ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"
WORKFLOW_ACTION_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-workflow-action-path.py"
PINNING_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py"
PIN_SCOPE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"
CROSS_FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

REQUIRED_FILES = (
    INSTALLER,
    TESTS_ALIGNMENT_CHECKER,
    CROSS_CHECKER,
    CROSS_ALIGNMENT_CHECKER,
    WORKFLOW_ACTION_CHECKER,
    PINNING_CHECKER,
    PIN_SCOPE_CHECKER,
    CROSS_FIXTURE,
)

EXACT_WORKFLOW_RUN_LINES = (
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-workflow-action-path.py --self-test",
    "run: python3 scripts/zigux/check-phase2-workflow-action-path.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
)

ORDERED_STEP_MARKERS = (
    "- name: Compile current scripts",
    "- name: Self-test current Zig installer helper",
    "- name: Self-test current staged pinned Zig archive helper",
    "- name: Self-test current Phase 2 tests README checker",
    "- name: Self-test current Phase 2 cross checker",
    "- name: Check current Phase 2 direct cross-route packet",
    "- name: Self-test current Phase 2 cross selftest alignment checker",
    "- name: Check current Phase 2 cross alignment packet",
    "- name: Self-test current Phase 2 workflow action-path checker",
    "- name: Check current Phase 2 workflow action-path packet",
    "- name: Self-test current Phase 2 toolchain pinning checker",
    "- name: Check current Phase 2 toolchain pinning packet",
    "- name: Self-test current Phase 2 toolchain pin-scope checker",
    "- name: Check current Phase 2 toolchain pin-scope packet",
)

EXPECTED_SELF_TEST_CASE_COUNT = 14


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


def swap_step_markers(text: str, first: str, second: str) -> str:
    first_line = f"      {first}"
    second_line = f"      {second}"
    placeholder = "__PHASE2_WORKFLOW_ACTION_PATH_PLACEHOLDER__"
    return (
        text.replace(first_line, placeholder, 1)
        .replace(second_line, first_line, 1)
        .replace(placeholder, second_line, 1)
    )


def validate_required_files(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for path in REQUIRED_FILES:
        resolved = resolve_path(root, path)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_FILE", str(path.relative_to(ROOT))))
    return issues


def validate_workflow_run_lines(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in EXACT_WORKFLOW_RUN_LINES:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_RUN_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_RUN_LINE", f"{marker}:count={count}"))
    return issues


def validate_step_order(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    positions: dict[str, int] = {}
    for marker in ORDERED_STEP_MARKERS:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append(("MISSING_STEP_MARKER", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_STEP_MARKER", f"{marker}:count={count}"))
            continue
        positions[marker] = find_exact_line_index(text, marker)
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
    issues.extend(validate_workflow_run_lines(workflow_text))
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


def build_sample_root(root: Path) -> None:
    for path in REQUIRED_FILES:
        resolved = resolve_path(root, path)
        if resolved.suffix == ".json":
            write_text(resolved, "{\n  \"phase\": \"Phase 2\"\n}\n")
        else:
            write_text(resolved, "#!/usr/bin/env python3\n")
    write_text(
        resolve_path(root, WORKFLOW),
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Compile current scripts",
                "        run: python3 -m py_compile scripts/zigux/*.py",
                "      - name: Self-test current Zig installer helper",
                "        run: python3 scripts/zigux/install-zig.py --self-test",
                "      - name: Self-test current staged pinned Zig archive helper",
                "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
                "      - name: Self-test current Phase 2 tests README checker",
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
                "      - name: Check current Phase 2 tests README packet",
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
                "      - name: Self-test current Phase 2 cross checker",
                "        run: python3 scripts/zigux/check-phase2-cross.py --self-test",
                "      - name: Check current Phase 2 direct cross-route packet",
                "        run: python3 scripts/zigux/check-phase2-cross.py",
                "      - name: Self-test current Phase 2 cross selftest alignment checker",
                "        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
                "      - name: Check current Phase 2 cross alignment packet",
                "        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
                "      - name: Self-test current Phase 2 workflow action-path checker",
                "        run: python3 scripts/zigux/check-phase2-workflow-action-path.py --self-test",
                "      - name: Check current Phase 2 workflow action-path packet",
                "        run: python3 scripts/zigux/check-phase2-workflow-action-path.py",
                "      - name: Self-test current Phase 2 toolchain pinning checker",
                "        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
                "      - name: Check current Phase 2 toolchain pinning packet",
                "        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
                "      - name: Self-test current Phase 2 toolchain pin-scope checker",
                "        run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "      - name: Check current Phase 2 toolchain pin-scope packet",
                "        run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "",
            )
        ),
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_workflow_action_path_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(
                workflow_path.read_text(encoding="utf-8"),
                EXACT_WORKFLOW_RUN_LINES[0],
                "        run: true",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_RUN_LINE", EXACT_WORKFLOW_RUN_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), EXACT_WORKFLOW_RUN_LINES[2]),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_WORKFLOW_RUN_LINE",
            f"{EXACT_WORKFLOW_RUN_LINES[2]}:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(
                workflow_path.read_text(encoding="utf-8"),
                EXACT_WORKFLOW_RUN_LINES[5],
                "        run: true",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_RUN_LINE", EXACT_WORKFLOW_RUN_LINES[5]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        resolve_path(root, INSTALLER).unlink()
        assert ("MISSING_REQUIRED_FILE", "scripts/zigux/install-zig.py") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        resolve_path(root, WORKFLOW_ACTION_CHECKER).unlink()
        assert (
            "MISSING_REQUIRED_FILE",
            "scripts/zigux/check-phase2-workflow-action-path.py",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            swap_step_markers(
                workflow_path.read_text(encoding="utf-8"),
                ORDERED_STEP_MARKERS[1],
                ORDERED_STEP_MARKERS[2],
            ),
            encoding="utf-8",
        )
        assert (
            "STEP_ORDER",
            f"{ORDERED_STEP_MARKERS[1]} -> {ORDERED_STEP_MARKERS[2]}",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            swap_step_markers(
                workflow_path.read_text(encoding="utf-8"),
                ORDERED_STEP_MARKERS[4],
                ORDERED_STEP_MARKERS[5],
            ),
            encoding="utf-8",
        )
        assert (
            "STEP_ORDER",
            f"{ORDERED_STEP_MARKERS[4]} -> {ORDERED_STEP_MARKERS[5]}",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            swap_step_markers(
                workflow_path.read_text(encoding="utf-8"),
                ORDERED_STEP_MARKERS[5],
                ORDERED_STEP_MARKERS[6],
            ),
            encoding="utf-8",
        )
        assert (
            "STEP_ORDER",
            f"{ORDERED_STEP_MARKERS[5]} -> {ORDERED_STEP_MARKERS[6]}",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            swap_step_markers(
                workflow_path.read_text(encoding="utf-8"),
                ORDERED_STEP_MARKERS[7],
                ORDERED_STEP_MARKERS[8],
            ),
            encoding="utf-8",
        )
        assert (
            "STEP_ORDER",
            f"{ORDERED_STEP_MARKERS[7]} -> {ORDERED_STEP_MARKERS[8]}",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            swap_step_markers(
                workflow_path.read_text(encoding="utf-8"),
                ORDERED_STEP_MARKERS[8],
                ORDERED_STEP_MARKERS[9],
            ),
            encoding="utf-8",
        )
        assert (
            "STEP_ORDER",
            f"{ORDERED_STEP_MARKERS[8]} -> {ORDERED_STEP_MARKERS[9]}",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            swap_step_markers(
                workflow_path.read_text(encoding="utf-8"),
                ORDERED_STEP_MARKERS[9],
                ORDERED_STEP_MARKERS[10],
            ),
            encoding="utf-8",
        )
        assert (
            "STEP_ORDER",
            f"{ORDERED_STEP_MARKERS[9]} -> {ORDERED_STEP_MARKERS[10]}",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), ORDERED_STEP_MARKERS[-1]),
            encoding="utf-8",
        )
        assert ("MISSING_STEP_MARKER", ORDERED_STEP_MARKERS[-1]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), ORDERED_STEP_MARKERS[4]),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_STEP_MARKER",
            f"{ORDERED_STEP_MARKERS[4]}:count=2",
        ) in collect_issues(root)
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_WORKFLOW_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_WORKFLOW_ACTION_PATH_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Guard the current Lane 18 Phase 2 workflow action-path packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in self-test suite.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_WORKFLOW_ACTION_PATH=pass")
    print(f"PHASE2_WORKFLOW_ACTION_PATH_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_WORKFLOW_ACTION_PATH_RUN_LINE_COUNT={len(EXACT_WORKFLOW_RUN_LINES)}")
    print(f"PHASE2_WORKFLOW_ACTION_PATH_ORDER_CHECK_COUNT={len(ORDERED_STEP_MARKERS) - 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

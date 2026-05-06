#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()
BRIDGE_CHECKER = Path("scripts/zigux/check-genksyms-bridge.py")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_BRIDGE_MARKERS = (
    "print('GENKSYMS_BRIDGE_SELF_TEST=pass')",
    "print('GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=6')",
)
REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: zig test scripts/zigux/genksyms.zig",
)
EXPECTED_SELF_TEST_CASE_COUNT = 7


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    bridge_text = read_text(root / BRIDGE_CHECKER)
    workflow_text = read_text(root / WORKFLOW)

    for marker in REQUIRED_BRIDGE_MARKERS:
        if marker not in bridge_text:
            issues.append(("MISSING_BRIDGE_MARKERS", marker))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for block, value in issues:
        grouped.setdefault(block, []).append(value)

    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=fail")
    for block, values in grouped.items():
        print(f"{block}_START")
        for value in values:
            print(value)
        print(f"{block}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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


def build_self_test_root(root: Path) -> None:
    write_text(
        root / BRIDGE_CHECKER,
        "\n".join(
            (
                "print('GENKSYMS_BRIDGE_SELF_TEST=pass')",
                "print('GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=6')",
                "",
            )
        ),
    )
    write_text(
        root / WORKFLOW,
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test Phase 2 genksyms bridge alignment",
                "        run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
                "      - name: Check Phase 2 genksyms bridge alignment",
                "        run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
                "      - name: Self-test bounded genksyms bridge parity checker",
                "        run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
                "      - name: Check bounded genksyms bridge parity",
                "        run: python3 scripts/zigux/check-genksyms-bridge.py",
                "      - name: Run bounded genksyms bridge unit tests",
                "        run: zig test scripts/zigux/genksyms.zig",
                "",
            )
        ),
    )


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_genksyms_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []

        build_self_test_root(root)
        path = root / BRIDGE_CHECKER
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_BRIDGE_MARKERS[0], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_BRIDGE_MARKERS", REQUIRED_BRIDGE_MARKERS[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_CHECKER
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_BRIDGE_MARKERS[1], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_BRIDGE_MARKERS", REQUIRED_BRIDGE_MARKERS[1]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[0], "        run: python3 other.py"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", REQUIRED_WORKFLOW_LINES[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[1]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{REQUIRED_WORKFLOW_LINES[1]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[2], "        run: python3 other.py --self-test"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", REQUIRED_WORKFLOW_LINES[2]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[3]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{REQUIRED_WORKFLOW_LINES[3]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[4], "        run: zig test scripts/zigux/other.zig"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", REQUIRED_WORKFLOW_LINES[4]) in issues
        cases += 1

    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 genksyms bridge self-test surface stays wired into CI."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=pass")
    print(f"PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_BRIDGE_MARKER_COUNT={len(REQUIRED_BRIDGE_MARKERS)}")
    print(f"PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
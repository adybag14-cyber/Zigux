#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()
CHECKER = Path("scripts/zigux/check-phase7-make-wrapper.py")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_CHECKER_MARKERS = (
    "EXPECTED_MAKE_EXPANSIONS = {",
    '"phase7-validate": [',
    '"phase7-test": [',
    '"phase7": [',
    'print("PHASE7_MAKE_WRAPPER_SELF_TEST=pass")',
    'print("PHASE7_MAKE_WRAPPER_SELF_TEST_CASE_COUNT=12")',
    'print(f"PHASE7_MAKE_WRAPPER_TARGET_COUNT={len(EXPECTED_MAKE_EXPANSIONS)}")',
)
REQUIRED_CHECKER_EXACT_COUNTS = {
    '"phase7-validate": [': 1,
    '"phase7-test": [': 1,
    '"phase7": [': 1,
    'print("PHASE7_MAKE_WRAPPER_SELF_TEST=pass")': 1,
    'print("PHASE7_MAKE_WRAPPER_SELF_TEST_CASE_COUNT=12")': 1,
    'print(f"PHASE7_MAKE_WRAPPER_TARGET_COUNT={len(EXPECTED_MAKE_EXPANSIONS)}")': 1,
}
REQUIRED_MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py",
)
REQUIRED_WORKFLOW_LINES = (
    "run: make -C zigux phase7-validate",
    "run: zig build test --build-file zigux/tests/phase7_build.zig --summary all",
)
FORBIDDEN_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
    "run: python3 scripts/zigux/check-phase7-make-wrapper.py",
)
EXPECTED_SELF_TEST_CASE_COUNT = 9


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    checker_text = read_text(root / CHECKER)
    makefile_text = read_text(root / MAKEFILE)
    workflow_text = read_text(root / WORKFLOW)

    for marker in REQUIRED_CHECKER_MARKERS:
        if marker not in checker_text:
            issues.append(("MISSING_CHECKER_MARKERS", marker))

    for marker, expected_count in REQUIRED_CHECKER_EXACT_COUNTS.items():
        count = checker_text.count(marker)
        if count != expected_count:
            issues.append(
                (
                    "DUPLICATE_CHECKER_MARKERS",
                    f"{marker}:count={count}:expected={expected_count}",
                )
            )

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_HOOKS", f"{marker}:count={count}"))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    for marker in FORBIDDEN_WORKFLOW_LINES:
        if count_exact_lines(workflow_text, marker):
            issues.append(("FORBIDDEN_WORKFLOW_HOOKS", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for block, value in issues:
        grouped.setdefault(block, []).append(value)

    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=fail")
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
        root / CHECKER,
        "\n".join(
            (
                "EXPECTED_MAKE_EXPANSIONS = {",
                '    "phase7-validate": [',
                '    "phase7-test": [',
                '    "phase7": [',
                "}",
                'print("PHASE7_MAKE_WRAPPER_SELF_TEST=pass")',
                'print("PHASE7_MAKE_WRAPPER_SELF_TEST_CASE_COUNT=12")',
                'print(f"PHASE7_MAKE_WRAPPER_TARGET_COUNT={len(EXPECTED_MAKE_EXPANSIONS)}")',
                "",
            )
        ),
    )
    write_text(
        root / MAKEFILE,
        "\n".join(
            (
                "phase7-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py",
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
                "      - name: Validate Phase 7 runtime helper gates",
                "        run: make -C zigux phase7-validate",
                "      - name: Run Phase 7 runtime helper tests",
                "        run: zig build test --build-file zigux/tests/phase7_build.zig --summary all",
                "",
            )
        ),
    )


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p7_make_wrapper_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []

        build_self_test_root(root)
        path = root / CHECKER
        path.write_text(
            path.read_text(encoding="utf-8").replace(REQUIRED_CHECKER_MARKERS[4], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_CHECKER_MARKERS", REQUIRED_CHECKER_MARKERS[4]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / CHECKER
        path.write_text(
            path.read_text(encoding="utf-8").replace(REQUIRED_CHECKER_MARKERS[5], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_CHECKER_MARKERS", REQUIRED_CHECKER_MARKERS[5]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / CHECKER
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                REQUIRED_CHECKER_MARKERS[3],
                REQUIRED_CHECKER_MARKERS[3] + "\n" + REQUIRED_CHECKER_MARKERS[3],
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "DUPLICATE_CHECKER_MARKERS",
            f'{REQUIRED_CHECKER_MARKERS[3]}:count=2:expected=1',
        ) in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[0], "\ttrue"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_HOOKS", REQUIRED_MAKEFILE_LINES[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(
            duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[1]),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("DUPLICATE_MAKEFILE_HOOKS", f"{REQUIRED_MAKEFILE_LINES[1]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[0], "        run: true"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", REQUIRED_WORKFLOW_LINES[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[1]),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{REQUIRED_WORKFLOW_LINES[1]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            path.read_text(encoding="utf-8")
            + "        run: python3 scripts/zigux/check-phase7-make-wrapper.py --self-test\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("FORBIDDEN_WORKFLOW_HOOKS", FORBIDDEN_WORKFLOW_LINES[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / CHECKER
        path.write_text(
            path.read_text(encoding="utf-8").replace(REQUIRED_CHECKER_MARKERS[6], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_CHECKER_MARKERS", REQUIRED_CHECKER_MARKERS[6]) in issues
        cases += 1

    assert cases == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 7 make-wrapper self-test surface stays centralized in the shared make route."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_MARKER_COUNT={len(REQUIRED_CHECKER_MARKERS)}")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_MAKEFILE_HOOK_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

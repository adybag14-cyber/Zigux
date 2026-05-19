#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()

ACTIVE_CHECKER = Path("scripts/zigux/check-phase7-shared-control-gap.py")
SEQUENCING_NOTE = Path("Documentation/zigux/phase7-helper-lane-sequencing.md")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
PARKED_PATHS = (
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/validate-phase7.py",
    "zigux/tests/phase7_build.zig",
)

REQUIRED_CHECKER_MARKERS = (
    "PARKED_SHARED_CONTROL_PATHS = [",
    '"scripts/zigux/check-phase7-make-wrapper.py",',
    '"scripts/zigux/validate-phase7.py",',
    '"zigux/tests/phase7_build.zig",',
    'print("PHASE7_SHARED_CONTROL_GAP_SELF_TEST=pass")',
    'print(f"PHASE7_SHARED_CONTROL_GAP_SELF_TEST_CASE_COUNT={cases_run}")',
    'print("PHASE7_SHARED_CONTROL_GAP=pass")',
)

REQUIRED_SEQUENCING_MARKERS = (
    "- shared control-surface packet, lane `P7-Y05`:",
    "- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
    "- `scripts/zigux/check-phase7-shared-control-gap.py`",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
)

FORBIDDEN_WORKFLOW_LINES = (
    "run: make -C zigux phase7-validate",
    "run: make -C zigux phase7-test",
    "run: python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
    "run: python3 scripts/zigux/check-phase7-make-wrapper.py",
    "run: python3 scripts/zigux/validate-phase7.py --self-test",
    "run: python3 scripts/zigux/validate-phase7.py",
    "run: zig build test --build-file zigux/tests/phase7_build.zig --summary all",
)

FORBIDDEN_MAKEFILE_LINES = (
    "phase7-validate:",
    "phase7-test:",
    "phase7:",
)

EXPECTED_SELF_TEST_CASE_COUNT = 18


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    checker_path = root / ACTIVE_CHECKER
    if not checker_path.is_file():
        issues.append(("MISSING_ACTIVE_CHECKER", str(ACTIVE_CHECKER)))
        return issues

    checker_text = read_text(checker_path)
    sequencing_text = read_text(root / SEQUENCING_NOTE)
    makefile_text = read_text(root / MAKEFILE)
    workflow_text = read_text(root / WORKFLOW)

    for marker in REQUIRED_CHECKER_MARKERS:
        if marker not in checker_text:
            issues.append(("MISSING_CHECKER_MARKERS", marker))

    for marker in REQUIRED_SEQUENCING_MARKERS:
        if marker not in sequencing_text:
            issues.append(("MISSING_SEQUENCING_MARKERS", marker))

    for rel in PARKED_PATHS:
        if (root / rel).exists():
            issues.append(("UNEXPECTED_REMATERIALIZED_PATHS", rel))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    for marker in FORBIDDEN_WORKFLOW_LINES:
        if count_exact_lines(workflow_text, marker):
            issues.append(("FORBIDDEN_WORKFLOW_HOOKS", marker))

    for marker in FORBIDDEN_MAKEFILE_LINES:
        if count_exact_lines(makefile_text, marker):
            issues.append(("FORBIDDEN_MAKEFILE_LINES", marker))

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


def build_self_test_root(root: Path) -> None:
    write_text(
        root / ACTIVE_CHECKER,
        "\n".join(REQUIRED_CHECKER_MARKERS) + "\n",
    )
    write_text(
        root / SEQUENCING_NOTE,
        "\n".join(REQUIRED_SEQUENCING_MARKERS) + "\n",
    )
    write_text(
        root / MAKEFILE,
        "\n".join(
            (
                "phase2-validate:",
                "\tpython3 scripts/zigux/validate-phase2.py",
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
                "      - name: Self-test current Phase 7 shared-control gap checker",
                "        run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
                "      - name: Check current Phase 7 shared-control gap packet",
                "        run: python3 scripts/zigux/check-phase7-shared-control-gap.py",
                "      - name: Self-test current Phase 7 make-wrapper selftest alignment checker",
                "        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
                "      - name: Check current Phase 7 make-wrapper selftest alignment packet",
                "        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
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
        path = root / ACTIVE_CHECKER
        path.write_text(
            path.read_text(encoding="utf-8").replace(REQUIRED_CHECKER_MARKERS[4], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_CHECKER_MARKERS", REQUIRED_CHECKER_MARKERS[4]) in issues
        cases += 1

        for marker in REQUIRED_SEQUENCING_MARKERS:
            build_self_test_root(root)
            path = root / SEQUENCING_NOTE
            path.write_text(
                path.read_text(encoding="utf-8").replace(marker + "\n", "", 1),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_SEQUENCING_MARKERS", marker) in issues
            cases += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            path = root / WORKFLOW
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "        run: true"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_HOOKS", marker) in issues
            cases += 1

        for marker in FORBIDDEN_WORKFLOW_LINES:
            build_self_test_root(root)
            path = root / WORKFLOW
            path.write_text(path.read_text(encoding="utf-8") + f"        {marker}\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_WORKFLOW_HOOKS", marker) in issues
            cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(path.read_text(encoding="utf-8") + "phase7-validate:\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("FORBIDDEN_MAKEFILE_LINES", "phase7-validate:") in issues
        cases += 1

        build_self_test_root(root)
        parked_path = root / PARKED_PATHS[0]
        write_text(parked_path, "# stale parked path returned\n")
        issues = collect_issues(root)
        assert ("UNEXPECTED_REMATERIALIZED_PATHS", PARKED_PATHS[0]) in issues
        cases += 1

        build_self_test_root(root)
        (root / ACTIVE_CHECKER).unlink()
        issues = collect_issues(root)
        assert ("MISSING_ACTIVE_CHECKER", str(ACTIVE_CHECKER)) in issues
        cases += 1

    assert cases == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the parked Phase 7 make-wrapper posture stays aligned with the live shared-control checker."
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
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_PARKED_PATH_COUNT={len(PARKED_PATHS)}")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_FORBIDDEN_WORKFLOW_HOOK_COUNT={len(FORBIDDEN_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

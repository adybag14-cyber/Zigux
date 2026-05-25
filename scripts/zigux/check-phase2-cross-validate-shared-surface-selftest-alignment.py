#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-shared-surface.py"

REQUIRED_SOURCE_MARKERS = (
    'WORKFLOW_ORDER_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-workflow-order.py"',
    'WORKFLOW_ORDER_ALIGNMENT = (',
    '    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-workflow-order-selftest-alignment.py"',
    'MAKEFILE_ORDER_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-makefile-order.py"',
    'MAKEFILE_ORDER_ALIGNMENT = (',
    '    ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-makefile-order-selftest-alignment.py"',
    '    WORKFLOW_ORDER_CHECKER,',
    '    WORKFLOW_ORDER_ALIGNMENT,',
    '    MAKEFILE_ORDER_CHECKER,',
    '    MAKEFILE_ORDER_ALIGNMENT,',
    '    \'    "scripts/zigux/check-phase2-cross-validate-workflow-order.py",\',',
    '    \'    "scripts/zigux/check-phase2-cross-validate-workflow-order-selftest-alignment.py",\',',
    '    \'    "scripts/zigux/check-phase2-cross-validate-makefile-order.py",\',',
    '    \'    "scripts/zigux/check-phase2-cross-validate-makefile-order-selftest-alignment.py",\',',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-workflow-order-selftest-alignment.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-makefile-order.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-makefile-order.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-makefile-order-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-makefile-order-selftest-alignment.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface-selftest-alignment.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-makefile-order.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-makefile-order.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-makefile-order-selftest-alignment.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-makefile-order-selftest-alignment.py",',
    '        for path in REQUIRED_PATHS[3:]:',
    '    print("PHASE2_CROSS_VALIDATE_SHARED_SURFACE=pass")',
    '    print("PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELF_TEST=pass")',
)

REQUIRED_CASE_MARKERS = (
    '        write_text(resolve_path(root, VALIDATE), "CHECKS = ()\\n")',
    '            + "\\n".join(REQUIRED_VALIDATE_MARKERS + (REQUIRED_VALIDATE_MARKERS[0],))',
    '            + "\\n".join(REQUIRED_WORKFLOW_LINES + (REQUIRED_WORKFLOW_LINES[0],))',
    '        makefile_lines.extend(f"\\t{line}" for line in REQUIRED_MAKEFILE_LINES + (REQUIRED_MAKEFILE_LINES[0],))',
    '        for path in (VALIDATE, WORKFLOW, MAKEFILE):',
    '            resolve_path(root, path).unlink()',
)


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


def count_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    checker_text = read_text(resolve_path(root, CHECKER))
    issues: list[tuple[str, str]] = []

    for marker in REQUIRED_SOURCE_MARKERS:
        count = count_occurrences(checker_text, marker)
        if count == 0:
            issues.append(("MISSING_SOURCE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_SOURCE_MARKER", f"{marker}:count={count}"))

    for marker in REQUIRED_CASE_MARKERS:
        count = count_occurrences(checker_text, marker)
        if count == 0:
            issues.append(("MISSING_CASE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_CASE_MARKER", f"{marker}:count={count}"))

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELFTEST_ALIGNMENT_ISSUE={code}:{detail}")
        print(f"PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELFTEST_ALIGNMENT_ISSUE_COUNT={len(issues)}")
        return 1

    print("PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELFTEST_ALIGNMENT=pass")
    print(f"PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELFTEST_ALIGNMENT_SOURCE_MARKER_COUNT={len(REQUIRED_SOURCE_MARKERS)}")
    print(f"PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELFTEST_ALIGNMENT_CASE_MARKER_COUNT={len(REQUIRED_CASE_MARKERS)}")
    return 0


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, CHECKER), "\n".join((*REQUIRED_SOURCE_MARKERS, *REQUIRED_CASE_MARKERS, "")))


def run_self_test() -> int:
    expected_checks = 1 + len(REQUIRED_SOURCE_MARKERS) + len(REQUIRED_CASE_MARKERS) + 1
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_validate_shared_surface_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert run_check(root) == 0
        checks += 1

        for marker in REQUIRED_SOURCE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, CHECKER)
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert run_check(root) == 1
            checks += 1

        for marker in REQUIRED_CASE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, CHECKER)
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert run_check(root) == 1
            checks += 1

        build_self_test_root(root)
        path = resolve_path(root, CHECKER)
        path.write_text(path.read_text(encoding="utf-8") + REQUIRED_SOURCE_MARKERS[0] + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

    assert checks == expected_checks
    print("PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 21 shared-surface checker self-test markers intact."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())

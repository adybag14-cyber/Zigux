#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-makefile-order.py"

REQUIRED_SOURCE_MARKERS = (
    'MAKEFILE = ROOT / "zigux" / "Makefile"',
    'CONTRACT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-contract.py"',
    'ROUTE_POLICY_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-route-policy.py"',
    'DIRECT_WORKFLOW_CHECKER = (',
    'SHARED_SURFACE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-shared-surface.py"',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-contract.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-route-policy.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-direct-tool-manifest-workflow.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface.py --self-test",',
    '        collect_block_order_issues("DIRECT_WORKFLOW_BLOCK", DIRECT_WORKFLOW_MAKEFILE_LINES, validate_commands)',
    '        issues.append(("INVALID_SHARED_SURFACE_PLACEMENT", ",".join(SHARED_SURFACE_MAKEFILE_LINES)))',
    '            issues.append(("INVALID_DIRECT_WORKFLOW_TARGET_PLACEMENT", marker))',
    '    print("PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER=pass")',
    '    print("PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER_SELF_TEST=pass")',
)

REQUIRED_CASE_MARKERS = (
    '            read_text(makefile_path).replace(CONTRACT_MAKEFILE_LINES[0] + "\\n", "", 1),',
    '            read_text(makefile_path).replace(DIRECT_WORKFLOW_MAKEFILE_LINES[0] + "\\n", "", 1),',
    '            read_text(makefile_path) + f"\\t{SHARED_SURFACE_MAKEFILE_LINES[0]}\\n",',
    '        first = makefile_lines.index(f"\\t{CONTRACT_MAKEFILE_LINES[0]}")',
    '        contract_index = makefile_lines.index(f"\\t{CONTRACT_MAKEFILE_LINES[-1]}")',
    '        direct_index = makefile_lines.index(f"\\t{DIRECT_WORKFLOW_MAKEFILE_LINES[0]}")',
    '        direct_tail = makefile_lines.index(f"\\t{DIRECT_WORKFLOW_MAKEFILE_LINES[-1]}")',
    '        shared_index = makefile_lines.index(f"\\t{SHARED_SURFACE_MAKEFILE_LINES[0]}")',
    '        cross_header = makefile_lines.index(REQUIRED_CROSS_TARGET)',
    '        resolve_path(root, DIRECT_WORKFLOW_ALIGNMENT).unlink()',
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
            print(f"PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER_SELFTEST_ALIGNMENT_ISSUE={code}:{detail}")
        print(f"PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER_SELFTEST_ALIGNMENT_ISSUE_COUNT={len(issues)}")
        return 1

    print("PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER_SELFTEST_ALIGNMENT=pass")
    print(
        "PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER_SELFTEST_ALIGNMENT_SOURCE_MARKER_COUNT="
        f"{len(REQUIRED_SOURCE_MARKERS)}"
    )
    print(
        "PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER_SELFTEST_ALIGNMENT_CASE_MARKER_COUNT="
        f"{len(REQUIRED_CASE_MARKERS)}"
    )
    return 0


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, CHECKER), "\n".join((*REQUIRED_SOURCE_MARKERS, *REQUIRED_CASE_MARKERS, "")))


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(
        prefix="zigux_phase2_cross_validate_makefile_order_alignment_"
    ) as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert run_check(root) == 0
        checks += 1

        for marker in REQUIRED_SOURCE_MARKERS:
            build_self_test_root(root)
            checker_path = resolve_path(root, CHECKER)
            checker_path.write_text(
                read_text(checker_path).replace(marker, "", 1),
                encoding="utf-8",
            )
            assert run_check(root) == 1
            checks += 1

        for marker in REQUIRED_CASE_MARKERS:
            build_self_test_root(root)
            checker_path = resolve_path(root, CHECKER)
            checker_path.write_text(
                read_text(checker_path).replace(marker, "", 1),
                encoding="utf-8",
            )
            assert run_check(root) == 1
            checks += 1

        build_self_test_root(root)
        checker_path = resolve_path(root, CHECKER)
        checker_path.write_text(
            read_text(checker_path) + REQUIRED_SOURCE_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        assert run_check(root) == 1
        checks += 1

        build_self_test_root(root)
        checker_path = resolve_path(root, CHECKER)
        checker_path.write_text(
            read_text(checker_path) + REQUIRED_CASE_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        assert run_check(root) == 1
        checks += 1

    print("PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(
        "PHASE2_CROSS_VALIDATE_MAKEFILE_ORDER_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT="
        f"{checks}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 21 cross validate makefile-order checker self-test markers intact."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
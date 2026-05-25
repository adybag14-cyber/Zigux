#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-shared-surface.py"

REQUIRED_SOURCE_MARKERS = (
    'SHARED_SURFACE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-shared-surface.py"',
    'SHARED_SURFACE_ALIGNMENT = (',
    'ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-shared-surface-selftest-alignment.py"',
    '    SHARED_SURFACE_CHECKER,\n    SHARED_SURFACE_ALIGNMENT,',
    '    \'    "scripts/zigux/check-phase2-cross-validate-shared-surface.py",\',\n'
    '    \'    "scripts/zigux/check-phase2-cross-validate-shared-surface-selftest-alignment.py",\',',
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface.py --self-test",\n'
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface.py",\n'
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface-selftest-alignment.py --self-test",\n'
    '    "run: python3 scripts/zigux/check-phase2-cross-validate-shared-surface-selftest-alignment.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface.py --self-test",\n'
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface.py",\n'
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface-selftest-alignment.py --self-test",\n'
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-validate-shared-surface-selftest-alignment.py",',
    '        for path in REQUIRED_PATHS[3:]:',
    '    print("PHASE2_CROSS_VALIDATE_SHARED_SURFACE=pass")',
    '    print("PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELF_TEST=pass")',
)

REQUIRED_CASE_MARKERS = (
    '        write_text(resolve_path(root, VALIDATE), "CHECKS = ()\\n")',
    '            + "\\n".join(REQUIRED_VALIDATE_MARKERS + (REQUIRED_VALIDATE_MARKERS[0],))',
    '            + "\\n".join(REQUIRED_WORKFLOW_LINES + (REQUIRED_WORKFLOW_LINES[0],))',
    '            + "\\n".join(f"\\t{line}" for line in REQUIRED_MAKEFILE_LINES + (REQUIRED_MAKEFILE_LINES[0],))',
    '        resolve_path(root, VALIDATE).unlink()',
    '        resolve_path(root, WORKFLOW).unlink()',
    '        resolve_path(root, MAKEFILE).unlink()',
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


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELFTEST_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, CHECKER), "\n".join((*REQUIRED_SOURCE_MARKERS, *REQUIRED_CASE_MARKERS, "")))


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_validate_shared_surface_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in REQUIRED_SOURCE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, CHECKER)
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_SOURCE_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_CASE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, CHECKER)
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_CASE_MARKER", marker) in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        path = resolve_path(root, CHECKER)
        path.write_text(path.read_text(encoding="utf-8") + REQUIRED_SOURCE_MARKERS[0] + "\n", encoding="utf-8")
        assert ("DUPLICATE_SOURCE_MARKER", f"{REQUIRED_SOURCE_MARKERS[0]}:count=2") in collect_issues(root)
        checks += 1

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

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELFTEST_ALIGNMENT=pass")
    print(f"PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELFTEST_ALIGNMENT_SOURCE_MARKER_COUNT={len(REQUIRED_SOURCE_MARKERS)}")
    print(f"PHASE2_CROSS_VALIDATE_SHARED_SURFACE_SELFTEST_ALIGNMENT_CASE_MARKER_COUNT={len(REQUIRED_CASE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

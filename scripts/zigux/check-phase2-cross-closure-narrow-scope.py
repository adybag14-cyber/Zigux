#!/usr/bin/env python3
"""Keep the Lane 21 checker-only closure restack narrow and truthful."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TARGET = ROOT / "scripts" / "zigux" / "check-phase2-cross-closure-packet.py"

REQUIRED_MARKERS = (
    'CHECKER_PATH = "scripts/zigux/check-phase2-cross-closure-packet.py"',
    'DIRECT_CHECKER_PATH = "scripts/zigux/check-phase2-cross.py"',
    'ALIGNMENT_CHECKER_PATH = "scripts/zigux/check-phase2-cross-selftest-alignment.py"',
    'EXPECTED_SELF_TEST_CASE_COUNT = 9',
    'print(f"PHASE2_CROSS_CLOSURE_MARKER_COUNT={len(CLOSURE_MARKERS)}")',
    'print("PHASE2_CROSS_CLOSURE_MANIFEST_KEYS=checkers,cross_route_support,make_wrappers,validators")',
)

DISALLOWED_MARKERS = (
    'MAKEFILE = ROOT / "zigux" / "Makefile"',
    "MAKEFILE_LINES = (",
    "collect_exact_line_issues(",
    'Path(CHECKER_PATH).name',
    'print(f"PHASE2_CROSS_CLOSURE_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")',
    '"MISSING_MAKEFILE_LINE"',
    '"DUPLICATE_MAKEFILE_LINE"',
)

EXPECTED_SELF_TEST_CASE_COUNT = 5


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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    source = read_text(resolve_path(root, TARGET))
    issues: list[tuple[str, str]] = []

    for marker in REQUIRED_MARKERS:
        if marker not in source:
            issues.append(("MISSING_REQUIRED_MARKER", marker))

    for marker in DISALLOWED_MARKERS:
        if marker in source:
            issues.append(("UNEXPECTED_WIDE_SCOPE_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_CLOSURE_NARROW_SCOPE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    payload = "\n".join((*REQUIRED_MARKERS, "")) + "\n"
    write_text(resolve_path(root, TARGET), payload)


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_closure_narrow_scope_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TARGET)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), REQUIRED_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_REQUIRED_MARKER", REQUIRED_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TARGET)
        path.write_text(path.read_text(encoding="utf-8") + DISALLOWED_MARKERS[0] + "\n", encoding="utf-8")
        assert ("UNEXPECTED_WIDE_SCOPE_MARKER", DISALLOWED_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TARGET)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), "EXPECTED_SELF_TEST_CASE_COUNT = 9", "EXPECTED_SELF_TEST_CASE_COUNT = 11"),
            encoding="utf-8",
        )
        assert ("MISSING_REQUIRED_MARKER", "EXPECTED_SELF_TEST_CASE_COUNT = 9") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, TARGET).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing target did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_CLOSURE_NARROW_SCOPE_SELF_TEST=pass")
    print(f"PHASE2_CROSS_CLOSURE_NARROW_SCOPE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 21 checker-only closure restack stays narrow and does not re-claim the Makefile hook-up."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_CLOSURE_NARROW_SCOPE=pass")
    print(f"PHASE2_CROSS_CLOSURE_NARROW_SCOPE_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE2_CROSS_CLOSURE_NARROW_SCOPE_DISALLOWED_MARKER_COUNT={len(DISALLOWED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

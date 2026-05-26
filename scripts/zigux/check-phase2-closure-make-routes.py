#!/usr/bin/env python3
"""Guard the exact Phase 2 shared make-route packet in the closure note."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
CLOSURE_NOTE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
MAKEFILE = ROOT / "zigux" / "Makefile"

ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
    "phase2",
)
ROUTE_MARKERS = tuple(f"- `make -C zigux {route}`" for route in ROUTES)
SHARED_ROUTES_MARKER = "- `PHASE2_SHARED_MAKE_ROUTES=" + ",".join(
    f"make -C zigux {route}" for route in ROUTES
) + "`"
REQUIRED_NOTE_MARKERS = (
    "## Closure Validation",
    *ROUTE_MARKERS,
    SHARED_ROUTES_MARKER,
)
EXACT_COUNT_MARKERS = (*ROUTE_MARKERS, SHARED_ROUTES_MARKER)
PHONY_LINE = ".PHONY: " + " ".join(ROUTES)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def phony_targets(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith(".PHONY:"):
            continue
        _, suffix = stripped.split(":", 1)
        targets.update(token for token in suffix.strip().split() if token)
    return targets


def count_target_definitions(text: str, route: str) -> int:
    target_line = f"{route}:"
    return sum(1 for line in text.splitlines() if line.strip() == target_line)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    note_text = read_text(root / CLOSURE_NOTE.relative_to(ROOT))
    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_NOTE_MARKER", marker))
    for marker in EXACT_COUNT_MARKERS:
        count = count_exact_lines(note_text, marker)
        if count != 1:
            issues.append(("NOTE_EXACT_COUNT_MISMATCH", f"{count}::{marker}"))

    makefile_text = read_text(root / MAKEFILE.relative_to(ROOT))
    if not set(ROUTES).issubset(phony_targets(makefile_text)):
        issues.append(("MISSING_MAKEFILE_PHONY", PHONY_LINE))
    for route in ROUTES:
        target_line = f"{route}:"
        count = count_target_definitions(makefile_text, route)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_TARGET", target_line))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_TARGET", f"{count}::{target_line}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CLOSURE_MAKE_ROUTES=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(root / CLOSURE_NOTE.relative_to(ROOT), "\n".join(REQUIRED_NOTE_MARKERS) + "\n")
    write_text(
        root / MAKEFILE.relative_to(ROOT),
        "\n".join(
            [
                PHONY_LINE,
                *[f"{route}:" for route in ROUTES],
            ]
        )
        + "\n",
    )


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


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


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(REQUIRED_NOTE_MARKERS) + len(EXACT_COUNT_MARKERS) + 1 + len(ROUTES) + len(ROUTES)

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_make_routes_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        note_path = root / CLOSURE_NOTE.relative_to(ROOT)
        note_text = read_text(note_path)
        for marker in REQUIRED_NOTE_MARKERS:
            write_text(note_path, replace_once(note_text, marker))
            issues = collect_issues(root)
            assert ("MISSING_NOTE_MARKER", marker) in issues
            build_sample_root(root)
            note_text = read_text(note_path)
            checks_run += 1

        for marker in EXACT_COUNT_MARKERS:
            write_text(note_path, duplicate_exact_line(note_text, marker))
            issues = collect_issues(root)
            assert ("NOTE_EXACT_COUNT_MISMATCH", f"2::{marker}") in issues
            build_sample_root(root)
            note_text = read_text(note_path)
            checks_run += 1

        makefile_path = root / MAKEFILE.relative_to(ROOT)
        makefile_text = read_text(makefile_path)
        write_text(
            makefile_path,
            replace_exact_line(makefile_text, PHONY_LINE, ".PHONY: phase2-toolchain phase2-tools"),
        )
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_PHONY", PHONY_LINE) in issues
        build_sample_root(root)
        checks_run += 1

        makefile_text = read_text(makefile_path)
        for route in ROUTES:
            target_line = f"{route}:"
            write_text(makefile_path, replace_exact_line(makefile_text, target_line))
            issues = collect_issues(root)
            assert ("MISSING_MAKEFILE_TARGET", target_line) in issues
            build_sample_root(root)
            makefile_text = read_text(makefile_path)
            checks_run += 1

        for route in ROUTES:
            target_line = f"{route}:"
            write_text(makefile_path, duplicate_exact_line(makefile_text, target_line))
            issues = collect_issues(root)
            assert ("DUPLICATE_MAKEFILE_TARGET", f"2::{target_line}") in issues
            build_sample_root(root)
            makefile_text = read_text(makefile_path)
            checks_run += 1

        assert checks_run == expected_case_count

    print("PHASE2_CLOSURE_MAKE_ROUTES_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_MAKE_ROUTES_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run built-in regression checks.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root and exit.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_CLOSURE_MAKE_ROUTES_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_MAKE_ROUTES=pass")
    print(f"PHASE2_CLOSURE_MAKE_ROUTE_COUNT={len(ROUTES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

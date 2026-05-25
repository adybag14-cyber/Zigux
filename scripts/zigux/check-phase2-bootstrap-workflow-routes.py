#!/usr/bin/env python3
"""Guard the live Phase 2 bootstrap workflow-route packet against reminder drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"

REQUIRED_FILES = (
    BOOTSTRAP_NOTES,
    WORKFLOW,
    MAKEFILE,
)

NOTE_MARKERS = (
    "`.github/workflows/zigux-bootstrap.yml` now runs",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
)

NOTE_FORBIDDEN_MARKERS = (
    "`make -C zigux phase2-toolchain`, `make -C zigux phase2-cross`, `make -C zigux phase2-fixdep`, and `make -C zigux phase2-validate`, so the live bootstrap packet exercises",
)

WORKFLOW_LINES = (
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
)

MAKEFILE_LINES = (
    ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase2-fixdep:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
)


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_missing_paths(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for path in REQUIRED_FILES:
        resolved = resolve_path(root, path)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_FILE", str(path.relative_to(ROOT))))
    return issues


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_exact_line_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues = collect_missing_paths(root)
    if issues:
        return issues

    notes_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    issues.extend(collect_missing_markers(notes_text, NOTE_MARKERS, "MISSING_NOTE_MARKER"))
    issues.extend(collect_forbidden_markers(notes_text, NOTE_FORBIDDEN_MARKERS, "FORBIDDEN_NOTE_MARKER"))
    issues.extend(collect_exact_line_issues(workflow_text, WORKFLOW_LINES, "MISSING_WORKFLOW_LINE", "DUPLICATE_WORKFLOW_LINE"))
    issues.extend(collect_exact_line_issues(makefile_text, MAKEFILE_LINES, "MISSING_MAKEFILE_LINE", "DUPLICATE_MAKEFILE_LINE"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_BOOTSTRAP_WORKFLOW_ROUTES=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        resolve_path(root, BOOTSTRAP_NOTES),
        "\n".join(
            (
                "# Phase 2 Toolchain Bootstrap Notes",
                "",
                "## Current direct packet",
                "",
                "- `.github/workflows/zigux-bootstrap.yml` now runs `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, and `make -C zigux phase2-validate` so the live bootstrap packet keeps the current make-route slice explicit.",
                "",
            )
        )
        + "\n",
    )
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(
        resolve_path(root, MAKEFILE),
        "\n".join(
            (
                ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
                "",
                "phase2-toolchain:",
                "\t@true",
                "",
                "phase2-tools:",
                "\t@true",
                "",
                "phase2-kconfig:",
                "\t@true",
                "",
                "phase2-cross:",
                "\t@true",
                "",
                "phase2-genksyms:",
                "\t@true",
                "",
                "phase2-fixdep:",
                "\t@true",
                "",
                "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
                "\t@true",
                "",
                "phase2: phase2-validate",
                "\t@true",
            )
        )
        + "\n",
    )


def remove_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


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


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(NOTE_MARKERS)
        + len(WORKFLOW_LINES)
        + len(WORKFLOW_LINES)
        + len(MAKEFILE_LINES)
        + len(MAKEFILE_LINES)
        + len(NOTE_FORBIDDEN_MARKERS)
        + len(REQUIRED_FILES)
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_workflow_routes_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in NOTE_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            write_text(path, remove_once(read_text(path), marker))
            assert ("MISSING_NOTE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            path = resolve_path(root, WORKFLOW)
            write_text(path, replace_exact_line(read_text(path), marker, "run: python3 scripts/zigux/other.py"))
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            path = resolve_path(root, WORKFLOW)
            write_text(path, duplicate_exact_line(read_text(path), marker))
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            write_text(path, replace_exact_line(read_text(path), marker, "phase2-broken:"))
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            write_text(path, duplicate_exact_line(read_text(path), marker))
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in NOTE_FORBIDDEN_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            write_text(path, read_text(path) + marker + "\n")
            assert ("FORBIDDEN_NOTE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for rel_path in REQUIRED_FILES:
            build_sample_root(root)
            resolve_path(root, rel_path).unlink()
            issues = collect_issues(root)
            assert ("MISSING_REQUIRED_FILE", str(rel_path.relative_to(ROOT))) in issues
            checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def write_sample_root(root: Path) -> int:
    build_sample_root(root)
    print(f"PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SAMPLE_ROOT={root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in self-test suite.")
    parser.add_argument("--write-sample-root", type=Path, help="Write a synthetic passing root for local validation.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_WORKFLOW_ROUTES=pass")
    print(f"PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

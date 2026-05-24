#!/usr/bin/env python3
"""Guard the rematerialized Phase 2 bootstrap kconfig route packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "run: make -C zigux phase2-kconfig",
)

MAKEFILE_LINES = (
    "phase2-kconfig:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
)

SURFACE_MARKERS = (
    ("PHASE2_CLOSURE", PHASE2_CLOSURE, "`make -C zigux phase2-kconfig`"),
    ("BOOTSTRAP_NOTES", BOOTSTRAP_NOTES, "`make -C zigux phase2-kconfig`"),
    ("REVIEW_CHECKLIST", REVIEW_CHECKLIST, "`make -C zigux phase2-kconfig`"),
    ("TESTS_README", TESTS_README, "Keep the current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`"),
    ("SCRIPTS_README", SCRIPTS_README, "`make -C zigux phase2-kconfig`"),
)

HELPER_MARKERS = (
    ("PHASE2_CLOSURE", PHASE2_CLOSURE, "`scripts/zigux/check-kconfig-bridge.py`"),
    ("PHASE2_CLOSURE", PHASE2_CLOSURE, "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`"),
    ("BOOTSTRAP_NOTES", BOOTSTRAP_NOTES, "`scripts/zigux/check-kconfig-bridge.py`"),
    ("BOOTSTRAP_NOTES", BOOTSTRAP_NOTES, "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`"),
    ("REVIEW_CHECKLIST", REVIEW_CHECKLIST, "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`"),
    ("REVIEW_CHECKLIST", REVIEW_CHECKLIST, "`make -C zigux phase2-kconfig`"),
    ("TESTS_README", TESTS_README, "`scripts/zigux/check-kconfig-bridge.py`"),
    ("TESTS_README", TESTS_README, "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`"),
    ("SCRIPTS_README", SCRIPTS_README, "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`"),
)

EXPECTED_SELF_TEST_CASE_COUNT = 1 + len(WORKFLOW_LINES) + len(WORKFLOW_LINES) + len(MAKEFILE_LINES) + len(MAKEFILE_LINES) + len(SURFACE_MARKERS) + len(HELPER_MARKERS)


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


def collect_line_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    workflow_text = read_text(root / WORKFLOW)
    makefile_text = read_text(root / MAKEFILE)

    issues.extend(collect_line_issues(workflow_text, WORKFLOW_LINES, "MISSING_WORKFLOW_LINES", "DUPLICATE_WORKFLOW_LINES"))
    issues.extend(collect_line_issues(makefile_text, MAKEFILE_LINES, "MISSING_MAKEFILE_LINES", "DUPLICATE_MAKEFILE_LINES"))

    for code_prefix, path, marker in SURFACE_MARKERS + HELPER_MARKERS:
        text = read_text(root / path)
        if marker not in text:
            issues.append((f"MISSING_{code_prefix}_MARKERS", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_KCONFIG_ROUTE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(root / WORKFLOW, "\n".join(("name: zigux-bootstrap", *WORKFLOW_LINES)) + "\n")
    write_text(root / MAKEFILE, "\n".join(("ZIGUX_ROOT := ..", "PHASE2_SCRIPT_ROOT := ../scripts/zigux", "PYTHON ?= python3", "ZIG ?= zig", *MAKEFILE_LINES)) + "\n")
    write_text(root / PHASE2_CLOSURE, "\n".join(("phase2", "`scripts/zigux/check-kconfig-bridge.py`", "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`", "`make -C zigux phase2-kconfig`")) + "\n")
    write_text(root / BOOTSTRAP_NOTES, "\n".join(("notes", "`scripts/zigux/check-kconfig-bridge.py`", "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`", "`make -C zigux phase2-kconfig`")) + "\n")
    write_text(root / REVIEW_CHECKLIST, "\n".join(("checklist", "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`", "`make -C zigux phase2-kconfig`")) + "\n")
    write_text(root / TESTS_README, "\n".join(("tests", "`scripts/zigux/check-kconfig-bridge.py`", "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`", "Keep the current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`")) + "\n")
    write_text(root / SCRIPTS_README, "\n".join(("scripts", "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`", "`make -C zigux phase2-kconfig`")) + "\n")


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
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_kconfig_route_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = root / WORKFLOW
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINES", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = root / WORKFLOW
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_LINES", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = root / MAKEFILE
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINES", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = root / MAKEFILE
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_LINES", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for code_prefix, path, marker in SURFACE_MARKERS + HELPER_MARKERS:
            build_self_test_root(root)
            resolved = root / path
            resolved.write_text(resolved.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert (f"MISSING_{code_prefix}_MARKERS", marker) in collect_issues(root)
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT, (checks_run, EXPECTED_SELF_TEST_CASE_COUNT)
    print("PHASE2_BOOTSTRAP_KCONFIG_ROUTE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_KCONFIG_ROUTE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_KCONFIG_ROUTE_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_KCONFIG_ROUTE_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_BOOTSTRAP_KCONFIG_ROUTE_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
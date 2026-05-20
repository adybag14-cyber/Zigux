#!/usr/bin/env python3
"""Guard the live bootstrap fixdep packet against workflow and companion drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"

SURFACE_PATHS = (
    ROOT / "scripts" / "zigux" / "check-phase2-fixdep-gate.py",
    ROOT / "scripts" / "zigux" / "check-fixdep-diff.py",
    ROOT / "scripts" / "zigux" / "fixdep.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "cases.json",
    WORKFLOW,
    SCRIPTS_README,
    PHASE2_CLOSURE,
    TESTS_README,
    MAKEFILE,
)

WORKFLOW_PACKET_LINES = (
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py --self-test",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
)

PHASE2_CLOSURE_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
    "- `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`",
    "- `python3 scripts/zigux/check-phase2-fixdep-gate.py`",
    "- `python3 scripts/zigux/check-fixdep-diff.py --self-test`",
    "- `python3 scripts/zigux/check-fixdep-diff.py`",
)

TESTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
)

MAKEFILE_LINES = (
    "phase2-fixdep:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(SURFACE_PATHS)
    + len(WORKFLOW_PACKET_LINES)
    + len(WORKFLOW_PACKET_LINES)
    + 1
    + len(SCRIPTS_README_MARKERS)
    + len(PHASE2_CLOSURE_MARKERS)
    + len(TESTS_README_MARKERS)
    + len(MAKEFILE_LINES)
    + len(MAKEFILE_LINES)
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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_line_issues(
    text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_workflow_order_issues(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    positions: list[int] = []
    lines = [line.strip() for line in text.splitlines()]
    for marker in WORKFLOW_PACKET_LINES:
        for index, line in enumerate(lines):
            if line == marker:
                positions.append(index)
                break
    if len(positions) != len(WORKFLOW_PACKET_LINES):
        return issues
    if positions != sorted(positions):
        issues.append(
            (
                "MISORDERED_WORKFLOW_PACKET",
                " -> ".join(WORKFLOW_PACKET_LINES),
            )
        )
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in SURFACE_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()))

    if issues:
        return issues

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    scripts_readme_text = read_text(resolve_path(root, SCRIPTS_README))
    phase2_closure_text = read_text(resolve_path(root, PHASE2_CLOSURE))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    makefile_text = read_text(resolve_path(root, MAKEFILE))

    issues.extend(
        collect_exact_line_issues(
            workflow_text,
            WORKFLOW_PACKET_LINES,
            "MISSING_WORKFLOW_PACKET_LINE",
            "DUPLICATE_WORKFLOW_PACKET_LINE",
        )
    )
    issues.extend(collect_workflow_order_issues(workflow_text))
    issues.extend(
        collect_missing_markers(
            scripts_readme_text, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKER"
        )
    )
    issues.extend(
        collect_missing_markers(
            phase2_closure_text, PHASE2_CLOSURE_MARKERS, "MISSING_PHASE2_CLOSURE_MARKER"
        )
    )
    issues.extend(
        collect_missing_markers(
            tests_readme_text, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKER"
        )
    )
    issues.extend(
        collect_exact_line_issues(
            makefile_text,
            MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINE",
            "DUPLICATE_MAKEFILE_LINE",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_FIXDEP_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


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
    workflow_lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
    ]
    for index, marker in enumerate(WORKFLOW_PACKET_LINES, start=1):
        workflow_lines.append(f"      - name: packet-step-{index}")
        workflow_lines.append(f"        {marker}")
    write_text(resolve_path(root, WORKFLOW), "\n".join(workflow_lines) + "\n")
    write_text(
        resolve_path(root, SCRIPTS_README),
        "\n".join(("# scripts/zigux", "", *SCRIPTS_README_MARKERS)) + "\n",
    )
    write_text(
        resolve_path(root, PHASE2_CLOSURE),
        "\n".join(("# Phase 2 Closure", "", *PHASE2_CLOSURE_MARKERS)) + "\n",
    )
    write_text(
        resolve_path(root, TESTS_README),
        "\n".join(("# zigux/tests", "", *TESTS_README_MARKERS)) + "\n",
    )
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    for path in SURFACE_PATHS:
        if path in (WORKFLOW, SCRIPTS_README, PHASE2_CLOSURE, TESTS_README, MAKEFILE):
            continue
        write_text(resolve_path(root, path), "present\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_fixdep_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for path in SURFACE_PATHS:
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            issues = collect_issues(root)
            assert ("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()) in issues
            checks_run += 1

        for marker in WORKFLOW_PACKET_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_PACKET_LINE", marker) in issues
            checks_run += 1

        for marker in WORKFLOW_PACKET_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("DUPLICATE_WORKFLOW_PACKET_LINE", f"{marker}:count=2") in issues
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, WORKFLOW)
        text = path.read_text(encoding="utf-8")
        before = WORKFLOW_PACKET_LINES[1]
        after = WORKFLOW_PACKET_LINES[5]
        text = replace_exact_line(text, before, "__TEMP_SWAP__")
        text = replace_exact_line(text, after, before)
        text = replace_exact_line(text, "__TEMP_SWAP__", after)
        path.write_text(text, encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "MISORDERED_WORKFLOW_PACKET" for code, _ in issues)
        checks_run += 1

        for marker in SCRIPTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_SCRIPTS_README_MARKER", marker) in issues
            checks_run += 1

        for marker in PHASE2_CLOSURE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_CLOSURE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_PHASE2_CLOSURE_MARKER", marker) in issues
            checks_run += 1

        for marker in TESTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKER", marker) in issues
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_MAKEFILE_LINE", marker) in issues
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in issues
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT, (checks_run, EXPECTED_SELF_TEST_CASE_COUNT)
    print("PHASE2_BOOTSTRAP_FIXDEP_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_FIXDEP_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the live bootstrap fixdep packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_FIXDEP_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_FIXDEP_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_PACKET_LINES)}")
    print(f"PHASE2_BOOTSTRAP_FIXDEP_PACKET_SURFACE_COUNT={len(SURFACE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

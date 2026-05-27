#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
BOOTSTRAP_NOTES = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = "Documentation/zigux/review-checklist.md"
SCRIPTS_README = "scripts/zigux/README.md"
TESTS_README = "zigux/tests/README.md"
TOOL_MANIFEST = "zigux/tests/fixtures/phase2_tool_manifest.json"

REQUIRED_PATHS = (
    WORKFLOW,
    MAKEFILE,
    BOOTSTRAP_NOTES,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    TESTS_README,
    TOOL_MANIFEST,
)

REQUIRED_WORKFLOW_LINES = (
    "run: make -C zigux phase2-tools",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
)

REQUIRED_MARKERS = {
    BOOTSTRAP_NOTES: (
        "`phase2-tools`",
        "`scripts/zigux/check-phase2-kbuild-routes.py`",
        "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
        "`scripts/zigux/check-phase2-required-make-routes.py`",
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`make -C zigux phase2-tools`",
    ),
    REVIEW_CHECKLIST: (
        "`scripts/zigux/check-phase2-kbuild-routes.py`",
        "`scripts/zigux/check-phase2-required-make-routes.py`",
        "`make -C zigux phase2-tools`",
    ),
    SCRIPTS_README: (
        "`scripts/zigux/check-phase2-kbuild-routes.py`",
        "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
        "`scripts/zigux/check-phase2-required-make-routes.py`",
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`make -C zigux phase2-tools`",
    ),
    TESTS_README: (
        "`scripts/zigux/check-phase2-kbuild-routes.py`",
        "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
        "`scripts/zigux/check-phase2-required-make-routes.py`",
        "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
        "`make -C zigux phase2-tools`",
    ),
    TOOL_MANIFEST: (
        "\"scripts/zigux/check-phase2-kbuild-routes.py\"",
        "\"scripts/zigux/check-phase2-docs-shared-reminder.py\"",
        "\"scripts/zigux/check-phase2-required-make-routes.py\"",
        "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"",
        "\"make -C zigux phase2-tools\"",
    ),
}


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


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


def replace_marker(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(root, WORKFLOW)
    makefile_text = read_text(root, MAKEFILE)

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    for rel, markers in REQUIRED_MARKERS.items():
        if not (root / rel).exists():
            continue
        text = read_text(root, rel)
        for marker in markers:
            count = text.count(marker)
            if count == 0:
                issues.append(("MISSING_SURFACE_MARKER", f"{rel}::{marker}"))
            elif count != 1:
                issues.append(("DUPLICATE_SURFACE_MARKER", f"{rel}::{marker}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOLS_ACTION_PATH=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Replay phase2-tools wrapper",
                "        run: make -C zigux phase2-tools",
            )
        )
        + "\n",
    )
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
                "PYTHON ?= python3",
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "",
                *REQUIRED_MAKEFILE_LINES,
            )
        )
        + "\n",
    )
    write_text(
        root,
        BOOTSTRAP_NOTES,
        "\n".join(
            (
                "# Phase 2 Toolchain Bootstrap Notes",
                "",
                "- `phase2-tools` stays explicit beside the returned wrapper packet.",
                "- `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-required-make-routes.py`, and `scripts/zigux/check-phase2-artifact-tools-manifest.py` remain the current tools-route companions.",
                "- `make -C zigux phase2-tools` keeps the shipped wrapper route explicit.",
            )
        )
        + "\n",
    )
    write_text(
        root,
        REVIEW_CHECKLIST,
        "\n".join(
            (
                "# Zigux Review Checklist",
                "",
                "- keep `scripts/zigux/check-phase2-kbuild-routes.py` and `scripts/zigux/check-phase2-required-make-routes.py` aligned with `make -C zigux phase2-tools`.",
            )
        )
        + "\n",
    )
    write_text(
        root,
        SCRIPTS_README,
        "\n".join(
            (
                "# scripts/zigux",
                "",
                "- `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-required-make-routes.py`, and `scripts/zigux/check-phase2-artifact-tools-manifest.py` stay explicit beside `make -C zigux phase2-tools`.",
            )
        )
        + "\n",
    )
    write_text(
        root,
        TESTS_README,
        "\n".join(
            (
                "# zigux/tests",
                "",
                "- `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, and `make -C zigux phase2-tools` keep the current tests-root reminder packet explicit.",
            )
        )
        + "\n",
    )
    write_text(
        root,
        TOOL_MANIFEST,
        "\n".join(
            (
                "{",
                '  "present_surfaces": {',
                '    "checkers": [',
                '      "scripts/zigux/check-phase2-kbuild-routes.py",',
                '      "scripts/zigux/check-phase2-docs-shared-reminder.py",',
                '      "scripts/zigux/check-phase2-required-make-routes.py",',
                '      "scripts/zigux/check-phase2-artifact-tools-manifest.py"',
                "    ],",
                '    "make_wrappers": ["make -C zigux phase2-tools"]',
                "  }",
                "}",
            )
        )
        + "\n",
    )


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(REQUIRED_WORKFLOW_LINES)
        + len(REQUIRED_WORKFLOW_LINES)
        + len(REQUIRED_MAKEFILE_LINES)
        + len(REQUIRED_MAKEFILE_LINES)
        + sum(len(markers) for markers in REQUIRED_MARKERS.values())
        + (len(REQUIRED_PATHS) - 2)
        + 2
    )
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tools_action_path_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_sample_root(root)
            write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), marker, "run: make -C zigux phase2-other"))
            expect_issue(root, ("MISSING_WORKFLOW_LINE", marker))
            checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_sample_root(root)
            write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), marker))
            expect_issue(root, ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2"))
            checks += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_sample_root(root)
            write_text(root, MAKEFILE, replace_exact_line(read_text(root, MAKEFILE), marker, "# removed"))
            expect_issue(root, ("MISSING_MAKEFILE_LINE", marker))
            checks += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_sample_root(root)
            write_text(root, MAKEFILE, duplicate_exact_line(read_text(root, MAKEFILE), marker))
            expect_issue(root, ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2"))
            checks += 1

        for rel, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                build_sample_root(root)
                write_text(root, rel, replace_marker(read_text(root, rel), marker, "marker drift"))
                expect_issue(root, ("MISSING_SURFACE_MARKER", f"{rel}::{marker}"))
                checks += 1

        for rel in REQUIRED_PATHS:
            if rel in {WORKFLOW, MAKEFILE}:
                continue
            build_sample_root(root)
            (root / rel).unlink()
            expect_issue(root, ("MISSING_REQUIRED_PATH", rel))
            checks += 1

        for rel in (WORKFLOW, MAKEFILE):
            build_sample_root(root)
            (root / rel).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel}")

    assert checks == expected_case_count
    print("PHASE2_TOOLS_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_TOOLS_ACTION_PATH_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Lane 18 phase2-tools action-path packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for the phase2-tools action-path packet",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLS_ACTION_PATH=pass")
    print(f"PHASE2_TOOLS_ACTION_PATH_REQUIRED_FILE_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_TOOLS_ACTION_PATH_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_TOOLS_ACTION_PATH_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(
        "PHASE2_TOOLS_ACTION_PATH_MARKER_COUNT="
        + str(sum(len(markers) for markers in REQUIRED_MARKERS.values()))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

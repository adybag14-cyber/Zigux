#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PHASE2_CLOSURE = "Documentation/zigux/phase2-closure.md"
SCRIPTS_README = "scripts/zigux/README.md"
TESTS_README = "zigux/tests/README.md"
MAKEFILE = "zigux/Makefile"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_PATHS = (
    PHASE2_CLOSURE,
    SCRIPTS_README,
    TESTS_README,
    MAKEFILE,
    WORKFLOW,
)

CHECKER_MARKERS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-toolchain-policy-route-alignment.py",
    "scripts/zigux/check-phase2-bootstrap-route-cluster.py",
    "scripts/zigux/check-phase2-pinned-archive-packet.py",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-cross",
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
)


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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    phase2_closure = read_text(root, PHASE2_CLOSURE)
    scripts_readme = read_text(root, SCRIPTS_README)
    tests_readme = read_text(root, TESTS_README)
    makefile = read_text(root, MAKEFILE)
    workflow = read_text(root, WORKFLOW)

    for marker in CHECKER_MARKERS:
        if marker not in phase2_closure:
            issues.append(("MISSING_PHASE2_CLOSURE_MARKER", marker))
        if marker not in scripts_readme:
            issues.append(("MISSING_SCRIPTS_README_MARKER", marker))
        if marker not in tests_readme:
            issues.append(("MISSING_TESTS_README_MARKER", marker))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOLCHAIN_CHECKER_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    closure_list = "\n".join(f"- `{marker}`" for marker in CHECKER_MARKERS)
    readme_list = "\n".join(f"- `{marker}`" for marker in CHECKER_MARKERS)

    write_text(
        root,
        PHASE2_CLOSURE,
        "\n".join(
            (
                "# Phase 2 Closure",
                "",
                "This note keeps the shared Lane 03 toolchain-checker packet visible.",
                "",
                "## Current Closure Packet",
                "",
                closure_list,
                "",
                "## Closure Validation",
                "",
                "- `python3 scripts/zigux/check-zig-toolchain.py --self-test`",
                "- `python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
                "- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
                "- `make -C zigux phase2-toolchain`",
                "- `make -C zigux phase2-tools`",
                "- `make -C zigux phase2-cross`",
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
                "This directory holds shipped Zigux validation helpers and compact reminder surfaces.",
                "",
                "## Phase 2",
                "",
                readme_list,
                "",
                "- `python3 scripts/zigux/check-zig-toolchain.py --self-test`",
                "- `python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
                "- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
                "- `make -C zigux phase2-toolchain`",
                "- `make -C zigux phase2-tools`",
                "- `make -C zigux phase2-cross`",
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
                "## Phase 2 review packet",
                "",
                readme_list,
                "",
                "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`.",
                "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, and `make -C zigux phase2-cross`.",
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
                ".PHONY: phase2-toolchain phase2-tools phase2-cross",
                "",
                "phase2-toolchain:",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
                "",
                "phase2-tools:",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
                "",
                "phase2-cross:",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
            )
        )
        + "\n",
    )
    write_text(root, WORKFLOW, "\n".join(("name: zigux-bootstrap", *WORKFLOW_LINES)) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_toolchain_checker_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            PHASE2_CLOSURE,
            read_text(root, PHASE2_CLOSURE).replace(CHECKER_MARKERS[-1], "scripts/zigux/other-checker.py", 1),
        )
        assert ("MISSING_PHASE2_CLOSURE_MARKER", CHECKER_MARKERS[-1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            SCRIPTS_README,
            read_text(root, SCRIPTS_README).replace(CHECKER_MARKERS[-2], "scripts/zigux/other-checker.py", 1),
        )
        assert ("MISSING_SCRIPTS_README_MARKER", CHECKER_MARKERS[-2]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            TESTS_README,
            read_text(root, TESTS_README).replace(CHECKER_MARKERS[-3], "scripts/zigux/other-checker.py", 1),
        )
        assert ("MISSING_TESTS_README_MARKER", CHECKER_MARKERS[-3]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                WORKFLOW_LINES[-1],
                "run: make -C zigux phase2-genksyms",
            ),
        )
        assert ("MISSING_WORKFLOW_LINE", WORKFLOW_LINES[-1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), WORKFLOW_LINES[0]))
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_LINES[0]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE,
            replace_exact_line(
                read_text(root, MAKEFILE),
                MAKEFILE_LINES[-1],
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
            ),
        )
        assert ("MISSING_MAKEFILE_LINE", MAKEFILE_LINES[-1]) in collect_issues(root)
        checks += 1

    print("PHASE2_TOOLCHAIN_CHECKER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_CHECKER_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def write_sample_root(root: Path) -> None:
    build_sample_root(root)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 2 Lane 03 toolchain-checker packet stays aligned across reminder surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="write a current-like sample root for validation")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_CHECKER_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_CHECKER_COUNT={len(CHECKER_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_CHECKER_SURFACE_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

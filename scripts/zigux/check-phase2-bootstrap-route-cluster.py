#!/usr/bin/env python3
"""Guard the current Phase 2 bootstrap route cluster packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"

SELFTEST_LINE = "run: python3 scripts/zigux/check-phase2-bootstrap-route-cluster.py --self-test"
CHECK_LINE = "run: python3 scripts/zigux/check-phase2-bootstrap-route-cluster.py"

WORKFLOW_PACKET_LINES = (
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

ROUTE_MARKERS = (
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

CHECKER_MARKERS = (
    "`scripts/zigux/check-phase2-bootstrap-route-cluster.py`",
    "`python3 scripts/zigux/check-phase2-bootstrap-route-cluster.py --self-test`",
    "`python3 scripts/zigux/check-phase2-bootstrap-route-cluster.py`",
)

MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase2-fixdep:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

SURFACES = (
    (PHASE2_NOTES, "MISSING_PHASE2_NOTES_MARKERS", "MISSING_PHASE2_NOTES_ROUTE_MARKERS"),
    (PHASE2_CLOSURE, "MISSING_PHASE2_CLOSURE_MARKERS", "MISSING_PHASE2_CLOSURE_ROUTE_MARKERS"),
    (REVIEW_CHECKLIST, "MISSING_REVIEW_CHECKLIST_MARKERS", "MISSING_REVIEW_CHECKLIST_ROUTE_MARKERS"),
    (SCRIPTS_README, "MISSING_SCRIPTS_README_MARKERS", "MISSING_SCRIPTS_README_ROUTE_MARKERS"),
    (TESTS_README, "MISSING_TESTS_README_MARKERS", "MISSING_TESTS_README_ROUTE_MARKERS"),
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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    for marker in (SELFTEST_LINE, CHECK_LINE):
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINES", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINES", f"{marker}:count={count}"))
    for marker in WORKFLOW_PACKET_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_PACKET_LINES", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_PACKET_LINES", f"{marker}:count={count}"))

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    for marker in MAKEFILE_MARKERS:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_MARKERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_MARKERS", f"{marker}:count={count}"))

    for path, checker_code, route_code in SURFACES:
        text = read_text(resolve_path(root, path))
        for marker in CHECKER_MARKERS:
            if marker not in text:
                issues.append((checker_code, marker))
        for marker in ROUTE_MARKERS:
            if marker not in text:
                issues.append((route_code, marker))

    return issues


def phase2_notes_text() -> str:
    return """# Phase 2 Toolchain Bootstrap Notes

This note keeps the current directly readable Phase 2 toolchain packet honest from the docs root.

## Current direct packet

- `scripts/zigux/check-phase2-bootstrap-route-cluster.py`, `python3 scripts/zigux/check-phase2-bootstrap-route-cluster.py --self-test`, and `python3 scripts/zigux/check-phase2-bootstrap-route-cluster.py` keep the returned workflow route cluster reviewable beside the existing toolchain, cross-route, genksyms, fixdep, and closure validator packet.
- `.github/workflows/zigux-bootstrap.yml` keeps the current make-wrapper cluster explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.
"""


def phase2_closure_text() -> str:
    return """# Phase 2 Closure

This note keeps the current Phase 2 closure-side packet aligned to the directly readable toolchain, local-first archive, installer, cross-route, kconfig-bridge, genksyms bridge, fixdep, make-wrapper, manifest-guard, and validator surfaces on current `master`.

## Current Closure Packet

- `scripts/zigux/check-phase2-bootstrap-route-cluster.py`
- `python3 scripts/zigux/check-phase2-bootstrap-route-cluster.py --self-test`
- `python3 scripts/zigux/check-phase2-bootstrap-route-cluster.py`
- `make -C zigux phase2-toolchain`
- `make -C zigux phase2-tools`
- `make -C zigux phase2-kconfig`
- `make -C zigux phase2-cross`
- `make -C zigux phase2-genksyms`
- `make -C zigux phase2-fixdep`
- `make -C zigux phase2-validate`
- `make -C zigux phase2`
"""


def review_checklist_text() -> str:
    return """# Zigux Review Checklist

Use this checklist before opening or merging Zigux product work.

## Validation

- if the change touches the shared Phase 2 bootstrap route cluster packet, do `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase2-bootstrap-route-cluster.py`, `python3 scripts/zigux/check-phase2-bootstrap-route-cluster.py --self-test`, `python3 scripts/zigux/check-phase2-bootstrap-route-cluster.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` still agree on the current returned workflow route cluster?
"""


def scripts_readme_text() -> str:
    return """# scripts/zigux

## Phase 2

- `scripts/zigux/check-phase2-bootstrap-route-cluster.py`, `python3 scripts/zigux/check-phase2-bootstrap-route-cluster.py --self-test`, and `python3 scripts/zigux/check-phase2-bootstrap-route-cluster.py` keep the current Phase 2 bootstrap route cluster explicit from the scripts root.
- `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` stay explicit as the current rematerialized make-wrapper packet.
"""


def tests_readme_text() -> str:
    return """# zigux/tests

## Phase 2 review packet

- `scripts/zigux/check-phase2-bootstrap-route-cluster.py`
- `python3 scripts/zigux/check-phase2-bootstrap-route-cluster.py --self-test`
- `python3 scripts/zigux/check-phase2-bootstrap-route-cluster.py`

Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.
"""


def makefile_text() -> str:
    return """PYTHON ?= python3
PHASE2_SCRIPT_ROOT := ../scripts/zigux
ZIGUX_ROOT := ..

.PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2

phase2-toolchain:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only

phase2-tools:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py

phase2-kconfig:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py

phase2-cross:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py

phase2-genksyms:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-genksyms-bridge.py

phase2-fixdep:
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-fixdep-gate.py

phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py

phase2: phase2-validate
"""


def workflow_text() -> str:
    lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
        "      - name: Self-test current Phase 2 bootstrap route cluster checker",
        f"        {SELFTEST_LINE}",
        "      - name: Check current Phase 2 bootstrap route cluster packet",
        f"        {CHECK_LINE}",
        "      - name: Run current Phase 2 toolchain make route",
        "        run: make -C zigux phase2-toolchain",
        "      - name: Run current Phase 2 tools make route",
        "        run: make -C zigux phase2-tools",
        "      - name: Run current Phase 2 kconfig make route",
        "        run: make -C zigux phase2-kconfig",
        "      - name: Run current Phase 2 cross make route",
        "        run: make -C zigux phase2-cross",
        "      - name: Run current Phase 2 genksyms make route",
        "        run: make -C zigux phase2-genksyms",
        "      - name: Run current Phase 2 fixdep make route",
        "        run: make -C zigux phase2-fixdep",
        "      - name: Run current Phase 2 validate make route",
        "        run: make -C zigux phase2-validate",
        "      - name: Validate current Phase 2 tool packet",
        "        run: python3 scripts/zigux/validate-phase2.py",
    ]
    return "\n".join(lines) + "\n"


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), workflow_text())
    write_text(resolve_path(root, PHASE2_NOTES), phase2_notes_text())
    write_text(resolve_path(root, PHASE2_CLOSURE), phase2_closure_text())
    write_text(resolve_path(root, REVIEW_CHECKLIST), review_checklist_text())
    write_text(resolve_path(root, SCRIPTS_README), scripts_readme_text())
    write_text(resolve_path(root, TESTS_README), tests_readme_text())
    write_text(resolve_path(root, MAKEFILE), makefile_text())


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        build_self_test_root(root)
        issues = collect_issues(root)
        if issues:
            raise SystemExit(
                "self-test expected a passing packet, got "
                + ", ".join(f"{code}:{detail}" for code, detail in issues)
            )

        broken_workflow = read_text(resolve_path(root, WORKFLOW)).replace(
            "run: make -C zigux phase2-genksyms\n", "", 1
        )
        write_text(resolve_path(root, WORKFLOW), broken_workflow)
        missing = collect_issues(root)
        if ("MISSING_WORKFLOW_PACKET_LINES", "run: make -C zigux phase2-genksyms") not in missing:
            raise SystemExit("self-test expected missing genksyms workflow route failure")

    print("PHASE2_BOOTSTRAP_ROUTE_CLUSTER_SELF_TEST=pass")
    print("PHASE2_BOOTSTRAP_ROUTE_CLUSTER_SELF_TEST_CASE_COUNT=2")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="exercise the built-in test cases")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a passing current-like sample tree to the given directory",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return

    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root)
        print(f"PHASE2_BOOTSTRAP_ROUTE_CLUSTER_SAMPLE_ROOT={args.write_sample_root}")
        return

    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_BOOTSTRAP_ROUTE_CLUSTER=fail")
        for code, detail in issues:
            print(code)
            print(detail)
        raise SystemExit(1)

    print("PHASE2_BOOTSTRAP_ROUTE_CLUSTER=pass")
    print(f"PHASE2_BOOTSTRAP_ROUTE_CLUSTER_ROUTE_COUNT={len(ROUTE_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_ROUTE_CLUSTER_WORKFLOW_STEP_COUNT={len(WORKFLOW_PACKET_LINES)}")
    print(f"PHASE2_BOOTSTRAP_ROUTE_CLUSTER_SURFACE_COUNT={len(SURFACES)}")


if __name__ == "__main__":
    main()

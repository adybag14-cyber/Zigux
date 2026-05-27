#!/usr/bin/env python3
"""Guard the Phase 1 workflow-slot shared reminder surfaces."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
SLOT_CHECKER_REL = Path("scripts/zigux/check-phase1-workflow-slot.py")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
BUILD_REL = Path("zigux/tests/build.zig")
MAKEFILE_REL = Path("zigux/Makefile")

WORKFLOW_CHAIN = (
    "      - name: Check current Phase 1 shared reminder packet",
    "      - name: Self-test current Phase 1 workflow-slot checker",
    "      - name: Check current Phase 1 workflow-slot packet",
    "      - name: Self-test current Phase 1 closure validator",
    "      - name: Check current Phase 1 closure packet",
)

WORKFLOW_LINES = (
    "        run: python3 scripts/zigux/check-phase1-workflow-slot.py --self-test",
    "        run: python3 scripts/zigux/check-phase1-workflow-slot.py",
    "        run: python3 scripts/zigux/validate-phase1-closure.py",
    "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

SLOT_CHECKER_MARKERS = (
    'WORKFLOW_SLOT_SELF_TEST_STEP = "      - name: Self-test current Phase 1 workflow-slot checker"',
    'WORKFLOW_SLOT_CHECK_STEP = "      - name: Check current Phase 1 workflow-slot packet"',
    '"      - name: Check current Phase 1 shared reminder packet"',
    '"      - name: Self-test current Phase 1 closure validator"',
    '"      - name: Run current Phase 1 shared tests-root smoke"',
)

SCRIPTS_README_MARKERS = (
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    "zigux/tests/build.zig",
    "zigux/Makefile",
)

TESTS_README_MARKERS = (
    "current direct-readback Phase 1 reminder packet:",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/build.zig",
    "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "zigux/Makefile",
)

BUILD_MARKERS = (
    'const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);',
    '"phase1-host-tools-smoke",',
    "phase1_step.dependOn(&phase1_host_tools_smoke.step);",
    "smoke_step.dependOn(&phase1_host_tools_smoke.step);",
    "test_step.dependOn(&phase1_host_tools_smoke.step);",
)

MAKEFILE_MARKERS = (
    ".PHONY: phase1-route-summary",
    "phase1-route-summary:",
    "scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "scripts/zigux/check-phase1-route-summary-counts.py",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative: Path) -> str:
    return (root / relative).read_text(encoding="utf-8")


def write_text(root: Path, relative: Path, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_file(root: Path, relative: Path) -> list[str]:
    path = root / relative
    if not path.exists():
        return [f"missing_file:{relative.as_posix()}"]
    if not path.is_file():
        return [f"non_file_path:{relative.as_posix()}"]
    return []


def require_contains(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count >= 1 else [f"missing_marker:{label}:{marker}"]


def require_exact_line(text: str, line: str, expected: int = 1) -> list[str]:
    count = sum(1 for current in text.splitlines() if current == line)
    return [] if count == expected else [f"line_count:{line}:expected={expected}:actual={count}"]


def require_adjacent_chain(text: str, chain: tuple[str, ...]) -> list[str]:
    lines = [line for line in text.splitlines() if line.startswith("      - name: ")]
    span = len(chain)
    for index in range(len(lines) - span + 1):
        if tuple(lines[index : index + span]) == chain:
            return []
    return [f"adjacent_chain_missing:{' -> '.join(chain)}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative in (
        WORKFLOW_REL,
        SLOT_CHECKER_REL,
        SCRIPTS_README_REL,
        TESTS_README_REL,
        BUILD_REL,
        MAKEFILE_REL,
    ):
        failures.extend(require_file(root, relative))
    if failures:
        return failures

    workflow_text = read_text(root, WORKFLOW_REL)
    slot_checker_text = read_text(root, SLOT_CHECKER_REL)
    scripts_readme_text = read_text(root, SCRIPTS_README_REL)
    tests_readme_text = read_text(root, TESTS_README_REL)
    build_text = read_text(root, BUILD_REL)
    makefile_text = read_text(root, MAKEFILE_REL)

    failures.extend(require_adjacent_chain(workflow_text, WORKFLOW_CHAIN))
    for line in WORKFLOW_LINES:
        failures.extend(require_exact_line(workflow_text, line))
    for marker in SLOT_CHECKER_MARKERS:
        failures.extend(require_contains(slot_checker_text, SLOT_CHECKER_REL.as_posix(), marker))
    for marker in SCRIPTS_README_MARKERS:
        failures.extend(require_contains(scripts_readme_text, SCRIPTS_README_REL.as_posix(), marker))
    for marker in TESTS_README_MARKERS:
        failures.extend(require_contains(tests_readme_text, TESTS_README_REL.as_posix(), marker))
    for marker in BUILD_MARKERS:
        failures.extend(require_contains(build_text, BUILD_REL.as_posix(), marker))
    for marker in MAKEFILE_MARKERS:
        failures.extend(require_contains(makefile_text, MAKEFILE_REL.as_posix(), marker))

    return failures


def build_sample_root(root: Path) -> None:
    workflow_lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
        "      - name: Self-test current Phase 1 shared reminder checker",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "      - name: Check current Phase 1 shared reminder packet",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "      - name: Self-test current Phase 1 workflow-slot checker",
        "        run: python3 scripts/zigux/check-phase1-workflow-slot.py --self-test",
        "      - name: Check current Phase 1 workflow-slot packet",
        "        run: python3 scripts/zigux/check-phase1-workflow-slot.py",
        "      - name: Self-test current Phase 1 closure validator",
        "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "      - name: Check current Phase 1 closure packet",
        "        run: python3 scripts/zigux/validate-phase1-closure.py",
        "      - name: Run current Phase 1 shared tests-root smoke",
        "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ]
    write_text(root, WORKFLOW_REL, "\n".join(workflow_lines) + "\n")

    slot_checker_text = """#!/usr/bin/env python3
WORKFLOW_SLOT_SELF_TEST_STEP = \"      - name: Self-test current Phase 1 workflow-slot checker\"
WORKFLOW_SLOT_CHECK_STEP = \"      - name: Check current Phase 1 workflow-slot packet\"
ORDERED = (
    \"      - name: Check current Phase 1 shared reminder packet\",
    \"      - name: Self-test current Phase 1 workflow-slot checker\",
    \"      - name: Check current Phase 1 workflow-slot packet\",
    \"      - name: Self-test current Phase 1 closure validator\",
    \"      - name: Run current Phase 1 shared tests-root smoke\",
)
"""
    write_text(root, SLOT_CHECKER_REL, slot_checker_text)

    scripts_readme = """# scripts/zigux

- scripts/zigux/check-phase1-shared-reminder-packet.py
- scripts/zigux/validate-phase1-closure.py
- zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig
- zigux/tests/build.zig
- zigux/Makefile
- .github/workflows/zigux-bootstrap.yml
"""
    write_text(root, SCRIPTS_README_REL, scripts_readme)

    tests_readme = """# zigux/tests

current direct-readback Phase 1 reminder packet:
- scripts/zigux/validate-phase1-closure.py
- zigux/tests/build.zig
- zigux/Makefile
current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
"""
    write_text(root, TESTS_README_REL, tests_readme)

    build_text = """const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);
"phase1-host-tools-smoke",
phase1_step.dependOn(&phase1_host_tools_smoke.step);
smoke_step.dependOn(&phase1_host_tools_smoke.step);
test_step.dependOn(&phase1_host_tools_smoke.step);
"""
    write_text(root, BUILD_REL, build_text)

    makefile_text = """.PHONY: phase1-route-summary
phase1-route-summary:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py
"""
    write_text(root, MAKEFILE_REL, makefile_text)


def remove_once(path: Path, needle: str) -> None:
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        raise ValueError(f"missing needle: {needle}")
    path.write_text(text.replace(needle, "", 1), encoding="utf-8")


def run_self_test() -> int:
    cases = (
        ("success", None),
        ("missing_slot_checker", ("delete", SLOT_CHECKER_REL)),
        ("missing_slot_check_step", ("remove", WORKFLOW_REL, "      - name: Check current Phase 1 workflow-slot packet\n")),
        ("broken_slot_adjacency", ("insert", WORKFLOW_REL, "      - name: Lane drift spacer\n        run: python3 drift.py\n", "      - name: Self-test current Phase 1 closure validator\n")),
        ("missing_scripts_readme_marker", ("remove", SCRIPTS_README_REL, "zigux/Makefile")),
        ("missing_tests_smoke_route", ("remove", TESTS_README_REL, "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`")),
        ("missing_build_dependency", ("remove", BUILD_REL, "smoke_step.dependOn(&phase1_host_tools_smoke.step);")),
        ("missing_makefile_route", ("remove", MAKEFILE_REL, "scripts/zigux/check-phase1-route-summary-counts.py --self-test")),
    )

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-workflow-slot-shared-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            if mutation is not None:
                kind = mutation[0]
                if kind == "delete":
                    (root / mutation[1]).unlink()
                elif kind == "remove":
                    remove_once(root / mutation[1], mutation[2])
                elif kind == "insert":
                    path = root / mutation[1]
                    text = path.read_text(encoding="utf-8")
                    anchor = mutation[3]
                    if anchor not in text:
                        raise ValueError(f"missing anchor: {anchor}")
                    path.write_text(text.replace(anchor, mutation[2] + anchor, 1), encoding="utf-8")
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("PHASE1_WORKFLOW_SLOT_SHARED_SURFACES_SELF_TEST=fail")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"PHASE1_WORKFLOW_SLOT_SHARED_SURFACES_SELF_TEST_CASE_FAILED={name}")
                return 1

    print("PHASE1_WORKFLOW_SLOT_SHARED_SURFACES_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_SLOT_SHARED_SURFACES_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--write-sample-root", help="write a current-like sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        root = Path(args.write_sample_root).resolve()
        if root.exists():
            shutil.rmtree(root)
        root.mkdir(parents=True, exist_ok=True)
        build_sample_root(root)
        print(f"phase1-workflow-slot-shared-surfaces:sample-root-written:{root}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_WORKFLOW_SLOT_SHARED_SURFACES=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_WORKFLOW_SLOT_SHARED_SURFACES=pass")
    print(
        "PHASE1_WORKFLOW_SLOT_SHARED_SURFACES_MARKER_COUNT="
        f"{len(SLOT_CHECKER_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(BUILD_MARKERS) + len(MAKEFILE_MARKERS)}"
    )
    print(
        "PHASE1_WORKFLOW_SLOT_SHARED_SURFACES_WORKFLOW_LINE_COUNT="
        f"{len(WORKFLOW_CHAIN) + len(WORKFLOW_LINES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

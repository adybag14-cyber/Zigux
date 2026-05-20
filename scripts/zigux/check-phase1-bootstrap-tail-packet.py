#!/usr/bin/env python3
"""Guard the current Lane 03 bootstrap Phase 1 tail packet against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else Path.cwd()

WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
PHASE1_CLOSURE = ROOT / "Documentation" / "zigux" / "phase1-closure.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
PHASE1_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase1-closure.py"

SURFACE_PATHS = (
    WORKFLOW,
    PHASE1_CLOSURE,
    SCRIPTS_README,
    TESTS_README,
    MAKEFILE,
    PHASE1_VALIDATOR,
    ROOT / "scripts" / "zigux" / "check-phase1-direct-owner-markers.py",
    ROOT / "scripts" / "zigux" / "check-phase1-string-review-packet.py",
    ROOT / "scripts" / "zigux" / "check-phase1-route-summary-counts.py",
    ROOT / "scripts" / "zigux" / "check-phase1-bench.py",
    ROOT / "scripts" / "zigux" / "check-phase1-shared-reminder-packet.py",
    ROOT / "zigux" / "tests" / "build.zig",
    ROOT / "zigux" / "tests" / "phase1_host_tools_smoke.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json",
)

WORKFLOW_BOUNDARY_BEFORE = (
    "Validate current Phase 2 tool packet",
    "run: python3 scripts/zigux/validate-phase2.py",
)
WORKFLOW_PACKET_STEPS = (
    (
        "Self-test current Phase 1 direct-owner checker",
        "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    ),
    (
        "Check current Phase 1 direct-owner markers",
        "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    ),
    (
        "Self-test current Phase 1 string review checker",
        "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    ),
    (
        "Check current Phase 1 string review packet",
        "run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    ),
    (
        "Self-test current Phase 1 route summary checker",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    ),
    (
        "Check current Phase 1 route summary packet",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    ),
    (
        "Self-test current Phase 1 bench checker",
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    (
        "Self-test current Phase 1 shared reminder checker",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    ),
    (
        "Check current Phase 1 shared reminder packet",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    ),
    (
        "Self-test current Phase 1 closure validator",
        "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    ),
    (
        "Check current Phase 1 closure packet",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
    ),
)
WORKFLOW_BOUNDARY_AFTER = (
    "Self-test current Phase 3 interop packet",
    "run: python3 scripts/zigux/validate_phase3_selftest.py",
)

MAKEFILE_LINES = (
    "phase1-route-summary:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py",
)
FORBIDDEN_MAKEFILE_LINES = (
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
)

PHASE1_CLOSURE_MARKERS = (
    "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet:",
)

SCRIPTS_README_MARKERS = (
    "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
    "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
)

TESTS_README_MARKERS = (
    "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    "Tests-root reviewer prompt:",
)

VALIDATOR_MARKERS = (
    'ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")',
    '"route_summary_guard": "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",',
    '(ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts"),',
)


class ValidationError(Exception):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_exact_line(text: str, snippet: str, label: str) -> int:
    matches = [index for index, line in enumerate(text.splitlines()) if line.strip() == snippet]
    count = len(matches)
    if count != 1:
        raise ValidationError(f"{label} must appear exactly once; found {count}")
    return matches[0]


def require_absent_line(text: str, snippet: str, label: str) -> None:
    count = sum(1 for line in text.splitlines() if line.strip() == snippet)
    if count != 0:
        raise ValidationError(f"{label} must be absent; found {count}")


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise ValidationError(f"{label} missing marker: {marker}")


def validate_workflow(workflow_text: str) -> None:
    before_name, before_run = WORKFLOW_BOUNDARY_BEFORE
    after_name, after_run = WORKFLOW_BOUNDARY_AFTER

    before_name_index = require_exact_line(
        workflow_text, f"- name: {before_name}", "workflow boundary-before step"
    )
    before_run_index = require_exact_line(
        workflow_text, before_run, "workflow boundary-before command"
    )
    if before_name_index > before_run_index:
        raise ValidationError("workflow boundary-before command must follow its step name")

    previous_index = before_run_index
    for step_name, run_line in WORKFLOW_PACKET_STEPS:
        name_index = require_exact_line(
            workflow_text, f"- name: {step_name}", f"workflow step {step_name}"
        )
        run_index = require_exact_line(workflow_text, run_line, f"workflow command {run_line}")
        if name_index > run_index:
            raise ValidationError(f"workflow command for {step_name} must follow its step name")
        if previous_index >= name_index:
            raise ValidationError(f"workflow step {step_name} is out of order")
        previous_index = run_index

    after_name_index = require_exact_line(
        workflow_text, f"- name: {after_name}", "workflow boundary-after step"
    )
    after_run_index = require_exact_line(
        workflow_text, after_run, "workflow boundary-after command"
    )
    if after_name_index > after_run_index:
        raise ValidationError("workflow boundary-after command must follow its step name")
    if previous_index >= after_name_index:
        raise ValidationError("workflow Phase 1 tail packet must finish before the Phase 3 handoff")


def validate_root(root: Path) -> None:
    for path in SURFACE_PATHS:
        rel = path.relative_to(ROOT)
        if not (root / rel).exists():
            raise ValidationError(f"missing required file: {root / rel}")

    workflow_text = read_text(root / WORKFLOW.relative_to(ROOT))
    phase1_closure_text = read_text(root / PHASE1_CLOSURE.relative_to(ROOT))
    scripts_readme_text = read_text(root / SCRIPTS_README.relative_to(ROOT))
    tests_readme_text = read_text(root / TESTS_README.relative_to(ROOT))
    makefile_text = read_text(root / MAKEFILE.relative_to(ROOT))
    validator_text = read_text(root / PHASE1_VALIDATOR.relative_to(ROOT))

    validate_workflow(workflow_text)

    for line in MAKEFILE_LINES:
        require_exact_line(makefile_text, line, f"Makefile line {line}")
    for line in FORBIDDEN_MAKEFILE_LINES:
        require_absent_line(makefile_text, line, f"forbidden Makefile line {line}")

    require_markers(phase1_closure_text, PHASE1_CLOSURE_MARKERS, "phase1 closure note")
    require_markers(scripts_readme_text, SCRIPTS_README_MARKERS, "scripts README")
    require_markers(tests_readme_text, TESTS_README_MARKERS, "tests README")
    require_markers(validator_text, VALIDATOR_MARKERS, "validate-phase1-closure.py")


SAMPLE_WORKFLOW = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Validate current Phase 2 tool packet
        run: python3 scripts/zigux/validate-phase2.py
      - name: Self-test current Phase 1 direct-owner checker
        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
      - name: Check current Phase 1 direct-owner markers
        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
      - name: Self-test current Phase 1 string review checker
        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test
      - name: Check current Phase 1 string review packet
        run: python3 scripts/zigux/check-phase1-string-review-packet.py
      - name: Self-test current Phase 1 route summary checker
        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test
      - name: Check current Phase 1 route summary packet
        run: python3 scripts/zigux/check-phase1-route-summary-counts.py
      - name: Self-test current Phase 1 bench checker
        run: python3 scripts/zigux/check-phase1-bench.py --self-test
      - name: Self-test current Phase 1 shared reminder checker
        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test
      - name: Check current Phase 1 shared reminder packet
        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py
      - name: Self-test current Phase 1 closure validator
        run: python3 scripts/zigux/validate-phase1-closure.py --self-test
      - name: Check current Phase 1 closure packet
        run: python3 scripts/zigux/validate-phase1-closure.py
      - name: Self-test current Phase 3 interop packet
        run: python3 scripts/zigux/validate_phase3_selftest.py
"""

SAMPLE_PHASE1_CLOSURE = """# Phase 1 Closure

- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`
- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`
- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`

The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet:
"""

SAMPLE_SCRIPTS_README = """# scripts/zigux

- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes
- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route
- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root
"""

SAMPLE_TESTS_README = """# zigux/tests

  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`

Tests-root reviewer prompt:
"""

SAMPLE_MAKEFILE = """PYTHON ?= python3
ZIGUX_ROOT := ..

phase1-route-summary:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py
"""

SAMPLE_VALIDATOR = """#!/usr/bin/env python3
from pathlib import Path

ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
EXPECTED_MARKERS = {
    "route_summary_guard": "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
}
DELEGATED_CHECKERS = (
    (ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts"),
)
"""


def write_sample_root(root: Path) -> None:
    write_text(root / WORKFLOW.relative_to(ROOT), SAMPLE_WORKFLOW)
    write_text(root / PHASE1_CLOSURE.relative_to(ROOT), SAMPLE_PHASE1_CLOSURE)
    write_text(root / SCRIPTS_README.relative_to(ROOT), SAMPLE_SCRIPTS_README)
    write_text(root / TESTS_README.relative_to(ROOT), SAMPLE_TESTS_README)
    write_text(root / MAKEFILE.relative_to(ROOT), SAMPLE_MAKEFILE)
    write_text(root / PHASE1_VALIDATOR.relative_to(ROOT), SAMPLE_VALIDATOR)
    for path in SURFACE_PATHS:
        rel = path.relative_to(ROOT)
        if rel in (
            WORKFLOW.relative_to(ROOT),
            PHASE1_CLOSURE.relative_to(ROOT),
            SCRIPTS_README.relative_to(ROOT),
            TESTS_README.relative_to(ROOT),
            MAKEFILE.relative_to(ROOT),
            PHASE1_VALIDATOR.relative_to(ROOT),
        ):
            continue
        content = "{}\n" if rel.suffix == ".json" else "present\n"
        write_text(root / rel, content)


def run_self_test() -> int:
    case_count = 0

    def expect_pass(mutator=None) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane03_phase1_tail_pass_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            if mutator is not None:
                mutator(root)
            validate_root(root)
            case_count += 1

    def expect_fail(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane03_phase1_tail_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                validate_root(root)
            except ValidationError as exc:
                if expected_substring not in str(exc):
                    raise AssertionError(f"expected {expected_substring!r} in {exc!r}") from exc
                case_count += 1
                return
            raise AssertionError("expected ValidationError")

    expect_pass()
    expect_fail(
        lambda root: write_text(
            root / WORKFLOW.relative_to(ROOT),
            read_text(root / WORKFLOW.relative_to(ROOT)).replace(
                "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test\n",
                "",
                1,
            ),
        ),
        "workflow command run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test must appear exactly once",
    )
    expect_fail(
        lambda root: write_text(
            root / WORKFLOW.relative_to(ROOT),
            read_text(root / WORKFLOW.relative_to(ROOT)).replace(
                "      - name: Self-test current Phase 1 shared reminder checker\n"
                "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n"
                "      - name: Check current Phase 1 shared reminder packet\n"
                "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n"
                "      - name: Self-test current Phase 1 closure validator\n"
                "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n",
                "      - name: Self-test current Phase 1 closure validator\n"
                "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n"
                "      - name: Self-test current Phase 1 shared reminder checker\n"
                "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n"
                "      - name: Check current Phase 1 shared reminder packet\n"
                "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n",
            ),
        ),
        "workflow step Self-test current Phase 1 closure validator is out of order",
    )
    expect_fail(
        lambda root: write_text(
            root / MAKEFILE.relative_to(ROOT),
            read_text(root / MAKEFILE.relative_to(ROOT)) + "phase1:\n",
        ),
        "forbidden Makefile line phase1: must be absent; found 1",
    )
    expect_fail(
        lambda root: write_text(
            root / PHASE1_CLOSURE.relative_to(ROOT),
            read_text(root / PHASE1_CLOSURE.relative_to(ROOT)).replace(
                "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`\n",
                "",
                1,
            ),
        ),
        "phase1 closure note missing marker: - `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    )
    expect_fail(
        lambda root: write_text(
            root / PHASE1_VALIDATOR.relative_to(ROOT),
            read_text(root / PHASE1_VALIDATOR.relative_to(ROOT)).replace(
                '(ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts"),',
                "",
                1,
            ),
        ),
        'validate-phase1-closure.py missing marker: (ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts"),',
    )
    expect_fail(
        lambda root: (root / SCRIPTS_README.relative_to(ROOT)).unlink(),
        "missing required file:",
    )
    expect_fail(
        lambda root: write_text(
            root / WORKFLOW.relative_to(ROOT),
            read_text(root / WORKFLOW.relative_to(ROOT)).replace(
                "      - name: Check current Phase 1 closure packet\n"
                "        run: python3 scripts/zigux/validate-phase1-closure.py\n"
                "      - name: Self-test current Phase 3 interop packet\n"
                "        run: python3 scripts/zigux/validate_phase3_selftest.py\n",
                "      - name: Self-test current Phase 3 interop packet\n"
                "        run: python3 scripts/zigux/validate_phase3_selftest.py\n"
                "      - name: Check current Phase 1 closure packet\n"
                "        run: python3 scripts/zigux/validate-phase1-closure.py\n",
            ),
        ),
        "workflow Phase 1 tail packet must finish before the Phase 3 handoff",
    )

    print("PHASE1_BOOTSTRAP_TAIL_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BOOTSTRAP_TAIL_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Lane 03 bootstrap Phase 1 tail packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root to validate.")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root and exit.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE1_BOOTSTRAP_TAIL_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    try:
        validate_root(args.root.resolve())
    except ValidationError as exc:
        print("PHASE1_BOOTSTRAP_TAIL_PACKET=fail")
        print(f"PHASE1_BOOTSTRAP_TAIL_PACKET_ROOT={args.root}")
        print(f"PHASE1_BOOTSTRAP_TAIL_PACKET_NOTE={exc}")
        return 1

    print("PHASE1_BOOTSTRAP_TAIL_PACKET=pass")
    print(f"PHASE1_BOOTSTRAP_TAIL_PACKET_ROOT={args.root}")
    print(f"PHASE1_BOOTSTRAP_TAIL_PACKET_WORKFLOW_STEP_COUNT={len(WORKFLOW_PACKET_STEPS)}")
    print(f"PHASE1_BOOTSTRAP_TAIL_PACKET_REQUIRED_FILE_COUNT={len(SURFACE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

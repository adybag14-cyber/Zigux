#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
STATUS = "PHASE2_BOOTSTRAP_BRIDGE_PACKET"
SELF_TEST = f"{STATUS}_SELF_TEST"

REQUIRED_FILES = [
    Path("scripts/zigux/check-kconfig-bridge.py"),
    Path("scripts/zigux/kconfig/conf_bridge.zig"),
    Path("scripts/zigux/kconfig/confdata_bridge.zig"),
    Path("scripts/zigux/check-phase2-kconfig-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-kbuild-routes.py"),
    Path("scripts/zigux/check-phase2-tests-readme-alignment.py"),
    Path("scripts/zigux/check-phase2-cross.py"),
    Path("scripts/zigux/check-phase2-cross-selftest-alignment.py"),
    Path("zigux/tests/fixtures/phase2_cross_targets.json"),
]

BOUNDARY_BEFORE = (
    "Check current Lane 01 bootstrap charter packet",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py",
)
BRIDGE_STEPS = [
    ("Self-test current kconfig bridge checker", "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test"),
    ("Check current kconfig bridge packet", "run: python3 scripts/zigux/check-kconfig-bridge.py"),
    ("Run current Phase 2 conf bridge unit tests", "run: zig test scripts/zigux/kconfig/conf_bridge.zig"),
    ("Run current Phase 2 confdata bridge unit tests", "run: zig test scripts/zigux/kconfig/confdata_bridge.zig"),
    (
        "Self-test current Phase 2 kconfig bridge checker",
        "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    ),
    ("Check current Phase 2 kconfig bridge packet", "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py"),
    ("Self-test current Phase 2 kbuild routes checker", "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test"),
    ("Check current Phase 2 kbuild packet", "run: python3 scripts/zigux/check-phase2-kbuild-routes.py"),
    ("Self-test current Phase 2 tests README checker", "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test"),
    ("Check current Phase 2 tests README packet", "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py"),
    ("Self-test current Phase 2 cross checker", "run: python3 scripts/zigux/check-phase2-cross.py --self-test"),
    ("Check current Phase 2 direct cross-route packet", "run: python3 scripts/zigux/check-phase2-cross.py"),
    (
        "Self-test current Phase 2 cross selftest alignment checker",
        "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    ),
    ("Check current Phase 2 cross alignment packet", "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py"),
]
BOUNDARY_AFTER = (
    "Self-test current Phase 2 toolchain pinning checker",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
)

SAMPLE_WORKFLOW = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Check current Lane 01 bootstrap charter packet
        run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py
      - name: Self-test current kconfig bridge checker
        run: python3 scripts/zigux/check-kconfig-bridge.py --self-test
      - name: Check current kconfig bridge packet
        run: python3 scripts/zigux/check-kconfig-bridge.py
      - name: Run current Phase 2 conf bridge unit tests
        run: zig test scripts/zigux/kconfig/conf_bridge.zig
      - name: Run current Phase 2 confdata bridge unit tests
        run: zig test scripts/zigux/kconfig/confdata_bridge.zig
      - name: Self-test current Phase 2 kconfig bridge checker
        run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test
      - name: Check current Phase 2 kconfig bridge packet
        run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py
      - name: Self-test current Phase 2 kbuild routes checker
        run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test
      - name: Check current Phase 2 kbuild packet
        run: python3 scripts/zigux/check-phase2-kbuild-routes.py
      - name: Self-test current Phase 2 tests README checker
        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test
      - name: Check current Phase 2 tests README packet
        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py
      - name: Self-test current Phase 2 cross checker
        run: python3 scripts/zigux/check-phase2-cross.py --self-test
      - name: Check current Phase 2 direct cross-route packet
        run: python3 scripts/zigux/check-phase2-cross.py
      - name: Self-test current Phase 2 cross selftest alignment checker
        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test
      - name: Check current Phase 2 cross alignment packet
        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py
      - name: Self-test current Phase 2 toolchain pinning checker
        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test
"""


class ValidationError(Exception):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc


def require_once(lines: list[str], needle: str, label: str) -> int:
    matches = [index for index, line in enumerate(lines) if line.strip() == needle]
    if len(matches) != 1:
        raise ValidationError(f"{label} must appear exactly once; found {len(matches)}")
    return matches[0]


def validate_workflow(text: str) -> None:
    lines = text.splitlines()
    previous_line = require_once(lines, f"- name: {BOUNDARY_BEFORE[0]}", "workflow boundary-before step")
    before_run_line = require_once(lines, BOUNDARY_BEFORE[1], "workflow boundary-before command")
    if previous_line > before_run_line:
        raise ValidationError("workflow boundary-before command must follow its step name")

    previous_line = before_run_line
    for step_name, run_line in BRIDGE_STEPS:
        step_line = require_once(lines, f"- name: {step_name}", f"workflow step {step_name}")
        command_line = require_once(lines, run_line, f"workflow command {run_line}")
        if step_line > command_line:
            raise ValidationError(f"workflow command for {step_name} must follow its step name")
        if previous_line >= step_line:
            raise ValidationError(f"workflow step {step_name} is out of order")
        previous_line = command_line

    after_step_line = require_once(lines, f"- name: {BOUNDARY_AFTER[0]}", "workflow boundary-after step")
    after_run_line = require_once(lines, BOUNDARY_AFTER[1], "workflow boundary-after command")
    if after_step_line > after_run_line:
        raise ValidationError("workflow boundary-after command must follow its step name")
    if previous_line >= after_step_line:
        raise ValidationError("workflow bridge packet must finish before toolchain pinning")


def validate_files(root: Path) -> None:
    missing = [str(path) for path in REQUIRED_FILES if not (root / path).is_file()]
    if missing:
        raise ValidationError(f"missing required file set: {', '.join(missing)}")


def validate_root(root: Path) -> None:
    validate_files(root)
    validate_workflow(read_text(root / WORKFLOW))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(root / WORKFLOW, SAMPLE_WORKFLOW)
    for rel_path in REQUIRED_FILES:
        content = "{}\n" if rel_path.suffix == ".json" else "// sample\n"
        write_text(root / rel_path, content)


def run_self_test() -> int:
    case_count = 0

    def expect_pass(mutator=None) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane03_bridge_pass_") as tmp_dir:
            root = Path(tmp_dir)
            build_sample_root(root)
            if mutator is not None:
                mutator(root)
            validate_root(root)
            case_count += 1

    def expect_fail(mutator, expected: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane03_bridge_fail_") as tmp_dir:
            root = Path(tmp_dir)
            build_sample_root(root)
            mutator(root)
            try:
                validate_root(root)
            except ValidationError as exc:
                if expected not in str(exc):
                    raise AssertionError(f"expected {expected!r} in {exc!r}") from exc
                case_count += 1
                return
            raise AssertionError("expected ValidationError")

    expect_pass()
    expect_fail(
        lambda root: (root / WORKFLOW).write_text(
            read_text(root / WORKFLOW).replace(
                "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "workflow command run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test must appear exactly once",
    )
    expect_fail(
        lambda root: (root / WORKFLOW).write_text(
            read_text(root / WORKFLOW).replace(
                "      - name: Self-test current Phase 2 tests README checker\n"
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test\n"
                "      - name: Check current Phase 2 tests README packet\n"
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py\n"
                "      - name: Self-test current Phase 2 cross checker\n"
                "        run: python3 scripts/zigux/check-phase2-cross.py --self-test\n"
                "      - name: Check current Phase 2 direct cross-route packet\n"
                "        run: python3 scripts/zigux/check-phase2-cross.py\n",
                "      - name: Self-test current Phase 2 cross checker\n"
                "        run: python3 scripts/zigux/check-phase2-cross.py --self-test\n"
                "      - name: Check current Phase 2 direct cross-route packet\n"
                "        run: python3 scripts/zigux/check-phase2-cross.py\n"
                "      - name: Self-test current Phase 2 tests README checker\n"
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test\n"
                "      - name: Check current Phase 2 tests README packet\n"
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py\n",
                1,
            ),
            encoding="utf-8",
        ),
        "workflow step Self-test current Phase 2 cross checker is out of order",
    )
    expect_fail(
        lambda root: (root / WORKFLOW).write_text(
            read_text(root / WORKFLOW).replace(
                "      - name: Check current Phase 2 cross alignment packet\n"
                "        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\n"
                "      - name: Self-test current Phase 2 toolchain pinning checker\n"
                "        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test\n",
                "      - name: Self-test current Phase 2 toolchain pinning checker\n"
                "        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test\n"
                "      - name: Check current Phase 2 cross alignment packet\n"
                "        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\n",
                1,
            ),
            encoding="utf-8",
        ),
        "workflow bridge packet must finish before toolchain pinning",
    )
    expect_fail(
        lambda root: (root / REQUIRED_FILES[-1]).unlink(),
        "missing required file set:",
    )
    expect_fail(
        lambda root: (root / WORKFLOW).write_text(
            read_text(root / WORKFLOW).replace(
                "run: zig test scripts/zigux/kconfig/confdata_bridge.zig\n",
                "run: zig test scripts/zigux/kconfig/confdata_bridge_replaced.zig\n",
                1,
            ),
            encoding="utf-8",
        ),
        "workflow command run: zig test scripts/zigux/kconfig/confdata_bridge.zig must appear exactly once",
    )
    expect_fail(
        lambda root: (root / WORKFLOW).write_text(
            read_text(root / WORKFLOW).replace(
                "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\n",
                "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\n"
                "        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\n",
                1,
            ),
            encoding="utf-8",
        ),
        "workflow command run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py must appear exactly once",
    )

    print(f"{SELF_TEST}=pass")
    print(f"{SELF_TEST}_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Lane 03 bootstrap Phase 2 bridge workflow packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root and exit.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"{STATUS}_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    try:
        validate_root(args.root)
    except ValidationError as exc:
        print(f"{STATUS}=fail")
        print(f"{STATUS}_ROOT={args.root}")
        print(f"{STATUS}_NOTE={exc}")
        return 1

    print(f"{STATUS}=pass")
    print(f"{STATUS}_ROOT={args.root}")
    print(f"{STATUS}_WORKFLOW_STEP_COUNT={len(BRIDGE_STEPS)}")
    print(f"{STATUS}_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

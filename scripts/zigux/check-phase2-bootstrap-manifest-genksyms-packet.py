#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
STATUS = "PHASE2_BOOTSTRAP_MANIFEST_GENKSYMS_PACKET"
SELF_TEST = f"{STATUS}_SELF_TEST"

REQUIRED_FILES = [
    Path("scripts/zigux/check-phase2-docs-shared-reminder.py"),
    Path("scripts/zigux/check-phase2-tool-manifest.py"),
    Path("zigux/tests/fixtures/phase2_tool_manifest.json"),
    Path("scripts/zigux/check-phase2-artifact-tools-manifest.py"),
    Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json"),
    Path("scripts/zigux/check-genksyms-bridge.py"),
    Path("scripts/zigux/genksyms.zig"),
    Path("zigux/tests/fixtures/genksyms_bridge/cases.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/help_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/minimal_expected.json"),
]

BOUNDARY_BEFORE = (
    "Check current Phase 2 required-make-routes packet",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
)
PACKET_STEPS = [
    (
        "Self-test current Phase 2 shared reminder checker",
        "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    ),
    (
        "Check current Phase 2 shared reminder packet",
        "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    ),
    (
        "Self-test current Phase 2 tool manifest checker",
        "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    ),
    (
        "Check current Phase 2 tool manifest packet",
        "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    ),
    (
        "Self-test current Phase 2 artifact tools manifest checker",
        "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    ),
    (
        "Check current Phase 2 artifact tools manifest packet",
        "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    ),
    (
        "Self-test current Phase 2 genksyms bridge checker",
        "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    ),
    (
        "Check current Phase 2 genksyms bridge packet",
        "run: python3 scripts/zigux/check-genksyms-bridge.py",
    ),
    (
        "Run current Phase 2 genksyms unit replay",
        "run: zig test scripts/zigux/genksyms.zig",
    ),
]
BOUNDARY_AFTER = (
    "Run current Phase 2 validate make route",
    "run: make -C zigux phase2-validate",
)

SAMPLE_WORKFLOW = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Check current Phase 2 required-make-routes packet
        run: python3 scripts/zigux/check-phase2-required-make-routes.py
      - name: Self-test current Phase 2 shared reminder checker
        run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test
      - name: Check current Phase 2 shared reminder packet
        run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py
      - name: Self-test current Phase 2 tool manifest checker
        run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test
      - name: Check current Phase 2 tool manifest packet
        run: python3 scripts/zigux/check-phase2-tool-manifest.py
      - name: Self-test current Phase 2 artifact tools manifest checker
        run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test
      - name: Check current Phase 2 artifact tools manifest packet
        run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py
      - name: Self-test current Phase 2 genksyms bridge checker
        run: python3 scripts/zigux/check-genksyms-bridge.py --self-test
      - name: Check current Phase 2 genksyms bridge packet
        run: python3 scripts/zigux/check-genksyms-bridge.py
      - name: Run current Phase 2 genksyms unit replay
        run: zig test scripts/zigux/genksyms.zig
      - name: Run current Phase 2 validate make route
        run: make -C zigux phase2-validate
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
    for step_name, run_line in PACKET_STEPS:
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
        raise ValidationError("workflow packet must finish before the Phase 2 validate make route")


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
        with tempfile.TemporaryDirectory(prefix="lane03_manifest_genksyms_pass_") as tmp_dir:
            root = Path(tmp_dir)
            build_sample_root(root)
            if mutator is not None:
                mutator(root)
            validate_root(root)
            case_count += 1

    def expect_fail(mutator, expected: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane03_manifest_genksyms_fail_") as tmp_dir:
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
                "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "workflow command run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test must appear exactly once",
    )
    expect_fail(
        lambda root: (root / WORKFLOW).write_text(
            read_text(root / WORKFLOW).replace(
                "      - name: Self-test current Phase 2 artifact tools manifest checker\n"
                "        run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test\n"
                "      - name: Check current Phase 2 artifact tools manifest packet\n"
                "        run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py\n"
                "      - name: Self-test current Phase 2 genksyms bridge checker\n"
                "        run: python3 scripts/zigux/check-genksyms-bridge.py --self-test\n"
                "      - name: Check current Phase 2 genksyms bridge packet\n"
                "        run: python3 scripts/zigux/check-genksyms-bridge.py\n",
                "      - name: Self-test current Phase 2 genksyms bridge checker\n"
                "        run: python3 scripts/zigux/check-genksyms-bridge.py --self-test\n"
                "      - name: Check current Phase 2 genksyms bridge packet\n"
                "        run: python3 scripts/zigux/check-genksyms-bridge.py\n"
                "      - name: Self-test current Phase 2 artifact tools manifest checker\n"
                "        run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test\n"
                "      - name: Check current Phase 2 artifact tools manifest packet\n"
                "        run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py\n",
                1,
            ),
            encoding="utf-8",
        ),
        "workflow step Self-test current Phase 2 genksyms bridge checker is out of order",
    )
    expect_fail(
        lambda root: (root / WORKFLOW).write_text(
            read_text(root / WORKFLOW).replace(
                "      - name: Run current Phase 2 genksyms unit replay\n"
                "        run: zig test scripts/zigux/genksyms.zig\n"
                "      - name: Run current Phase 2 validate make route\n"
                "        run: make -C zigux phase2-validate\n",
                "      - name: Run current Phase 2 validate make route\n"
                "        run: make -C zigux phase2-validate\n"
                "      - name: Run current Phase 2 genksyms unit replay\n"
                "        run: zig test scripts/zigux/genksyms.zig\n",
                1,
            ),
            encoding="utf-8",
        ),
        "workflow packet must finish before the Phase 2 validate make route",
    )
    expect_fail(
        lambda root: (root / REQUIRED_FILES[-1]).unlink(),
        "missing required file set:",
    )
    expect_fail(
        lambda root: (root / WORKFLOW).write_text(
            read_text(root / WORKFLOW).replace(
                "run: zig test scripts/zigux/genksyms.zig\n",
                "run: zig test scripts/zigux/genksyms.zig\n"
                "        run: zig test scripts/zigux/genksyms.zig\n",
                1,
            ),
            encoding="utf-8",
        ),
        "workflow command run: zig test scripts/zigux/genksyms.zig must appear exactly once",
    )
    expect_fail(
        lambda root: (root / WORKFLOW).write_text(
            read_text(root / WORKFLOW).replace(
                "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py\n",
                "run: python3 scripts/zigux/check-phase2-docs-shared-reminder-moved.py\n",
                1,
            ),
            encoding="utf-8",
        ),
        "workflow command run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py must appear exactly once",
    )

    print(f"{SELF_TEST}=pass")
    print(f"{SELF_TEST}_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Lane 03 bootstrap manifest and genksyms workflow packet."
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
    print(f"{STATUS}_WORKFLOW_STEP_COUNT={len(PACKET_STEPS)}")
    print(f"{STATUS}_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

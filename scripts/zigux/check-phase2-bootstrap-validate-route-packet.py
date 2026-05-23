#!/usr/bin/env python3
"""Guard the live bootstrap Phase 2 validate-route packet against tail drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else Path.cwd()

WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
PHASE2_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

SURFACE_PATHS = (
    WORKFLOW,
    MAKEFILE,
    PHASE2_VALIDATOR,
    ROOT / "scripts" / "zigux" / "validate-phase2-closure.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest.py",
    ROOT / "scripts" / "zigux" / "check-genksyms-bridge.py",
    ROOT / "scripts" / "zigux" / "genksyms.zig",
    PHASE2_CLOSURE,
    TESTS_README,
    TOOL_MANIFEST,
)

WORKFLOW_BOUNDARY_BEFORE = (
    "Run current Phase 2 genksyms unit replay",
    "run: zig test scripts/zigux/genksyms.zig",
)
WORKFLOW_PACKET_STEPS = (
    (
        "Run current Phase 2 validate make route",
        "run: make -C zigux phase2-validate",
    ),
    (
        "Validate current Phase 2 tool packet",
        "run: python3 scripts/zigux/validate-phase2.py",
    ),
)
WORKFLOW_BOUNDARY_AFTER = (
    "Self-test current Phase 1 direct-owner checker",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
)

MAKEFILE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

PHASE2_CLOSURE_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "- `python3 scripts/zigux/validate-phase2.py`",
)

TESTS_README_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
)

VALIDATOR_MARKERS = (
    "\"run: make -C zigux phase2-validate\",",
    "\"run: python3 scripts/zigux/validate-phase2.py\",",
    "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py\",",
    "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py\",",
    "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py\",",
)

MANIFEST_MARKERS = (
    "\"scripts/zigux/validate-phase2.py\"",
    "\"scripts/zigux/validate-phase2-closure.py\"",
    "\"zigux/Makefile\"",
    "\"make -C zigux phase2-validate\"",
    "\"make -C zigux phase2\"",
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


def require_once(text: str, snippet: str, label: str) -> int:
    count = text.count(snippet)
    if count != 1:
        raise ValidationError(f"{label} must appear exactly once; found {count}")
    return text.index(snippet)


def require_exact_line(text: str, snippet: str, label: str) -> int:
    matches = [i for i, line in enumerate(text.splitlines()) if line.strip() == snippet]
    count = len(matches)
    if count != 1:
        raise ValidationError(f"{label} must appear exactly once; found {count}")
    return matches[0]


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise ValidationError(f"{label} missing marker: {marker}")


def validate_workflow(workflow_text: str) -> None:
    before_name, before_run = WORKFLOW_BOUNDARY_BEFORE
    after_name, after_run = WORKFLOW_BOUNDARY_AFTER

    before_name_index = require_once(workflow_text, before_name, "workflow boundary-before step")
    before_run_index = require_once(workflow_text, before_run, "workflow boundary-before command")
    if before_name_index > before_run_index:
        raise ValidationError("workflow boundary-before command must follow its step name")

    previous_index = before_run_index
    for step_name, run_line in WORKFLOW_PACKET_STEPS:
        name_index = require_once(workflow_text, step_name, f"workflow step {step_name}")
        run_index = require_once(workflow_text, run_line, f"workflow command {run_line}")
        if name_index > run_index:
            raise ValidationError(f"workflow command for {step_name} must follow its step name")
        if previous_index >= name_index:
            raise ValidationError(f"workflow step {step_name} is out of order")
        previous_index = run_index

    after_name_index = require_once(workflow_text, after_name, "workflow boundary-after step")
    after_run_index = require_once(workflow_text, after_run, "workflow boundary-after command")
    if after_name_index > after_run_index:
        raise ValidationError("workflow boundary-after command must follow its step name")
    if previous_index >= after_name_index:
        raise ValidationError("workflow validate-route packet must finish before the Phase 1 handoff")


def validate_root(root: Path) -> None:
    for path in SURFACE_PATHS:
        rel = path.relative_to(ROOT)
        if not (root / rel).exists():
            raise ValidationError(f"missing required file: {root / rel}")

    workflow_text = read_text(root / WORKFLOW.relative_to(ROOT))
    makefile_text = read_text(root / MAKEFILE.relative_to(ROOT))
    phase2_closure_text = read_text(root / PHASE2_CLOSURE.relative_to(ROOT))
    tests_readme_text = read_text(root / TESTS_README.relative_to(ROOT))
    validator_text = read_text(root / PHASE2_VALIDATOR.relative_to(ROOT))
    manifest_text = read_text(root / TOOL_MANIFEST.relative_to(ROOT))

    validate_workflow(workflow_text)

    for line in MAKEFILE_LINES:
        require_exact_line(makefile_text, line, f"Makefile line {line}")

    require_markers(phase2_closure_text, PHASE2_CLOSURE_MARKERS, "phase2 closure note")
    require_markers(tests_readme_text, TESTS_README_MARKERS, "tests README")
    require_markers(validator_text, VALIDATOR_MARKERS, "validate-phase2.py")
    require_markers(manifest_text, MANIFEST_MARKERS, "phase2 tool manifest")


SAMPLE_WORKFLOW = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Run current Phase 2 genksyms unit replay
        run: zig test scripts/zigux/genksyms.zig
      - name: Run current Phase 2 validate make route
        run: make -C zigux phase2-validate
      - name: Validate current Phase 2 tool packet
        run: python3 scripts/zigux/validate-phase2.py
      - name: Self-test current Phase 1 direct-owner checker
        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
"""

SAMPLE_MAKEFILE = """PYTHON ?= python3
PHASE2_SCRIPT_ROOT := ../scripts/zigux

phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py
	$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py

phase2: phase2-validate
"""

SAMPLE_PHASE2_CLOSURE = """# Phase 2 Closure

- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `make -C zigux phase2-validate`
- `make -C zigux phase2`
- `python3 scripts/zigux/validate-phase2.py`
"""

SAMPLE_TESTS_README = """# zigux/tests

- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `make -C zigux phase2-validate`
- `make -C zigux phase2`
Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.
"""

SAMPLE_VALIDATOR = """REQUIRED_WORKFLOW_LINES = (
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)
REQUIRED_MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)
"""

SAMPLE_MANIFEST = """{
  "present_surfaces": {
    "validators": [
      "scripts/zigux/validate-phase2.py",
      "scripts/zigux/validate-phase2-closure.py"
    ],
    "make_wrappers": [
      "zigux/Makefile",
      "make -C zigux phase2-validate",
      "make -C zigux phase2"
    ]
  }
}
"""


def write_sample_root(root: Path) -> None:
    write_text(root / WORKFLOW.relative_to(ROOT), SAMPLE_WORKFLOW)
    write_text(root / MAKEFILE.relative_to(ROOT), SAMPLE_MAKEFILE)
    write_text(root / PHASE2_CLOSURE.relative_to(ROOT), SAMPLE_PHASE2_CLOSURE)
    write_text(root / TESTS_README.relative_to(ROOT), SAMPLE_TESTS_README)
    write_text(root / PHASE2_VALIDATOR.relative_to(ROOT), SAMPLE_VALIDATOR)
    write_text(root / TOOL_MANIFEST.relative_to(ROOT), SAMPLE_MANIFEST)
    for path in SURFACE_PATHS:
        rel = path.relative_to(ROOT)
        if rel in (
            WORKFLOW.relative_to(ROOT),
            MAKEFILE.relative_to(ROOT),
            PHASE2_CLOSURE.relative_to(ROOT),
            TESTS_README.relative_to(ROOT),
            PHASE2_VALIDATOR.relative_to(ROOT),
            TOOL_MANIFEST.relative_to(ROOT),
        ):
            continue
        write_text(root / rel, "present\n")


def run_self_test() -> int:
    case_count = 0

    def expect_pass(mutator=None) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane03_validate_route_pass_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            if mutator is not None:
                mutator(root)
            validate_root(root)
            case_count += 1

    def expect_fail(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane03_validate_route_fail_") as tmp_dir:
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
                "run: make -C zigux phase2-validate\n",
                "",
            ),
        ),
        "workflow command run: make -C zigux phase2-validate must appear exactly once",
    )
    expect_fail(
        lambda root: write_text(
            root / WORKFLOW.relative_to(ROOT),
            read_text(root / WORKFLOW.relative_to(ROOT)).replace(
                "      - name: Validate current Phase 2 tool packet\n"
                "        run: python3 scripts/zigux/validate-phase2.py\n"
                "      - name: Self-test current Phase 1 direct-owner checker\n"
                "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test\n",
                "      - name: Self-test current Phase 1 direct-owner checker\n"
                "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test\n"
                "      - name: Validate current Phase 2 tool packet\n"
                "        run: python3 scripts/zigux/validate-phase2.py\n",
            ),
        ),
        "workflow validate-route packet must finish before the Phase 1 handoff",
    )
    expect_fail(
        lambda root: write_text(
            root / MAKEFILE.relative_to(ROOT),
            read_text(root / MAKEFILE.relative_to(ROOT)).replace(
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py\n",
                "",
            ),
        ),
        "Makefile line $(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py must appear exactly once",
    )
    expect_fail(
        lambda root: write_text(
            root / PHASE2_VALIDATOR.relative_to(ROOT),
            read_text(root / PHASE2_VALIDATOR.relative_to(ROOT)).replace(
                "\"run: python3 scripts/zigux/validate-phase2.py\",",
                "",
            ),
        ),
        "validate-phase2.py missing marker: \"run: python3 scripts/zigux/validate-phase2.py\",",
    )
    expect_fail(
        lambda root: write_text(
            root / TOOL_MANIFEST.relative_to(ROOT),
            read_text(root / TOOL_MANIFEST.relative_to(ROOT)).replace(
                "\"make -C zigux phase2-validate\"",
                "\"make -C zigux phase2-other\"",
                1,
            ),
        ),
        "phase2 tool manifest missing marker: \"make -C zigux phase2-validate\"",
    )
    expect_fail(
        lambda root: (root / TESTS_README.relative_to(ROOT)).unlink(),
        "missing required file:",
    )

    print("PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Lane 03 bootstrap Phase 2 validate-route packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root to validate.")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root and exit.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    try:
        validate_root(args.root.resolve())
    except ValidationError as exc:
        print("PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET=fail")
        print(f"PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET_ROOT={args.root}")
        print(f"PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET_NOTE={exc}")
        return 1

    print("PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET_ROOT={args.root}")
    print(f"PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET_WORKFLOW_STEP_COUNT={len(WORKFLOW_PACKET_STEPS)}")
    print(f"PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET_MAKE_LINE_COUNT={len(MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

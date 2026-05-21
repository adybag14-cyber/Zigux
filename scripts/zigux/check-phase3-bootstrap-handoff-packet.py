#!/usr/bin/env python3
"""Guard the current Lane 03 Phase 1 to Phase 3 bootstrap handoff packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else Path.cwd()

WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
PHASE3_SELFTEST = ROOT / "scripts" / "zigux" / "validate_phase3_selftest.py"
PHASE3_RUNNER = ROOT / "scripts" / "zigux" / "run-phase3-checks.py"
PHASE3_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase3.py"
PHASE3_SHARED_ROUTES = ROOT / "scripts" / "zigux" / "check-phase3-shared-tests-routes.py"
PHASE3_SELFTEST_SURFACE = ROOT / "scripts" / "zigux" / "check-phase3-selftest-surface.py"
PHASE3_LOW_LEVEL_SURVEY = (
    ROOT / "scripts" / "zigux" / "validate-phase3-low-level-wrapper-survey.py"
)

SURFACE_PATHS = (
    WORKFLOW,
    MAKEFILE,
    SCRIPTS_README,
    PHASE3_SELFTEST,
    PHASE3_RUNNER,
    PHASE3_VALIDATOR,
    PHASE3_SHARED_ROUTES,
    PHASE3_SELFTEST_SURFACE,
    PHASE3_LOW_LEVEL_SURVEY,
)

WORKFLOW_BOUNDARY_BEFORE = (
    "Check current Phase 1 closure packet",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
)
WORKFLOW_PACKET_STEPS = (
    (
        "Self-test current Phase 3 interop packet",
        "run: python3 scripts/zigux/validate_phase3_selftest.py",
    ),
    (
        "Check current Phase 3 interop packet",
        "run: python3 scripts/zigux/run-phase3-checks.py",
    ),
    (
        "Run current Phase 3 policy starter-packet replay",
        "run: make -C zigux phase3-policy-starter-packet-test",
    ),
    (
        "Run current Phase 3 policy dump replay",
        "run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    ),
    (
        "Self-test current Phase 3 low-level wrapper survey validator",
        "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    ),
    (
        "Check current Phase 3 low-level wrapper survey packet",
        "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    ),
    (
        "Run current Phase 3 low-level wrapper replay",
        "run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    (
        "Run current Phase 3 shared tests-root packet",
        "run: zig build phase3-test --build-file zigux/tests/build.zig",
    ),
    (
        "Run current Phase 3 ABI dump replay",
        "run: zig build phase3-dump --build-file zigux/tests/build.zig",
    ),
)
WORKFLOW_BOUNDARY_AFTER = (
    "Run current Phase 1 shared tests-root smoke",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

MAKEFILE_LINES = (
    "phase3-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py",
    "phase3-dump:",
    "phase3-low-level-wrappers-test:",
    "phase3-policy-starter-packet-test:",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-low-level-wrappers phase3-test phase3-policy-dump phase3-dump",
)

SCRIPTS_README_MARKERS = (
    "- Phase 3 flow - the current scripts-root ABI/runtime packet stays reviewable through the bounded `dev_t` starter packet, the focused helper-local `err_ptr` / `xarray` slice, the directly readable `xarray_slot` starter-and-checker packet, the focused policy slice with the returned notifier binding companion plus the dedicated policy-dump and policy-unsafe survey guards, the dedicated validator-support and selftest reminder guards, the adjacent low-level-wrapper packet, the packet-local export/UAPI survey note plus validator, the directly readable catalog helper, and the dedicated export/UAPI layout replay pair instead of rebuilding the broader export/UAPI, catalog-selftest, closure, or shared replay story from routes that current `master` still does not serve",
    "- `python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test`, `python3 scripts/zigux/check-phase3-selftest-surface.py --self-test`, `python3 scripts/zigux/validate-phase3-validator-support-surface.py --self-test`, and `python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test` replay the shipped Phase 3 scripts-root reminder checks",
    "- `python3 scripts/zigux/check-phase3-readme-tooling-inventory.py`, `scripts/zigux/check-phase3-selftest-surface.py`, `scripts/zigux/check-phase3-shared-tests-routes.py`, `scripts/zigux/validate-phase3-validator-support-surface.py`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `scripts/zigux/validate-phase3-abi-header-family-survey.py`, `scripts/zigux/validate-phase3-policy-unsafe-survey.py`, `scripts/zigux/validate_phase3_selftest.py`, `scripts/zigux/run-phase3-checks.py`, `scripts/zigux/validate-phase3.py`, `scripts/zigux/phase3_catalog.py`, `scripts/zigux/check-phase3-catalog-selftest.py`, `scripts/zigux/check-phase3-dev-t-starter-packet.py`, `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`, `scripts/zigux/check-phase3-xarray-slot-starter-packet.py`, `scripts/zigux/check-phase3-policy-starter-packet.py`, `scripts/zigux/check-phase3-policy-dump.py`, and `scripts/zigux/validate-phase3-low-level-wrapper-survey.py` keep the shipped scripts-root validation packet explicit on current `master`",
    "- `zigux/tests/phase3_dev_t_starter_packet.zig`, `zigux/tests/phase3_dev_t_starter_packet_build.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`, `zigux/tests/phase3_xarray_slot_starter_packet.zig`, `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`, `zigux/tests/build.zig`, `zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig`, `zigux/tests/phase3_policy_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet_build.zig`, `zigux/tests/phase3_policy_dump.zig`, `zigux/tests/phase3_policy_dump_build.zig`, `zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, and `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`, and `.github/workflows/zigux-bootstrap.yml` keep the current starter-packet, policy-dump replay, wrapper replay, focused export/UAPI layout replay, and CI-backed reminder surfaces explicit",
)

PHASE3_SELFTEST_MARKERS = (
    'Path("scripts/zigux/run-phase3-checks.py")',
    '"PHASE3_CHECK_RUNNER_SELF_TEST=pass",',
    '"PHASE3_CHECK_RUNNER_SELF_TEST_CASE_COUNT=",',
    'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
    '"PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass",',
    '"PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=",',
    'Path("scripts/zigux/validate-phase3.py")',
    '"PHASE3_VALIDATION_SELF_TEST=pass",',
    '"PHASE3_VALIDATION_SELF_TEST_CASE_COUNT=",',
)

PHASE3_RUNNER_MARKERS = (
    'Path("scripts/zigux/validate-phase3.py")',
    '("PHASE3_VALIDATION=pass",),',
    'Path("scripts/zigux/check-phase3-shared-tests-routes.py")',
    '"validated zigux/tests/build.zig",',
    '"validated scripts/zigux/validate_phase3_selftest.py",',
    'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
    '"validated Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",',
    '"PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass",',
    'Path("scripts/zigux/check-phase3-selftest-surface.py")',
    '("validated scripts/zigux/README.md",),',
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
        raise ValidationError("workflow Phase 3 handoff packet must finish before the next smoke step")


def validate_root(root: Path) -> None:
    for path in SURFACE_PATHS:
        rel = path.relative_to(ROOT)
        if not (root / rel).exists():
            raise ValidationError(f"missing required file: {root / rel}")

    workflow_text = read_text(root / WORKFLOW.relative_to(ROOT))
    makefile_text = read_text(root / MAKEFILE.relative_to(ROOT))
    scripts_readme_text = read_text(root / SCRIPTS_README.relative_to(ROOT))
    phase3_selftest_text = read_text(root / PHASE3_SELFTEST.relative_to(ROOT))
    phase3_runner_text = read_text(root / PHASE3_RUNNER.relative_to(ROOT))

    validate_workflow(workflow_text)

    for line in MAKEFILE_LINES:
        require_exact_line(makefile_text, line, f"Makefile line {line}")

    require_markers(scripts_readme_text, SCRIPTS_README_MARKERS, "scripts README")
    require_markers(phase3_selftest_text, PHASE3_SELFTEST_MARKERS, "validate_phase3_selftest.py")
    require_markers(phase3_runner_text, PHASE3_RUNNER_MARKERS, "run-phase3-checks.py")


SAMPLE_WORKFLOW = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Check current Phase 1 closure packet
        run: python3 scripts/zigux/validate-phase1-closure.py
      - name: Self-test current Phase 3 interop packet
        run: python3 scripts/zigux/validate_phase3_selftest.py
      - name: Check current Phase 3 interop packet
        run: python3 scripts/zigux/run-phase3-checks.py
      - name: Run current Phase 3 policy starter-packet replay
        run: make -C zigux phase3-policy-starter-packet-test
      - name: Run current Phase 3 policy dump replay
        run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig
      - name: Self-test current Phase 3 low-level wrapper survey validator
        run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test
      - name: Check current Phase 3 low-level wrapper survey packet
        run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py
      - name: Run current Phase 3 low-level wrapper replay
        run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig
      - name: Run current Phase 3 shared tests-root packet
        run: zig build phase3-test --build-file zigux/tests/build.zig
      - name: Run current Phase 3 ABI dump replay
        run: zig build phase3-dump --build-file zigux/tests/build.zig
      - name: Run current Phase 1 shared tests-root smoke
        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig
"""

SAMPLE_MAKEFILE = """PYTHON ?= python3
ZIGUX_ROOT := ..

phase3-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py

phase3-dump:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig

phase3-low-level-wrappers-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig

phase3-policy-starter-packet-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig

phase3: phase3-validate phase3-export-uapi-layout phase3-low-level-wrappers phase3-test phase3-policy-dump phase3-dump
"""

SAMPLE_SCRIPTS_README = "\n".join(SCRIPTS_README_MARKERS) + "\n"
SAMPLE_PHASE3_SELFTEST = "\n".join(PHASE3_SELFTEST_MARKERS) + "\n"
SAMPLE_PHASE3_RUNNER = "\n".join(PHASE3_RUNNER_MARKERS) + "\n"


def write_sample_root(root: Path) -> None:
    write_text(root / WORKFLOW.relative_to(ROOT), SAMPLE_WORKFLOW)
    write_text(root / MAKEFILE.relative_to(ROOT), SAMPLE_MAKEFILE)
    write_text(root / SCRIPTS_README.relative_to(ROOT), SAMPLE_SCRIPTS_README)
    write_text(root / PHASE3_SELFTEST.relative_to(ROOT), SAMPLE_PHASE3_SELFTEST)
    write_text(root / PHASE3_RUNNER.relative_to(ROOT), SAMPLE_PHASE3_RUNNER)
    for path in SURFACE_PATHS:
        rel = path.relative_to(ROOT)
        if rel in (
            WORKFLOW.relative_to(ROOT),
            MAKEFILE.relative_to(ROOT),
            SCRIPTS_README.relative_to(ROOT),
            PHASE3_SELFTEST.relative_to(ROOT),
            PHASE3_RUNNER.relative_to(ROOT),
        ):
            continue
        write_text(root / rel, "present\n")


def run_self_test() -> int:
    case_count = 0

    def expect_pass(mutator=None) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane03_phase3_handoff_pass_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            if mutator is not None:
                mutator(root)
            validate_root(root)
            case_count += 1

    def expect_fail(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane03_phase3_handoff_fail_") as tmp_dir:
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
                "run: python3 scripts/zigux/run-phase3-checks.py\n", "", 1
            ),
        ),
        "workflow command run: python3 scripts/zigux/run-phase3-checks.py must appear exactly once",
    )
    expect_fail(
        lambda root: write_text(
            root / WORKFLOW.relative_to(ROOT),
            read_text(root / WORKFLOW.relative_to(ROOT)).replace(
                "      - name: Run current Phase 3 ABI dump replay\n"
                "        run: zig build phase3-dump --build-file zigux/tests/build.zig\n"
                "      - name: Run current Phase 1 shared tests-root smoke\n"
                "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
                "      - name: Run current Phase 1 shared tests-root smoke\n"
                "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n"
                "      - name: Run current Phase 3 ABI dump replay\n"
                "        run: zig build phase3-dump --build-file zigux/tests/build.zig\n",
            ),
        ),
        "workflow Phase 3 handoff packet must finish before the next smoke step",
    )
    expect_fail(
        lambda root: write_text(
            root / MAKEFILE.relative_to(ROOT),
            read_text(root / MAKEFILE.relative_to(ROOT)).replace(
                "phase3-policy-starter-packet-test:\n", "", 1
            ),
        ),
        "Makefile line phase3-policy-starter-packet-test: must appear exactly once",
    )
    expect_fail(
        lambda root: write_text(
            root / PHASE3_SELFTEST.relative_to(ROOT),
            read_text(root / PHASE3_SELFTEST.relative_to(ROOT)).replace(
                '"PHASE3_CHECK_RUNNER_SELF_TEST=pass",\n', "", 1
            ),
        ),
        'validate_phase3_selftest.py missing marker: "PHASE3_CHECK_RUNNER_SELF_TEST=pass",',
    )
    expect_fail(
        lambda root: write_text(
            root / PHASE3_RUNNER.relative_to(ROOT),
            read_text(root / PHASE3_RUNNER.relative_to(ROOT)).replace(
                '"PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass",\n', "", 1
            ),
        ),
        'run-phase3-checks.py missing marker: "PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass",',
    )
    expect_fail(
        lambda root: (root / SCRIPTS_README.relative_to(ROOT)).unlink(),
        "missing required file:",
    )

    print("PHASE3_BOOTSTRAP_HANDOFF_PACKET_SELF_TEST=pass")
    print(f"PHASE3_BOOTSTRAP_HANDOFF_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Lane 03 Phase 1 to Phase 3 bootstrap handoff packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root to validate.")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root and exit.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE3_BOOTSTRAP_HANDOFF_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    try:
        validate_root(args.root.resolve())
    except ValidationError as exc:
        print("PHASE3_BOOTSTRAP_HANDOFF_PACKET=fail")
        print(f"PHASE3_BOOTSTRAP_HANDOFF_PACKET_ROOT={args.root}")
        print(f"PHASE3_BOOTSTRAP_HANDOFF_PACKET_NOTE={exc}")
        return 1

    print("PHASE3_BOOTSTRAP_HANDOFF_PACKET=pass")
    print(f"PHASE3_BOOTSTRAP_HANDOFF_PACKET_ROOT={args.root}")
    print(f"PHASE3_BOOTSTRAP_HANDOFF_PACKET_WORKFLOW_STEP_COUNT={len(WORKFLOW_PACKET_STEPS)}")
    print(f"PHASE3_BOOTSTRAP_HANDOFF_PACKET_REQUIRED_FILE_COUNT={len(SURFACE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

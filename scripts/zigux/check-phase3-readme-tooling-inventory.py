#!/usr/bin/env python3
"""Fail-close the Phase 3 tooling inventory reminder, shared interop route markers, and shared Phase 4 route markers."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from tempfile import TemporaryDirectory


README_PATH = Path("scripts/zigux/README.md")
MAKEFILE_REL = Path("zigux/Makefile")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
PHASE3_VALIDATE_TARGET = "phase3-validate"
PHASE3_INTEROP_TARGET = "phase3-interop"
PHASE3_POLICY_UNSAFE_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-unsafe-focused-replay.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-unsafe-focused-replay.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
)
PHASE3_INTEROP_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig",
)
PHASE3_WORKFLOW_MARKERS = (
    "- name: Check discovered Phase 3 parity",
    "run: python3 scripts/zigux/run-phase3-checks.py",
)
PHASE4_VALIDATE_TARGET = "phase4-validate"
PHASE4_VALIDATE_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py",
)
PHASE4_VALIDATE_ROUTE_SNIPPET = (
    "- `make -C zigux phase4-validate` reruns the validator-first Phase 4 route, including "
    "`scripts/zigux/check-artifact-diff-contract.py`, "
    "`scripts/zigux/check-phase4-artifact-diff-determinism.py`, "
    "`scripts/zigux/check-phase4-gate-evidence.py`, and "
    "`scripts/zigux/check-phase4-workflow-route-counts.py`, before the shared "
    "`zigux/tests/phase4_build.zig` replay."
)
REQUIRED_MARKERS = (
    "validate-phase3.py",
    "validate_phase3_selftest.py",
    "check-phase3-selftest-surface.py",
    "check-phase3-readme-tooling-inventory.py",
    "check-phase3-abi-dump-gate.py",
    "check-phase3-catalog-selftest.py",
    "validate-phase3-policy-unsafe-survey.py",
    "check-phase3-policy-byte-guards.py",
    "check-phase3-policy-unsafe-focused-replay.py",
    "check-phase3-policy-unsafe-mmio-consumer.py",
    "validate-phase3-low-level-wrapper-survey.py",
    "validate-phase3-export-uapi-survey.py",
    "validate-phase3-abi-header-family-survey.py",
    "validate-phase3-validator-support-surface.py",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "validate-phase3-abi-bindings-syntax.py",
    "survey-phase3-abi-constant-parity.py",
    "phase3_catalog.py",
    "phase3_check_lib.py",
    "generate-phase3-check-wrappers.py",
    "run-phase3-checks.py",
    "generated `check-phase3-*.py` wrappers stay as compatibility entrypoints derived from the discovered slice catalog",
    "zigux/uapi/dev_t.zig",
    "python3 scripts/zigux/phase3_catalog.py --self-test",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "make -C zigux phase3-validate",
    "make -C zigux phase3-selftest",
    "make -C zigux phase3",
    "validate-phase4.py",
    "check-artifact-diff-contract.py",
    "check-phase4-gate-evidence.py",
    "check-phase4-artifact-diff-determinism.py",
    "check-phase4-workflow-route-counts.py",
    "make -C zigux phase4-validate",
    "make -C zigux phase4",
)
REQUIRED_README_SNIPPETS = (
    PHASE4_VALIDATE_ROUTE_SNIPPET,
)
# Keep this checker scoped to helpers the scripts README still presents directly.
# Broader Phase 2 replay surfaces currently live in docs/tests/make routes instead.
REQUIRED_REPO_FILES = (
    Path("scripts/zigux/check-phase2-toolchain-pin-scope.py"),
    Path("scripts/zigux/check-phase2-tests-readme-alignment.py"),
    Path("scripts/zigux/check-phase2-cross.py"),
    Path("scripts/zigux/check-phase2-cross-selftest-alignment.py"),
    Path("scripts/zigux/validate-phase3.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/check-phase3-selftest-surface.py"),
    Path("scripts/zigux/check-phase3-readme-tooling-inventory.py"),
    Path("scripts/zigux/check-phase3-abi-dump-gate.py"),
    Path("scripts/zigux/check-phase3-catalog-selftest.py"),
    Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),
    Path("scripts/zigux/check-phase3-policy-byte-guards.py"),
    Path("scripts/zigux/check-phase3-policy-unsafe-focused-replay.py"),
    Path("scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
    Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"),
    Path("scripts/zigux/validate-phase3-validator-support-surface.py"),
    Path("scripts/zigux/validate-phase3-abi-bindings-syntax.py"),
    Path("scripts/zigux/survey-phase3-abi-constant-parity.py"),
    Path("scripts/zigux/phase3_catalog.py"),
    Path("scripts/zigux/phase3_check_lib.py"),
    Path("scripts/zigux/generate-phase3-check-wrappers.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
    Path("scripts/zigux/validate-phase4.py"),
    Path("scripts/zigux/check-artifact-diff-contract.py"),
    Path("scripts/zigux/check-phase4-gate-evidence.py"),
    Path("scripts/zigux/check-phase4-workflow-route-counts.py"),
)


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing scripts README: {path}") from exc


def validate_text(text: str) -> list[str]:
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


def validate_readme_snippets(text: str) -> list[str]:
    return [snippet for snippet in REQUIRED_README_SNIPPETS if snippet not in text]


def validate_repo_files(repo_root: Path) -> list[str]:
    missing = []
    for rel_path in REQUIRED_REPO_FILES:
        if not (repo_root / rel_path).is_file():
            missing.append(f"missing repo file: {rel_path.as_posix()}")
    return missing


def _extract_make_target_commands(text: str, target: str) -> list[str] | None:
    target_header = f"{target}:"
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line != target_header:
            continue
        commands: list[str] = []
        for body_line in lines[index + 1 :]:
            if not body_line.startswith("\t"):
                break
            commands.append(body_line.strip())
        return commands
    return None


def validate_makefile(repo_root: Path) -> list[str]:
    makefile_path = repo_root / MAKEFILE_REL
    try:
        makefile_text = makefile_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing repo file: {MAKEFILE_REL.as_posix()}"]

    issues: list[str] = []

    phase3_commands = _extract_make_target_commands(makefile_text, PHASE3_VALIDATE_TARGET)
    if phase3_commands is None:
        issues.append(f"missing_makefile_target:{PHASE3_VALIDATE_TARGET}")
    else:
        issues.extend(
            f"missing_makefile_command:{PHASE3_VALIDATE_TARGET}:{command}"
            for command in PHASE3_POLICY_UNSAFE_COMMANDS
            if command not in phase3_commands
        )
        ordered_phase3_policy_unsafe_commands = tuple(
            command for command in phase3_commands if command in PHASE3_POLICY_UNSAFE_COMMANDS
        )
        if ordered_phase3_policy_unsafe_commands != PHASE3_POLICY_UNSAFE_COMMANDS:
            issues.append(f"makefile_command_order_drift:{PHASE3_VALIDATE_TARGET}:policy_unsafe_support")

    phase3_interop_commands = _extract_make_target_commands(
        makefile_text,
        PHASE3_INTEROP_TARGET,
    )
    if phase3_interop_commands is None:
        issues.append(f"missing_makefile_target:{PHASE3_INTEROP_TARGET}")
    else:
        issues.extend(
            f"missing_makefile_command:{PHASE3_INTEROP_TARGET}:{command}"
            for command in PHASE3_INTEROP_COMMANDS
            if command not in phase3_interop_commands
        )

    commands = _extract_make_target_commands(makefile_text, PHASE4_VALIDATE_TARGET)
    if commands is None:
        issues.append(f"missing_makefile_target:{PHASE4_VALIDATE_TARGET}")
        return issues

    issues.extend(
        f"missing_makefile_command:{PHASE4_VALIDATE_TARGET}:{command}"
        for command in PHASE4_VALIDATE_COMMANDS
        if command not in commands
    )
    if tuple(commands) != PHASE4_VALIDATE_COMMANDS:
        issues.append(f"makefile_command_order_drift:{PHASE4_VALIDATE_TARGET}")
    return issues


def validate_workflow(repo_root: Path) -> list[str]:
    workflow_path = repo_root / WORKFLOW_REL
    try:
        workflow_text = workflow_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing repo file: {WORKFLOW_REL.as_posix()}"]

    return [
        f"missing_workflow_marker:{marker}"
        for marker in PHASE3_WORKFLOW_MARKERS
        if marker not in workflow_text
    ]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _populate_repo_files(root: Path) -> None:
    for rel_path in REQUIRED_REPO_FILES:
        _write(root / rel_path, "# stub\n")
    _write(root / MAKEFILE_REL, _baseline_makefile())
    _write(root / WORKFLOW_REL, _baseline_workflow())


def _baseline_makefile() -> str:
    phase3_body = "\n".join(f"\t{command}" for command in PHASE3_POLICY_UNSAFE_COMMANDS)
    phase3_interop_body = "\n".join(
        f"\t{command}" for command in PHASE3_INTEROP_COMMANDS
    )
    phase4_body = "\n".join(f"\t{command}" for command in PHASE4_VALIDATE_COMMANDS)
    return (
        f"{PHASE3_VALIDATE_TARGET}:\n{phase3_body}\n\n"
        f"{PHASE3_INTEROP_TARGET}:\n{phase3_interop_body}\n\n"
        f"{PHASE4_VALIDATE_TARGET}:\n{phase4_body}\n"
    )


def _baseline_workflow() -> str:
    return "\n".join(PHASE3_WORKFLOW_MARKERS) + "\n"


def run_self_test() -> int:
    sample = "\n".join(REQUIRED_MARKERS) + "\n\n" + "\n".join(REQUIRED_README_SNIPPETS)
    missing = validate_text(sample)
    if missing:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("\n".join(missing))
        return 1

    missing = validate_readme_snippets(sample)
    if missing:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("\n".join(missing))
        return 1

    broken = validate_text(sample.replace("Documentation/zigux/phase3-abi-h-boundary-next-step.md", "", 1))
    if "Documentation/zigux/phase3-abi-h-boundary-next-step.md" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected missing marker was not reported")
        return 1

    broken = validate_text(sample.replace("validate-phase3-abi-header-family-survey.py", "", 1))
    if "validate-phase3-abi-header-family-survey.py" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected header-family validator marker was not reported")
        return 1

    broken = validate_text(sample.replace("validate-phase3-validator-support-surface.py", "", 1))
    if "validate-phase3-validator-support-surface.py" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected validator-support surface marker was not reported")
        return 1

    broken = validate_text(sample.replace("Documentation/zigux/phase3-validator-support-surface.md", "", 1))
    if "Documentation/zigux/phase3-validator-support-surface.md" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected validator-support note marker was not reported")
        return 1

    broken = validate_text(sample.replace("check-phase3-policy-unsafe-focused-replay.py", "", 1))
    if "check-phase3-policy-unsafe-focused-replay.py" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected policy-unsafe focused-replay marker was not reported")
        return 1

    broken = validate_text(sample.replace("check-phase3-policy-unsafe-mmio-consumer.py", "", 1))
    if "check-phase3-policy-unsafe-mmio-consumer.py" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected policy-unsafe mmio-consumer marker was not reported")
        return 1

    broken = validate_text(sample.replace("Documentation/zigux/phase3-boundary-lane-sequencing.md", "", 1))
    if "Documentation/zigux/phase3-boundary-lane-sequencing.md" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected boundary-lane sequencing marker was not reported")
        return 1

    broken = validate_text(sample.replace("Documentation/zigux/phase3-export-uapi-boundary-survey.md", "", 1))
    if "Documentation/zigux/phase3-export-uapi-boundary-survey.md" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected export-uapi boundary marker was not reported")
        return 1

    broken = validate_text(sample.replace("make -C zigux phase3-selftest", "", 1))
    if "make -C zigux phase3-selftest" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected phase3 selftest route marker was not reported")
        return 1

    broken = validate_text(
        sample.replace(
            "generated `check-phase3-*.py` wrappers stay as compatibility entrypoints derived from the discovered slice catalog",
            "",
            1,
        )
    )
    if (
        "generated `check-phase3-*.py` wrappers stay as compatibility entrypoints derived from the discovered slice catalog"
        not in broken
    ):
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected compatibility-entrypoint marker was not reported")
        return 1

    broken = validate_readme_snippets(sample.replace(PHASE4_VALIDATE_ROUTE_SNIPPET, "", 1))
    if PHASE4_VALIDATE_ROUTE_SNIPPET not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected phase4 validate sentence was not reported")
        return 1

    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write(root / README_PATH, sample)
        _populate_repo_files(root)
        broken = validate_repo_files(root)
        if broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("\n".join(broken))
            return 1

        broken = validate_workflow(root)
        if broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("\n".join(broken))
            return 1

        missing_phase2_toolchain_pin_scope_path = Path("scripts/zigux/check-phase2-toolchain-pin-scope.py")
        (root / missing_phase2_toolchain_pin_scope_path).unlink()
        broken = validate_repo_files(root)
        expected = f"missing repo file: {missing_phase2_toolchain_pin_scope_path.as_posix()}"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 2 toolchain-pin-scope repo file was not reported")
            return 1
        _write(root / missing_phase2_toolchain_pin_scope_path, "# stub\n")

        missing_phase2_tests_readme_alignment_path = Path("scripts/zigux/check-phase2-tests-readme-alignment.py")
        (root / missing_phase2_tests_readme_alignment_path).unlink()
        broken = validate_repo_files(root)
        expected = f"missing repo file: {missing_phase2_tests_readme_alignment_path.as_posix()}"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 2 tests-readme-alignment repo file was not reported")
            return 1
        _write(root / missing_phase2_tests_readme_alignment_path, "# stub\n")

        missing_phase2_cross_path = Path("scripts/zigux/check-phase2-cross.py")
        (root / missing_phase2_cross_path).unlink()
        broken = validate_repo_files(root)
        expected = f"missing repo file: {missing_phase2_cross_path.as_posix()}"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 2 cross repo file was not reported")
            return 1
        _write(root / missing_phase2_cross_path, "# stub\n")

        missing_phase2_cross_selftest_alignment_path = Path("scripts/zigux/check-phase2-cross-selftest-alignment.py")
        (root / missing_phase2_cross_selftest_alignment_path).unlink()
        broken = validate_repo_files(root)
        expected = f"missing repo file: {missing_phase2_cross_selftest_alignment_path.as_posix()}"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 2 cross-selftest-alignment repo file was not reported")
            return 1
        _write(root / missing_phase2_cross_selftest_alignment_path, "# stub\n")

        missing_phase3_path = Path("scripts/zigux/phase3_catalog.py")
        (root / missing_phase3_path).unlink()
        broken = validate_repo_files(root)
        expected = f"missing repo file: {missing_phase3_path.as_posix()}"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 3 repo file was not reported")
            return 1
        _write(root / missing_phase3_path, "# stub\n")

        missing_validator_support_path = Path("scripts/zigux/validate-phase3-validator-support-surface.py")
        (root / missing_validator_support_path).unlink()
        broken = validate_repo_files(root)
        expected = f"missing repo file: {missing_validator_support_path.as_posix()}"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing validator-support surface repo file was not reported")
            return 1
        _write(root / missing_validator_support_path, "# stub\n")

        missing_phase4_path = Path("scripts/zigux/check-phase4-gate-evidence.py")
        (root / missing_phase4_path).unlink()
        broken = validate_repo_files(root)
        expected = f"missing repo file: {missing_phase4_path.as_posix()}"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 4 repo file was not reported")
            return 1
        _write(root / missing_phase4_path, "# stub\n")

        missing_phase4_workflow_path = Path("scripts/zigux/check-phase4-workflow-route-counts.py")
        (root / missing_phase4_workflow_path).unlink()
        broken = validate_repo_files(root)
        expected = f"missing repo file: {missing_phase4_workflow_path.as_posix()}"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 4 workflow-route repo file was not reported")
            return 1
        _write(root / missing_phase4_workflow_path, "# stub\n")

        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n",
            "",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        broken = validate_makefile(root)
        expected = (
            "missing_makefile_command:phase4-validate:"
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py"
        )
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 4 gate-evidence makefile command was not reported")
            return 1
        if f"makefile_command_order_drift:{PHASE4_VALIDATE_TARGET}" not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected Phase 4 makefile command order drift was not reported")
            return 1

        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-unsafe-focused-replay.py\n",
            "",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        broken = validate_makefile(root)
        expected = (
            "missing_makefile_command:phase3-validate:"
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-unsafe-focused-replay.py"
        )
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 3 focused-replay makefile command was not reported")
            return 1
        if f"makefile_command_order_drift:{PHASE3_VALIDATE_TARGET}:policy_unsafe_support" not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected Phase 3 policy-unsafe makefile command order drift was not reported")
            return 1
        _write(root / MAKEFILE_REL, _baseline_makefile())

        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py --self-test\n",
            "",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        broken = validate_makefile(root)
        expected = (
            "missing_makefile_command:phase3-validate:"
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py --self-test"
        )
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 3 mmio-consumer self-test makefile command was not reported")
            return 1
        if f"makefile_command_order_drift:{PHASE3_VALIDATE_TARGET}:policy_unsafe_support" not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected Phase 3 policy-unsafe makefile command order drift was not reported")
            return 1

        _write(root / MAKEFILE_REL, _baseline_makefile())
        makefile = _baseline_makefile().replace(
            "phase3-interop:\n",
            "phase3-interop-shadow:\n",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        broken = validate_makefile(root)
        expected = f"missing_makefile_target:{PHASE3_INTEROP_TARGET}"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 3 interop target was not reported")
            return 1

        _write(root / MAKEFILE_REL, _baseline_makefile())
        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py\n",
            "",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        broken = validate_makefile(root)
        expected = (
            "missing_makefile_command:phase3-interop:"
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/run-phase3-checks.py"
        )
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 3 interop runner command was not reported")
            return 1

        _write(root / MAKEFILE_REL, _baseline_makefile())
        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig\n",
            "",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        broken = validate_makefile(root)
        expected = (
            "missing_makefile_command:phase3-interop:"
            "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig"
        )
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 3 interop dump command was not reported")
            return 1

        _write(root / WORKFLOW_REL, _baseline_workflow().replace(
            "- name: Check discovered Phase 3 parity\n",
            "",
            1,
        ))
        broken = validate_workflow(root)
        expected = "missing_workflow_marker:- name: Check discovered Phase 3 parity"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 3 workflow step name was not reported")
            return 1

        _write(root / WORKFLOW_REL, _baseline_workflow().replace(
            "run: python3 scripts/zigux/run-phase3-checks.py\n",
            "",
            1,
        ))
        broken = validate_workflow(root)
        expected = "missing_workflow_marker:run: python3 scripts/zigux/run-phase3-checks.py"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 3 workflow parity command was not reported")
            return 1

    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains scripts/zigux/README.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in validator coverage without reading repo files",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    readme_path = args.repo_root / README_PATH
    text = load_text(readme_path)
    missing = validate_text(text)
    missing.extend(
        f"missing_readme_snippet:{snippet}"
        for snippet in validate_readme_snippets(text)
    )
    missing.extend(validate_repo_files(args.repo_root))
    missing.extend(validate_makefile(args.repo_root))
    missing.extend(validate_workflow(args.repo_root))
    if missing:
        for entry in missing:
            if entry.startswith("missing repo file: "):
                print(entry, file=sys.stderr)
            else:
                print(f"missing marker: {entry}", file=sys.stderr)
        return 1

    print(f"validated {readme_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

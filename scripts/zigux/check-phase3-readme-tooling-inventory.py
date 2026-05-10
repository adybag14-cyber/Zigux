#!/usr/bin/env python3
"""Fail-close the Phase 3 tooling inventory reminder and shared Phase 4 route markers."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from tempfile import TemporaryDirectory


README_PATH = Path("scripts/zigux/README.md")
MAKEFILE_REL = Path("zigux/Makefile")
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
REQUIRED_MARKERS = (
    "validate-phase3.py",
    "validate_phase3_selftest.py",
    "check-phase3-selftest-surface.py",
    "check-phase3-readme-tooling-inventory.py",
    "check-phase3-abi-dump-gate.py",
    "check-phase3-catalog-selftest.py",
    "validate-phase3-policy-unsafe-survey.py",
    "check-phase3-policy-byte-guards.py",
    "validate-phase3-low-level-wrapper-survey.py",
    "validate-phase3-export-uapi-survey.py",
    "validate-phase3-abi-header-family-survey.py",
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
REQUIRED_REPO_FILES = (
    Path("scripts/zigux/check-phase2-toolchain-pin-scope.py"),
    Path("scripts/zigux/check-phase2-cross.py"),
    Path("scripts/zigux/validate-phase3.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/check-phase3-selftest-surface.py"),
    Path("scripts/zigux/check-phase3-readme-tooling-inventory.py"),
    Path("scripts/zigux/check-phase3-abi-dump-gate.py"),
    Path("scripts/zigux/check-phase3-catalog-selftest.py"),
    Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),
    Path("scripts/zigux/check-phase3-policy-byte-guards.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
    Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"),
    Path("scripts/zigux/validate-phase3-abi-bindings-syntax.py"),
    Path("scripts/zigux/survey-phase3-abi-constant-parity.py"),
    Path("scripts/zigux/phase3_catalog.py"),
    Path("scripts/zigux/phase3_check_lib.py"),
    Path("scripts/zigux/generate-phase3-check-wrappers.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
    Path("scripts/zigux/validate-phase4.py"),
    Path("scripts/zigux/check-artifact-diff-contract.py"),
    Path("scripts/zigux/check-phase4-gate-evidence.py"),
    Path("scripts/zigux/check-phase4-artifact-diff-determinism.py"),
    Path("scripts/zigux/check-phase4-workflow-route-counts.py"),
)


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing scripts README: {path}") from exc


def validate_text(text: str) -> list[str]:
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


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

    commands = _extract_make_target_commands(makefile_text, PHASE4_VALIDATE_TARGET)
    if commands is None:
        return [f"missing_makefile_target:{PHASE4_VALIDATE_TARGET}"]

    issues = [
        f"missing_makefile_command:{PHASE4_VALIDATE_TARGET}:{command}"
        for command in PHASE4_VALIDATE_COMMANDS
        if command not in commands
    ]
    if tuple(commands) != PHASE4_VALIDATE_COMMANDS:
        issues.append(f"makefile_command_order_drift:{PHASE4_VALIDATE_TARGET}")
    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _populate_repo_files(root: Path) -> None:
    for rel_path in REQUIRED_REPO_FILES:
        _write(root / rel_path, "# stub\n")
    _write(root / MAKEFILE_REL, _baseline_makefile())


def _baseline_makefile() -> str:
    body = "\n".join(f"\t{command}" for command in PHASE4_VALIDATE_COMMANDS)
    return f"{PHASE4_VALIDATE_TARGET}:\n{body}\n"


def run_self_test() -> int:
    sample = "\n".join(REQUIRED_MARKERS)
    missing = validate_text(sample)
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

    broken = validate_text(sample.replace("make -C zigux phase3-selftest", "", 1))
    if "make -C zigux phase3-selftest" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected phase3 selftest route marker was not reported")
        return 1

    broken = validate_text(sample.replace("check-phase4-gate-evidence.py", "", 1))
    if "check-phase4-gate-evidence.py" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected phase4 gate-evidence marker was not reported")
        return 1

    broken = validate_text(sample.replace("make -C zigux phase4-validate", "", 1))
    if "make -C zigux phase4-validate" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected phase4 validate route marker was not reported")
        return 1

    broken = validate_text(sample.replace("check-phase4-workflow-route-counts.py", "", 1))
    if "check-phase4-workflow-route-counts.py" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected phase4 workflow-route-counts marker was not reported")
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

    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write(root / README_PATH, sample)
        _populate_repo_files(root)
        broken = validate_repo_files(root)
        if broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("\n".join(broken))
            return 1

        missing_phase3_path = Path("scripts/zigux/phase3_catalog.py")
        (root / missing_phase3_path).unlink()
        broken = validate_repo_files(root)
        expected = f"missing repo file: {missing_phase3_path.as_posix()}"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 3 repo file was not reported")
            return 1
        _write(root / missing_phase3_path, "# stub\n")

        missing_phase4_path = Path("scripts/zigux/check-phase4-gate-evidence.py")
        (root / missing_phase4_path).unlink()
        broken = validate_repo_files(root)
        expected = f"missing repo file: {missing_phase4_path.as_posix()}"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 4 repo file was not reported")
            return 1
        _write(root / missing_phase4_path, "# stub\n")

        missing_phase2_toolchain_path = Path("scripts/zigux/check-phase2-toolchain-pin-scope.py")
        (root / missing_phase2_toolchain_path).unlink()
        broken = validate_repo_files(root)
        expected = f"missing repo file: {missing_phase2_toolchain_path.as_posix()}"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 2 toolchain-pin-scope repo file was not reported")
            return 1
        _write(root / missing_phase2_toolchain_path, "# stub\n")

        missing_phase2_cross_path = Path("scripts/zigux/check-phase2-cross.py")
        (root / missing_phase2_cross_path).unlink()
        broken = validate_repo_files(root)
        expected = f"missing repo file: {missing_phase2_cross_path.as_posix()}"
        if expected not in broken:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("expected missing Phase 2 cross repo file was not reported")
            return 1
        _write(root / missing_phase2_cross_path, "# stub\n")

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
    missing.extend(validate_repo_files(args.repo_root))
    missing.extend(validate_makefile(args.repo_root))
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

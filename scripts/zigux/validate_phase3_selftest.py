#!/usr/bin/env python3
"""Run the focused Phase 3 validator-support self-test packet."""

from __future__ import annotations

import argparse
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile


SELFTEST_COMMANDS = (
    (Path("scripts/zigux/validate-phase3.py"), ("--self-test",)),
    (Path("scripts/zigux/check-phase3-readme-tooling-inventory.py"), ("--self-test",)),
    (Path("scripts/zigux/check-phase3-selftest-surface.py"), ("--self-test",)),
    (Path("scripts/zigux/check-phase3-abi-dump-gate.py"), ("--self-test",)),
    (Path("scripts/zigux/check-phase3-catalog-selftest.py"), ("--self-test",)),
    (Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"), ("--self-test",)),
    (Path("scripts/zigux/check-phase3-policy-byte-guards.py"), ("--self-test",)),
    (Path("scripts/zigux/check-phase3-policy-unsafe-focused-replay.py"), ("--self-test",)),
    (Path("scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"), ("--self-test",)),
    (Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"), ("--self-test",)),
    (Path("scripts/zigux/validate-phase3-export-uapi-survey.py"), ("--self-test",)),
    (Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"), ("--self-test",)),
    (Path("scripts/zigux/validate-phase3-validator-support-surface.py"), ("--self-test",)),
    (Path("scripts/zigux/validate-phase3-abi-bindings-syntax.py"), ("--self-test",)),
    (Path("scripts/zigux/survey-phase3-abi-constant-parity.py"), ("--self-test",)),
    (Path("scripts/zigux/phase3_catalog.py"), ("--self-test",)),
    (Path("scripts/zigux/phase3_check_lib.py"), ("--self-test",)),
    (Path("scripts/zigux/generate-phase3-check-wrappers.py"), ("--self-test",)),
    (Path("scripts/zigux/run-phase3-checks.py"), ("--self-test",)),
)
MAKEFILE_PATH = Path("zigux/Makefile")
PHASE3_VALIDATE_TARGET = "phase3-validate"
PHASE3_SELFTEST_DRIVER_COMMAND = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py"
)
PHASE3_VALIDATE_SUPPORT_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check",
)
REQUIRED_SELFTEST_DRIVER_PATHS = (
    Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),
    Path("scripts/zigux/check-phase3-policy-byte-guards.py"),
    Path("scripts/zigux/check-phase3-policy-unsafe-focused-replay.py"),
    Path("scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"),
    Path("scripts/zigux/validate-phase3-validator-support-surface.py"),
    Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
)


def validate_driver_inventory(
    commands: tuple[tuple[Path, tuple[str, ...]], ...] = SELFTEST_COMMANDS,
) -> list[str]:
    command_paths = {rel_path for rel_path, _args in commands}
    return [
        f"missing selftest command entry: {rel_path.as_posix()}"
        for rel_path in REQUIRED_SELFTEST_DRIVER_PATHS
        if rel_path not in command_paths
    ]


def validate_script_list(repo_root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path, _args in SELFTEST_COMMANDS:
        if not (repo_root / rel_path).is_file():
            missing.append(f"missing selftest script: {rel_path.as_posix()}")
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


def _selftest_make_command(rel_path: Path, args: tuple[str, ...]) -> str:
    suffix = " ".join(args)
    return f"cd $(ZIGUX_ROOT) && $(PYTHON) {rel_path.as_posix()} {suffix}".rstrip()


def _required_phase3_validate_commands() -> tuple[str, ...]:
    commands = [PHASE3_SELFTEST_DRIVER_COMMAND, *PHASE3_VALIDATE_SUPPORT_COMMANDS]
    commands.extend(_selftest_make_command(rel_path, args) for rel_path, args in SELFTEST_COMMANDS)
    return tuple(commands)


def validate_makefile(repo_root: Path) -> list[str]:
    makefile_path = repo_root / MAKEFILE_PATH
    try:
        makefile_text = makefile_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing repo file: {MAKEFILE_PATH.as_posix()}"]

    commands = _extract_make_target_commands(makefile_text, PHASE3_VALIDATE_TARGET)
    if commands is None:
        return [f"missing make target: {PHASE3_VALIDATE_TARGET}"]

    issues: list[str] = []
    for command in _required_phase3_validate_commands():
        if command not in commands:
            issues.append(f"missing make command: {command}")

    return issues


def run_packet(repo_root: Path) -> int:
    missing = validate_driver_inventory()
    missing.extend(validate_script_list(repo_root))
    missing.extend(validate_makefile(repo_root))
    if missing:
        print("PHASE3_VALIDATE_SELFTEST=fail")
        print("\n".join(missing))
        return 1

    for rel_path, args in SELFTEST_COMMANDS:
        result = subprocess.run(
            [sys.executable, rel_path.as_posix(), *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("PHASE3_VALIDATE_SELFTEST=fail")
            print(
                "self-test failed: "
                + " ".join([rel_path.as_posix(), *args])
            )
            if result.stdout:
                print(result.stdout.rstrip())
            if result.stderr:
                print(result.stderr.rstrip())
            return 1

    print("PHASE3_VALIDATE_SELFTEST=pass")
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validate_selftest_") as temp_dir:
        root = Path(temp_dir)
        for rel_path, _args in SELFTEST_COMMANDS:
            path = root / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "#!/usr/bin/env python3\n"
                "raise SystemExit(0)\n",
                encoding="utf-8",
            )

        commands = list(_required_phase3_validate_commands())
        (root / MAKEFILE_PATH).parent.mkdir(parents=True, exist_ok=True)
        (root / MAKEFILE_PATH).write_text(
            PHASE3_VALIDATE_TARGET
            + ":\n"
            + "\n".join(f"\t{command}" for command in commands)
            + "\n",
            encoding="utf-8",
        )

        if validate_driver_inventory():
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected synthetic selftest command inventory to validate")
            return 1
        if validate_script_list(root):
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected synthetic self-test script set to validate")
            return 1
        if validate_makefile(root):
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected synthetic makefile self-test route to validate")
            return 1

        for required_path in REQUIRED_SELFTEST_DRIVER_PATHS:
            missing = validate_driver_inventory(
                tuple(
                    entry
                    for entry in SELFTEST_COMMANDS
                    if entry[0] != required_path
                )
            )
            expected = f"missing selftest command entry: {required_path.as_posix()}"
            if expected not in missing:
                print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
                print(
                    "expected missing selftest command entry was not reported: "
                    f"{required_path.as_posix()}"
                )
                return 1

        first_path = SELFTEST_COMMANDS[0][0]
        (root / first_path).unlink()
        missing = validate_script_list(root)
        expected = f"missing selftest script: {first_path.as_posix()}"
        if expected not in missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing script was not reported")
            return 1

        (root / first_path).write_text(
            "#!/usr/bin/env python3\n"
            "raise SystemExit(0)\n",
            encoding="utf-8",
        )
        makefile = (root / MAKEFILE_PATH).read_text(encoding="utf-8").replace(
            "\t"
            + _selftest_make_command(SELFTEST_COMMANDS[-1][0], SELFTEST_COMMANDS[-1][1])
            + "\n",
            "",
            1,
        )
        (root / MAKEFILE_PATH).write_text(makefile, encoding="utf-8")
        missing = validate_makefile(root)
        expected = (
            "missing make command: "
            + _selftest_make_command(SELFTEST_COMMANDS[-1][0], SELFTEST_COMMANDS[-1][1])
        )
        if expected not in missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing makefile self-test command was not reported")
            return 1

        commands = list(_required_phase3_validate_commands())
        (root / MAKEFILE_PATH).write_text(
            PHASE3_VALIDATE_TARGET
            + ":\n"
            + "\n".join(f"\t{command}" for command in commands)
            + "\n",
            encoding="utf-8",
        )
        makefile = (root / MAKEFILE_PATH).read_text(encoding="utf-8").replace(
            "\t" + PHASE3_SELFTEST_DRIVER_COMMAND + "\n",
            "",
            1,
        )
        (root / MAKEFILE_PATH).write_text(makefile, encoding="utf-8")
        missing = validate_makefile(root)
        expected = f"missing make command: {PHASE3_SELFTEST_DRIVER_COMMAND}"
        if expected not in missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing selftest driver makefile command was not reported")
            return 1

        commands = list(_required_phase3_validate_commands())
        (root / MAKEFILE_PATH).write_text(
            PHASE3_VALIDATE_TARGET
            + ":\n"
            + "\n".join(f"\t{command}" for command in commands)
            + "\n",
            encoding="utf-8",
        )
        makefile = (root / MAKEFILE_PATH).read_text(encoding="utf-8").replace(
            "\t" + PHASE3_VALIDATE_SUPPORT_COMMANDS[0] + "\n",
            "",
            1,
        )
        (root / MAKEFILE_PATH).write_text(makefile, encoding="utf-8")
        missing = validate_makefile(root)
        expected = f"missing make command: {PHASE3_VALIDATE_SUPPORT_COMMANDS[0]}"
        if expected not in missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing audit-doc-sync makefile command was not reported")
            return 1

        commands = list(_required_phase3_validate_commands())
        (root / MAKEFILE_PATH).write_text(
            PHASE3_VALIDATE_TARGET
            + ":\n"
            + "\n".join(f"\t{command}" for command in commands)
            + "\n",
            encoding="utf-8",
        )
        makefile = (root / MAKEFILE_PATH).read_text(encoding="utf-8").replace(
            "\t" + PHASE3_VALIDATE_SUPPORT_COMMANDS[1] + "\n",
            "",
            1,
        )
        (root / MAKEFILE_PATH).write_text(makefile, encoding="utf-8")
        missing = validate_makefile(root)
        expected = f"missing make command: {PHASE3_VALIDATE_SUPPORT_COMMANDS[1]}"
        if expected not in missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing wrapper-check makefile command was not reported")
            return 1

        commands = list(_required_phase3_validate_commands())
        (root / MAKEFILE_PATH).write_text(
            PHASE3_VALIDATE_TARGET
            + ":\n"
            + "\n".join(f"\t{command}" for command in commands)
            + "\n",
            encoding="utf-8",
        )
        failing_path = SELFTEST_COMMANDS[1][0]
        (root / failing_path).write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "print('intentional stdout breadcrumb')\n"
            "print('intentional stderr breadcrumb', file=sys.stderr)\n"
            "raise SystemExit(9)\n",
            encoding="utf-8",
        )
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            result = run_packet(root)
        if result == 0:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected non-zero self-test command to fail the packet")
            return 1
        output = buffer.getvalue()
        for marker in (
            "PHASE3_VALIDATE_SELFTEST=fail",
            "self-test failed: scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test",
            "intentional stdout breadcrumb",
            "intentional stderr breadcrumb",
        ):
            if marker not in output:
                print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
                print(f"expected failing self-test output marker was not reported: {marker}")
                return 1

    print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the focused Phase 3 validator-support self-test packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains scripts/zigux/",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_packet(args.repo_root)


if __name__ == "__main__":
    raise SystemExit(main())

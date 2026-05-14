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
    (Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py"), ("--self-test",)),
    (Path("scripts/zigux/validate-phase3-validator-support-surface.py"), ("--self-test",)),
    (Path("scripts/zigux/validate-phase3-abi-bindings-syntax.py"), ("--self-test",)),
    (Path("scripts/zigux/survey-phase3-abi-constant-parity.py"), ("--self-test",)),
    (Path("scripts/zigux/phase3_catalog.py"), ("--self-test",)),
    (Path("scripts/zigux/phase3_check_lib.py"), ("--self-test",)),
    (Path("scripts/zigux/generate-phase3-check-wrappers.py"), ("--self-test",)),
    (Path("scripts/zigux/run-phase3-checks.py"), ("--self-test",)),
)
SELFTEST_OUTPUT_MARKERS = {
    Path("scripts/zigux/check-phase3-selftest-surface.py"): (
        "PHASE3_SELFTEST_SURFACE_SELF_TEST=pass",
    ),
    Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"): (
        "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass",
        "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=12",
    ),
    Path("scripts/zigux/check-phase3-policy-byte-guards.py"): (
        "PHASE3_POLICY_BYTE_GUARDS_SELF_TEST=pass",
        "PHASE3_POLICY_BYTE_GUARDS_SELF_TEST_CASE_COUNT=13",
    ),
    Path("scripts/zigux/check-phase3-policy-unsafe-focused-replay.py"): (
        "PHASE3_POLICY_UNSAFE_PACKET_SELF_TEST=pass",
        "PHASE3_POLICY_UNSAFE_PACKET_SELF_TEST_CASE_COUNT=6",
    ),
    Path("scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"): (
        "PHASE3_POLICY_UNSAFE_MMIO_CONSUMER_SELF_TEST=pass",
        "PHASE3_POLICY_UNSAFE_MMIO_CONSUMER_SELF_TEST_CASE_COUNT=5",
    ),
    Path("scripts/zigux/validate-phase3-export-uapi-survey.py"): (
        "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass",
        "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT=15",
    ),
    Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"): (
        "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass",
    ),
    Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py"): (
        "PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass",
    ),
    Path("scripts/zigux/validate-phase3-validator-support-surface.py"): (
        "PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=pass",
    ),
}
MAKEFILE_PATH = Path("zigux/Makefile")
PHASE3_VALIDATE_TARGET = "phase3-validate"
PHASE3_SELFTEST_TARGET = "phase3-selftest"
PHASE3_SELFTEST_DRIVER_COMMAND = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate_phase3_selftest.py"
)
PHASE3_VALIDATE_SUPPORT_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/generate-phase3-check-wrappers.py --check",
)
INDIRECT_PHASE3_VALIDATE_COMMANDS = frozenset(
    {
        Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py"),
    }
)
REQUIRED_SELFTEST_DRIVER_PATHS = tuple(
    rel_path for rel_path, _args in SELFTEST_COMMANDS
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
    commands.extend(
        _selftest_make_command(rel_path, args)
        for rel_path, args in SELFTEST_COMMANDS
        if rel_path not in INDIRECT_PHASE3_VALIDATE_COMMANDS
    )
    return tuple(commands)


def _required_phase3_selftest_commands() -> tuple[str, ...]:
    return (PHASE3_SELFTEST_DRIVER_COMMAND,)


def _check_make_target_commands(
    text: str,
    target: str,
    required_commands: tuple[str, ...],
    label: str,
) -> list[str]:
    commands = _extract_make_target_commands(text, target)
    if commands is None:
        return [f"missing make target: {target}"]

    issues: list[str] = []
    for command in required_commands:
        if command not in commands:
            issues.append(f"missing {label} command: {command}")
    return issues


def validate_makefile(repo_root: Path) -> list[str]:
    makefile_path = repo_root / MAKEFILE_PATH
    try:
        makefile_text = makefile_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing repo file: {MAKEFILE_PATH.as_posix()}"]

    issues: list[str] = []
    issues.extend(
        _check_make_target_commands(
            makefile_text,
            PHASE3_VALIDATE_TARGET,
            _required_phase3_validate_commands(),
            PHASE3_VALIDATE_TARGET,
        )
    )
    issues.extend(
        _check_make_target_commands(
            makefile_text,
            PHASE3_SELFTEST_TARGET,
            _required_phase3_selftest_commands(),
            PHASE3_SELFTEST_TARGET,
        )
    )
    return issues


def _validate_selftest_output(rel_path: Path, stdout: str) -> list[str]:
    expected_markers = SELFTEST_OUTPUT_MARKERS.get(rel_path, ())
    if not expected_markers:
        return []

    stdout_lines = set(stdout.splitlines())
    return [
        f"missing selftest output marker: {rel_path.as_posix()}: {marker}"
        for marker in expected_markers
        if marker not in stdout_lines
    ]


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

        missing_output_markers = _validate_selftest_output(rel_path, result.stdout)
        if missing_output_markers:
            print("PHASE3_VALIDATE_SELFTEST=fail")
            print("\n".join(missing_output_markers))
            if result.stdout:
                print(result.stdout.rstrip())
            if result.stderr:
                print(result.stderr.rstrip())
            return 1

    print("PHASE3_VALIDATE_SELFTEST=pass")
    return 0


def _synthetic_makefile_text() -> str:
    validate_commands = list(_required_phase3_validate_commands())
    selftest_commands = list(_required_phase3_selftest_commands())
    return (
        PHASE3_VALIDATE_TARGET
        + ":\n"
        + "\n".join(f"\t{command}" for command in validate_commands)
        + "\n"
        + PHASE3_SELFTEST_TARGET
        + ":\n"
        + "\n".join(f"\t{command}" for command in selftest_commands)
        + "\n"
    )


def _synthetic_selftest_script(rel_path: Path) -> str:
    lines = ["#!/usr/bin/env python3"]
    for marker in SELFTEST_OUTPUT_MARKERS.get(rel_path, ()):
        lines.append(f"print({marker!r})")
    lines.append("raise SystemExit(0)")
    lines.append("")
    return "\n".join(lines)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validate_selftest_") as temp_dir:
        root = Path(temp_dir)
        for rel_path, _args in SELFTEST_COMMANDS:
            path = root / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                _synthetic_selftest_script(rel_path),
                encoding="utf-8",
            )

        (root / MAKEFILE_PATH).parent.mkdir(parents=True, exist_ok=True)
        (root / MAKEFILE_PATH).write_text(
            _synthetic_makefile_text(),
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
            _synthetic_selftest_script(first_path),
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
            "missing phase3-validate command: "
            + _selftest_make_command(SELFTEST_COMMANDS[-1][0], SELFTEST_COMMANDS[-1][1])
        )
        if expected not in missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing makefile self-test command was not reported")
            return 1

        (root / MAKEFILE_PATH).write_text(
            _synthetic_makefile_text(),
            encoding="utf-8",
        )
        makefile = (root / MAKEFILE_PATH).read_text(encoding="utf-8").replace(
            PHASE3_SELFTEST_TARGET + ":\n\t" + PHASE3_SELFTEST_DRIVER_COMMAND + "\n",
            PHASE3_SELFTEST_TARGET
            + ":\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py --self-test\n",
            1,
        )
        (root / MAKEFILE_PATH).write_text(makefile, encoding="utf-8")
        missing = validate_makefile(root)
        expected = f"missing phase3-selftest command: {PHASE3_SELFTEST_DRIVER_COMMAND}"
        if expected not in missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected dedicated selftest target command was not reported")
            return 1

        (root / MAKEFILE_PATH).write_text(
            _synthetic_makefile_text(),
            encoding="utf-8",
        )
        makefile = (root / MAKEFILE_PATH).read_text(encoding="utf-8").replace(
            PHASE3_SELFTEST_TARGET + ":",
            "phase3-selftest-shadow:",
            1,
        )
        (root / MAKEFILE_PATH).write_text(makefile, encoding="utf-8")
        missing = validate_makefile(root)
        expected = f"missing make target: {PHASE3_SELFTEST_TARGET}"
        if expected not in missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing dedicated selftest target was not reported")
            return 1

        (root / MAKEFILE_PATH).write_text(
            _synthetic_makefile_text(),
            encoding="utf-8",
        )
        makefile = (root / MAKEFILE_PATH).read_text(encoding="utf-8").replace(
            PHASE3_SELFTEST_TARGET + ":\n\t" + PHASE3_SELFTEST_DRIVER_COMMAND + "\n",
            PHASE3_SELFTEST_TARGET + ":\n",
            1,
        )
        makefile = makefile.replace(
            PHASE3_SELFTEST_TARGET + ":\n",
            PHASE3_SELFTEST_TARGET + ":\n\t" + PHASE3_VALIDATE_SUPPORT_COMMANDS[0] + "\n",
            1,
        )
        (root / MAKEFILE_PATH).write_text(makefile, encoding="utf-8")
        missing = validate_makefile(root)
        expected = f"missing phase3-selftest command: {PHASE3_SELFTEST_DRIVER_COMMAND}"
        if expected not in missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected target-scoped selftest drift was not reported")
            return 1

        (root / MAKEFILE_PATH).write_text(
            _synthetic_makefile_text(),
            encoding="utf-8",
        )
        makefile = (root / MAKEFILE_PATH).read_text(encoding="utf-8").replace(
            "\t" + PHASE3_VALIDATE_SUPPORT_COMMANDS[0] + "\n",
            "",
            1,
        )
        makefile = makefile.replace(
            PHASE3_SELFTEST_TARGET + ":\n\t" + PHASE3_SELFTEST_DRIVER_COMMAND + "\n",
            PHASE3_SELFTEST_TARGET
            + ":\n\t"
            + PHASE3_SELFTEST_DRIVER_COMMAND
            + "\n\t"
            + PHASE3_VALIDATE_SUPPORT_COMMANDS[0]
            + "\n",
            1,
        )
        (root / MAKEFILE_PATH).write_text(makefile, encoding="utf-8")
        missing = validate_makefile(root)
        expected = f"missing phase3-validate command: {PHASE3_VALIDATE_SUPPORT_COMMANDS[0]}"
        if expected not in missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected target-scoped phase3-validate drift was not reported")
            return 1

        (root / MAKEFILE_PATH).write_text(
            _synthetic_makefile_text(),
            encoding="utf-8",
        )
        makefile = (root / MAKEFILE_PATH).read_text(encoding="utf-8").replace(
            "\t" + PHASE3_SELFTEST_DRIVER_COMMAND + "\n",
            "",
            1,
        )
        (root / MAKEFILE_PATH).write_text(makefile, encoding="utf-8")
        missing = validate_makefile(root)
        expected = f"missing phase3-validate command: {PHASE3_SELFTEST_DRIVER_COMMAND}"
        if expected not in missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing selftest driver makefile command was not reported")
            return 1

        (root / MAKEFILE_PATH).write_text(
            _synthetic_makefile_text(),
            encoding="utf-8",
        )
        makefile = (root / MAKEFILE_PATH).read_text(encoding="utf-8").replace(
            "\t" + PHASE3_VALIDATE_SUPPORT_COMMANDS[0] + "\n",
            "",
            1,
        )
        (root / MAKEFILE_PATH).write_text(makefile, encoding="utf-8")
        missing = validate_makefile(root)
        expected = f"missing phase3-validate command: {PHASE3_VALIDATE_SUPPORT_COMMANDS[0]}"
        if expected not in missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing audit-doc-sync makefile command was not reported")
            return 1

        (root / MAKEFILE_PATH).write_text(
            _synthetic_makefile_text(),
            encoding="utf-8",
        )
        makefile = (root / MAKEFILE_PATH).read_text(encoding="utf-8").replace(
            "\t" + PHASE3_VALIDATE_SUPPORT_COMMANDS[1] + "\n",
            "",
            1,
        )
        (root / MAKEFILE_PATH).write_text(makefile, encoding="utf-8")
        missing = validate_makefile(root)
        expected = f"missing phase3-validate command: {PHASE3_VALIDATE_SUPPORT_COMMANDS[1]}"
        if expected not in missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing wrapper-check makefile command was not reported")
            return 1

        governance_command = _selftest_make_command(
            Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py"),
            ("--self-test",),
        )
        makefile = (root / MAKEFILE_PATH).read_text(encoding="utf-8")
        if governance_command in makefile:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected governance validator to stay indirect through the selftest driver")
            return 1

        for rel_path, expected_markers in SELFTEST_OUTPUT_MARKERS.items():
            if not expected_markers:
                continue
            (root / MAKEFILE_PATH).write_text(
                _synthetic_makefile_text(),
                encoding="utf-8",
            )
            stale_script = _synthetic_selftest_script(rel_path).replace(
                expected_markers[0],
                expected_markers[0].replace("=pass", "=stale"),
                1,
            )
            (root / rel_path).write_text(
                stale_script,
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                result = run_packet(root)
            if result == 0:
                print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
                print("expected missing selftest output marker to fail the packet")
                return 1
            output = buffer.getvalue()
            expected_missing_marker = (
                f"missing selftest output marker: {rel_path.as_posix()}: {expected_markers[0]}"
            )
            expected_stale_marker = expected_markers[0].replace("=pass", "=stale")
            for marker in (
                "PHASE3_VALIDATE_SELFTEST=fail",
                expected_missing_marker,
                expected_stale_marker,
            ):
                if marker not in output:
                    print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
                    print(
                        "expected missing selftest output marker coverage was not reported: "
                        f"{marker}"
                    )
                    return 1
            (root / rel_path).write_text(
                _synthetic_selftest_script(rel_path),
                encoding="utf-8",
            )

        (root / MAKEFILE_PATH).write_text(
            _synthetic_makefile_text(),
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

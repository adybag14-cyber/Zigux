#!/usr/bin/env python3

"""Run the current bounded Phase 3 interop self-test packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
ORCHESTRATION_ROUTES = frozenset(
    {
        Path("scripts/zigux/run-phase3-checks.py"),
        Path("scripts/zigux/validate_phase3_selftest.py"),
    }
)

SELFTEST_COMMANDS = (
    (
        Path("scripts/zigux/check-phase3-dev-t-starter-packet.py"),
        ("--self-test",),
        (
            "PHASE3_DEV_T_STARTER_PACKET_SELF_TEST=pass",
            "PHASE3_DEV_T_STARTER_PACKET_SELF_TEST_CASES=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py"),
        ("--self-test",),
        (
            "PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=pass",
            "PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST_CASES=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py"),
        ("--self-test",),
        (
            "PHASE3_XARRAY_SLOT_STARTER_PACKET_SELF_TEST=pass",
            "PHASE3_XARRAY_SLOT_STARTER_PACKET_SELF_TEST_CASES=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-xarray-slot.py"),
        ("--self-test",),
        (
            "PHASE3_XARRAY_SLOT_SELF_TEST=pass",
            "PHASE3_XARRAY_SLOT_SELF_TEST_CASES=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-policy-starter-packet.py"),
        ("--self-test",),
        (
            "PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass",
            "PHASE3_POLICY_STARTER_PACKET_SELF_TEST_CASES=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-policy-dump.py"),
        ("--self-test",),
        (
            "PHASE3_POLICY_DUMP_SELF_TEST=pass",
            "PHASE3_POLICY_DUMP_EXPECTED_LINE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/validate-phase3.py"),
        ("--self-test",),
        (
            "PHASE3_VALIDATION_SELF_TEST=pass",
            "PHASE3_VALIDATION_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-abi.py"),
        ("--self-test",),
        (
            "PHASE3_ABI_CHECK_SELF_TEST=pass",
            "PHASE3_ABI_CHECK_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-abi-support-packet.py"),
        ("--self-test",),
        (
            "PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=pass",
            "PHASE3_ABI_SUPPORT_PACKET_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-abi-manifest-replay-routes.py"),
        ("--self-test",),
        (
            "PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=pass",
            "PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-shared-tests-routes.py"),
        ("--self-test",),
        (
            "PHASE3_SHARED_TESTS_ROUTES_SELF_TEST=pass",
            "PHASE3_SHARED_TESTS_ROUTES_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-readme-tooling-inventory.py"),
        ("--self-test",),
        (
            "PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass",
            "PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-wrapper-templates.py"),
        ("--self-test",),
        (
            "PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=pass",
            "PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-catalog-selftest.py"),
        ("--self-test",),
        (
            "PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=pass",
            "PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/run-phase3-checks.py"),
        ("--self-test",),
        (
            "PHASE3_CHECK_RUNNER_SELF_TEST=pass",
            "PHASE3_CHECK_RUNNER_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/validate-phase3-validator-support-surface.py"),
        ("--self-test",),
        (
            "PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=pass",
            "PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
        ("--self-test",),
        (
            "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass",
            "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASES=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"),
        ("--self-test",),
        (
            "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass",
            "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"),
        ("--self-test",),
        (
            "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass",
            "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),
        ("--self-test",),
        (
            "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass",
            "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
        ("--self-test",),
        (
            "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass",
            "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-low-level-wrappers.py"),
        ("--self-test",),
        (
            "PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST=pass",
            "PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST_CASES=",
        ),
    ),
    (
        Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py"),
        ("--self-test",),
        ("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass",),
    ),
    (
        Path("scripts/zigux/generate-phase3-check-wrappers.py"),
        ("--self-test",),
        (
            "PHASE3_WRAPPER_SELF_TEST=pass",
            "PHASE3_WRAPPER_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-selftest-surface.py"),
        ("--self-test",),
        (
            "PHASE3_SELFTEST_SURFACE_SELF_TEST=pass",
            "PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-bitmap-cpumask.py"),
        ("--self-test",),
        (
            "PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=pass",
            "PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-list-hlist-starter-packet.py"),
        ("--self-test",),
        (
            "PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=pass",
            "PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST_CASE_COUNT=",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-list-hlist.py"),
        ("--self-test",),
        (
            "PHASE3_LIST_HLIST_SELF_TEST=pass",
            "PHASE3_LIST_HLIST_SELF_TEST_CASES=",
        ),
    ),
)


def _has_output_marker(stdout: str, marker: str) -> bool:
    if marker.endswith("="):
        return any(line.startswith(marker) for line in stdout.splitlines())
    return marker in stdout


def _missing_output_markers(stdout: str, markers: tuple[str, ...]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        if not _has_output_marker(stdout, marker):
            missing.append(marker)
    return missing


def _expected_manifest_selftest_routes(
    manifest: object,
) -> set[tuple[Path, tuple[str, ...]]]:
    if not isinstance(manifest, dict):
        return set()

    replay_routes = manifest.get("replay_routes")
    if not isinstance(replay_routes, list):
        return set()

    expected: set[tuple[Path, tuple[str, ...]]] = set()
    for route in replay_routes:
        if not isinstance(route, str):
            continue
        parts = shlex.split(route)
        if len(parts) < 3 or parts[0] != "python3" or "--self-test" not in parts[2:]:
            continue
        script_path = Path(parts[1])
        if (
            script_path.parts[:2] == ("scripts", "zigux")
            and script_path.suffix == ".py"
            and script_path not in ORCHESTRATION_ROUTES
        ):
            expected.add((script_path, tuple(parts[2:])))
    return expected


def validate_script_list(repo_root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path, _args, _markers in SELFTEST_COMMANDS:
        if not (repo_root / rel_path).is_file():
            missing.append(f"missing selftest script: {rel_path.as_posix()}")
    return missing


def validate_manifest_selftest_coverage(repo_root: Path) -> list[str]:
    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.is_file():
        return [f"missing phase3 manifest: {MANIFEST_PATH.as_posix()}"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid phase3 manifest JSON: {MANIFEST_PATH.as_posix()}: {exc}"]

    expected = _expected_manifest_selftest_routes(manifest)
    actual = {(rel_path, args) for rel_path, args, _markers in SELFTEST_COMMANDS}
    missing = sorted(expected - actual, key=lambda item: (item[0].as_posix(), item[1]))
    return [
        "manifest self-test replay route missing from SELFTEST_COMMANDS: "
        + " ".join([rel_path.as_posix(), *args])
        for rel_path, args in missing
    ]


def run_packet(repo_root: Path) -> int:
    missing = validate_script_list(repo_root)
    missing.extend(validate_manifest_selftest_coverage(repo_root))
    if missing:
        print("PHASE3_VALIDATE_SELFTEST=fail")
        print("\n".join(missing))
        return 1
    for rel_path, args, output_markers in SELFTEST_COMMANDS:
        result = subprocess.run(
            [sys.executable, rel_path.as_posix(), *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("PHASE3_VALIDATE_SELFTEST=fail")
            print("self-test failed: " + " ".join([rel_path.as_posix(), *args]))
            if result.stdout:
                print(result.stdout.rstrip())
            if result.stderr:
                print(result.stderr.rstrip())
            return 1

        marker_issues = _missing_output_markers(result.stdout, output_markers)
        if marker_issues:
            print("PHASE3_VALIDATE_SELFTEST=fail")
            print(
                "\n".join(
                    f"missing selftest output marker for {rel_path.as_posix()}: {marker}"
                    for marker in marker_issues
                )
            )
            if result.stdout:
                print(result.stdout.rstrip())
            if result.stderr:
                print(result.stderr.rstrip())
            return 1
    print("PHASE3_VALIDATE_SELFTEST=pass")
    return 0


def _write_synthetic_script(
    path: Path,
    pass_marker: str | None,
    count_marker: str | None,
    *,
    failure_code: int | None = None,
) -> None:
    lines = ["#!/usr/bin/env python3", "import sys"]
    if pass_marker is not None:
        lines.append(f"print({pass_marker!r})")
    if count_marker is not None:
        lines.append(f"print({count_marker!r} + '1')")
    if failure_code is None:
        lines.append("raise SystemExit(0)")
    else:
        lines.append("print('synthetic stderr detail', file=sys.stderr)")
        lines.append(f"raise SystemExit({failure_code})")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_synthetic_manifest(root: Path, replay_routes: list[str] | None = None) -> None:
    manifest_path = root / MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if replay_routes is None:
        replay_routes = [
            f"python3 {rel_path.as_posix()} {' '.join(args)}".rstrip()
            for rel_path, args, _markers in SELFTEST_COMMANDS
        ]
        replay_routes.extend(
            [
                "python3 scripts/zigux/run-phase3-checks.py",
                "python3 scripts/zigux/validate_phase3_selftest.py",
                "python3 scripts/zigux/check-phase3-abi.py",
                "zig build phase3-test --build-file zigux/tests/build.zig",
            ]
        )
    manifest_path.write_text(
        json.dumps({"replay_routes": replay_routes}, indent=2) + "\n",
        encoding="utf-8",
    )


def _populate_repo(root: Path) -> None:
    for rel_path, _args, output_markers in SELFTEST_COMMANDS:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        pass_marker = output_markers[0] if output_markers else None
        count_marker = output_markers[1] if len(output_markers) > 1 else None
        _write_synthetic_script(path, pass_marker, count_marker)
    _write_synthetic_manifest(root)


def _command_index(script_name: str) -> int:
    for index, (rel_path, _args, _markers) in enumerate(SELFTEST_COMMANDS):
        if rel_path.name == script_name:
            return index
    raise AssertionError(f"missing selftest command for {script_name}")


def _expect_missing(root: Path, script_name: str, message: str) -> int:
    _populate_repo(root)
    index = _command_index(script_name)
    missing_path = SELFTEST_COMMANDS[index][0]
    (root / missing_path).unlink()
    missing = validate_script_list(root)
    expected = f"missing selftest script: {missing_path.as_posix()}"
    if expected not in missing:
        print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validate_selftest_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)
        if validate_script_list(root):
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected synthetic self-test script set to validate")
            return 1

        manifest_missing = validate_manifest_selftest_coverage(root)
        if manifest_missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected synthetic self-test manifest coverage to validate")
            print("\n".join(manifest_missing))
            return 1

        if run_packet(root) != 0:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected synthetic self-test packet to pass")
            return 1

        missing_cases = (
            ("check-phase3-dev-t-starter-packet.py", "expected missing leading script was not reported"),
            ("check-phase3-errptr-xarray-starter-packet.py", "expected errptr-xarray starter script omission was not reported"),
            ("check-phase3-xarray-slot-starter-packet.py", "expected xarray-slot starter script omission was not reported"),
            ("check-phase3-xarray-slot.py", "expected xarray-slot checker omission was not reported"),
            ("check-phase3-policy-starter-packet.py", "expected policy starter script omission was not reported"),
            ("check-phase3-policy-dump.py", "expected policy dump script omission was not reported"),
            ("validate-phase3.py", "expected shared ABI validator omission was not reported"),
            ("check-phase3-abi.py", "expected shared ABI checker omission was not reported"),
            ("check-phase3-abi-support-packet.py", "expected shared ABI support-packet omission was not reported"),
            ("check-phase3-abi-manifest-replay-routes.py", "expected abi manifest replay-routes omission was not reported"),
            ("check-phase3-shared-tests-routes.py", "expected shared-routes script omission was not reported"),
            ("check-phase3-readme-tooling-inventory.py", "expected readme-tooling script omission was not reported"),
            ("check-phase3-wrapper-templates.py", "expected wrapper-template script omission was not reported"),
            ("check-phase3-catalog-selftest.py", "expected catalog-selftest script omission was not reported"),
            ("run-phase3-checks.py", "expected runner omission was not reported"),
            ("validate-phase3-validator-support-surface.py", "expected validator-support script omission was not reported"),
            ("validate-phase3-export-uapi-survey.py", "expected export-uapi survey script omission was not reported"),
            ("check-phase3-export-uapi-c-header-smoke.py", "expected export-uapi c-header smoke script omission was not reported"),
            ("validate-phase3-abi-header-family-survey.py", "expected abi-header-family survey script omission was not reported"),
            ("validate-phase3-policy-unsafe-survey.py", "expected policy-unsafe survey script omission was not reported"),
            ("validate-phase3-low-level-wrapper-survey.py", "expected low-level-wrapper survey script omission was not reported"),
            ("check-phase3-low-level-wrappers.py", "expected low-level-wrapper compile-route script omission was not reported"),
            ("validate-phase3-linux-zigux-header-governance.py", "expected linux-zigux header governance validator omission was not reported"),
            ("generate-phase3-check-wrappers.py", "expected wrapper-generator script omission was not reported"),
            ("check-phase3-selftest-surface.py", "expected selftest-surface script omission was not reported"),
            ("check-phase3-bitmap-cpumask.py", "expected bitmap-cpumask script omission was not reported"),
            ("check-phase3-list-hlist-starter-packet.py", "expected list-hlist starter script omission was not reported"),
            ("check-phase3-list-hlist.py", "expected full list-hlist script omission was not reported"),
        )
        for script_name, message in missing_cases:
            if _expect_missing(root, script_name, message) != 0:
                return 1

        _populate_repo(root)
        _write_synthetic_manifest(
            root,
            replay_routes=[
                f"python3 {rel_path.as_posix()} {' '.join(args)}".rstrip()
                for rel_path, args, _markers in SELFTEST_COMMANDS
            ]
            + ["python3 scripts/zigux/manifest-only-selftest.py --self-test"],
        )
        manifest_missing = validate_manifest_selftest_coverage(root)
        expected_manifest_gap = (
            "manifest self-test replay route missing from SELFTEST_COMMANDS: "
            "scripts/zigux/manifest-only-selftest.py --self-test"
        )
        if expected_manifest_gap not in manifest_missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected manifest-only self-test replay route omission to be reported")
            return 1

        _populate_repo(root)
        (root / MANIFEST_PATH).unlink()
        manifest_missing = validate_manifest_selftest_coverage(root)
        expected_manifest_missing = f"missing phase3 manifest: {MANIFEST_PATH.as_posix()}"
        if expected_manifest_missing not in manifest_missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing manifest to be reported")
            return 1

        _populate_repo(root)
        failing_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-low-level-wrappers.py")][0]
        _write_synthetic_script(
            failing_path,
            "PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST=pass",
            "PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST_CASES=",
            failure_code=7,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected failing child self-test to fail the packet")
            return 1

        _populate_repo(root)
        missing_pass_path = root / SELFTEST_COMMANDS[_command_index("run-phase3-checks.py")][0]
        _write_synthetic_script(
            missing_pass_path,
            None,
            "PHASE3_CHECK_RUNNER_SELF_TEST_CASE_COUNT=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_wrapper_count_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-wrapper-templates.py")][0]
        _write_synthetic_script(
            missing_wrapper_count_path,
            "PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing wrapper-template count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_generator_pass_path = root / SELFTEST_COMMANDS[_command_index("generate-phase3-check-wrappers.py")][0]
        _write_synthetic_script(
            missing_generator_pass_path,
            None,
            "PHASE3_WRAPPER_SELF_TEST_CASE_COUNT=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing wrapper-generator pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_generator_count_path = root / SELFTEST_COMMANDS[_command_index("generate-phase3-check-wrappers.py")][0]
        _write_synthetic_script(
            missing_generator_count_path,
            "PHASE3_WRAPPER_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing wrapper-generator count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_xarray_slot_pass_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-xarray-slot.py")][0]
        _write_synthetic_script(
            missing_xarray_slot_pass_path,
            None,
            "PHASE3_XARRAY_SLOT_SELF_TEST_CASES=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing xarray-slot pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_xarray_slot_count_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-xarray-slot.py")][0]
        _write_synthetic_script(
            missing_xarray_slot_count_path,
            "PHASE3_XARRAY_SLOT_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing xarray-slot count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_policy_dump_pass_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-policy-dump.py")][0]
        _write_synthetic_script(
            missing_policy_dump_pass_path,
            None,
            "PHASE3_POLICY_DUMP_EXPECTED_LINE_COUNT=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing policy-dump pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_policy_dump_count_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-policy-dump.py")][0]
        _write_synthetic_script(
            missing_policy_dump_count_path,
            "PHASE3_POLICY_DUMP_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing policy-dump count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_count_path = root / SELFTEST_COMMANDS[_command_index("validate-phase3.py")][0]
        _write_synthetic_script(
            missing_count_path,
            "PHASE3_VALIDATION_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_manifest_replay_pass_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-abi-manifest-replay-routes.py")][0]
        _write_synthetic_script(
            missing_manifest_replay_pass_path,
            None,
            "PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST_CASE_COUNT=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing manifest replay-routes pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_manifest_replay_count_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-abi-manifest-replay-routes.py")][0]
        _write_synthetic_script(
            missing_manifest_replay_count_path,
            "PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing manifest replay-routes count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_support_packet_pass_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-abi-support-packet.py")][0]
        _write_synthetic_script(
            missing_support_packet_pass_path,
            None,
            "PHASE3_ABI_SUPPORT_PACKET_SELF_TEST_CASE_COUNT=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing support-packet pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_support_packet_count_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-abi-support-packet.py")][0]
        _write_synthetic_script(
            missing_support_packet_count_path,
            "PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing support-packet count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_export_uapi_pass_path = root / SELFTEST_COMMANDS[_command_index("validate-phase3-export-uapi-survey.py")][0]
        _write_synthetic_script(
            missing_export_uapi_pass_path,
            None,
            "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASES=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing export-uapi pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_export_uapi_count_path = root / SELFTEST_COMMANDS[_command_index("validate-phase3-export-uapi-survey.py")][0]
        _write_synthetic_script(
            missing_export_uapi_count_path,
            "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing export-uapi count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_export_uapi_c_header_smoke_pass_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-export-uapi-c-header-smoke.py")][0]
        _write_synthetic_script(
            missing_export_uapi_c_header_smoke_pass_path,
            None,
            "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing export-uapi c-header smoke pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_export_uapi_c_header_smoke_count_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-export-uapi-c-header-smoke.py")][0]
        _write_synthetic_script(
            missing_export_uapi_c_header_smoke_count_path,
            "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing export-uapi c-header smoke count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_header_family_pass_path = root / SELFTEST_COMMANDS[_command_index("validate-phase3-abi-header-family-survey.py")][0]
        _write_synthetic_script(
            missing_header_family_pass_path,
            None,
            "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST_CASE_COUNT=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing abi-header-family pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_header_family_count_path = root / SELFTEST_COMMANDS[_command_index("validate-phase3-abi-header-family-survey.py")][0]
        _write_synthetic_script(
            missing_header_family_count_path,
            "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing abi-header-family count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_policy_unsafe_pass_path = root / SELFTEST_COMMANDS[_command_index("validate-phase3-policy-unsafe-survey.py")][0]
        _write_synthetic_script(
            missing_policy_unsafe_pass_path,
            None,
            "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing policy-unsafe pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_policy_unsafe_count_path = root / SELFTEST_COMMANDS[_command_index("validate-phase3-policy-unsafe-survey.py")][0]
        _write_synthetic_script(
            missing_policy_unsafe_count_path,
            "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing policy-unsafe count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_low_level_wrappers_pass_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-low-level-wrappers.py")][0]
        _write_synthetic_script(
            missing_low_level_wrappers_pass_path,
            None,
            "PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST_CASES=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing low-level-wrapper compile-route pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_low_level_wrappers_count_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-low-level-wrappers.py")][0]
        _write_synthetic_script(
            missing_low_level_wrappers_count_path,
            "PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing low-level-wrapper compile-route count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_governance_pass_path = root / SELFTEST_COMMANDS[_command_index("validate-phase3-linux-zigux-header-governance.py")][0]
        _write_synthetic_script(
            missing_governance_pass_path,
            None,
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing governance pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_bitmap_cpumask_pass_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-bitmap-cpumask.py")][0]
        _write_synthetic_script(
            missing_bitmap_cpumask_pass_path,
            None,
            "PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST_CASE_COUNT=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing bitmap-cpumask pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_bitmap_cpumask_count_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-bitmap-cpumask.py")][0]
        _write_synthetic_script(
            missing_bitmap_cpumask_count_path,
            "PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing bitmap-cpumask count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_list_hlist_starter_pass_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-list-hlist-starter-packet.py")][0]
        _write_synthetic_script(
            missing_list_hlist_starter_pass_path,
            None,
            "PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST_CASE_COUNT=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing list-hlist starter pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_list_hlist_starter_count_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-list-hlist-starter-packet.py")][0]
        _write_synthetic_script(
            missing_list_hlist_starter_count_path,
            "PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing list-hlist starter count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_list_hlist_pass_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-list-hlist.py")][0]
        _write_synthetic_script(
            missing_list_hlist_pass_path,
            None,
            "PHASE3_LIST_HLIST_SELF_TEST_CASES=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing full list-hlist pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_list_hlist_count_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-list-hlist.py")][0]
        _write_synthetic_script(
            missing_list_hlist_count_path,
            "PHASE3_LIST_HLIST_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing full list-hlist count marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_shared_tests_routes_pass_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-shared-tests-routes.py")][0]
        _write_synthetic_script(
            missing_shared_tests_routes_pass_path,
            None,
            "PHASE3_SHARED_TESTS_ROUTES_SELF_TEST_CASE_COUNT=",
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing shared-tests-routes pass marker to fail the packet")
            return 1

        _populate_repo(root)
        missing_shared_tests_routes_count_path = root / SELFTEST_COMMANDS[_command_index("check-phase3-shared-tests-routes.py")][0]
        _write_synthetic_script(
            missing_shared_tests_routes_count_path,
            "PHASE3_SHARED_TESTS_ROUTES_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing shared-tests-routes count marker to fail the packet")
            return 1

    print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=pass")
    print(
        "PHASE3_VALIDATE_SELFTEST_SELF_TEST_CASE_COUNT="
        f"{len(missing_cases) + 37}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the current bounded Phase 3 interop self-test packet."
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

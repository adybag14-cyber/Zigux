#!/usr/bin/env python3

"""Run the current bounded Phase 3 interop self-test packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

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
        Path("scripts/zigux/check-phase3-policy-starter-packet.py"),
        ("--self-test",),
        (
            "PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass",
            "PHASE3_POLICY_STARTER_PACKET_SELF_TEST_CASES=",
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
        Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
        ("--self-test",),
        (
            "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass",
            "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=",
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
)


def _has_output_marker(stdout: str, marker: str) -> bool:
    if marker.endswith("="):
        return any(line.startswith(marker) for line in stdout.splitlines())
    return marker in stdout


def _missing_output_markers(rel_path: Path, stdout: str, markers: tuple[str, ...]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        if not _has_output_marker(stdout, marker):
            missing.append(
                f"missing selftest output marker for {rel_path.as_posix()}: {marker}"
            )
    return missing


def validate_script_list(repo_root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path, _args, _markers in SELFTEST_COMMANDS:
        if not (repo_root / rel_path).is_file():
            missing.append(f"missing selftest script: {rel_path.as_posix()}")
    return missing


def run_packet(repo_root: Path) -> int:
    missing = validate_script_list(repo_root)
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

        marker_issues = _missing_output_markers(rel_path, result.stdout, output_markers)
        if marker_issues:
            print("PHASE3_VALIDATE_SELFTEST=fail")
            print("\n".join(marker_issues))
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


def _populate_repo(root: Path) -> None:
    for rel_path, _args, output_markers in SELFTEST_COMMANDS:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_synthetic_script(path, output_markers[0], output_markers[1])


def _expect_missing(root: Path, index: int, message: str) -> int:
    _populate_repo(root)
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

        if run_packet(root) != 0:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected synthetic self-test packet to pass")
            return 1

        missing_cases = (
            (0, "expected missing leading script was not reported"),
            (2, "expected xarray-slot script omission was not reported"),
            (4, "expected shared ABI validator omission was not reported"),
            (5, "expected shared-routes script omission was not reported"),
            (6, "expected readme-tooling script omission was not reported"),
            (7, "expected runner omission was not reported"),
            (8, "expected validator-support script omission was not reported"),
            (9, "expected export-uapi survey script omission was not reported"),
            (10, "expected low-level-wrapper script omission was not reported"),
            (11, "expected missing trailing script was not reported"),
        )
        for index, message in missing_cases:
            if _expect_missing(root, index, message) != 0:
                return 1

        _populate_repo(root)
        failing_path = root / SELFTEST_COMMANDS[10][0]
        _write_synthetic_script(
            failing_path,
            "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass",
            "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=",
            failure_code=7,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected failing child self-test to fail the packet")
            return 1

        _populate_repo(root)
        missing_pass_path = root / SELFTEST_COMMANDS[7][0]
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
        missing_count_path = root / SELFTEST_COMMANDS[4][0]
        _write_synthetic_script(
            missing_count_path,
            "PHASE3_VALIDATION_SELF_TEST=pass",
            None,
        )
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing count marker to fail the packet")
            return 1

    print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=pass")
    print(
        "PHASE3_VALIDATE_SELFTEST_SELF_TEST_CASE_COUNT="
        f"{len(missing_cases) + 4}"
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
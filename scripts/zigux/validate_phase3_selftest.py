#!/usr/bin/env python3

"""Run the current bounded Phase 3 interop self-test packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

from phase3_manifest_routes import load_manifest_python_routes

MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
ORCHESTRATION_ROUTES = frozenset(
    {
        Path("scripts/zigux/run-phase3-checks.py"),
        Path("scripts/zigux/validate_phase3_selftest.py"),
    }
)

SELFTEST_COMMANDS = (
    (Path("scripts/zigux/check-phase3-dev-t-starter-packet.py"), ("--self-test",), ("PHASE3_DEV_T_STARTER_PACKET_SELF_TEST=pass", "PHASE3_DEV_T_STARTER_PACKET_SELF_TEST_CASES=")),
    (Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py"), ("--self-test",), ("PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=pass", "PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST_CASES=")),
    (Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py"), ("--self-test",), ("PHASE3_XARRAY_SLOT_STARTER_PACKET_SELF_TEST=pass", "PHASE3_XARRAY_SLOT_STARTER_PACKET_SELF_TEST_CASES=")),
    (Path("scripts/zigux/check-phase3-xarray-slot.py"), ("--self-test",), ("PHASE3_XARRAY_SLOT_SELF_TEST=pass", "PHASE3_XARRAY_SLOT_SELF_TEST_CASES=")),
    (Path("scripts/zigux/check-phase3-idr-slot-starter-packet.py"), ("--self-test",), ("PHASE3_IDR_SLOT_STARTER_PACKET_SELF_TEST=pass", "PHASE3_IDR_SLOT_STARTER_PACKET_SELF_TEST_CASES=")),
    (Path("scripts/zigux/check-phase3-idr-slot.py"), ("--self-test",), ("PHASE3_IDR_SLOT_SELF_TEST=pass", "PHASE3_IDR_SLOT_SELF_TEST_CASES=")),
    (Path("scripts/zigux/check-phase3-policy-starter-packet.py"), ("--self-test",), ("PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass", "PHASE3_POLICY_STARTER_PACKET_SELF_TEST_CASES=")),
    (Path("scripts/zigux/check-phase3-policy-dump.py"), ("--self-test",), ("PHASE3_POLICY_DUMP_SELF_TEST=pass", "PHASE3_POLICY_DUMP_EXPECTED_LINE_COUNT=")),
    (Path("scripts/zigux/validate-phase3.py"), ("--self-test",), ("PHASE3_VALIDATION_SELF_TEST=pass", "PHASE3_VALIDATION_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/check-phase3-abi.py"), ("--self-test",), ("PHASE3_ABI_CHECK_SELF_TEST=pass", "PHASE3_ABI_CHECK_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/check-phase3-abi-support-packet.py"), ("--self-test",), ("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=pass", "PHASE3_ABI_SUPPORT_PACKET_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/check-phase3-abi-manifest-replay-routes.py"), ("--self-test",), ("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=pass", "PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/check-phase3-shared-tests-routes.py"), ("--self-test",), ("PHASE3_SHARED_TESTS_ROUTES_SELF_TEST=pass", "PHASE3_SHARED_TESTS_ROUTES_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/check-phase3-readme-tooling-inventory.py"), ("--self-test",), ("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass", "PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/check-phase3-wrapper-templates.py"), ("--self-test",), ("PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=pass", "PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/check-phase3-catalog-selftest.py"), ("--self-test",), ("PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=pass", "PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/run-phase3-checks.py"), ("--self-test",), ("PHASE3_CHECK_RUNNER_SELF_TEST=pass", "PHASE3_CHECK_RUNNER_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/validate-phase3-validator-support-surface.py"), ("--self-test",), ("PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=pass", "PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/validate-phase3-export-uapi-survey.py"), ("--self-test",), ("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass", "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASES=")),
    (Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"), ("--self-test",), ("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass", "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"), ("--self-test",), ("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass", "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"), ("--self-test",), ("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass", "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"), ("--self-test",), ("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass", "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/check-phase3-low-level-wrappers.py"), ("--self-test",), ("PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST=pass", "PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST_CASES=")),
    (Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py"), ("--self-test",), ("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass",)),
    (Path("scripts/zigux/generate-phase3-check-wrappers.py"), ("--self-test",), ("PHASE3_WRAPPER_SELF_TEST=pass", "PHASE3_WRAPPER_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/check-phase3-selftest-surface.py"), ("--self-test",), ("PHASE3_SELFTEST_SURFACE_SELF_TEST=pass", "PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/check-phase3-bitmap-cpumask.py"), ("--self-test",), ("PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=pass", "PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/check-phase3-list-hlist-starter-packet.py"), ("--self-test",), ("PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=pass", "PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST_CASE_COUNT=")),
    (Path("scripts/zigux/check-phase3-list-hlist.py"), ("--self-test",), ("PHASE3_LIST_HLIST_SELF_TEST=pass", "PHASE3_LIST_HLIST_SELF_TEST_CASES=")),
)


def _has_output_marker(stdout: str, marker: str) -> bool:
    if marker.endswith("="):
        return any(line.startswith(marker) for line in stdout.splitlines())
    return marker in stdout


def _missing_output_markers(stdout: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if not _has_output_marker(stdout, marker)]


def validate_script_list(repo_root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path, _args, _markers in SELFTEST_COMMANDS:
        if not (repo_root / rel_path).is_file():
            missing.append(f"missing selftest script: {rel_path.as_posix()}")
    return missing


def validate_manifest_selftest_coverage(repo_root: Path) -> list[str]:
    expected, issues = load_manifest_python_routes(
        repo_root,
        MANIFEST_PATH,
        want_selftest=True,
        ignored_scripts=ORCHESTRATION_ROUTES,
    )
    if issues:
        return issues

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
            for marker in marker_issues:
                print(
                    f"missing selftest output marker for {rel_path.as_posix()}: {marker}"
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
    markers: tuple[str, ...],
    *,
    drop_index: int | None = None,
    failure_code: int | None = None,
) -> None:
    lines = ["#!/usr/bin/env python3", "import sys"]
    for index, marker in enumerate(markers):
        if drop_index == index:
            continue
        if marker.endswith("="):
            lines.append(f"print({marker!r} + '1')")
        else:
            lines.append(f"print({marker!r})")
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
        __import__("json").dumps({"replay_routes": replay_routes}, indent=2) + "\n",
        encoding="utf-8",
    )


def _populate_repo(root: Path) -> None:
    helper_source = Path(__file__).with_name("phase3_manifest_routes.py")
    helper_target = root / "scripts/zigux/phase3_manifest_routes.py"
    helper_target.parent.mkdir(parents=True, exist_ok=True)
    helper_target.write_text(helper_source.read_text(encoding="utf-8"), encoding="utf-8")
    for rel_path, _args, markers in SELFTEST_COMMANDS:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_synthetic_script(path, markers)
    _write_synthetic_manifest(root)


def _command_index(script_name: str) -> int:
    for index, (rel_path, _args, _markers) in enumerate(SELFTEST_COMMANDS):
        if rel_path.name == script_name:
            return index
    raise AssertionError(f"missing selftest command for {script_name}")


def _expect_missing_script(root: Path, script_name: str) -> bool:
    _populate_repo(root)
    index = _command_index(script_name)
    missing_path = root / SELFTEST_COMMANDS[index][0]
    missing_path.unlink()
    expected = f"missing selftest script: {SELFTEST_COMMANDS[index][0].as_posix()}"
    return expected in validate_script_list(root)


def _expect_missing_marker(root: Path, script_name: str, marker_index: int) -> bool:
    _populate_repo(root)
    index = _command_index(script_name)
    rel_path, _args, markers = SELFTEST_COMMANDS[index]
    _write_synthetic_script(root / rel_path, markers, drop_index=marker_index)
    return run_packet(root) == 1


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validate_selftest_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        case_count += 1
        if validate_script_list(root):
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected synthetic self-test script set to validate")
            return 1

        case_count += 1
        manifest_missing = validate_manifest_selftest_coverage(root)
        if manifest_missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected synthetic self-test manifest coverage to validate")
            print("\n".join(manifest_missing))
            return 1

        case_count += 1
        if run_packet(root) != 0:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected synthetic self-test packet to pass")
            return 1

        for rel_path, _args, _markers in SELFTEST_COMMANDS:
            case_count += 1
            if not _expect_missing_script(root, rel_path.name):
                print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
                print(f"expected missing script to be reported: {rel_path.as_posix()}")
                return 1

        case_count += 1
        _populate_repo(root)
        _write_synthetic_manifest(
            root,
            replay_routes=[
                f"python3 {rel_path.as_posix()} {' '.join(args)}".rstrip()
                for rel_path, args, _markers in SELFTEST_COMMANDS
            ]
            + ["python3 scripts/zigux/manifest-only-selftest.py --self-test"],
        )
        expected_manifest_gap = (
            "manifest self-test replay route missing from SELFTEST_COMMANDS: "
            "scripts/zigux/manifest-only-selftest.py --self-test"
        )
        if expected_manifest_gap not in validate_manifest_selftest_coverage(root):
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected manifest-only self-test replay route omission to be reported")
            return 1

        case_count += 1
        _populate_repo(root)
        (root / MANIFEST_PATH).unlink()
        expected_manifest_missing = f"missing phase3 manifest: {MANIFEST_PATH.as_posix()}"
        if expected_manifest_missing not in validate_manifest_selftest_coverage(root):
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing manifest to be reported")
            return 1

        case_count += 1
        _populate_repo(root)
        failing_index = _command_index("check-phase3-low-level-wrappers.py")
        failing_rel_path, _failing_args, failing_markers = SELFTEST_COMMANDS[failing_index]
        _write_synthetic_script(root / failing_rel_path, failing_markers, failure_code=7)
        if run_packet(root) != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected failing child self-test to fail the packet")
            return 1

        marker_cases = (
            ("run-phase3-checks.py", 0),
            ("validate-phase3.py", 1),
            ("check-phase3-idr-slot-starter-packet.py", 0),
            ("check-phase3-idr-slot-starter-packet.py", 1),
            ("check-phase3-idr-slot.py", 0),
            ("check-phase3-idr-slot.py", 1),
            ("check-phase3-list-hlist.py", 0),
            ("check-phase3-list-hlist.py", 1),
        )
        for script_name, marker_index in marker_cases:
            case_count += 1
            if not _expect_missing_marker(root, script_name, marker_index):
                print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
                print(
                    "expected missing self-test output marker to fail the packet: "
                    f"{script_name} marker {marker_index}"
                )
                return 1

    print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=pass")
    print(f"PHASE3_VALIDATE_SELFTEST_SELF_TEST_CASE_COUNT={case_count}")
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

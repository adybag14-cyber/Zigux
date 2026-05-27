#!/usr/bin/env python3
"""Run the current bounded Phase 3 validator packet."""

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

CHECK_COMMANDS = (
    (
        Path("scripts/zigux/check-phase3-dev-t-starter-packet.py"),
        (),
        ("PHASE3_DEV_T_STARTER_PACKET=pass",),
    ),
    (
        Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py"),
        (),
        ("PHASE3_ERRPTR_XARRAY_STARTER_PACKET=pass",),
    ),
    (
        Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py"),
        (),
        ("PHASE3_XARRAY_SLOT_STARTER_PACKET=pass",),
    ),
    (
        Path("scripts/zigux/check-phase3-xarray-slot.py"),
        (),
        (
            "validated zigux/tests/phase3_xarray_slot_dump.zig",
            "validated zigux/tests/fixtures/phase3_xarray_slot_manifest.json",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-idr-slot-starter-packet.py"),
        (),
        (
            "validated zigux/tests/phase3_idr_slot_starter_packet.zig",
            "validated zigux/tests/phase3_idr_slot_starter_packet_build.zig",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-idr-slot.py"),
        (),
        (
            "validated zigux/tests/phase3_idr_slot_dump.zig",
            "validated zigux/tests/fixtures/phase3_idr_slot/expected.json",
            "validated zigux/tests/fixtures/phase3_idr_slot_manifest.json",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-policy-starter-packet.py"),
        (),
        ("PHASE3_POLICY_STARTER_PACKET=pass",),
    ),
    (
        Path("scripts/zigux/check-phase3-policy-dump.py"),
        (),
        (
            "validated zigux/tests/phase3_policy_dump.zig",
            "validated zigux/tests/fixtures/phase3_policy_dump_expected.txt",
        ),
    ),
    (
        Path("scripts/zigux/validate-phase3.py"),
        (),
        ("PHASE3_VALIDATION=pass",),
    ),
    (
        Path("scripts/zigux/check-phase3-abi.py"),
        (),
        ("PHASE3_ABI_CHECK=pass",),
    ),
    (
        Path("scripts/zigux/check-phase3-abi-support-packet.py"),
        (),
        ("PHASE3_ABI_SUPPORT_PACKET=pass",),
    ),
    (
        Path("scripts/zigux/check-phase3-shared-tests-routes.py"),
        (),
        (
            "validated zigux/tests/build.zig",
            "validated scripts/zigux/validate_phase3_selftest.py",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-readme-tooling-inventory.py"),
        (),
        ("validated scripts/zigux/README.md",),
    ),
    (
        Path("scripts/zigux/check-phase3-wrapper-templates.py"),
        (),
        (
            "validated scripts/zigux/generate-phase3-check-wrappers.py",
            "PHASE3_WRAPPER_TEMPLATES_CHECK=pass",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-catalog-selftest.py"),
        (),
        (
            "validated scripts/zigux/phase3_catalog.py",
            "PHASE3_CATALOG_SELFTEST_CHECK=pass",
        ),
    ),
    (
        Path("scripts/zigux/validate-phase3-validator-support-surface.py"),
        (),
        (
            "validated Documentation/zigux/phase3-validator-support-surface.md",
            "validated Documentation/zigux/phase3-shared-reminder-gap.md",
        ),
    ),
    (
        Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
        (),
        (
            "validated Documentation/zigux/phase3-export-uapi-boundary-survey.md",
            "PHASE3_EXPORT_UAPI_SURVEY=pass",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"),
        (),
        (
            "validated zigux/tests/phase3_export_uapi_c_header_smoke.c",
            "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass",
        ),
    ),
    (
        Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"),
        (),
        (
            "validated Documentation/zigux/phase3-abi-header-family-survey.md",
            "PHASE3_ABI_HEADER_FAMILY_SURVEY=pass",
        ),
    ),
    (
        Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),
        (),
        (
            "validated Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
            "PHASE3_POLICY_UNSAFE_SURVEY=pass",
        ),
    ),
    (
        Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
        (),
        (
            "validated Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
            "PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-low-level-wrappers.py"),
        (),
        (
            "validated zigux/tests/phase3_low_level_wrappers.zig",
            "validated zigux/tests/phase3_low_level_wrappers_build.zig",
            "validated zigux/tests/build.zig",
            "validated zigux/Makefile",
        ),
    ),
    (
        Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py"),
        (),
        ("validated Documentation/zigux/phase3-linux-zigux-header-governance.md",),
    ),
    (
        Path("scripts/zigux/check-phase3-selftest-surface.py"),
        (),
        ("validated scripts/zigux/README.md",),
    ),
    (
        Path("scripts/zigux/check-phase3-abi-manifest-replay-routes.py"),
        (),
        ("PHASE3_ABI_MANIFEST_REPLAY_ROUTES=pass",),
    ),
    (
        Path("scripts/zigux/check-phase3-bitmap-cpumask.py"),
        (),
        (
            "PHASE3_BITMAP_CPUMASK_PACKET=pass",
            "validated zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json",
            "validated zigux/tests/phase3_bitmap_cpumask_starter_packet.zig",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-list-hlist-starter-packet.py"),
        (),
        (
            "validated zigux/helpers/list_view.zig",
            "validated zigux/helpers/hlist_view.zig",
            "validated zigux/tests/phase3_list_hlist_starter_packet.zig",
            "validated zigux/tests/phase3_list_hlist_starter_packet_build.zig",
            "validated zigux/tests/fixtures/phase3_list_hlist_manifest.json",
        ),
    ),
    (
        Path("scripts/zigux/check-phase3-list-hlist.py"),
        (),
        (
            "validated zigux/tests/phase3_list_hlist_dump.zig",
            "validated zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c",
            "validated zigux/tests/fixtures/phase3_list_hlist/expected.json",
            "validated zigux/tests/fixtures/phase3_list_hlist_manifest.json",
        ),
    ),
)

SELF_TEST_MISSING_CASES = (
    (0, "expected missing leading script was not reported"),
    (1, "expected errptr-xarray script omission was not reported"),
    (2, "expected xarray-slot starter script omission was not reported"),
    (3, "expected xarray-slot dump script omission was not reported"),
    (4, "expected idr-slot starter script omission was not reported"),
    (5, "expected idr-slot dump script omission was not reported"),
    (6, "expected policy starter script omission was not reported"),
    (7, "expected policy dump script omission was not reported"),
    (8, "expected shared ABI validator omission was not reported"),
    (9, "expected shared ABI checker omission was not reported"),
    (10, "expected shared ABI support-checker omission was not reported"),
    (11, "expected shared-tests-routes script omission was not reported"),
    (12, "expected readme-tooling script omission was not reported"),
    (13, "expected wrapper-template script omission was not reported"),
    (14, "expected catalog-selftest script omission was not reported"),
    (15, "expected validator-support script omission was not reported"),
    (16, "expected export-uapi survey script omission was not reported"),
    (17, "expected export-uapi c-header smoke omission was not reported"),
    (18, "expected abi-header-family survey script omission was not reported"),
    (19, "expected policy-unsafe survey script omission was not reported"),
    (20, "expected low-level-wrapper script omission was not reported"),
    (21, "expected low-level-wrapper compile-route script omission was not reported"),
    (22, "expected linux-zigux header-governance script omission was not reported"),
    (23, "expected selftest-surface script omission was not reported"),
    (24, "expected abi manifest replay-routes script omission was not reported"),
    (25, "expected bitmap-cpumask script omission was not reported"),
    (26, "expected list-hlist starter script omission was not reported"),
    (27, "expected full list-hlist script omission was not reported"),
)


def _missing_output_markers(stdout: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if marker not in stdout]


def _expected_manifest_python_routes(manifest: object) -> set[Path]:
    if not isinstance(manifest, dict):
        return set()
    replay_routes = manifest.get("replay_routes")
    if not isinstance(replay_routes, list):
        return set()
    expected: set[Path] = set()
    for route in replay_routes:
        if not isinstance(route, str):
            continue
        parts = shlex.split(route)
        if len(parts) < 2 or parts[0] != "python3" or "--self-test" in parts[2:]:
            continue
        script_path = Path(parts[1])
        if script_path.parts[:2] == ("scripts", "zigux") and script_path.suffix == ".py" and script_path not in ORCHESTRATION_ROUTES:
            expected.add(script_path)
    return expected


def validate_script_list(repo_root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path, _args, _markers in CHECK_COMMANDS:
        if not (repo_root / rel_path).is_file():
            missing.append(f"missing phase3 check script: {rel_path.as_posix()}")
    return missing


def validate_manifest_python_coverage(repo_root: Path) -> list[str]:
    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.is_file():
        return [f"missing phase3 manifest: {MANIFEST_PATH.as_posix()}"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid phase3 manifest JSON: {MANIFEST_PATH.as_posix()}: {exc}"]
    expected = _expected_manifest_python_routes(manifest)
    actual = {rel_path for rel_path, _args, _markers in CHECK_COMMANDS}
    missing = sorted(expected - actual)
    return ["manifest python replay route missing from CHECK_COMMANDS: " + rel_path.as_posix() for rel_path in missing]


def run_packet(repo_root: Path) -> int:
    missing = validate_script_list(repo_root)
    missing.extend(validate_manifest_python_coverage(repo_root))
    if missing:
        print("PHASE3_CHECK_RUNNER=fail")
        print("\n".join(missing))
        return 1
    for rel_path, args, output_markers in CHECK_COMMANDS:
        result = subprocess.run([sys.executable, rel_path.as_posix(), *args], cwd=repo_root, check=False, capture_output=True, text=True)
        if result.returncode != 0:
            print("PHASE3_CHECK_RUNNER=fail")
            print("phase3 check failed: " + " ".join([rel_path.as_posix(), *args]))
            if result.stdout:
                print(result.stdout.rstrip())
            if result.stderr:
                print(result.stderr.rstrip())
            return 1
        missing_markers = _missing_output_markers(result.stdout, output_markers)
        if missing_markers:
            print("PHASE3_CHECK_RUNNER=fail")
            print("phase3 check produced incomplete success output: " + rel_path.as_posix())
            for marker in missing_markers:
                print(f"missing output marker: {marker}")
            if result.stdout:
                print(result.stdout.rstrip())
            if result.stderr:
                print(result.stderr.rstrip())
            return 1
    print("PHASE3_CHECK_RUNNER=pass")
    print(f"PHASE3_CHECK_RUNNER_CASE_COUNT={len(CHECK_COMMANDS)}")
    return 0


def _write_synthetic_script(path: Path, output_markers: tuple[str, ...], *, failure_code: int | None = None) -> None:
    lines = ["#!/usr/bin/env python3", "import sys"]
    for marker in output_markers:
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
        replay_routes = [f"python3 {rel_path.as_posix()}" for rel_path, _args, _markers in CHECK_COMMANDS]
        replay_routes.extend(["python3 scripts/zigux/run-phase3-checks.py", "python3 scripts/zigux/validate_phase3_selftest.py", "python3 scripts/zigux/check-phase3-abi.py --self-test", "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig"])
    manifest_path.write_text(json.dumps({"replay_routes": replay_routes}, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_check_runner_") as temp_dir:
        root = Path(temp_dir)

        def populate_repo() -> None:
            for rel_path, _args, output_markers in CHECK_COMMANDS:
                path = root / rel_path
                path.parent.mkdir(parents=True, exist_ok=True)
                _write_synthetic_script(path, output_markers)
            _write_synthetic_manifest(root)

        def expect_missing_output_marker(index: int, missing_marker_index: int, message: str) -> int:
            populate_repo()
            output_markers = CHECK_COMMANDS[index][2]
            kept_markers = tuple(marker for marker_index, marker in enumerate(output_markers) if marker_index != missing_marker_index)
            target_path = root / CHECK_COMMANDS[index][0]
            _write_synthetic_script(target_path, kept_markers)
            if run_packet(root) != 1:
                print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
                print(message)
                return 1
            return 0

        populate_repo()
        if validate_script_list(root):
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected synthetic phase3 check set to validate")
            return 1
        manifest_missing = validate_manifest_python_coverage(root)
        if manifest_missing:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected synthetic manifest coverage to validate")
            print("\n".join(manifest_missing))
            return 1
        for index, message in SELF_TEST_MISSING_CASES:
            populate_repo()
            missing_path = CHECK_COMMANDS[index][0]
            (root / missing_path).unlink()
            missing = validate_script_list(root)
            expected = f"missing phase3 check script: {missing_path.as_posix()}"
            if expected not in missing:
                print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
                print(message)
                return 1
        populate_repo()
        _write_synthetic_manifest(root, replay_routes=[f"python3 {rel_path.as_posix()}" for rel_path, _args, _markers in CHECK_COMMANDS] + ["python3 scripts/zigux/manifest-only-check.py"])
        manifest_missing = validate_manifest_python_coverage(root)
        expected_manifest_gap = "manifest python replay route missing from CHECK_COMMANDS: scripts/zigux/manifest-only-check.py"
        if expected_manifest_gap not in manifest_missing:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected manifest-only python replay route omission to be reported")
            return 1
        populate_repo()
        (root / MANIFEST_PATH).unlink()
        manifest_missing = validate_manifest_python_coverage(root)
        expected_manifest_missing = f"missing phase3 manifest: {MANIFEST_PATH.as_posix()}"
        if expected_manifest_missing not in manifest_missing:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing manifest to be reported")
            return 1
        failing_path = root / CHECK_COMMANDS[-2][0]
        populate_repo()
        _write_synthetic_script(failing_path, CHECK_COMMANDS[-2][2], failure_code=9)
        result = run_packet(root)
        if result != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected failing child validator to fail the runner")
            return 1
        xarray_slot_dump_path = root / CHECK_COMMANDS[3][0]
        populate_repo()
        _write_synthetic_script(xarray_slot_dump_path, (CHECK_COMMANDS[3][2][0],))
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing xarray-slot dump output marker to fail the runner")
            return 1
        idr_slot_starter_path = root / CHECK_COMMANDS[4][0]
        populate_repo()
        _write_synthetic_script(idr_slot_starter_path, (CHECK_COMMANDS[4][2][0],))
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing idr-slot starter build marker to fail the runner")
            return 1
        idr_slot_dump_path = root / CHECK_COMMANDS[5][0]
        populate_repo()
        _write_synthetic_script(idr_slot_dump_path, (CHECK_COMMANDS[5][2][0], CHECK_COMMANDS[5][2][1]))
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing idr-slot dump manifest marker to fail the runner")
            return 1
        support_checker_path = root / CHECK_COMMANDS[10][0]
        populate_repo()
        _write_synthetic_script(support_checker_path, ())
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing support-checker output marker to fail the runner")
            return 1
        validator_support_path = root / CHECK_COMMANDS[15][0]
        populate_repo()
        _write_synthetic_script(validator_support_path, (CHECK_COMMANDS[15][2][0],))
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing validator-support shared-reminder marker to fail the runner")
            return 1
        populate_repo()
        _write_synthetic_script(validator_support_path, (CHECK_COMMANDS[15][2][1],))
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing validator-support note marker to fail the runner")
            return 1
        policy_dump_path = root / CHECK_COMMANDS[7][0]
        populate_repo()
        _write_synthetic_script(policy_dump_path, (CHECK_COMMANDS[7][2][0],))
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing policy-dump output marker to fail the runner")
            return 1
        shared_abi_validator_path = root / CHECK_COMMANDS[8][0]
        populate_repo()
        _write_synthetic_script(shared_abi_validator_path, ())
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing shared ABI validator pass marker to fail the runner")
            return 1
        shared_routes_path = root / CHECK_COMMANDS[11][0]
        populate_repo()
        _write_synthetic_script(shared_routes_path, (CHECK_COMMANDS[11][2][0],))
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing shared-routes output marker to fail the runner")
            return 1
        readme_inventory_path = root / CHECK_COMMANDS[12][0]
        populate_repo()
        _write_synthetic_script(readme_inventory_path, ())
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing readme-inventory output marker to fail the runner")
            return 1
        wrapper_templates_path = root / CHECK_COMMANDS[13][0]
        populate_repo()
        _write_synthetic_script(wrapper_templates_path, (CHECK_COMMANDS[13][2][0],))
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing wrapper-template pass marker to fail the runner")
            return 1
        c_header_smoke_path = root / CHECK_COMMANDS[17][0]
        populate_repo()
        _write_synthetic_script(c_header_smoke_path, (CHECK_COMMANDS[17][2][0],))
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing export-uapi c-header smoke pass marker to fail the runner")
            return 1
        header_family_path = root / CHECK_COMMANDS[18][0]
        populate_repo()
        _write_synthetic_script(header_family_path, (CHECK_COMMANDS[18][2][0],))
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing abi-header-family pass marker to fail the runner")
            return 1
        policy_unsafe_path = root / CHECK_COMMANDS[19][0]
        populate_repo()
        _write_synthetic_script(policy_unsafe_path, (CHECK_COMMANDS[19][2][0],))
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing policy-unsafe pass marker to fail the runner")
            return 1
        low_level_wrapper_path = root / CHECK_COMMANDS[20][0]
        populate_repo()
        _write_synthetic_script(low_level_wrapper_path, (CHECK_COMMANDS[20][2][0],))
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing low-level-wrapper pass marker to fail the runner")
            return 1
        if expect_missing_output_marker(21, 0, "expected missing low-level-wrapper replay output marker to fail the runner") != 0:
            return 1
        if expect_missing_output_marker(21, 1, "expected missing low-level-wrapper focused-build output marker to fail the runner") != 0:
            return 1
        if expect_missing_output_marker(21, 2, "expected missing low-level-wrapper shared-build output marker to fail the runner") != 0:
            return 1
        if expect_missing_output_marker(21, 3, "expected missing low-level-wrapper make-route output marker to fail the runner") != 0:
            return 1
        linux_zigux_header_path = root / CHECK_COMMANDS[22][0]
        populate_repo()
        _write_synthetic_script(linux_zigux_header_path, ())
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing linux-zigux header-governance output marker to fail the runner")
            return 1
        selftest_surface_path = root / CHECK_COMMANDS[23][0]
        populate_repo()
        _write_synthetic_script(selftest_surface_path, ())
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing selftest-surface output marker to fail the runner")
            return 1
        manifest_replay_routes_path = root / CHECK_COMMANDS[24][0]
        populate_repo()
        _write_synthetic_script(manifest_replay_routes_path, ())
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing abi manifest replay-routes pass marker to fail the runner")
            return 1
        if expect_missing_output_marker(25, 0, "expected missing bitmap-cpumask pass marker to fail the runner") != 0:
            return 1
        if expect_missing_output_marker(25, 1, "expected missing bitmap-cpumask manifest output marker to fail the runner") != 0:
            return 1
        if expect_missing_output_marker(25, 2, "expected missing bitmap-cpumask starter-packet output marker to fail the runner") != 0:
            return 1
        if expect_missing_output_marker(26, 0, "expected missing list-hlist list-view output marker to fail the runner") != 0:
            return 1
        if expect_missing_output_marker(26, 1, "expected missing list-hlist hlist-view output marker to fail the runner") != 0:
            return 1
        if expect_missing_output_marker(26, 2, "expected missing list-hlist starter-packet output marker to fail the runner") != 0:
            return 1
        if expect_missing_output_marker(26, 3, "expected missing list-hlist build output marker to fail the runner") != 0:
            return 1
        if expect_missing_output_marker(26, 4, "expected missing list-hlist manifest output marker to fail the runner") != 0:
            return 1
        if expect_missing_output_marker(27, 0, "expected missing full list-hlist dump output marker to fail the runner") != 0:
            return 1
        if expect_missing_output_marker(27, 1, "expected missing full list-hlist c-harness output marker to fail the runner") != 0:
            return 1
        if expect_missing_output_marker(27, 2, "expected missing full list-hlist expected-json output marker to fail the runner") != 0:
            return 1
        if expect_missing_output_marker(27, 3, "expected missing full list-hlist manifest output marker to fail the runner") != 0:
            return 1
        print("PHASE3_CHECK_RUNNER_SELF_TEST=pass")
        print("PHASE3_CHECK_RUNNER_SELF_TEST_CASE_COUNT=" f"{len(SELF_TEST_MISSING_CASES) + 38}")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the current bounded Phase 3 validator packet.")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="repository root that contains scripts/zigux/")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    return run_packet(args.repo_root)


if __name__ == "__main__":
    raise SystemExit(main())

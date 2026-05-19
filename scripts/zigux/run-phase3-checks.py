#!/usr/bin/env python3
"""Run the current bounded Phase 3 validator packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

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
        Path("scripts/zigux/check-phase3-policy-starter-packet.py"),
        (),
        ("PHASE3_POLICY_STARTER_PACKET=pass",),
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
        Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),
        (),
        (
            "validated Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
            "validated zigux/tests/phase3_policy_dump.zig",
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
        Path("scripts/zigux/check-phase3-selftest-surface.py"),
        (),
        ("validated scripts/zigux/README.md",),
    ),
)

SELF_TEST_MISSING_CASES = (
    (0, "expected missing leading script was not reported"),
    (1, "expected errptr-xarray script omission was not reported"),
    (2, "expected xarray-slot script omission was not reported"),
    (3, "expected policy starter script omission was not reported"),
    (4, "expected shared ABI validator omission was not reported"),
    (5, "expected shared ABI checker omission was not reported"),
    (6, "expected shared-tests-routes script omission was not reported"),
    (7, "expected readme-tooling script omission was not reported"),
    (8, "expected catalog-selftest script omission was not reported"),
    (9, "expected validator-support script omission was not reported"),
    (10, "expected export-uapi survey script omission was not reported"),
    (11, "expected policy-unsafe survey script omission was not reported"),
    (12, "expected low-level-wrapper script omission was not reported"),
    (13, "expected selftest-surface script omission was not reported"),
)


def _missing_output_markers(stdout: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if marker not in stdout]


def validate_script_list(repo_root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path, _args, _markers in CHECK_COMMANDS:
        if not (repo_root / rel_path).is_file():
            missing.append(f"missing phase3 check script: {rel_path.as_posix()}")
    return missing


def run_packet(repo_root: Path) -> int:
    missing = validate_script_list(repo_root)
    if missing:
        print("PHASE3_CHECK_RUNNER=fail")
        print("\n".join(missing))
        return 1

    for rel_path, args, output_markers in CHECK_COMMANDS:
        result = subprocess.run(
            [sys.executable, rel_path.as_posix(), *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
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


def _write_synthetic_script(
    path: Path,
    output_markers: tuple[str, ...],
    *,
    failure_code: int | None = None,
) -> None:
    lines = ["#!/usr/bin/env python3", "import sys"]
    for marker in output_markers:
        lines.append(f"print({marker!r})")
    if failure_code is None:
        lines.append("raise SystemExit(0)")
    else:
        lines.append("print('synthetic stderr detail', file=sys.stderr)")
        lines.append(f"raise SystemExit({failure_code})")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_check_runner_") as temp_dir:
        root = Path(temp_dir)

        def populate_repo() -> None:
            for rel_path, _args, output_markers in CHECK_COMMANDS:
                path = root / rel_path
                path.parent.mkdir(parents=True, exist_ok=True)
                _write_synthetic_script(path, output_markers)

        populate_repo()

        if validate_script_list(root):
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected synthetic phase3 check set to validate")
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

        failing_path = CHECK_COMMANDS[-2][0]
        populate_repo()
        _write_synthetic_script(
            root / failing_path,
            CHECK_COMMANDS[-2][2],
            failure_code=9,
        )
        result = run_packet(root)
        if result != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected failing child validator to fail the runner")
            return 1

        shared_routes_path = root / CHECK_COMMANDS[6][0]
        populate_repo()
        _write_synthetic_script(
            shared_routes_path,
            (CHECK_COMMANDS[6][2][0],),
        )
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing shared-routes output marker to fail the runner")
            return 1

        readme_inventory_path = root / CHECK_COMMANDS[7][0]
        populate_repo()
        _write_synthetic_script(readme_inventory_path, ())
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing readme-inventory output marker to fail the runner")
            return 1

        low_level_wrapper_path = root / CHECK_COMMANDS[12][0]
        populate_repo()
        _write_synthetic_script(
            low_level_wrapper_path,
            (CHECK_COMMANDS[12][2][0],),
        )
        if run_packet(root) != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected missing low-level-wrapper pass marker to fail the runner")
            return 1

        print("PHASE3_CHECK_RUNNER_SELF_TEST=pass")
        print(
            "PHASE3_CHECK_RUNNER_SELF_TEST_CASE_COUNT="
            f"{len(SELF_TEST_MISSING_CASES) + 5}"
        )
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the current bounded Phase 3 validator packet."
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

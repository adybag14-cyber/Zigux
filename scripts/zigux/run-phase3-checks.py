#!/usr/bin/env python3
"""Run the current bounded Phase 3 validator packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

CHECK_COMMANDS = (
    (Path("scripts/zigux/check-phase3-dev-t-starter-packet.py"), ()),
    (Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py"), ()),
    (Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py"), ()),
    (Path("scripts/zigux/check-phase3-policy-starter-packet.py"), ()),
    (Path("scripts/zigux/validate-phase3.py"), ()),
    (Path("scripts/zigux/check-phase3-shared-tests-routes.py"), ()),
    (Path("scripts/zigux/check-phase3-readme-tooling-inventory.py"), ()),
    (Path("scripts/zigux/validate-phase3-validator-support-surface.py"), ()),
    (Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"), ()),
    (Path("scripts/zigux/check-phase3-selftest-surface.py"), ()),
)

SELF_TEST_MISSING_CASES = (
    (0, "expected missing leading script was not reported"),
    (2, "expected xarray-slot script omission was not reported"),
    (4, "expected shared ABI validator omission was not reported"),
    (5, "expected shared-tests-routes script omission was not reported"),
    (6, "expected readme-tooling script omission was not reported"),
    (7, "expected validator-support script omission was not reported"),
    (8, "expected low-level-wrapper script omission was not reported"),
    (9, "expected selftest-surface script omission was not reported"),
)


def validate_script_list(repo_root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path, _args in CHECK_COMMANDS:
        if not (repo_root / rel_path).is_file():
            missing.append(f"missing phase3 check script: {rel_path.as_posix()}")
    return missing


def run_packet(repo_root: Path) -> int:
    missing = validate_script_list(repo_root)
    if missing:
        print("PHASE3_CHECK_RUNNER=fail")
        print("\n".join(missing))
        return 1

    for rel_path, args in CHECK_COMMANDS:
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

    print("PHASE3_CHECK_RUNNER=pass")
    print(f"PHASE3_CHECK_RUNNER_CASE_COUNT={len(CHECK_COMMANDS)}")
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_check_runner_") as temp_dir:
        root = Path(temp_dir)

        def populate_repo() -> None:
            for rel_path, _args in CHECK_COMMANDS:
                path = root / rel_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "#!/usr/bin/env python3\nraise SystemExit(0)\n",
                    encoding="utf-8",
                )

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
        (root / failing_path).write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "print('synthetic phase3 validator failure')\n"
            "print('synthetic stderr detail', file=sys.stderr)\n"
            "raise SystemExit(9)\n",
            encoding="utf-8",
        )
        result = run_packet(root)
        if result != 1:
            print("PHASE3_CHECK_RUNNER_SELF_TEST=fail")
            print("expected failing child validator to fail the runner")
            return 1

        print("PHASE3_CHECK_RUNNER_SELF_TEST=pass")
        print(
            "PHASE3_CHECK_RUNNER_SELF_TEST_CASE_COUNT="
            f"{len(SELF_TEST_MISSING_CASES) + 2}"
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
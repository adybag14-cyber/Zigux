#!/usr/bin/env python3

"""Run the current bounded Phase 3 interop self-test packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

SELFTEST_COMMANDS = (
    (Path("scripts/zigux/check-phase3-dev-t-starter-packet.py"), ("--self-test",)),
    (
        Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py"),
        ("--self-test",),
    ),
    (Path("scripts/zigux/check-phase3-policy-starter-packet.py"), ("--self-test",)),
    (Path("scripts/zigux/validate-phase3.py"), ("--self-test",)),
    (Path("scripts/zigux/check-phase3-shared-tests-routes.py"), ("--self-test",)),
    (Path("scripts/zigux/check-phase3-readme-tooling-inventory.py"), ("--self-test",)),
    (Path("scripts/zigux/run-phase3-checks.py"), ("--self-test",)),
    (
        Path("scripts/zigux/validate-phase3-validator-support-surface.py"),
        ("--self-test",),
    ),
    (
        Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
        ("--self-test",),
    ),
    (Path("scripts/zigux/check-phase3-selftest-surface.py"), ("--self-test",)),
)


def validate_script_list(repo_root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path, _args in SELFTEST_COMMANDS:
        if not (repo_root / rel_path).is_file():
            missing.append(f"missing selftest script: {rel_path.as_posix()}")
    return missing


def run_packet(repo_root: Path) -> int:
    missing = validate_script_list(repo_root)
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
            print("self-test failed: " + " ".join([rel_path.as_posix(), *args]))
            if result.stdout:
                print(result.stdout.rstrip())
            if result.stderr:
                print(result.stderr.rstrip())
            return 1
    print("PHASE3_VALIDATE_SELFTEST=pass")
    return 0


def _populate_repo(root: Path) -> None:
    for rel_path, _args in SELFTEST_COMMANDS:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "#!/usr/bin/env python3\nraise SystemExit(0)\n",
            encoding="utf-8",
        )


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

        missing_cases = (
            (0, "expected missing leading script was not reported"),
            (3, "expected shared ABI validator omission was not reported"),
            (4, "expected shared-routes script omission was not reported"),
            (6, "expected runner omission was not reported"),
            (7, "expected validator-support script omission was not reported"),
            (8, "expected low-level-wrapper script omission was not reported"),
            (9, "expected missing trailing script was not reported"),
        )
        for index, message in missing_cases:
            if _expect_missing(root, index, message) != 0:
                return 1

        _populate_repo(root)
        failing_path = SELFTEST_COMMANDS[8][0]
        (root / failing_path).write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "print('synthetic low-level-wrapper failure')\n"
            "print('synthetic stderr detail', file=sys.stderr)\n"
            "raise SystemExit(7)\n",
            encoding="utf-8",
        )
        result = run_packet(root)
        if result != 1:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected failing child self-test to fail the packet")
            return 1

        print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=pass")
        print("PHASE3_VALIDATE_SELFTEST_SELF_TEST_CASE_COUNT=9")
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

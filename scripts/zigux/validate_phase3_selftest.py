#!/usr/bin/env python3
"""Run the focused Phase 3 validator-support self-test packet."""

from __future__ import annotations

import argparse
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

        if validate_script_list(root):
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected synthetic self-test script set to validate")
            return 1

        first_path = SELFTEST_COMMANDS[0][0]
        (root / first_path).unlink()
        missing = validate_script_list(root)
        expected = f"missing selftest script: {first_path.as_posix()}"
        if expected not in missing:
            print("PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail")
            print("expected missing script was not reported")
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

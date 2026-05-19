#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

EXPECTED_MAKE_EXPANSIONS = {
    "phase7-validate": [
        "python3 scripts/zigux/validate-phase7.py --self-test",
        "python3 scripts/zigux/validate-phase7.py",
        "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper.py",
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
        "python3 scripts/zigux/check-phase7-build-wiring.py",
    ],
    "phase7-test": [
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    ],
    "phase7": [
        "python3 scripts/zigux/validate-phase7.py --self-test",
        "python3 scripts/zigux/validate-phase7.py",
        "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper.py",
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
        "python3 scripts/zigux/check-phase7-build-wiring.py",
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    ],
}

UNEXPECTED_MAKE_EXPANSIONS = {
    "phase7-validate": [
        "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        "python3 scripts/zigux/check-phase7-build-inventory.py",
        "zig build test --build-file zigux/tests/phase7_build.zig",
        "zig build test --build-file zigux/tests/build.zig",
    ],
    "phase7-test": [
        "python3 scripts/zigux/validate-phase7.py --self-test",
        "python3 scripts/zigux/validate-phase7.py",
        "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper.py",
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
        "python3 scripts/zigux/check-phase7-build-wiring.py",
        "zig build test --build-file zigux/tests/phase7_build.zig",
        "zig build test --build-file zigux/tests/build.zig",
    ],
    "phase7": [
        "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        "python3 scripts/zigux/check-phase7-build-inventory.py",
        "zig build test --build-file zigux/tests/phase7_build.zig",
        "zig build test --build-file zigux/tests/build.zig",
    ],
}


def normalize_wrapper_line(line: str) -> str:
    parts = [part.strip() for part in line.split("&&") if part.strip()]
    if parts:
        return parts[-1]
    return line.strip()


def collect_failures(root: Path, env: dict[str, str] | None = None) -> list[str]:
    failures: list[str] = []
    for target_name, expected_lines in EXPECTED_MAKE_EXPANSIONS.items():
        result = subprocess.run(
            ["make", "-n", "-C", str(root / "zigux"), target_name],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        if result.returncode != 0:
            failures.append(
                f"{target_name}: make -n failed with returncode {result.returncode}"
            )
            stderr = result.stderr.strip()
            if stderr:
                failures.append(stderr)
            continue

        wrapper_lines = [
            normalize_wrapper_line(line)
            for line in result.stdout.splitlines()
            if line.strip()
        ]
        for line in expected_lines:
            actual_count = wrapper_lines.count(line)
            if actual_count == 0:
                failures.append(
                    f"{target_name}: missing expected wrapper expansion: {line}"
                )
                continue
            if actual_count != 1:
                failures.append(
                    f"{target_name}: expected wrapper expansion count drift: {line} ({actual_count} != 1)"
                )

        for line in UNEXPECTED_MAKE_EXPANSIONS.get(target_name, []):
            if line in wrapper_lines:
                failures.append(
                    f"{target_name}: unexpected wrapper expansion: {line}"
                )

        expected_positions = {
            line: wrapper_lines.index(line)
            for line in expected_lines
            if line in wrapper_lines
        }
        for earlier, later in zip(expected_lines, expected_lines[1:]):
            earlier_pos = expected_positions.get(earlier)
            later_pos = expected_positions.get(later)
            if earlier_pos is None or later_pos is None:
                continue
            if earlier_pos >= later_pos:
                failures.append(
                    f"{target_name}: wrapper expansion order drift: expected {earlier!r} before {later!r}"
                )
                break

    return failures


def make_fake_make(fake_make_path: Path, outputs: dict[str, list[str]]) -> None:
    lines = [
        "#!/usr/bin/env python3",
        "import sys",
        "",
        "target = sys.argv[-1]",
        "outputs = {",
    ]
    for target, values in outputs.items():
        lines.append(f"    {target!r}: [")
        for value in values:
            lines.append(f"        {value!r},")
        lines.append("    ],")
    lines.extend(
        [
            "}",
            "for line in outputs.get(target, []):",
            "    print(line)",
        ]
    )
    fake_make_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    fake_make_path.chmod(0o755)


def expect_failure(
    label: str,
    root: Path,
    env: dict[str, str],
    expected_message: str,
) -> None:
    failures = collect_failures(root, env=env)
    joined = "\n".join(failures)
    if not failures:
        raise SystemExit(f"phase7-make-wrapper-selftest:{label}:unexpected_pass")
    if expected_message not in joined:
        raise SystemExit(
            f"phase7-make-wrapper-selftest:{label}:expected:{expected_message}:actual:{joined}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_make_wrapper_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        (tmp_root / "zigux").mkdir()
        fake_make_dir = tmp_root / "fake-bin"
        fake_make_dir.mkdir()
        fake_make_path = fake_make_dir / "make"
        fake_make_env = os.environ.copy()
        fake_make_env["PATH"] = f"{fake_make_dir}:{fake_make_env['PATH']}"

        make_fake_make(fake_make_path, EXPECTED_MAKE_EXPANSIONS)
        failures = collect_failures(tmp_root, env=fake_make_env)
        if failures:
            raise SystemExit(
                "phase7-make-wrapper-selftest:baseline_failed:" + " | ".join(failures)
            )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line != "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test"
                ],
            },
        )
        expect_failure(
            "missing_make_wrapper_selftest",
            tmp_root,
            fake_make_env,
            "phase7-validate: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    *EXPECTED_MAKE_EXPANSIONS["phase7-validate"],
                    EXPECTED_MAKE_EXPANSIONS["phase7-validate"][2],
                ],
            },
        )
        expect_failure(
            "duplicate_make_wrapper_selftest",
            tmp_root,
            fake_make_env,
            "phase7-validate: expected wrapper expansion count drift: python3 scripts/zigux/check-phase7-make-wrapper.py --self-test (2 != 1)",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line
                    != "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test"
                ],
            },
        )
        expect_failure(
            "missing_make_wrapper_alignment_selftest",
            tmp_root,
            fake_make_env,
            "phase7-validate: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    *EXPECTED_MAKE_EXPANSIONS["phase7-validate"],
                    EXPECTED_MAKE_EXPANSIONS["phase7-validate"][4],
                ],
            },
        )
        expect_failure(
            "duplicate_make_wrapper_alignment_selftest",
            tmp_root,
            fake_make_env,
            "phase7-validate: expected wrapper expansion count drift: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test (2 != 1)",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line
                    != "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py"
                ],
            },
        )
        expect_failure(
            "missing_make_wrapper_alignment_live",
            tmp_root,
            fake_make_env,
            "phase7-validate: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    *EXPECTED_MAKE_EXPANSIONS["phase7-validate"],
                    EXPECTED_MAKE_EXPANSIONS["phase7-validate"][5],
                ],
            },
        )
        expect_failure(
            "duplicate_make_wrapper_alignment_live",
            tmp_root,
            fake_make_env,
            "phase7-validate: expected wrapper expansion count drift: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py (2 != 1)",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line != "python3 scripts/zigux/check-phase7-build-wiring.py --self-test"
                ],
            },
        )
        expect_failure(
            "missing_build_wiring_selftest",
            tmp_root,
            fake_make_env,
            "phase7-validate: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    *EXPECTED_MAKE_EXPANSIONS["phase7-validate"],
                    EXPECTED_MAKE_EXPANSIONS["phase7-validate"][10],
                ],
            },
        )
        expect_failure(
            "duplicate_build_wiring_selftest",
            tmp_root,
            fake_make_env,
            "phase7-validate: expected wrapper expansion count drift: python3 scripts/zigux/check-phase7-build-wiring.py --self-test (2 != 1)",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    line
                    for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                    if line != "python3 scripts/zigux/check-phase7-build-wiring.py"
                ],
            },
        )
        expect_failure(
            "missing_build_wiring_live",
            tmp_root,
            fake_make_env,
            "phase7-validate: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-build-wiring.py",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    *EXPECTED_MAKE_EXPANSIONS["phase7-validate"],
                    EXPECTED_MAKE_EXPANSIONS["phase7-validate"][11],
                ],
            },
        )
        expect_failure(
            "duplicate_build_wiring_live",
            tmp_root,
            fake_make_env,
            "phase7-validate: expected wrapper expansion count drift: python3 scripts/zigux/check-phase7-build-wiring.py (2 != 1)",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-test": [
                    *EXPECTED_MAKE_EXPANSIONS["phase7-test"],
                    EXPECTED_MAKE_EXPANSIONS["phase7-test"][0],
                ],
            },
        )
        expect_failure(
            "duplicate_phase7_test_wrapper_line",
            tmp_root,
            fake_make_env,
            "phase7-test: expected wrapper expansion count drift: zig build test --build-file zigux/tests/phase7_build.zig --summary all (2 != 1)",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-test": [
                    "zig build test --build-file zigux/tests/phase7_build.zig",
                ],
            },
        )
        expect_failure(
            "stale_unsummarized_phase7_test",
            tmp_root,
            fake_make_env,
            "phase7-test: missing expected wrapper expansion: zig build test --build-file zigux/tests/phase7_build.zig --summary all",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-test": [
                    "python3 scripts/zigux/validate-phase7.py",
                    *EXPECTED_MAKE_EXPANSIONS["phase7-test"],
                ],
            },
        )
        expect_failure(
            "stale_validator_in_phase7_test",
            tmp_root,
            fake_make_env,
            "phase7-test: unexpected wrapper expansion: python3 scripts/zigux/validate-phase7.py",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-test": [
                    "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
                    *EXPECTED_MAKE_EXPANSIONS["phase7-test"],
                ],
            },
        )
        expect_failure(
            "stale_alignment_checker_in_phase7_test",
            tmp_root,
            fake_make_env,
            "phase7-test: unexpected wrapper expansion: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-test": [
                    "python3 scripts/zigux/check-phase7-build-wiring.py",
                    *EXPECTED_MAKE_EXPANSIONS["phase7-test"],
                ],
            },
        )
        expect_failure(
            "stale_build_wiring_in_phase7_test",
            tmp_root,
            fake_make_env,
            "phase7-test: unexpected wrapper expansion: python3 scripts/zigux/check-phase7-build-wiring.py",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7-validate": [
                    "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
                    *EXPECTED_MAKE_EXPANSIONS["phase7-validate"],
                ],
            },
        )
        expect_failure(
            "stale_inventory_checker_in_phase7_validate",
            tmp_root,
            fake_make_env,
            "phase7-validate: unexpected wrapper expansion: python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7": [
                    *EXPECTED_MAKE_EXPANSIONS["phase7"][:-1],
                    "python3 scripts/zigux/check-phase7-build-inventory.py",
                    EXPECTED_MAKE_EXPANSIONS["phase7"][-1],
                ],
            },
        )
        expect_failure(
            "stale_inventory_checker_in_phase7_bundle",
            tmp_root,
            fake_make_env,
            "phase7: unexpected wrapper expansion: python3 scripts/zigux/check-phase7-build-inventory.py",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7": [
                    "zig build test --build-file zigux/tests/build.zig",
                    *EXPECTED_MAKE_EXPANSIONS["phase7"],
                ],
            },
        )
        expect_failure(
            "stale_shared_build_in_phase7_bundle",
            tmp_root,
            fake_make_env,
            "phase7: unexpected wrapper expansion: zig build test --build-file zigux/tests/build.zig",
        )

        make_fake_make(
            fake_make_path,
            {
                **EXPECTED_MAKE_EXPANSIONS,
                "phase7": [
                    "python3 scripts/zigux/validate-phase7.py",
                    "python3 scripts/zigux/validate-phase7.py --self-test",
                    *EXPECTED_MAKE_EXPANSIONS["phase7"][2:],
                ],
            },
        )
        expect_failure(
            "phase7_order_drift",
            tmp_root,
            fake_make_env,
            "phase7: wrapper expansion order drift: expected 'python3 scripts/zigux/validate-phase7.py --self-test' before 'python3 scripts/zigux/validate-phase7.py'",
        )

    print("PHASE7_MAKE_WRAPPER_SELF_TEST=pass")
    print("PHASE7_MAKE_WRAPPER_SELF_TEST_CASE_COUNT=19")
    return 0


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return run_self_test()

    failures = collect_failures(ROOT)
    if failures:
        print("PHASE7_MAKE_WRAPPER=fail")
        print("PHASE7_MAKE_WRAPPER_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE7_MAKE_WRAPPER_FAILURES_END")
        return 1

    print("PHASE7_MAKE_WRAPPER=pass")
    print(f"PHASE7_MAKE_WRAPPER_TARGET_COUNT={len(EXPECTED_MAKE_EXPANSIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
        "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        "python3 scripts/zigux/check-phase7-build-inventory.py",
        "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper.py",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
    ],
    "phase7-test": [
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    ],
    "phase7": [
        "python3 scripts/zigux/validate-phase7.py --self-test",
        "python3 scripts/zigux/validate-phase7.py",
        "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        "python3 scripts/zigux/check-phase7-build-inventory.py",
        "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper.py",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    ],
}

UNEXPECTED_MAKE_EXPANSIONS = {
    "phase7-validate": [
        "zig build test --build-file zigux/tests/build.zig",
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    ],
    "phase7-test": [
        "python3 scripts/zigux/validate-phase7.py --self-test",
        "python3 scripts/zigux/validate-phase7.py",
        "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        "python3 scripts/zigux/check-phase7-build-inventory.py",
        "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper.py",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "zig build test --build-file zigux/tests/build.zig",
    ],
    "phase7": [
        "zig build test --build-file zigux/tests/build.zig",
    ],
}


def check_root(root: Path, env: dict[str, str] | None = None) -> tuple[bool, list[str]]:
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

        wrapper_lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        wrapper_line_set = set(wrapper_lines)
        for line in expected_lines:
            if line not in wrapper_line_set:
                failures.append(
                    f"{target_name}: missing expected wrapper expansion: {line}"
                )

        for line in UNEXPECTED_MAKE_EXPANSIONS.get(target_name, []):
            if line in wrapper_line_set:
                failures.append(
                    f"{target_name}: unexpected wrapper expansion: {line}"
                )

        expected_positions = {
            line: wrapper_lines.index(line)
            for line in expected_lines
            if line in wrapper_line_set
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

    return (len(failures) == 0, failures)


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
    label: str, root: Path, env: dict[str, str], expected_message: str
) -> None:
    ok, failures = check_root(root, env=env)
    if ok:
        raise SystemExit(f"phase7-make-wrapper-selftest:{label}:unexpected_pass")
    joined = "\n".join(failures)
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

        valid_outputs = {
            "phase7-validate": EXPECTED_MAKE_EXPANSIONS["phase7-validate"],
            "phase7-test": EXPECTED_MAKE_EXPANSIONS["phase7-test"],
            "phase7": EXPECTED_MAKE_EXPANSIONS["phase7"],
        }
        make_fake_make(fake_make_path, valid_outputs)
        ok, failures = check_root(tmp_root, env=fake_make_env)
        if not ok:
            raise SystemExit(
                "phase7-make-wrapper-selftest:baseline_failed:"
                + (" | ".join(failures) or "no_output")
            )

        missing_build_inventory_selftest = {
            "phase7-validate": [
                line
                for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                if line
                != "python3 scripts/zigux/check-phase7-build-inventory.py --self-test"
            ],
            "phase7-test": EXPECTED_MAKE_EXPANSIONS["phase7-test"],
            "phase7": EXPECTED_MAKE_EXPANSIONS["phase7"],
        }
        make_fake_make(fake_make_path, missing_build_inventory_selftest)
        expect_failure(
            "missing_build_inventory_selftest",
            tmp_root,
            fake_make_env,
            "phase7-validate: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        )

        missing_build_inventory_live = {
            "phase7-validate": [
                line
                for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                if line != "python3 scripts/zigux/check-phase7-build-inventory.py"
            ],
            "phase7-test": EXPECTED_MAKE_EXPANSIONS["phase7-test"],
            "phase7": EXPECTED_MAKE_EXPANSIONS["phase7"],
        }
        make_fake_make(fake_make_path, missing_build_inventory_live)
        expect_failure(
            "missing_build_inventory_live",
            tmp_root,
            fake_make_env,
            "phase7-validate: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-build-inventory.py",
        )

        missing_build_inventory_selftest_in_phase7_bundle = {
            "phase7-validate": EXPECTED_MAKE_EXPANSIONS["phase7-validate"],
            "phase7-test": EXPECTED_MAKE_EXPANSIONS["phase7-test"],
            "phase7": [
                line
                for line in EXPECTED_MAKE_EXPANSIONS["phase7"]
                if line
                != "python3 scripts/zigux/check-phase7-build-inventory.py --self-test"
            ],
        }
        make_fake_make(fake_make_path, missing_build_inventory_selftest_in_phase7_bundle)
        expect_failure(
            "missing_build_inventory_selftest_in_phase7_bundle",
            tmp_root,
            fake_make_env,
            "phase7: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        )

        missing_build_inventory_live_in_phase7_bundle = {
            "phase7-validate": EXPECTED_MAKE_EXPANSIONS["phase7-validate"],
            "phase7-test": EXPECTED_MAKE_EXPANSIONS["phase7-test"],
            "phase7": [
                line
                for line in EXPECTED_MAKE_EXPANSIONS["phase7"]
                if line != "python3 scripts/zigux/check-phase7-build-inventory.py"
            ],
        }
        make_fake_make(fake_make_path, missing_build_inventory_live_in_phase7_bundle)
        expect_failure(
            "missing_build_inventory_live_in_phase7_bundle",
            tmp_root,
            fake_make_env,
            "phase7: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-build-inventory.py",
        )

        missing_cmdline_selftest = {
            "phase7-validate": [
                line
                for line in EXPECTED_MAKE_EXPANSIONS["phase7-validate"]
                if line
                != "python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test"
            ],
            "phase7-test": EXPECTED_MAKE_EXPANSIONS["phase7-test"],
            "phase7": EXPECTED_MAKE_EXPANSIONS["phase7"],
        }
        make_fake_make(fake_make_path, missing_cmdline_selftest)
        expect_failure(
            "missing_cmdline_selftest",
            tmp_root,
            fake_make_env,
            "phase7-validate: missing expected wrapper expansion: python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test",
        )

        missing_summary = {
            "phase7-validate": EXPECTED_MAKE_EXPANSIONS["phase7-validate"],
            "phase7-test": [
                "zig build test --build-file zigux/tests/phase7_build.zig",
            ],
            "phase7": EXPECTED_MAKE_EXPANSIONS["phase7"],
        }
        make_fake_make(fake_make_path, missing_summary)
        expect_failure(
            "missing_summary",
            tmp_root,
            fake_make_env,
            "phase7-test: missing expected wrapper expansion: zig build test --build-file zigux/tests/phase7_build.zig --summary all",
        )

        stale_build = {
            "phase7-validate": EXPECTED_MAKE_EXPANSIONS["phase7-validate"],
            "phase7-test": [
                "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
                "zig build test --build-file zigux/tests/build.zig",
            ],
            "phase7": [
                *EXPECTED_MAKE_EXPANSIONS["phase7"],
                "zig build test --build-file zigux/tests/build.zig",
            ],
        }
        make_fake_make(fake_make_path, stale_build)
        expect_failure(
            "stale_build_wrapper",
            tmp_root,
            fake_make_env,
            "phase7-test: unexpected wrapper expansion: zig build test --build-file zigux/tests/build.zig",
        )

        stale_build_in_phase7_bundle = {
            "phase7-validate": EXPECTED_MAKE_EXPANSIONS["phase7-validate"],
            "phase7-test": EXPECTED_MAKE_EXPANSIONS["phase7-test"],
            "phase7": [
                *EXPECTED_MAKE_EXPANSIONS["phase7"],
                "zig build test --build-file zigux/tests/build.zig",
            ],
        }
        make_fake_make(fake_make_path, stale_build_in_phase7_bundle)
        expect_failure(
            "stale_build_in_phase7_bundle",
            tmp_root,
            fake_make_env,
            "phase7: unexpected wrapper expansion: zig build test --build-file zigux/tests/build.zig",
        )

        order_drift_phase7_validate = {
            "phase7-validate": [
                "python3 scripts/zigux/validate-phase7.py --self-test",
                "python3 scripts/zigux/validate-phase7.py",
                "python3 scripts/zigux/check-phase7-build-inventory.py",
                "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
                "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
                "python3 scripts/zigux/check-phase7-make-wrapper.py",
                "python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test",
                "python3 scripts/zigux/check-phase7-cmdline-parity.py",
                "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
                "python3 scripts/zigux/check-phase7-rbtree-parity.py",
            ],
            "phase7-test": EXPECTED_MAKE_EXPANSIONS["phase7-test"],
            "phase7": EXPECTED_MAKE_EXPANSIONS["phase7"],
        }
        make_fake_make(fake_make_path, order_drift_phase7_validate)
        expect_failure(
            "order_drift_phase7_validate",
            tmp_root,
            fake_make_env,
            "phase7-validate: wrapper expansion order drift: expected 'python3 scripts/zigux/check-phase7-build-inventory.py --self-test' before 'python3 scripts/zigux/check-phase7-build-inventory.py'",
        )

        order_drift_phase7_bundle = {
            "phase7-validate": EXPECTED_MAKE_EXPANSIONS["phase7-validate"],
            "phase7-test": EXPECTED_MAKE_EXPANSIONS["phase7-test"],
            "phase7": [
                "python3 scripts/zigux/validate-phase7.py --self-test",
                "python3 scripts/zigux/validate-phase7.py",
                "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
                "python3 scripts/zigux/check-phase7-build-inventory.py",
                "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
                "python3 scripts/zigux/check-phase7-make-wrapper.py",
                "python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test",
                "python3 scripts/zigux/check-phase7-cmdline-parity.py",
                "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
                "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
                "python3 scripts/zigux/check-phase7-rbtree-parity.py",
            ],
        }
        make_fake_make(fake_make_path, order_drift_phase7_bundle)
        expect_failure(
            "order_drift_phase7_bundle",
            tmp_root,
            fake_make_env,
            "phase7: wrapper expansion order drift: expected 'python3 scripts/zigux/check-phase7-rbtree-parity.py' before 'zig build test --build-file zigux/tests/phase7_build.zig --summary all'",
        )

    print("PHASE7_MAKE_WRAPPER_SELF_TEST=pass")
    print("PHASE7_MAKE_WRAPPER_SELF_TEST_CASE_COUNT=11")
    return 0


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return run_self_test()

    ok, failures = check_root(ROOT)
    if not ok:
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

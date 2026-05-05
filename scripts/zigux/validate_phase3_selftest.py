#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHASE3_VALIDATOR_SELF_TEST_CASE_COUNT = 12


@dataclass(frozen=True)
class SelfTestTarget:
    relpath: str
    marker: str | None


SELF_TEST_TARGETS = (
    SelfTestTarget("scripts/zigux/validate-phase3.py", "PHASE3_VALIDATE_SELF_TEST=pass"),
    SelfTestTarget(
        "scripts/zigux/check-phase3-selftest-surface.py",
        "PHASE3_SELFTEST_SURFACE_SELF_TEST=pass",
    ),
    SelfTestTarget(
        "scripts/zigux/check-phase3-readme-tooling-inventory.py",
        "PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass",
    ),
    SelfTestTarget(
        "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
        "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass",
    ),
    SelfTestTarget(
        "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
        "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass",
    ),
    SelfTestTarget(
        "scripts/zigux/phase3_catalog.py",
        "PHASE3_CATALOG_SELF_TEST=pass",
    ),
    SelfTestTarget("scripts/zigux/phase3_check_lib.py", "PHASE3_CHECK_LIB_SELF_TEST=pass"),
    SelfTestTarget("scripts/zigux/run-phase3-checks.py", "PHASE3_RUNNER_SELF_TEST=pass"),
    SelfTestTarget(
        "scripts/zigux/generate-phase3-check-wrappers.py",
        "PHASE3_WRAPPER_SELF_TEST=pass",
    ),
)


def run_targets(root: Path, targets: tuple[SelfTestTarget, ...] = SELF_TEST_TARGETS) -> list[str]:
    issues: list[str] = []
    for target in targets:
        script_path = root / target.relpath
        if not script_path.exists():
            issues.append(f"missing_script:{target.relpath}")
            continue

        completed = subprocess.run(
            [sys.executable, str(script_path), "--self-test"],
            cwd=str(root),
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            issues.append(f"self_test_failed:{target.relpath}:rc={completed.returncode}")
            stdout = completed.stdout.strip()
            stderr = completed.stderr.strip()
            if stdout:
                issues.append(f"self_test_stdout:{target.relpath}:{stdout}")
            if stderr:
                issues.append(f"self_test_stderr:{target.relpath}:{stderr}")
            continue

        if target.marker and target.marker not in completed.stdout:
            issues.append(f"missing_pass_marker:{target.relpath}:{target.marker}")

    return issues


def write_script(path: Path, marker: str, *, exit_code: int = 0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "#!/usr/bin/env python3",
        "from __future__ import annotations",
        "",
        "import sys",
        "",
        'if "--self-test" in sys.argv:',
        f'    print("{marker}")',
        f"    raise SystemExit({exit_code})",
        "",
        'raise SystemExit("expected --self-test")',
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validator_selftest_runner_") as tmp_dir:
        root = Path(tmp_dir)
        for target in SELF_TEST_TARGETS:
            write_script(root / target.relpath, target.marker or "PASS")

        issues = run_targets(root)
        assert issues == [], issues

        missing_root = Path(tmp_dir) / "missing"
        for target in SELF_TEST_TARGETS[1:]:
            write_script(missing_root / target.relpath, target.marker or "PASS")
        issues = run_targets(missing_root)
        assert issues == [f"missing_script:{SELF_TEST_TARGETS[0].relpath}"], issues

        failing_root = Path(tmp_dir) / "failing"
        for target in SELF_TEST_TARGETS:
            exit_code = 7 if target.relpath.endswith("run-phase3-checks.py") else 0
            write_script(failing_root / target.relpath, target.marker or "PASS", exit_code=exit_code)
        issues = run_targets(failing_root)
        assert f"self_test_failed:scripts/zigux/run-phase3-checks.py:rc=7" in issues

        validate_marker_root = Path(tmp_dir) / "validate-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("validate-phase3.py")
                else (target.marker or "PASS")
            )
            write_script(validate_marker_root / target.relpath, marker)
        issues = run_targets(validate_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/validate-phase3.py:PHASE3_VALIDATE_SELF_TEST=pass"
            in issues
        )

        marker_root = Path(tmp_dir) / "marker"
        for target in SELF_TEST_TARGETS:
            marker = "WRONG_MARKER=pass" if target.relpath.endswith("phase3_check_lib.py") else (target.marker or "PASS")
            write_script(marker_root / target.relpath, marker)
        issues = run_targets(marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/phase3_check_lib.py:PHASE3_CHECK_LIB_SELF_TEST=pass"
            in issues
        )

        surface_marker_root = Path(tmp_dir) / "surface-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("check-phase3-selftest-surface.py")
                else (target.marker or "PASS")
            )
            write_script(surface_marker_root / target.relpath, marker)
        issues = run_targets(surface_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/check-phase3-selftest-surface.py:"
            "PHASE3_SELFTEST_SURFACE_SELF_TEST=pass"
            in issues
        )

        tooling_inventory_marker_root = Path(tmp_dir) / "tooling-inventory-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("check-phase3-readme-tooling-inventory.py")
                else (target.marker or "PASS")
            )
            write_script(tooling_inventory_marker_root / target.relpath, marker)
        issues = run_targets(tooling_inventory_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/check-phase3-readme-tooling-inventory.py:"
            "PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass"
            in issues
        )

        policy_unsafe_marker_root = Path(tmp_dir) / "policy-unsafe-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("validate-phase3-policy-unsafe-survey.py")
                else (target.marker or "PASS")
            )
            write_script(policy_unsafe_marker_root / target.relpath, marker)
        issues = run_targets(policy_unsafe_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/validate-phase3-policy-unsafe-survey.py:"
            "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass"
            in issues
        )

        catalog_marker_root = Path(tmp_dir) / "catalog-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("phase3_catalog.py")
                else (target.marker or "PASS")
            )
            write_script(catalog_marker_root / target.relpath, marker)
        issues = run_targets(catalog_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/phase3_catalog.py:"
            "PHASE3_CATALOG_SELF_TEST=pass"
            in issues
        )

        runner_marker_root = Path(tmp_dir) / "runner-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("run-phase3-checks.py")
                else (target.marker or "PASS")
            )
            write_script(runner_marker_root / target.relpath, marker)
        issues = run_targets(runner_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/run-phase3-checks.py:PHASE3_RUNNER_SELF_TEST=pass"
            in issues
        )

        wrapper_marker_root = Path(tmp_dir) / "wrapper-marker"
        for target in SELF_TEST_TARGETS:
            marker = (
                "WRONG_MARKER=pass"
                if target.relpath.endswith("generate-phase3-check-wrappers.py")
                else (target.marker or "PASS")
            )
            write_script(wrapper_marker_root / target.relpath, marker)
        issues = run_targets(wrapper_marker_root)
        assert (
            "missing_pass_marker:scripts/zigux/generate-phase3-check-wrappers.py:"
            "PHASE3_WRAPPER_SELF_TEST=pass"
            in issues
        )

        stderr_root = Path(tmp_dir) / "stderr"
        for target in SELF_TEST_TARGETS:
            if target.relpath.endswith("validate-phase3.py"):
                path = stderr_root / target.relpath
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "\n".join(
                        [
                            "#!/usr/bin/env python3",
                            "from __future__ import annotations",
                            "",
                            "import sys",
                            "",
                            'if "--self-test" in sys.argv:',
                            '    print("PHASE3_VALIDATE_SELF_TEST=pass")',
                            '    print("broken", file=sys.stderr)',
                            "    raise SystemExit(3)",
                            "",
                            'raise SystemExit("expected --self-test")',
                            "",
                        ]
                    ),
                    encoding="utf-8",
                    newline="\n",
                )
            else:
                write_script(stderr_root / target.relpath, target.marker or "PASS")
        issues = run_targets(stderr_root)
        assert "self_test_failed:scripts/zigux/validate-phase3.py:rc=3" in issues
        assert "self_test_stderr:scripts/zigux/validate-phase3.py:broken" in issues

    print("PHASE3_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE3_VALIDATOR_SELF_TEST_CASE_COUNT={PHASE3_VALIDATOR_SELF_TEST_CASE_COUNT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the current Phase 3 validator helper self-tests through one shared runner."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated coverage for the shared Phase 3 validator self-test runner.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = run_targets(ROOT)
    if issues:
        print("PHASE3_VALIDATOR_SELF_TEST=fail")
        print("PHASE3_VALIDATOR_SELF_TEST_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_VALIDATOR_SELF_TEST_ISSUES_END")
        return 1

    print("PHASE3_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE3_VALIDATOR_SELF_TEST_TARGET_COUNT={len(SELF_TEST_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

REQUIRED_PATHS = (
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
    "Documentation/zigux/phase11-uapi-header-parity-survey.md",
    "Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md",
    "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "Documentation/zigux/phase11-dw-wdt-provenance-readback.md",
    "Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md",
    "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-gpio-wdt-survey.md",
    "Documentation/zigux/phase11-gpio-wdt-module-slice.md",
    "Documentation/zigux/phase11-gpio-wdt-teardown-note.md",
    "Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md",
    "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md",
    "Documentation/zigux/phase11-hvc-verify-helper-boundary.md",
    "scripts/zigux/check-phase11-build-inventory.py",
    "scripts/zigux/check-phase11-matrix-gap-survey.py",
    "scripts/zigux/check-phase11-validation-matrix-gap-survey.py",
    "scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
    "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py",
    "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py",
    "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py",
    "drivers/watchdog/dw_wdt.zig",
    "drivers/watchdog/dw_wdt_verify.zig",
    "drivers/watchdog/dw_wdt_pm.zig",
    "drivers/watchdog/dw_wdt_pm_scaffold.zig",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/phase11_dw_wdt_manifest.json",
    "zigux/tests/phase11_dw_wdt.zig",
    "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
)


@dataclass(frozen=True)
class CheckSpec:
    name: str
    command: tuple[str, ...]


CHECKS = (
    CheckSpec(
        "phase11-build-inventory-self-test",
        ("python", "scripts/zigux/check-phase11-build-inventory.py", "--self-test"),
    ),
    CheckSpec(
        "phase11-build-inventory",
        ("python", "scripts/zigux/check-phase11-build-inventory.py"),
    ),
    CheckSpec(
        "phase11-matrix-gap-survey-self-test",
        ("python", "scripts/zigux/check-phase11-matrix-gap-survey.py", "--self-test"),
    ),
    CheckSpec(
        "phase11-matrix-gap-survey",
        ("python", "scripts/zigux/check-phase11-matrix-gap-survey.py"),
    ),
    CheckSpec(
        "phase11-validation-matrix-gap-survey-self-test",
        ("python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py", "--self-test"),
    ),
    CheckSpec(
        "phase11-validation-matrix-gap-survey",
        ("python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py"),
    ),
    CheckSpec(
        "phase11-hvc-cleanup-current-head-self-test",
        ("python", "scripts/zigux/check-phase11-hvc-cleanup-current-head.py", "--self-test"),
    ),
    CheckSpec(
        "phase11-hvc-cleanup-current-head",
        ("python", "scripts/zigux/check-phase11-hvc-cleanup-current-head.py"),
    ),
    CheckSpec(
        "phase11-hvc-targetless-unregister-witness-self-test",
        ("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py", "--self-test"),
    ),
    CheckSpec(
        "phase11-hvc-targetless-unregister-witness",
        ("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"),
    ),
    CheckSpec(
        "phase11-dw-wdt-teardown-packet-self-test",
        ("python", "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py", "--self-test"),
    ),
    CheckSpec(
        "phase11-dw-wdt-teardown-packet",
        ("python", "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py"),
    ),
    CheckSpec(
        "phase11-dw-wdt-verify-alignment-self-test",
        ("python", "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py", "--self-test"),
    ),
    CheckSpec(
        "phase11-dw-wdt-verify-alignment",
        ("python", "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py"),
    ),
    CheckSpec(
        "phase11-hvc-hv-ops-layout-build",
        ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_hv_ops_layout_build.zig"),
    ),
    CheckSpec(
        "phase11-hvc-export-surface-layout-build",
        ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_export_surface_layout_build.zig"),
    ),
    CheckSpec(
        "phase11-hvc-cleanup-packet-build",
        ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_cleanup_packet_build.zig"),
    ),
    CheckSpec(
        "phase11-hvc-targetless-unregister-gap-build",
        ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig"),
    ),
)


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else ROOT.resolve()


def command_for(spec: CheckSpec, root: Path) -> list[str]:
    command = list(spec.command)
    if not command:
        raise ValueError(f"empty command for {spec.name}")
    if command[0] == "python":
        return [sys.executable, str(root / command[1]), *command[2:]]
    if command[0] == "zig":
        return ["zig", *command[1:]]
    raise ValueError(f"unsupported command kind for {spec.name}: {command[0]}")


def is_zig_check(spec: CheckSpec) -> bool:
    return bool(spec.command) and spec.command[0] == "zig"


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def append_output(issues: list[str], prefix: str, completed: subprocess.CompletedProcess[str]) -> None:
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if stdout:
        issues.append(f"{prefix}:stdout={stdout}")
    if stderr:
        issues.append(f"{prefix}:stderr={stderr}")


def collect_issues(root: Path, *, skip_zig_builds: bool = False) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_required_path:{rel}")

    if issues:
        return issues

    for spec in CHECKS:
        if skip_zig_builds and is_zig_check(spec):
            continue
        completed = run_command(command_for(spec, root), root)
        if completed.returncode != 0:
            issues.append(f"live_failed:{spec.name}:exit={completed.returncode}")
            append_output(issues, f"live_failed:{spec.name}", completed)

    return issues


def run_check(root: Path, *, skip_zig_builds: bool = False) -> int:
    issues = collect_issues(root, skip_zig_builds=skip_zig_builds)
    if issues:
        print("PHASE11_VALIDATION=fail")
        print("PHASE11_VALIDATION_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE11_VALIDATION_ISSUES_END")
        return 1

    print("PHASE11_VALIDATION=pass")
    print(f"PHASE11_VALIDATION_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE11_VALIDATION_CHECK_COUNT={len(CHECKS)}")
    return 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_stub_script(
    path: Path,
    *,
    self_test_exit_code: int = 0,
    live_exit_code: int | None = None,
) -> None:
    live_exit_literal = self_test_exit_code if live_exit_code is None else live_exit_code
    write_text(
        path,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import argparse",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--self-test', action='store_true')",
                "parser.add_argument('--root')",
                "parser.add_argument('--repo-root')",
                "args = parser.parse_args()",
                f"SELF_TEST_EXIT_CODE = {self_test_exit_code}",
                f"LIVE_EXIT_CODE = {live_exit_literal}",
                "raise SystemExit(SELF_TEST_EXIT_CODE if args.self_test else LIVE_EXIT_CODE)",
            ]
        )
        + "\n",
    )
    os.chmod(path, 0o755)


def build_fake_zig(path: Path, *, fail_build_file: str | None = None) -> None:
    fail_literal = repr(fail_build_file) if fail_build_file is not None else "None"
    write_text(
        path,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import sys",
                f"FAIL_BUILD_FILE = {fail_literal}",
                "args = sys.argv[1:]",
                "if args[:2] != ['build', 'test']:",
                "    raise SystemExit(2)",
                "try:",
                "    build_file = args[args.index('--build-file') + 1]",
                "except (ValueError, IndexError):",
                "    raise SystemExit(3)",
                "if FAIL_BUILD_FILE is not None and build_file == FAIL_BUILD_FILE:",
                "    print(f'fake zig failed for {build_file}')",
                "    raise SystemExit(1)",
                "raise SystemExit(0)",
            ]
        )
        + "\n",
    )
    os.chmod(path, 0o755)


def build_sample_repo(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        path = root / rel
        if rel.startswith("scripts/zigux/") and rel.endswith(".py"):
            build_stub_script(path)
            continue
        write_text(path, f"sample:{rel}\n")


def run_self_test() -> int:
    original_path = os.environ.get("PATH", "")
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_validate_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_repo(root)
        tool_root = root / ".tools"
        tool_root.mkdir(parents=True, exist_ok=True)
        fake_zig = tool_root / "zig"
        build_fake_zig(fake_zig)
        os.environ["PATH"] = f"{tool_root}{os.pathsep}{original_path}" if original_path else str(tool_root)

        baseline_issues = collect_issues(root)
        if baseline_issues:
            raise SystemExit(
                "phase11-validate-self-test:baseline_failed:" + ",".join(baseline_issues)
            )

        missing = root / "Documentation/zigux/phase11-hvc-verify-helper-boundary.md"
        missing.unlink()
        issues = collect_issues(root)
        expected_missing = "missing_required_path:Documentation/zigux/phase11-hvc-verify-helper-boundary.md"
        if expected_missing not in issues:
            raise SystemExit(
                "phase11-validate-self-test:missing_required_path_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        missing_dw_platform_plan = root / "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md"
        missing_dw_platform_plan.unlink()
        issues = collect_issues(root)
        expected_missing_dw_platform_plan = "missing_required_path:Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md"
        if expected_missing_dw_platform_plan not in issues:
            raise SystemExit(
                "phase11-validate-self-test:missing_dw_platform_plan_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        missing_dw_driver = root / "drivers/watchdog/dw_wdt.zig"
        missing_dw_driver.unlink()
        issues = collect_issues(root)
        expected_missing_dw_driver = "missing_required_path:drivers/watchdog/dw_wdt.zig"
        if expected_missing_dw_driver not in issues:
            raise SystemExit(
                "phase11-validate-self-test:missing_dw_driver_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        missing_dw_test = root / "zigux/tests/phase11_dw_wdt.zig"
        missing_dw_test.unlink()
        issues = collect_issues(root)
        expected_missing_dw_test = "missing_required_path:zigux/tests/phase11_dw_wdt.zig"
        if expected_missing_dw_test not in issues:
            raise SystemExit(
                "phase11-validate-self-test:missing_dw_test_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        missing_dw_pm = root / "drivers/watchdog/dw_wdt_pm.zig"
        missing_dw_pm.unlink()
        issues = collect_issues(root)
        expected_missing_dw_pm = "missing_required_path:drivers/watchdog/dw_wdt_pm.zig"
        if expected_missing_dw_pm not in issues:
            raise SystemExit(
                "phase11-validate-self-test:missing_dw_pm_path_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        missing_dw_pm_scaffold = root / "drivers/watchdog/dw_wdt_pm_scaffold.zig"
        missing_dw_pm_scaffold.unlink()
        issues = collect_issues(root)
        expected_missing_dw_pm_scaffold = "missing_required_path:drivers/watchdog/dw_wdt_pm_scaffold.zig"
        if expected_missing_dw_pm_scaffold not in issues:
            raise SystemExit(
                "phase11-validate-self-test:missing_dw_pm_scaffold_path_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        failing_build_inventory_self_test_script = root / "scripts/zigux/check-phase11-build-inventory.py"
        build_stub_script(failing_build_inventory_self_test_script, self_test_exit_code=1)
        issues = collect_issues(root)
        expected_build_inventory_self_test_failure = "live_failed:phase11-build-inventory-self-test:exit=1"
        if expected_build_inventory_self_test_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:build_inventory_self_test_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        failing_build_inventory_script = root / "scripts/zigux/check-phase11-build-inventory.py"
        build_stub_script(
            failing_build_inventory_script,
            self_test_exit_code=0,
            live_exit_code=1,
        )
        issues = collect_issues(root)
        expected_build_inventory_failure = "live_failed:phase11-build-inventory:exit=1"
        if expected_build_inventory_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:build_inventory_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        failing_matrix_gap_self_test_script = root / "scripts/zigux/check-phase11-matrix-gap-survey.py"
        build_stub_script(failing_matrix_gap_self_test_script, self_test_exit_code=1)
        issues = collect_issues(root)
        expected_matrix_gap_self_test_failure = "live_failed:phase11-matrix-gap-survey-self-test:exit=1"
        if expected_matrix_gap_self_test_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:matrix_gap_self_test_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        failing_matrix_gap_script = root / "scripts/zigux/check-phase11-matrix-gap-survey.py"
        build_stub_script(
            failing_matrix_gap_script,
            self_test_exit_code=0,
            live_exit_code=1,
        )
        issues = collect_issues(root)
        expected_matrix_gap_failure = "live_failed:phase11-matrix-gap-survey:exit=1"
        if expected_matrix_gap_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:matrix_gap_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        failing_validation_matrix_gap_self_test_script = root / "scripts/zigux/check-phase11-validation-matrix-gap-survey.py"
        build_stub_script(failing_validation_matrix_gap_self_test_script, self_test_exit_code=1)
        issues = collect_issues(root)
        expected_validation_matrix_gap_self_test_failure = "live_failed:phase11-validation-matrix-gap-survey-self-test:exit=1"
        if expected_validation_matrix_gap_self_test_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:validation_matrix_gap_self_test_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        failing_script = root / "scripts/zigux/check-phase11-validation-matrix-gap-survey.py"
        build_stub_script(
            failing_script,
            self_test_exit_code=0,
            live_exit_code=1,
        )
        issues = collect_issues(root)
        expected_failure = "live_failed:phase11-validation-matrix-gap-survey:exit=1"
        if expected_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:subcommand_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        failing_hvc_cleanup_self_test_script = root / "scripts/zigux/check-phase11-hvc-cleanup-current-head.py"
        build_stub_script(failing_hvc_cleanup_self_test_script, self_test_exit_code=1)
        issues = collect_issues(root)
        expected_hvc_cleanup_self_test_failure = "live_failed:phase11-hvc-cleanup-current-head-self-test:exit=1"
        if expected_hvc_cleanup_self_test_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:hvc_cleanup_self_test_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        failing_hvc_cleanup_script = root / "scripts/zigux/check-phase11-hvc-cleanup-current-head.py"
        build_stub_script(
            failing_hvc_cleanup_script,
            self_test_exit_code=0,
            live_exit_code=1,
        )
        issues = collect_issues(root)
        expected_hvc_cleanup_failure = "live_failed:phase11-hvc-cleanup-current-head:exit=1"
        if expected_hvc_cleanup_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:hvc_cleanup_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        failing_hvc_targetless_witness_self_test_script = root / "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"
        build_stub_script(failing_hvc_targetless_witness_self_test_script, self_test_exit_code=1)
        issues = collect_issues(root)
        expected_hvc_targetless_witness_self_test_failure = "live_failed:phase11-hvc-targetless-unregister-witness-self-test:exit=1"
        if expected_hvc_targetless_witness_self_test_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:hvc_targetless_witness_self_test_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        failing_hvc_targetless_witness_script = root / "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"
        build_stub_script(
            failing_hvc_targetless_witness_script,
            self_test_exit_code=0,
            live_exit_code=1,
        )
        issues = collect_issues(root)
        expected_hvc_targetless_witness_failure = "live_failed:phase11-hvc-targetless-unregister-witness:exit=1"
        if expected_hvc_targetless_witness_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:hvc_targetless_witness_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        failing_dw_teardown_self_test_script = root / "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py"
        build_stub_script(failing_dw_teardown_self_test_script, self_test_exit_code=1)
        issues = collect_issues(root)
        expected_dw_teardown_self_test_failure = "live_failed:phase11-dw-wdt-teardown-packet-self-test:exit=1"
        if expected_dw_teardown_self_test_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:dw_teardown_self_test_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        failing_dw_teardown_script = root / "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py"
        build_stub_script(
            failing_dw_teardown_script,
            self_test_exit_code=0,
            live_exit_code=1,
        )
        issues = collect_issues(root)
        expected_dw_teardown_failure = "live_failed:phase11-dw-wdt-teardown-packet:exit=1"
        if expected_dw_teardown_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:dw_teardown_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        failing_dw_verify_self_test_script = root / "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py"
        build_stub_script(failing_dw_verify_self_test_script, self_test_exit_code=1)
        issues = collect_issues(root)
        expected_dw_verify_self_test_failure = "live_failed:phase11-dw-wdt-verify-alignment-self-test:exit=1"
        if expected_dw_verify_self_test_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:dw_verify_self_test_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(fake_zig)
        failing_dw_script = root / "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py"
        build_stub_script(
            failing_dw_script,
            self_test_exit_code=0,
            live_exit_code=1,
        )
        issues = collect_issues(root)
        expected_dw_failure = "live_failed:phase11-dw-wdt-verify-alignment:exit=1"
        if expected_dw_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:dw_subcommand_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sampleRepo = build_sample_repo
        build_sampleRepo(root)
        build_fake_zig(
            fake_zig,
            fail_build_file="zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
        )
        issues = collect_issues(root)
        expected_hv_ops_build_failure = "live_failed:phase11-hvc-hv-ops-layout-build:exit=1"
        if expected_hv_ops_build_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:hv_ops_build_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(
            fake_zig,
            fail_build_file="zigux/tests/phase11_hvc_export_surface_layout_build.zig",
        )
        issues = collect_issues(root)
        expected_export_build_failure = "live_failed:phase11-hvc-export-surface-layout-build:exit=1"
        if expected_export_build_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:export_build_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(
            fake_zig,
            fail_build_file="zigux/tests/phase11_hvc_cleanup_packet_build.zig",
        )
        issues = collect_issues(root)
        expected_cleanup_build_failure = "live_failed:phase11-hvc-cleanup-packet-build:exit=1"
        if expected_cleanup_build_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:cleanup_build_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(
            fake_zig,
            fail_build_file="zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
        )
        issues = collect_issues(root)
        expected_targetless_gap_failure = "live_failed:phase11-hvc-targetless-unregister-gap-build:exit=1"
        if expected_targetless_gap_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:targetless_gap_build_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_fake_zig(
            fake_zig,
            fail_build_file="zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
        )
        issues = collect_issues(root, skip_zig_builds=True)
        if issues:
            raise SystemExit(
                "phase11-validate-self-test:skip_zig_builds_not_honored:"
                + ",".join(issues)
            )

    os.environ["PATH"] = original_path
    print("PHASE11_VALIDATE_SELF_TEST=pass")
    print("PHASE11_VALIDATE_SELF_TEST_CASE_COUNT=26")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--skip-zig-builds", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        return run_check(args.root.resolve(), skip_zig_builds=args.skip_zig_builds)
    except Exception as exc:  # pragma: no cover - defensive top-level guard
        print(f"PHASE11_VALIDATION=fail: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

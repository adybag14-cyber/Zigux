#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

REQUIRED_PATHS = (
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase11-shared-replay-contract.md",
    "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
    "Documentation/zigux/phase11-codegen-manifest-tooling-gap-survey.md",
    "Documentation/zigux/phase11-watchdog-lifecycle-parity-gap.md",
    "Documentation/zigux/phase11-uapi-header-parity-survey.md",
    "Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md",
    "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
    "Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md",
    "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md",
    "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "Documentation/zigux/phase11-dw-wdt-provenance-readback.md",
    "Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md",
    "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-dw-wdt-survey.md",
    "Documentation/zigux/phase11-gpio-wdt-survey.md",
    "Documentation/zigux/phase11-gpio-wdt-module-slice.md",
    "Documentation/zigux/phase11-gpio-wdt-teardown-note.md",
    "Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md",
    "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md",
    "Documentation/zigux/phase11-hvc-verify-helper-boundary.md",
    "Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md",
    "scripts/zigux/check-phase11-build-inventory.py",
    "scripts/zigux/check-phase11-validate-manifest-roster.py",
    "scripts/zigux/check-phase11-validate-check-roster.py",
    "scripts/zigux/check-phase11-validate-route-alignment.py",
    "scripts/zigux/check-phase11-shared-tooling-manifest.py",
    "scripts/zigux/check-phase11-focused-direct-build-replays.py",
    "scripts/zigux/check-phase11-shared-replay-contract-counts.py",
    "scripts/zigux/check-phase11-matrix-gap-survey.py",
    "scripts/zigux/check-phase11-validation-matrix-gap-survey.py",
    "scripts/zigux/check-phase11-watchdog-lifecycle-parity-gap.py",
    "scripts/zigux/check-phase11-header-boundary-packet.py",
    "scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
    "scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py",
    "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py",
    "scripts/zigux/check-phase11-hvc-current-head-manifest.py",
    "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py",
    "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py",
    "scripts/zigux/check-phase11-dw-wdt-build-route.py",
    "scripts/zigux/validate-phase11.py",
    "drivers/tty/hvc/hvc_console.h",
    "drivers/tty/hvc/hvc_console.zig",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "drivers/watchdog/bcm2835_wdt.zig",
    "drivers/watchdog/bcm2835_wdt_verify.zig",
    "drivers/watchdog/gpio_wdt.zig",
    "drivers/watchdog/gpio_wdt_verify.zig",
    "drivers/watchdog/dw_wdt_restart.zig",
    "drivers/watchdog/dw_wdt_pm.zig",
    "drivers/watchdog/dw_wdt_pm_scaffold.zig",
    "drivers/watchdog/dw_wdt_verify.zig",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
    "zigux/tests/phase11_bcm2835_wdt_manifest.json",
    "zigux/tests/phase11_dw_wdt_manifest.json",
    "zigux/tests/phase11_dw_wdt_survey.zig",
    "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
    "zigux/tests/phase11_dw_wdt_restart_build.zig",
    "zigux/tests/phase11_bcm2835_wdt.zig",
    "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig",
    "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
    "zigux/tests/phase11_dw_wdt_build.zig",
    "zigux/tests/phase11_dw_wdt_pm_build.zig",
    "zigux/tests/phase11_gpio_wdt_verify_helper_build.zig",
    "zigux/tests/phase11_gpio_wdt_preflight_review.zig",
    "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig",
    "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_modem_control_proof.zig",
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
)

MANIFEST_EXPECTATIONS = {
    "zigux/tests/phase11_bcm2835_wdt_manifest.json": "P11-L08",
    "zigux/tests/phase11_dw_wdt_manifest.json": "P11-L10",
}


@dataclass(frozen=True)
class CheckSpec:
    name: str
    command: tuple[str, ...]


CHECKS = (
    CheckSpec("phase11-validation-self-test", ("python", "scripts/zigux/validate-phase11.py", "--self-test")),
    CheckSpec("phase11-validate-manifest-roster-self-test", ("python", "scripts/zigux/check-phase11-validate-manifest-roster.py", "--self-test")),
    CheckSpec("phase11-validate-manifest-roster", ("python", "scripts/zigux/check-phase11-validate-manifest-roster.py")),
    CheckSpec("phase11-validate-check-roster-self-test", ("python", "scripts/zigux/check-phase11-validate-check-roster.py", "--self-test")),
    CheckSpec("phase11-validate-check-roster", ("python", "scripts/zigux/check-phase11-validate-check-roster.py")),
    CheckSpec("phase11-validate-route-alignment-self-test", ("python", "scripts/zigux/check-phase11-validate-route-alignment.py", "--self-test")),
    CheckSpec("phase11-validate-route-alignment", ("python", "scripts/zigux/check-phase11-validate-route-alignment.py")),
    CheckSpec("phase11-shared-tooling-manifest-self-test", ("python", "scripts/zigux/check-phase11-shared-tooling-manifest.py", "--self-test")),
    CheckSpec("phase11-shared-tooling-manifest", ("python", "scripts/zigux/check-phase11-shared-tooling-manifest.py")),
    CheckSpec("phase11-build-inventory-self-test", ("python", "scripts/zigux/check-phase11-build-inventory.py", "--self-test")),
    CheckSpec("phase11-build-inventory", ("python", "scripts/zigux/check-phase11-build-inventory.py")),
    CheckSpec("phase11-focused-direct-build-replays-self-test", ("python", "scripts/zigux/check-phase11-focused-direct-build-replays.py", "--self-test")),
    CheckSpec("phase11-focused-direct-build-replays", ("python", "scripts/zigux/check-phase11-focused-direct-build-replays.py")),
    CheckSpec("phase11-shared-replay-contract-counts-self-test", ("python", "scripts/zigux/check-phase11-shared-replay-contract-counts.py", "--self-test")),
    CheckSpec("phase11-shared-replay-contract-counts", ("python", "scripts/zigux/check-phase11-shared-replay-contract-counts.py")),
    CheckSpec("phase11-matrix-gap-survey-self-test", ("python", "scripts/zigux/check-phase11-matrix-gap-survey.py", "--self-test")),
    CheckSpec("phase11-matrix-gap-survey", ("python", "scripts/zigux/check-phase11-matrix-gap-survey.py")),
    CheckSpec("phase11-validation-matrix-gap-survey-self-test", ("python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py", "--self-test")),
    CheckSpec("phase11-validation-matrix-gap-survey", ("python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py")),
    CheckSpec("phase11-watchdog-lifecycle-parity-gap-self-test", ("python", "scripts/zigux/check-phase11-watchdog-lifecycle-parity-gap.py", "--self-test")),
    CheckSpec("phase11-watchdog-lifecycle-parity-gap", ("python", "scripts/zigux/check-phase11-watchdog-lifecycle-parity-gap.py")),
    CheckSpec("phase11-header-boundary-packet-self-test", ("python", "scripts/zigux/check-phase11-header-boundary-packet.py", "--self-test")),
    CheckSpec("phase11-header-boundary-packet", ("python", "scripts/zigux/check-phase11-header-boundary-packet.py")),
    CheckSpec("phase11-hvc-cleanup-current-head-self-test", ("python", "scripts/zigux/check-phase11-hvc-cleanup-current-head.py", "--self-test")),
    CheckSpec("phase11-hvc-cleanup-current-head", ("python", "scripts/zigux/check-phase11-hvc-cleanup-current-head.py")),
    CheckSpec("phase11-hvc-cleanup-prerequisite-packet-self-test", ("python", "scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py", "--self-test")),
    CheckSpec("phase11-hvc-cleanup-prerequisite-packet", ("python", "scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py")),
    CheckSpec("phase11-hvc-targetless-unregister-witness-self-test", ("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py", "--self-test")),
    CheckSpec("phase11-hvc-targetless-unregister-witness", ("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py")),
    CheckSpec("phase11-hvc-current-head-manifest-self-test", ("python", "scripts/zigux/check-phase11-hvc-current-head-manifest.py", "--self-test")),
    CheckSpec("phase11-hvc-current-head-manifest", ("python", "scripts/zigux/check-phase11-hvc-current-head-manifest.py")),
    CheckSpec("phase11-dw-wdt-teardown-packet-self-test", ("python", "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py", "--self-test")),
    CheckSpec("phase11-dw-wdt-teardown-packet", ("python", "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py")),
    CheckSpec("phase11-dw-wdt-verify-alignment-self-test", ("python", "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py", "--self-test")),
    CheckSpec("phase11-dw-wdt-verify-alignment", ("python", "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py")),
    CheckSpec("phase11-dw-wdt-build-route-self-test", ("python", "scripts/zigux/check-phase11-dw-wdt-build-route.py", "--self-test")),
    CheckSpec("phase11-dw-wdt-build-route", ("python", "scripts/zigux/check-phase11-dw-wdt-build-route.py")),
    CheckSpec("phase11-bcm2835-wdt-manifest-packet-survey-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig")),
    CheckSpec("phase11-dw-wdt-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_dw_wdt_build.zig")),
    CheckSpec("phase11-dw-wdt-restart-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_dw_wdt_restart_build.zig")),
    CheckSpec("phase11-dw-wdt-pm-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_dw_wdt_pm_build.zig")),
    CheckSpec("phase11-gpio-wdt-verify-helper-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_gpio_wdt_verify_helper_build.zig")),
    CheckSpec("phase11-gpio-wdt-preflight-review-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig")),
    CheckSpec("phase11-gpio-wdt-register-device-glue-review-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig")),
    CheckSpec("phase11-gpio-wdt-nowayout-policy-review-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig")),
    CheckSpec("phase11-gpio-wdt-remove-handoff-review-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig")),
    CheckSpec("phase11-hvc-hv-ops-layout-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_hv_ops_layout_build.zig")),
    CheckSpec("phase11-hvc-export-surface-layout-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_export_surface_layout_build.zig")),
    CheckSpec("phase11-hvc-cleanup-packet-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_cleanup_packet_build.zig")),
    CheckSpec("phase11-hvc-modem-control-proof-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_modem_control_proof_build.zig")),
    CheckSpec("phase11-hvc-targetless-unregister-gap-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig")),
)


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True, cwd=cwd)


def command_for(spec: CheckSpec, root: Path) -> list[str]:
    if spec.command[0] == "python":
        return [sys.executable, str(root / spec.command[1]), *spec.command[2:]]
    if spec.command[0] == "zig":
        return ["zig", *spec.command[1:]]
    raise ValueError(f"unsupported command kind for {spec.name}")


def is_zig_check(spec: CheckSpec) -> bool:
    return spec.command[0] == "zig"


def declared_command(spec: CheckSpec) -> str:
    return shlex.join(spec.command)


def partition_checks(*, skip_zig_builds: bool) -> tuple[list[CheckSpec], list[CheckSpec]]:
    executed: list[CheckSpec] = []
    skipped: list[CheckSpec] = []
    for spec in CHECKS:
        if skip_zig_builds and is_zig_check(spec):
            skipped.append(spec)
        else:
            executed.append(spec)
    return executed, skipped


def emit_success_report(*, skip_zig_builds: bool) -> None:
    executed, skipped = partition_checks(skip_zig_builds=skip_zig_builds)
    print("PHASE11_VALIDATION=pass")
    print(f"PHASE11_VALIDATION_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE11_VALIDATION_CHECK_COUNT={len(CHECKS)}")
    print(f"PHASE11_VALIDATION_EXECUTED_CHECK_COUNT={len(executed)}")
    print(f"PHASE11_VALIDATION_SKIPPED_CHECK_COUNT={len(skipped)}")
    print("PHASE11_VALIDATION_EXACT_CHECKS_START")
    for spec in CHECKS:
        status = "skipped" if spec in skipped else "executed"
        print(f"{status}:{spec.name}:{declared_command(spec)}")
    print("PHASE11_VALIDATION_EXACT_CHECKS_END")


def read_manifest(path: Path) -> dict[str, object] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def collect_manifest_metadata_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for rel, expected_lane_key in MANIFEST_EXPECTATIONS.items():
        manifest = read_manifest(root / rel)
        if manifest is None:
            issues.append(f"invalid_manifest_json:{rel}")
            continue
        lane_key = manifest.get("lane_key")
        if lane_key != expected_lane_key:
            issues.append(f"manifest_lane_key_mismatch:{rel}:expected={expected_lane_key}:actual={lane_key!r}")
        phase = manifest.get("phase")
        if phase != "Phase 11":
            issues.append(f"manifest_phase_mismatch:{rel}:expected='Phase 11':actual={phase!r}")
        gaps = manifest.get("gaps")
        if not isinstance(gaps, list) or not gaps:
            issues.append(f"manifest_gaps_invalid:{rel}")
    return issues


def collect_issues(root: Path, *, skip_zig_builds: bool = False) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_required_path:{rel}")
    if issues:
        return issues

    issues.extend(collect_manifest_metadata_issues(root))
    if issues:
        return issues

    executed, _skipped = partition_checks(skip_zig_builds=skip_zig_builds)
    for spec in executed:
        completed = run_command(command_for(spec, root), root)
        if completed.returncode != 0:
            issues.append(f"live_failed:{spec.name}:exit={completed.returncode}")
            stdout = completed.stdout.strip()
            stderr = completed.stderr.strip()
            if stdout:
                issues.append(f"live_failed:{spec.name}:stdout={stdout}")
            if stderr:
                issues.append(f"live_failed:{spec.name}:stderr={stderr}")
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
    emit_success_report(skip_zig_builds=skip_zig_builds)
    return 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_stub_script(path: Path, *, self_test_exit_code: int = 0, live_exit_code: int | None = None) -> None:
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
        if rel in MANIFEST_EXPECTATIONS:
            write_text(
                path,
                json.dumps(
                    {
                        "lane_key": MANIFEST_EXPECTATIONS[rel],
                        "phase": "Phase 11",
                        "gaps": [{"id": f"sample-{Path(rel).stem}"}],
                    }
                )
                + "\n",
            )
            continue
        if rel.startswith("scripts/zigux/") and rel.endswith(".py"):
            build_stub_script(path)
            continue
        write_text(path, f"sample:{rel}\n")


def capture_success_output(root: Path, *, skip_zig_builds: bool = False) -> list[str]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run_check(root, skip_zig_builds=skip_zig_builds)
    if result != 0:
        raise SystemExit("phase11-validate-self-test:expected_success_output")
    return [line for line in buffer.getvalue().splitlines() if line]


def require_output_line(lines: list[str], expected: str) -> None:
    if expected not in lines:
        actual = ",".join(lines) if lines else "none"
        raise SystemExit(f"phase11-validate-self-test:missing_output:{expected}:actual={actual}")


def require_exact_check_output(lines: list[str], *, status: str, spec: CheckSpec) -> None:
    require_output_line(lines, f"{status}:{spec.name}:{declared_command(spec)}")


def run_self_test() -> int:
    original_path = os.environ.get("PATH", "")
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_validate_") as tmp_dir:
        root = Path(tmp_dir)
        tool_root = root / ".tools"
        tool_root.mkdir(parents=True, exist_ok=True)
        fake_zig = tool_root / "zig"

        def reset_fixture(*, fail_build_file: str | None = None) -> None:
            for child in root.iterdir():
                if child.name == ".tools":
                    continue
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
            build_sample_repo(root)
            build_fake_zig(fake_zig, fail_build_file=fail_build_file)

        os.environ["PATH"] = f"{tool_root}{os.pathsep}{original_path}" if original_path else str(tool_root)

        reset_fixture()
        baseline_issues = collect_issues(root)
        if baseline_issues:
            raise SystemExit("phase11-validate-self-test:baseline_failed:" + ",".join(baseline_issues))
        case_count = 1

        baseline_output = capture_success_output(root)
        zig_check_count = sum(1 for spec in CHECKS if is_zig_check(spec))
        require_output_line(baseline_output, "PHASE11_VALIDATION=pass")
        require_output_line(baseline_output, f"PHASE11_VALIDATION_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
        require_output_line(baseline_output, f"PHASE11_VALIDATION_CHECK_COUNT={len(CHECKS)}")
        require_output_line(baseline_output, f"PHASE11_VALIDATION_EXECUTED_CHECK_COUNT={len(CHECKS)}")
        require_output_line(baseline_output, "PHASE11_VALIDATION_SKIPPED_CHECK_COUNT=0")
        require_output_line(baseline_output, "PHASE11_VALIDATION_EXACT_CHECKS_START")
        require_output_line(baseline_output, "PHASE11_VALIDATION_EXACT_CHECKS_END")
        require_exact_check_output(baseline_output, status="executed", spec=CHECKS[0])
        require_exact_check_output(baseline_output, status="executed", spec=CHECKS[-1])
        case_count += 1

        skip_output = capture_success_output(root, skip_zig_builds=True)
        require_output_line(skip_output, "PHASE11_VALIDATION=pass")
        require_output_line(skip_output, f"PHASE11_VALIDATION_EXECUTED_CHECK_COUNT={len(CHECKS) - zig_check_count}")
        require_output_line(skip_output, f"PHASE11_VALIDATION_SKIPPED_CHECK_COUNT={zig_check_count}")
        require_exact_check_output(skip_output, status="executed", spec=CHECKS[0])
        require_exact_check_output(skip_output, status="skipped", spec=CHECKS[-1])
        case_count += 1

        def expect_issue(fragment: str) -> None:
            issues = collect_issues(root)
            if fragment not in issues:
                raise SystemExit(
                    "phase11-validate-self-test:missing_expected_issue:"
                    + fragment
                    + ":"
                    + ",".join(issues or ["none"])
                )

        reset_fixture()
        (root / "scripts/zigux/check-phase11-dw-wdt-build-route.py").unlink()
        expect_issue("missing_required_path:scripts/zigux/check-phase11-dw-wdt-build-route.py")
        case_count += 1

        reset_fixture()
        (root / "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json").unlink()
        expect_issue("missing_required_path:zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json")
        case_count += 1

        reset_fixture()
        manifest_path = root / "zigux/tests/phase11_dw_wdt_manifest.json"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["lane_key"] = "P11-L99"
        write_text(manifest_path, json.dumps(payload) + "\n")
        expect_issue("manifest_lane_key_mismatch:zigux/tests/phase11_dw_wdt_manifest.json:expected=P11-L10:actual='P11-L99'")
        case_count += 1

        reset_fixture()
        build_stub_script(root / "scripts/zigux/check-phase11-dw-wdt-build-route.py", self_test_exit_code=1, live_exit_code=0)
        expect_issue("live_failed:phase11-dw-wdt-build-route-self-test:exit=1")
        case_count += 1

        reset_fixture()
        build_stub_script(root / "scripts/zigux/check-phase11-dw-wdt-build-route.py", self_test_exit_code=0, live_exit_code=1)
        expect_issue("live_failed:phase11-dw-wdt-build-route:exit=1")
        case_count += 1

        reset_fixture(fail_build_file="zigux/tests/phase11_dw_wdt_build.zig")
        expect_issue("live_failed:phase11-dw-wdt-build:exit=1")
        case_count += 1

        reset_fixture(fail_build_file="zigux/tests/phase11_dw_wdt_build.zig")
        if collect_issues(root, skip_zig_builds=True):
            raise SystemExit("phase11-validate-self-test:skip_zig_builds_not_honored")
        skip_output = capture_success_output(root, skip_zig_builds=True)
        require_exact_check_output(skip_output, status="skipped", spec=CHECKS[-1])
        case_count += 1

        os.environ["PATH"] = original_path
        print("PHASE11_VALIDATE_SELF_TEST=pass")
        print(f"PHASE11_VALIDATE_SELF_TEST_CASE_COUNT={case_count}")
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
    except Exception as exc:
        print(f"PHASE11_VALIDATION=fail: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

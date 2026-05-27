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
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
    "Documentation/zigux/phase10-virtio-core-slice.md",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "drivers/virtio/virtio.zig",
    "drivers/virtio/virtio_driver_id.zig",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "drivers/virtio/virtio_mmio.zig",
    "drivers/virtio/virtio_mmio_apply_observation.zig",
    "drivers/virtio/virtio_mmio_config_write_plan_freshness.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_ring_notification_data.zig",
    "drivers/virtio/virtio_ring_publish_readiness.zig",
    "drivers/virtio/virtio_ring_registration_summary.zig",
    "drivers/virtio/virtio_ring_reset_readiness.zig",
    "drivers/virtio/virtio_ring_verify.zig",
    "drivers/virtio/virtio_verify.zig",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase10-bootstrap-route.py",
    "scripts/zigux/check-phase10-core-packet.py",
    "scripts/zigux/check-phase10-shared-freeze-boundary.py",
    "scripts/zigux/check-phase10-ring-packet.py",
    "scripts/zigux/check-phase10-input-packet.py",
    "scripts/zigux/check-phase10-mmio-packet.py",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "scripts/zigux/check-phase10-closure-manifest-counts.py",
    "scripts/zigux/validate-phase10-closure.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "zigux/tests/phase10_virtio_driver_id.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig",
    "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig",
    "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
    "zigux/tests/phase10_virtio_ring_queue_build.zig",
    "zigux/tests/phase10_virtio_ring_queue_build_survey.zig",
    "zigux/tests/phase10_virtio_ring_registration_replay.zig",
    "zigux/tests/phase10_virtio_ring_reset_readiness.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_survey.zig",
)


@dataclass(frozen=True)
class CheckSpec:
    name: str
    script_rel: str
    live_args: tuple[str, ...] = ()


CHECKS = (
    CheckSpec("phase10-bootstrap-route", "scripts/zigux/check-phase10-bootstrap-route.py"),
    CheckSpec("phase10-core-packet", "scripts/zigux/check-phase10-core-packet.py"),
    CheckSpec("phase10-shared-freeze-boundary", "scripts/zigux/check-phase10-shared-freeze-boundary.py"),
    CheckSpec("phase10-ring-packet", "scripts/zigux/check-phase10-ring-packet.py"),
    CheckSpec("phase10-input-packet", "scripts/zigux/check-phase10-input-packet.py"),
    CheckSpec("phase10-mmio-packet", "scripts/zigux/check-phase10-mmio-packet.py"),
    CheckSpec("phase10-harness-coverage", "scripts/zigux/check-phase10-harness-coverage.py"),
    CheckSpec(
        "phase10-tests-readme-core-surfaces",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    ),
    CheckSpec(
        "phase10-closure-manifest-counts",
        "scripts/zigux/check-phase10-closure-manifest-counts.py",
    ),
    CheckSpec("phase10-closure", "scripts/zigux/validate-phase10-closure.py"),
)


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else ROOT.resolve()


def command_for(spec: CheckSpec, root: Path) -> list[str]:
    args = [arg.format(root=str(root)) for arg in spec.live_args]
    return [sys.executable, str(root / spec.script_rel), *args]


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


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_required_path:{rel}")

    if issues:
        return issues

    for spec in CHECKS:
        completed = run_command(command_for(spec, root), root)
        if completed.returncode != 0:
            issues.append(f"live_failed:{spec.name}:exit={completed.returncode}")
            append_output(issues, f"live_failed:{spec.name}", completed)

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE10_VALIDATION=fail")
        print("PHASE10_VALIDATION_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE10_VALIDATION_ISSUES_END")
        return 1

    print("PHASE10_VALIDATION=pass")
    print(f"PHASE10_VALIDATION_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE10_VALIDATION_CHECK_COUNT={len(CHECKS)}")
    print("PHASE10_VALIDATION_CORE_PACKET=pass")
    return 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_stub_script(path: Path, *, exit_code: int = 0) -> None:
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
                "parser.parse_args()",
                f"raise SystemExit({exit_code})",
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
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_validate_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_repo(root)

        baseline_issues = collect_issues(root)
        if baseline_issues:
            raise SystemExit(
                "phase10-validate-self-test:baseline_failed:" + ",".join(baseline_issues)
            )

        def assert_missing_required_path(path_rel: str, failure_label: str) -> None:
            build_sample_repo(root)
            (root / path_rel).unlink()
            issues = collect_issues(root)
            expected_missing = f"missing_required_path:{path_rel}"
            if expected_missing not in issues:
                raise SystemExit(
                    f"phase10-validate-self-test:{failure_label}_not_detected:"
                    + ",".join(issues or ["none"])
                )

        assert_missing_required_path(
            REQUIRED_PATHS[0],
            "missing_required_path",
        )
        assert_missing_required_path(
            "drivers/virtio/virtio_ring_notification_data.zig",
            "missing_ring_notification_data_path",
        )
        assert_missing_required_path(
            "drivers/virtio/virtio_ring_publish_readiness.zig",
            "missing_ring_publish_readiness_path",
        )
        assert_missing_required_path(
            "drivers/virtio/virtio_ring_registration_summary.zig",
            "missing_ring_registration_summary_path",
        )
        assert_missing_required_path(
            "drivers/virtio/virtio_ring_reset_readiness.zig",
            "missing_ring_reset_readiness_path",
        )
        assert_missing_required_path(
            "drivers/virtio/virtio_mmio_apply_observation.zig",
            "missing_mmio_apply_observation_path",
        )
        assert_missing_required_path(
            "drivers/virtio/virtio_mmio_config_write_plan_freshness.zig",
            "missing_mmio_config_write_plan_freshness_path",
        )
        assert_missing_required_path(
            "zigux/tests/phase10_virtio_mmio_survey.zig",
            "missing_mmio_survey_path",
        )
        assert_missing_required_path(
            "drivers/virtio/virtio_input_probe_preflight.zig",
            "missing_input_probe_preflight_path",
        )
        assert_missing_required_path(
            "drivers/virtio/virtio_input_teardown_preflight.zig",
            "missing_input_teardown_preflight_path",
        )
        assert_missing_required_path(
            "drivers/virtio/virtio_input_teardown_observation.zig",
            "missing_input_teardown_observation_path",
        )
        assert_missing_required_path(
            "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
            "missing_input_queue_callback_preflight_test_path",
        )
        assert_missing_required_path(
            "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
            "missing_input_teardown_preflight_test_path",
        )
        assert_missing_required_path(
            "zigux/tests/phase10_virtio_input_survey.zig",
            "missing_input_survey_path",
        )
        assert_missing_required_path(
            "zigux/tests/phase10_virtio_ring_queue_build.zig",
            "missing_ring_queue_build_path",
        )
        assert_missing_required_path(
            "zigux/tests/phase10_virtio_ring_queue_build_survey.zig",
            "missing_ring_queue_build_survey_path",
        )
        assert_missing_required_path(
            "zigux/tests/phase10_virtio_ring_registration_replay.zig",
            "missing_ring_registration_replay_path",
        )
        assert_missing_required_path(
            "zigux/tests/phase10_virtio_ring_reset_readiness.zig",
            "missing_ring_reset_readiness_test_path",
        )
        assert_missing_required_path(
            "scripts/zigux/check-phase10-closure-manifest-counts.py",
            "missing_closure_manifest_counts_checker_path",
        )
        assert_missing_required_path(
            "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
            "missing_lane_sequencing_path",
        )

        def assert_subcommand_failure(
            script_rel: str,
            check_name: str,
            failure_label: str,
        ) -> None:
            build_sample_repo(root)
            failing_script = root / script_rel
            build_stub_script(failing_script, exit_code=1)
            issues = collect_issues(root)
            expected_failure = f"live_failed:{check_name}:exit=1"
            if expected_failure not in issues:
                raise SystemExit(
                    f"phase10-validate-self-test:{failure_label}_not_detected:"
                    + ",".join(issues or ["none"])
                )

        assert_subcommand_failure(
            "scripts/zigux/check-phase10-bootstrap-route.py",
            "phase10-bootstrap-route",
            "bootstrap_route_subcommand_failure",
        )
        assert_subcommand_failure(
            "scripts/zigux/check-phase10-core-packet.py",
            "phase10-core-packet",
            "core_subcommand_failure",
        )
        assert_subcommand_failure(
            "scripts/zigux/check-phase10-shared-freeze-boundary.py",
            "phase10-shared-freeze-boundary",
            "shared_freeze_boundary_subcommand_failure",
        )
        assert_subcommand_failure(
            "scripts/zigux/check-phase10-ring-packet.py",
            "phase10-ring-packet",
            "ring_subcommand_failure",
        )
        assert_subcommand_failure(
            "scripts/zigux/check-phase10-input-packet.py",
            "phase10-input-packet",
            "input_subcommand_failure",
        )
        assert_subcommand_failure(
            "scripts/zigux/check-phase10-mmio-packet.py",
            "phase10-mmio-packet",
            "mmio_subcommand_failure",
        )
        assert_subcommand_failure(
            "scripts/zigux/check-phase10-harness-coverage.py",
            "phase10-harness-coverage",
            "harness_coverage_subcommand_failure",
        )
        assert_subcommand_failure(
            "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
            "phase10-tests-readme-core-surfaces",
            "tests_readme_core_surfaces_subcommand_failure",
        )
        assert_subcommand_failure(
            "scripts/zigux/check-phase10-closure-manifest-counts.py",
            "phase10-closure-manifest-counts",
            "closure_manifest_counts_subcommand_failure",
        )
        assert_subcommand_failure(
            "scripts/zigux/validate-phase10-closure.py",
            "phase10-closure",
            "closure_subcommand_failure",
        )

    print("PHASE10_VALIDATE_SELF_TEST=pass")
    print("PHASE10_VALIDATE_SELF_TEST_CASE_COUNT=31")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_check(repo_root(args.root))


if __name__ == "__main__":
    sys.exit(main())

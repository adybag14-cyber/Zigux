#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

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
    "drivers/virtio/virtio_verify.zig",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase10-bootstrap-route.py",
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
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux/tests/phase10_virtio_ring_manifest.json",
)

CORE_TRUE_SUMMARY_KEYS = (
    "preexisting_phase10_build_present",
    "preexisting_virtio_core_zig_present",
    "preexisting_virtio_core_test_present",
    "preexisting_virtio_core_reset_queue_test_present",
    "preexisting_virtio_core_slice_note_present",
)

CORE_FALSE_SUMMARY_KEYS = (
    "preexisting_virtio_driver_id_zig_present",
    "preexisting_virtio_driver_id_test_present",
)

CORE_EXPECTED_GAPS = {
    "phase10-build-gate": "starter_landed",
    "phase10-driver-id-helper": "starter_landed",
    "phase10-driver-id-coverage-disposition-helper": "starter_landed",
    "phase10-virtio-core-reset-queue-gate": "starter_landed",
    "phase10-virtio-core-slice-note": "starter_landed",
    "phase10-virtio-core-survey-gate": "starter_landed",
    "phase10-virtio-core-survey-note": "starter_landed",
    "phase10-virtio-core-verify-replay": "starter_landed",
    "phase10-core-lab-validation-evidence": "starter_landed",
    "phase10-interrupt-compound-ack-gate": "starter_landed",
    "phase10-core-dual-implementation-bridge": "blocked_on_risky_transport",
    "phase10-core-probe-remove-lifecycle": "blocked_on_risky_transport",
}

CORE_SURVEY_REQUIRED_MARKERS = (
    "lane: `P10-L01`",
    "phase10-core-lab-validation-evidence",
    "phase10-core-probe-remove-lifecycle",
    "scripts/zigux/validate-phase10.py",
)

CORE_SURVEY_DRIVER_ID_MARKERS = (
    "phase10-driver-id-helper",
    "phase10-driver-id-coverage-disposition-helper",
    "`drivers/virtio/virtio_driver_id.zig`",
    "`zigux/tests/phase10_virtio_driver_id.zig`",
)

CORE_SURVEY_STALE_GUARDRAIL_MARKERS = (
    "stale guardrail reference drift",
    "`scripts/zigux/check-phase10-core-packet.py`",
    "does not materialize on `master`",
)

CORE_SLICE_REQUIRED_MARKERS = (
    "phase10_virtio_core_manifest.json",
    "phase10_virtio_core_survey.zig",
    "scripts/zigux/validate-phase10.py",
    "zigux/tests/phase10_build.zig",
)

CORE_SLICE_DRIVER_ID_BOUNDARY_MARKERS = (
    "It does not claim:",
    "landed `virtio_driver_id` helper or replay coverage on current `master`",
    "those exact paths stay unreadable as shipped evidence in this runtime",
)


@dataclass(frozen=True)
class CheckSpec:
    name: str
    script_rel: str
    live_args: tuple[str, ...] = ()


CHECKS = (
    CheckSpec("phase10-bootstrap-route", "scripts/zigux/check-phase10-bootstrap-route.py"),
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


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def collect_core_packet_issues(root: Path) -> list[str]:
    issues: list[str] = []
    try:
        manifest = json.loads(read_text(root, "zigux/tests/phase10_virtio_core_manifest.json"))
    except json.JSONDecodeError as exc:
        return [f"phase10_core_packet:manifest_json:{exc.msg}"]

    if manifest.get("lane_key") != "P10-L01":
        issues.append("phase10_core_packet:manifest_lane_key")
    if manifest.get("phase") != "Phase 10":
        issues.append("phase10_core_packet:manifest_phase")
    if manifest.get("anchor") != "drivers/virtio/virtio.c":
        issues.append("phase10_core_packet:manifest_anchor")

    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or COMMIT_RE.fullmatch(surveyed_commit) is None:
        issues.append("phase10_core_packet:surveyed_commit_format")

    if manifest.get("roadmap_destinations") != ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"]:
        issues.append("phase10_core_packet:roadmap_destinations")

    summary = manifest.get("survey_summary", {})
    for key in CORE_TRUE_SUMMARY_KEYS:
        if summary.get(key) is not True:
            issues.append(f"phase10_core_packet:summary:{key}")
    for key in CORE_FALSE_SUMMARY_KEYS:
        if summary.get(key) is not False:
            issues.append(f"phase10_core_packet:summary:{key}")

    gap_index = {
        gap.get("id"): gap
        for gap in manifest.get("gaps", [])
        if isinstance(gap, dict) and isinstance(gap.get("id"), str)
    }
    for gap_id, expected_status in CORE_EXPECTED_GAPS.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            issues.append(f"phase10_core_packet:gap_missing:{gap_id}")
            continue
        if gap.get("status") != expected_status:
            issues.append(f"phase10_core_packet:gap_status:{gap_id}={gap.get('status')}")

    survey_note = read_text(root, "Documentation/zigux/phase10-virtio-core-survey.md")
    for marker in CORE_SURVEY_REQUIRED_MARKERS:
        if marker not in survey_note:
            issues.append(f"phase10_core_packet:survey_note:{marker}")
    if isinstance(surveyed_commit, str) and COMMIT_RE.fullmatch(surveyed_commit) is not None and surveyed_commit not in survey_note:
        issues.append("phase10_core_packet:survey_note:surveyed_commit_alignment")
    if not all(marker in survey_note for marker in CORE_SURVEY_DRIVER_ID_MARKERS):
        issues.append("phase10_core_packet:survey_note:driver_id_visibility_gap")
    if not all(marker in survey_note for marker in CORE_SURVEY_STALE_GUARDRAIL_MARKERS):
        issues.append("phase10_core_packet:survey_note:stale_guardrail_drift")

    slice_note = read_text(root, "Documentation/zigux/phase10-virtio-core-slice.md")
    for marker in CORE_SLICE_REQUIRED_MARKERS:
        if marker not in slice_note:
            issues.append(f"phase10_core_packet:slice_note:{marker}")
    if not all(marker in slice_note for marker in CORE_SLICE_DRIVER_ID_BOUNDARY_MARKERS):
        issues.append("phase10_core_packet:slice_note:driver_id_boundary")

    build_text = read_text(root, "zigux/tests/phase10_build.zig")
    for marker in (
        "phase10-virtio-core-tests",
        "phase10-virtio-core-interrupt-compound-ack-tests",
        "phase10-virtio-core-reset-queue-tests",
        "phase10-virtio-core-verify-tests",
        "phase10-virtio-core-survey-tests",
        "phase10-virtio-driver-id-tests",
        "run_phase10_virtio_core_tests",
        "run_phase10_virtio_core_interrupt_compound_ack_tests",
        "run_phase10_virtio_core_reset_queue_tests",
        "run_phase10_virtio_core_verify_tests",
        "run_phase10_virtio_core_survey_tests",
        "run_phase10_virtio_driver_id_tests",
    ):
        if marker not in build_text:
            issues.append(f"phase10_core_packet:build:{marker}")

    makefile_text = read_text(root, "zigux/Makefile")
    for marker in ("phase10-validate:", "phase10-test:", "phase10:"):
        if marker not in makefile_text:
            issues.append(f"phase10_core_packet:makefile:{marker}")

    return issues


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_required_path:{rel}")

    if issues:
        return issues

    issues.extend(collect_core_packet_issues(root))

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
    sample_manifest = {
        "lane_key": "P10-L01",
        "phase": "Phase 10",
        "surveyed_commit": "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
        "anchor": "drivers/virtio/virtio.c",
        "roadmap_destinations": ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"],
        "survey_summary": {
            "preexisting_phase10_build_present": True,
            "preexisting_virtio_core_zig_present": True,
            "preexisting_virtio_core_test_present": True,
            "preexisting_virtio_core_reset_queue_test_present": True,
            "preexisting_virtio_driver_id_zig_present": False,
            "preexisting_virtio_driver_id_test_present": False,
            "preexisting_virtio_core_slice_note_present": True,
        },
        "gaps": [
            {"id": "phase10-build-gate", "status": "starter_landed"},
            {"id": "phase10-driver-id-helper", "status": "starter_landed"},
            {"id": "phase10-driver-id-coverage-disposition-helper", "status": "starter_landed"},
            {"id": "phase10-virtio-core-reset-queue-gate", "status": "starter_landed"},
            {"id": "phase10-virtio-core-slice-note", "status": "starter_landed"},
            {"id": "phase10-virtio-core-survey-gate", "status": "starter_landed"},
            {"id": "phase10-virtio-core-survey-note", "status": "starter_landed"},
            {"id": "phase10-virtio-core-verify-replay", "status": "starter_landed"},
            {"id": "phase10-core-lab-validation-evidence", "status": "starter_landed"},
            {"id": "phase10-interrupt-compound-ack-gate", "status": "starter_landed"},
            {"id": "phase10-core-dual-implementation-bridge", "status": "blocked_on_risky_transport"},
            {"id": "phase10-core-probe-remove-lifecycle", "status": "blocked_on_risky_transport"},
        ],
    }

    sample_text = {
        "Documentation/zigux/phase10-virtio-core-survey.md": (
            "# Phase 10 Virtio Core Survey\n"
            "- lane: `P10-L01`\n"
            "- surveyed packet commit recorded by the live core manifest: c11221dc7a68d7511ae1c69d64b3f08528287ed8\n"
            "- scripts/zigux/validate-phase10.py\n"
            "- phase10-driver-id-helper\n"
            "- phase10-driver-id-coverage-disposition-helper\n"
            "- phase10-core-lab-validation-evidence\n"
            "- phase10-core-probe-remove-lifecycle\n"
            "- stale guardrail reference drift: `scripts/zigux/check-phase10-core-packet.py` does not materialize on `master`\n"
            "- `drivers/virtio/virtio_driver_id.zig`\n"
            "- `zigux/tests/phase10_virtio_driver_id.zig`\n"
        ),
        "Documentation/zigux/phase10-virtio-core-slice.md": (
            "# Phase 10 Virtio Core Slice\n"
            "- phase10_virtio_core_manifest.json\n"
            "- phase10_virtio_core_survey.zig\n"
            "- scripts/zigux/validate-phase10.py\n"
            "- zigux/tests/phase10_build.zig\n"
            "- It does not claim: landed `virtio_driver_id` helper or replay coverage on current `master` while those exact paths stay unreadable as shipped evidence in this runtime\n"
        ),
        "drivers/virtio/virtio.zig": "pub const anchor_path = \"drivers/virtio/virtio.c\";\n",
        "zigux/Makefile": "phase10-validate:\n\t@true\n\nphase10-test:\n\t@true\n\nphase10:\n\t@true\n",
        "zigux/tests/phase10_build.zig": (
            "const run_phase10_virtio_core_tests = 1;\n"
            "const run_phase10_virtio_core_interrupt_compound_ack_tests = 1;\n"
            "const run_phase10_virtio_core_reset_queue_tests = 1;\n"
            "const run_phase10_virtio_core_verify_tests = 1;\n"
            "const run_phase10_virtio_core_survey_tests = 1;\n"
            "const run_phase10_virtio_driver_id_tests = 1;\n"
            "const names = .{\"phase10-virtio-core-tests\", \"phase10-virtio-core-interrupt-compound-ack-tests\", \"phase10-virtio-core-reset-queue-tests\", \"phase10-virtio-core-verify-tests\", \"phase10-virtio-core-survey-tests\", \"phase10-virtio-driver-id-tests\"};\n"
        ),
        "zigux/tests/phase10_virtio_core.zig": "test \"sample\" {}\n",
        "zigux/tests/phase10_virtio_core_survey.zig": "test \"sample survey\" {}\n",
    }

    for rel in REQUIRED_PATHS:
        path = root / rel
        if rel.startswith("scripts/zigux/") and rel.endswith(".py"):
            build_stub_script(path)
            continue
        if rel == "zigux/tests/phase10_virtio_core_manifest.json":
            write_text(path, json.dumps(sample_manifest, indent=2) + "\n")
            continue
        if rel in sample_text:
            write_text(path, sample_text[rel])
            continue
        write_text(path, f"sample:{rel}\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_validate_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_repo(root)

        baseline_issues = collect_issues(root)
        if baseline_issues:
            raise SystemExit(
                "phase10-validate-self-test:baseline_failed:"
                + ",".join(baseline_issues)
            )

        missing = root / REQUIRED_PATHS[0]
        missing.unlink()
        issues = collect_issues(root)
        expected_missing = f"missing_required_path:{REQUIRED_PATHS[0]}"
        if expected_missing not in issues:
            raise SystemExit(
                "phase10-validate-self-test:missing_required_path_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        failing_script = root / "scripts/zigux/check-phase10-harness-coverage.py"
        build_stub_script(failing_script, exit_code=1)
        issues = collect_issues(root)
        expected_failure = "live_failed:phase10-harness-coverage:exit=1"
        if expected_failure not in issues:
            raise SystemExit(
                "phase10-validate-self-test:subcommand_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        failing_script = root / "scripts/zigux/check-phase10-input-packet.py"
        build_stub_script(failing_script, exit_code=1)
        issues = collect_issues(root)
        expected_input_failure = "live_failed:phase10-input-packet:exit=1"
        if expected_input_failure not in issues:
            raise SystemExit(
                "phase10-validate-self-test:input_subcommand_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        failing_script = root / "scripts/zigux/validate-phase10-closure.py"
        build_stub_script(failing_script, exit_code=1)
        issues = collect_issues(root)
        expected_closure_failure = "live_failed:phase10-closure:exit=1"
        if expected_closure_failure not in issues:
            raise SystemExit(
                "phase10-validate-self-test:closure_subcommand_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        manifest_path = root / "zigux/tests/phase10_virtio_core_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["surveyed_commit"] = "master"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        if "phase10_core_packet:surveyed_commit_format" not in issues:
            raise SystemExit(
                "phase10-validate-self-test:surveyed_commit_format_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        manifest_path = root / "zigux/tests/phase10_virtio_core_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_summary"]["preexisting_virtio_driver_id_zig_present"] = True
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        if "phase10_core_packet:summary:preexisting_virtio_driver_id_zig_present" not in issues:
            raise SystemExit(
                "phase10-validate-self-test:driver_id_summary_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        survey_path = root / "Documentation/zigux/phase10-virtio-core-survey.md"
        survey_text = survey_path.read_text(encoding="utf-8").replace(
            "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            1,
        )
        survey_path.write_text(survey_text, encoding="utf-8")
        issues = collect_issues(root)
        if "phase10_core_packet:survey_note:surveyed_commit_alignment" not in issues:
            raise SystemExit(
                "phase10-validate-self-test:surveyed_commit_alignment_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        build_path = root / "zigux/tests/phase10_build.zig"
        build_path.write_text("const only_core = 1;\n", encoding="utf-8")
        issues = collect_issues(root)
        if "phase10_core_packet:build:phase10-virtio-core-reset-queue-tests" not in issues:
            raise SystemExit(
                "phase10-validate-self-test:core_build_marker_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        manifest_path = root / "zigux/tests/phase10_virtio_core_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["gaps"] = [
            gap for gap in manifest["gaps"]
            if gap["id"] != "phase10-virtio-core-verify-replay"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        if "phase10_core_packet:gap_missing:phase10-virtio-core-verify-replay" not in issues:
            raise SystemExit(
                "phase10-validate-self-test:core_gap_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        survey_path = root / "Documentation/zigux/phase10-virtio-core-survey.md"
        survey_text = survey_path.read_text(encoding="utf-8").replace(
            "phase10-driver-id-coverage-disposition-helper",
            "phase10-driver-id-coverage-removed",
            1,
        )
        survey_path.write_text(survey_text, encoding="utf-8")
        issues = collect_issues(root)
        if "phase10_core_packet:survey_note:driver_id_visibility_gap" not in issues:
            raise SystemExit(
                "phase10-validate-self-test:driver_id_visibility_gap_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sampleRepo(root)
        slice_path = root / "Documentation/zigux/phase10-virtio-core-slice.md"
        slice_text = slice_path.read_text(encoding="utf-8").replace(
            "landed `virtio_driver_id` helper or replay coverage on current `master` while those exact paths stay unreadable as shipped evidence in this runtime",
            "landed driver-id coverage",
            1,
        )
        slice_path.write_text(slice_text, encoding="utf-8")
        issues = collect_issues(root)
        if "phase10_core_packet:slice_note:driver_id_boundary" not in issues:
            raise SystemExit(
                "phase10-validate-self-test:driver_id_boundary_not_detected:"
                + ",".join(issues or ["none"])
            )

    print("PHASE10_VALIDATE_SELF_TEST=pass")
    print("PHASE10_VALIDATE_SELF_TEST_CASE_COUNT=12")
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

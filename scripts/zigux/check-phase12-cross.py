#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase12_cross_targets.json"
BUILD_FILE = ROOT / "zigux" / "tests" / "phase12_cross_build.zig"
NOTE = ROOT / "Documentation" / "zigux" / "phase12-cross-compile-smoke.md"
EXPECTED_PHASE = "Phase 12"
EXPECTED_LANE_KEY = "P12-L02"
EXPECTED_BUILD_STEP = "cross"
EXPECTED_BUILD_MARKERS = [
    ("virtio_net_syntax_lab_module", 'b.path("phase12_virtio_net_syntax_lab.zig")'),
    ("virtio_scsi_recovery_state_module", 'b.path("phase12_virtio_scsi_recovery_state.zig")'),
    ("virtio_scsi_syntax_lab_module", 'b.path("phase12_virtio_scsi_syntax_lab.zig")'),
    ("raw_github_coverage_module", 'b.path("phase12_raw_github_coverage_survey.zig")'),
    ("virtio_net_syntax_lab_import", 'phase12_virtio_net_syntax_lab_module.addImport("virtio_net", virtio_net_module);'),
    ("virtio_scsi_recovery_state_import", 'phase12_virtio_scsi_recovery_state_module.addImport("virtio_scsi", virtio_scsi_module);'),
    ("virtio_scsi_syntax_lab_import", 'phase12_virtio_scsi_syntax_lab_module.addImport("virtio_scsi", virtio_scsi_module);'),
    ("virtio_net_syntax_lab_test", '.name = "phase12-cross-virtio-net-syntax-lab-tests"'),
    ("virtio_scsi_recovery_state_test", '.name = "phase12-cross-virtio-scsi-recovery-state-tests"'),
    ("virtio_scsi_syntax_lab_test", '.name = "phase12-cross-virtio-scsi-syntax-lab-tests"'),
    ("raw_github_coverage_test", '.name = "phase12-cross-raw-github-coverage-survey-tests"'),
    ("virtio_net_syntax_lab_step", "cross_step.dependOn(&phase12_virtio_net_syntax_lab_tests.step);"),
    ("virtio_scsi_recovery_state_step", "cross_step.dependOn(&phase12_virtio_scsi_recovery_state_tests.step);"),
    ("virtio_scsi_syntax_lab_step", "cross_step.dependOn(&phase12_virtio_scsi_syntax_lab_tests.step);"),
    ("raw_github_coverage_step", "cross_step.dependOn(&phase12_raw_github_coverage_survey_tests.step);"),
]


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    env = shutil.which("zig")
    if env:
        return env
    raise SystemExit("zig not found; pass --zig or add zig to PATH")


def load_json_object(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("phase12-cross:fixture_expected_object")
    return data


def validate_build_text(build_text: str) -> None:
    for label, marker in EXPECTED_BUILD_MARKERS:
        if marker not in build_text:
            raise SystemExit(f"phase12-cross:build_marker:{label}")


def validate_note_text(note_text: str, allowed_targets: list[str]) -> None:
    expected_targets = ", ".join(f"`{target}`" for target in allowed_targets)
    expected_markers = [
        ("title", "# Phase 12 Cross Compile Smoke"),
        ("compile_entrypoint", "- compile entrypoint: `python3 scripts/zigux/check-phase12-cross.py --zig <zig-path>`"),
        ("build_file", "- build file: `zigux/tests/phase12_cross_build.zig`"),
        ("approved_targets", f"- approved targets: {expected_targets}"),
        (
            "landed_gates",
            "- current packet now includes the landed `phase12_virtio_scsi_recovery_state.zig`, `phase12_virtio_net_syntax_lab.zig`, `phase12_virtio_scsi_syntax_lab.zig`, and `phase12_raw_github_coverage_survey.zig` gates in addition to the existing driver and libbpf survey modules",
        ),
        (
            "rollback_posture",
            "- rollback posture: if this packet drifts, repair the cross-build wiring or remove the stale claim from this note, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-shared-replay-contract.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` before widening any Phase 12 driver implementation work",
        ),
    ]
    for label, marker in expected_markers:
        if marker not in note_text:
            raise SystemExit(f"phase12-cross:note_marker:{label}")


def validate_fixture(doc: dict[str, object]) -> list[str]:
    if doc.get("phase") != EXPECTED_PHASE:
        raise SystemExit("phase12-cross:fixture_phase")
    if doc.get("lane_key") != EXPECTED_LANE_KEY:
        raise SystemExit("phase12-cross:fixture_lane_key")
    if doc.get("build_file") != BUILD_FILE.relative_to(ROOT).as_posix():
        raise SystemExit("phase12-cross:fixture_build_file")
    if doc.get("build_step") != EXPECTED_BUILD_STEP:
        raise SystemExit("phase12-cross:fixture_build_step")
    if not BUILD_FILE.exists():
        raise SystemExit("phase12-cross:build_file_missing")
    if not NOTE.exists():
        raise SystemExit("phase12-cross:note_file_missing")

    validate_build_text(BUILD_FILE.read_text(encoding="utf-8"))

    targets = doc.get("targets")
    if not isinstance(targets, list) or not targets:
        raise SystemExit("phase12-cross:fixture_targets")
    if doc.get("target_count") != len(targets):
        raise SystemExit("phase12-cross:target_count_mismatch")

    normalized_targets: list[str] = []
    seen_targets: set[str] = set()
    for target in targets:
        if not isinstance(target, str) or not target:
            raise SystemExit("phase12-cross:fixture_target_entry")
        if target in seen_targets:
            raise SystemExit(f"phase12-cross:duplicate_manifest_target:{target}")
        seen_targets.add(target)
        normalized_targets.append(target)

    validate_note_text(NOTE.read_text(encoding="utf-8"), normalized_targets)
    return normalized_targets


def resolve_targets(explicit_targets: list[str] | None, allowed_targets: list[str]) -> list[str]:
    if not explicit_targets:
        return allowed_targets

    allowed = set(allowed_targets)
    selected: list[str] = []
    seen_targets: set[str] = set()
    unexpected_targets: list[str] = []

    for target in explicit_targets:
        if target in seen_targets:
            raise SystemExit(f"phase12-cross:duplicate_target:{target}")
        seen_targets.add(target)
        if target not in allowed:
            unexpected_targets.append(target)
            continue
        selected.append(target)

    if unexpected_targets:
        raise SystemExit("phase12-cross:unexpected_target:" + ",".join(unexpected_targets))

    return selected


def expect_system_exit(label: str, callback, expected_message: str) -> None:
    try:
        callback()
    except SystemExit as exc:
        actual_message = str(exc)
        if actual_message != expected_message:
            raise SystemExit(
                f"phase12-cross:self-test:{label}:expected={expected_message!r}:actual={actual_message!r}"
            ) from exc
        return
    raise SystemExit(f"phase12-cross:self-test:{label}:missing_system_exit:{expected_message!r}")


def run_self_test() -> int:
    doc = load_json_object(FIXTURE)
    allowed_targets = validate_fixture(doc)
    build_text = BUILD_FILE.read_text(encoding="utf-8")
    note_text = NOTE.read_text(encoding="utf-8")

    if resolve_targets(None, allowed_targets) != allowed_targets:
        raise SystemExit("phase12-cross:self-test:default_target_selection")

    explicit_targets = [allowed_targets[2], allowed_targets[0]]
    if resolve_targets(explicit_targets, allowed_targets) != explicit_targets:
        raise SystemExit("phase12-cross:self-test:explicit_target_selection")

    expect_system_exit(
        "duplicate_target",
        lambda: resolve_targets([allowed_targets[0], allowed_targets[0]], allowed_targets),
        f"phase12-cross:duplicate_target:{allowed_targets[0]}",
    )
    expect_system_exit(
        "unexpected_target",
        lambda: resolve_targets(["sparc64-linux-musl"], allowed_targets),
        "phase12-cross:unexpected_target:sparc64-linux-musl",
    )

    bad_phase = dict(doc)
    bad_phase["phase"] = "Phase 11"
    expect_system_exit(
        "fixture_phase",
        lambda: validate_fixture(bad_phase),
        "phase12-cross:fixture_phase",
    )

    bad_lane = dict(doc)
    bad_lane["lane_key"] = "P12-L06"
    expect_system_exit(
        "fixture_lane_key",
        lambda: validate_fixture(bad_lane),
        "phase12-cross:fixture_lane_key",
    )

    bad_build_file = dict(doc)
    bad_build_file["build_file"] = "zigux/tests/phase12_build.zig"
    expect_system_exit(
        "fixture_build_file",
        lambda: validate_fixture(bad_build_file),
        "phase12-cross:fixture_build_file",
    )

    bad_build_step = dict(doc)
    bad_build_step["build_step"] = "test"
    expect_system_exit(
        "fixture_build_step",
        lambda: validate_fixture(bad_build_step),
        "phase12-cross:fixture_build_step",
    )

    bad_target_count = dict(doc)
    bad_target_count["target_count"] = len(allowed_targets) + 1
    expect_system_exit(
        "target_count_mismatch",
        lambda: validate_fixture(bad_target_count),
        "phase12-cross:target_count_mismatch",
    )

    duplicate_targets = dict(doc)
    duplicate_targets["targets"] = [allowed_targets[0], allowed_targets[0]]
    duplicate_targets["target_count"] = 2
    expect_system_exit(
        "duplicate_manifest_target",
        lambda: validate_fixture(duplicate_targets),
        f"phase12-cross:duplicate_manifest_target:{allowed_targets[0]}",
    )

    missing_net_syntax_lab = build_text.replace(
        'b.path("phase12_virtio_net_syntax_lab.zig")',
        'b.path("phase12_virtio_net_syntax_lab_missing.zig")',
        1,
    )
    expect_system_exit(
        "build_marker_net_syntax_lab",
        lambda: validate_build_text(missing_net_syntax_lab),
        "phase12-cross:build_marker:virtio_net_syntax_lab_module",
    )

    missing_scsi_recovery_state = build_text.replace(
        'b.path("phase12_virtio_scsi_recovery_state.zig")',
        'b.path("phase12_virtio_scsi_recovery_state_missing.zig")',
        1,
    )
    expect_system_exit(
        "build_marker_scsi_recovery_state",
        lambda: validate_build_text(missing_scsi_recovery_state),
        "phase12-cross:build_marker:virtio_scsi_recovery_state_module",
    )

    missing_raw_github_step = build_text.replace(
        "cross_step.dependOn(&phase12_raw_github_coverage_survey_tests.step);",
        "cross_step.dependOn(&phase12_libbpf_segments_tests.step);",
        1,
    )
    expect_system_exit(
        "build_marker_raw_github_step",
        lambda: validate_build_text(missing_raw_github_step),
        "phase12-cross:build_marker:raw_github_coverage_step",
    )

    missing_note_targets = note_text.replace(
        f"- approved targets: {', '.join(f'`{target}`' for target in allowed_targets)}",
        "- approved targets: `x86_64-linux-musl`, `aarch64-linux-gnu`, `riscv64-linux-musl`",
        1,
    )
    expect_system_exit(
        "note_marker_approved_targets",
        lambda: validate_note_text(missing_note_targets, allowed_targets),
        "phase12-cross:note_marker:approved_targets",
    )

    missing_note_gate = note_text.replace("`phase12_raw_github_coverage_survey.zig`", "`phase12_raw_github_coverage_missing.zig`", 1)
    expect_system_exit(
        "note_marker_landed_gates",
        lambda: validate_note_text(missing_note_gate, allowed_targets),
        "phase12-cross:note_marker:landed_gates",
    )

    missing_note_entrypoint = note_text.replace(
        "`python3 scripts/zigux/check-phase12-cross.py --zig <zig-path>`",
        "`python3 scripts/zigux/check-phase12-cross.py`",
        1,
    )
    expect_system_exit(
        "note_marker_compile_entrypoint",
        lambda: validate_note_text(missing_note_entrypoint, allowed_targets),
        "phase12-cross:note_marker:compile_entrypoint",
    )

    print("PHASE12_CROSS_SELF_TEST=pass")
    print("PHASE12_CROSS_SELF_TEST_CASE_COUNT=16")
    return 0


def run_build(zig: str, target: str) -> None:
    run(
        [
            zig,
            "build",
            EXPECTED_BUILD_STEP,
            "--build-file",
            str(BUILD_FILE),
            "--summary",
            "all",
            f"-Dtarget={target}",
        ],
        cwd=str(ROOT),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile the bounded Phase 12 packet for approved non-native musl targets."
    )
    parser.add_argument("--zig", help="Explicit zig executable path")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in fixture and target-selection checks",
    )
    parser.add_argument("--target", action="append", help="Explicit target triple to compile")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    zig = find_zig(args.zig)
    doc = load_json_object(FIXTURE)
    allowed_targets = validate_fixture(doc)
    targets = resolve_targets(args.target, allowed_targets)

    for target in targets:
        run_build(zig, target)

    print("PHASE12_CROSS=pass")
    print(f"PHASE12_CROSS_TARGET_COUNT={len(targets)}")
    print(f"PHASE12_CROSS_BUILD_STEP={EXPECTED_BUILD_STEP}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

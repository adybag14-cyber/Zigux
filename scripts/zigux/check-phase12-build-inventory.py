#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILD_PATH = Path("zigux/tests/phase12_build.zig")
FIXTURE_PATH = Path("zigux/tests/fixtures/phase12_build_inventory.json")

MODULE_RE = re.compile(
    r'const\s+([A-Za-z0-9_]+)\s*=\s*b\.createModule\(\.\{\s*'
    r'\.root_source_file\s*=\s*b\.path\("([^"]+)"\)',
    re.S,
)
IMPORT_RE = re.compile(
    r'([A-Za-z0-9_]+)\.addImport\(\s*"([^"]+)"\s*,\s*([A-Za-z0-9_]+)\s*,?\s*\);',
    re.S,
)
TEST_RE = re.compile(
    r'const\s+([A-Za-z0-9_]+)\s*=\s*b\.addTest\(\.\{\s*'
    r'\.name\s*=\s*"([^"]+)"\s*,\s*'
    r'\.root_module\s*=\s*([A-Za-z0-9_]+)\s*,',
    re.S,
)
DEPEND_RE = re.compile(r'test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);')


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def render_inventory(build_text: str) -> dict[str, object]:
    modules = [
        {"module": module_name, "path": path}
        for module_name, path in MODULE_RE.findall(build_text)
    ]
    imports = [
        {
            "module": module_name,
            "import_name": import_name,
            "imported_module": imported_module,
        }
        for module_name, import_name, imported_module in IMPORT_RE.findall(build_text)
    ]
    tests = TEST_RE.findall(build_text)
    return {
        "build_test_names": [test_name for _, test_name, _ in tests],
        "shared_test_depend_steps": DEPEND_RE.findall(build_text),
        "module_root_source_files": modules,
        "module_imports": imports,
        "test_root_modules": [
            {"test": test_name, "root_module": root_module}
            for _, test_name, root_module in tests
        ],
    }


def validate(root: Path) -> list[str]:
    build_path = root / BUILD_PATH
    fixture_path = root / FIXTURE_PATH
    failures: list[str] = []

    if not build_path.exists():
        failures.append(f"missing_file:{BUILD_PATH.as_posix()}")
    if not fixture_path.exists():
        failures.append(f"missing_file:{FIXTURE_PATH.as_posix()}")
    if failures:
        return failures

    expected = load_json(fixture_path)
    actual = render_inventory(build_path.read_text(encoding="utf-8"))

    build_test_names = actual["build_test_names"]
    shared_depend_steps = actual["shared_test_depend_steps"]
    test_root_modules = actual["test_root_modules"]

    if not build_test_names:
        failures.append("phase12_build_inventory_missing_tests")
    if len(build_test_names) != len(shared_depend_steps):
        failures.append("phase12_build_inventory_depend_step_count_mismatch")
    if len(build_test_names) != len(test_root_modules):
        failures.append("phase12_build_inventory_test_root_count_mismatch")
    if len(set(build_test_names)) != len(build_test_names):
        failures.append("phase12_build_inventory_duplicate_test_name")

    if expected != actual:
        failures.append("phase12_build_inventory_mismatch")
        failures.append("expected=" + json.dumps(expected, sort_keys=True))
        failures.append("actual=" + json.dumps(actual, sort_keys=True))
    return failures


CURRENT_BUILD_TEXT = """const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_net_queue_resume_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_queue_resume.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_queue_resume_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_queue_resume.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_queue_resume_root_module.addImport(
        "virtio_net_queue_resume",
        virtio_net_queue_resume_module,
    );

    const virtio_net_transmit_recycle_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_transmit_recycle.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_transmit_recycle_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_transmit_recycle.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_transmit_recycle_root_module.addImport(
        "virtio_net_transmit_recycle",
        virtio_net_transmit_recycle_module,
    );

    const virtio_net_receive_refill_replay_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_receive_refill_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_receive_refill_replay_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_receive_refill_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_receive_refill_replay_root_module.addImport(
        "virtio_net_receive_refill_replay",
        virtio_net_receive_refill_replay_module,
    );

    const virtio_net_post_reset_replay_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_post_reset_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_post_reset_replay_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_post_reset_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_post_reset_replay_root_module.addImport(
        "virtio_net_post_reset_replay",
        virtio_net_post_reset_replay_module,
    );

    const virtio_net_throughput_parity_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_throughput_parity.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_throughput_parity_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_throughput_parity.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_throughput_parity_root_module.addImport(
        "virtio_net_throughput_parity",
        virtio_net_throughput_parity_module,
    );

    const virtio_net_survey_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase12_virtio_net_queue_resume_tests = b.addTest(.{
        .name = "phase12-virtio-net-queue-resume-tests",
        .root_module = virtio_net_queue_resume_root_module,
    });
    const run_virtio_net_queue_resume_tests = b.addRunArtifact(
        phase12_virtio_net_queue_resume_tests,
    );

    const phase12_virtio_net_transmit_recycle_tests = b.addTest(.{
        .name = "phase12-virtio-net-transmit-recycle-tests",
        .root_module = virtio_net_transmit_recycle_root_module,
    });
    const run_virtio_net_transmit_recycle_tests = b.addRunArtifact(
        phase12_virtio_net_transmit_recycle_tests,
    );

    const phase12_virtio_net_receive_refill_replay_tests = b.addTest(.{
        .name = "phase12-virtio-net-receive-refill-replay-tests",
        .root_module = virtio_net_receive_refill_replay_root_module,
    });
    const run_virtio_net_receive_refill_replay_tests = b.addRunArtifact(
        phase12_virtio_net_receive_refill_replay_tests,
    );

    const phase12_virtio_net_post_reset_replay_tests = b.addTest(.{
        .name = "phase12-virtio-net-post-reset-replay-tests",
        .root_module = virtio_net_post_reset_replay_root_module,
    });
    const run_virtio_net_post_reset_replay_tests = b.addRunArtifact(
        phase12_virtio_net_post_reset_replay_tests,
    );

    const phase12_virtio_net_throughput_parity_tests = b.addTest(.{
        .name = "phase12-virtio-net-throughput-parity-tests",
        .root_module = virtio_net_throughput_parity_root_module,
    });
    const run_virtio_net_throughput_parity_tests = b.addRunArtifact(
        phase12_virtio_net_throughput_parity_tests,
    );

    const phase12_virtio_net_survey_tests = b.addTest(.{
        .name = "phase12-virtio-net-survey-tests",
        .root_module = virtio_net_survey_root_module,
    });
    const run_virtio_net_survey_tests = b.addRunArtifact(
        phase12_virtio_net_survey_tests,
    );

    const smoke_step = b.step(
        "smoke",
        "Run the Phase 12 virtio_net queue-resume, transmit-recycle, receive-refill replay, post-reset replay, throughput-parity, and survey-gate smoke tests",
    );
    smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);
    smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);
    smoke_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);
    smoke_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);
    smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);
    smoke_step.dependOn(&run_virtio_net_survey_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 12 virtio_net queue-resume, transmit-recycle, receive-refill replay, post-reset replay, throughput-parity, and survey-gate tests",
    );
    test_step.dependOn(&run_virtio_net_queue_resume_tests.step);
    test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);
    test_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);
    test_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);
    test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);
    test_step.dependOn(&run_virtio_net_survey_tests.step);
}
"""

CURRENT_FIXTURE = {
    "build_test_names": [
        "phase12-virtio-net-queue-resume-tests",
        "phase12-virtio-net-transmit-recycle-tests",
        "phase12-virtio-net-receive-refill-replay-tests",
        "phase12-virtio-net-post-reset-replay-tests",
        "phase12-virtio-net-throughput-parity-tests",
        "phase12-virtio-net-survey-tests",
    ],
    "shared_test_depend_steps": [
        "run_virtio_net_queue_resume_tests",
        "run_virtio_net_transmit_recycle_tests",
        "run_virtio_net_receive_refill_replay_tests",
        "run_virtio_net_post_reset_replay_tests",
        "run_virtio_net_throughput_parity_tests",
        "run_virtio_net_survey_tests",
    ],
    "module_root_source_files": [
        {
            "module": "virtio_net_queue_resume_module",
            "path": "../../drivers/net/virtio_net_queue_resume.zig",
        },
        {
            "module": "virtio_net_queue_resume_root_module",
            "path": "phase12_virtio_net_queue_resume.zig",
        },
        {
            "module": "virtio_net_transmit_recycle_module",
            "path": "../../drivers/net/virtio_net_transmit_recycle.zig",
        },
        {
            "module": "virtio_net_transmit_recycle_root_module",
            "path": "phase12_virtio_net_transmit_recycle.zig",
        },
        {
            "module": "virtio_net_receive_refill_replay_module",
            "path": "../../drivers/net/virtio_net_receive_refill_replay.zig",
        },
        {
            "module": "virtio_net_receive_refill_replay_root_module",
            "path": "phase12_virtio_net_receive_refill_replay.zig",
        },
        {
            "module": "virtio_net_post_reset_replay_module",
            "path": "../../drivers/net/virtio_net_post_reset_replay.zig",
        },
        {
            "module": "virtio_net_post_reset_replay_root_module",
            "path": "phase12_virtio_net_post_reset_replay.zig",
        },
        {
            "module": "virtio_net_throughput_parity_module",
            "path": "../../drivers/net/virtio_net_throughput_parity.zig",
        },
        {
            "module": "virtio_net_throughput_parity_root_module",
            "path": "phase12_virtio_net_throughput_parity.zig",
        },
        {
            "module": "virtio_net_survey_root_module",
            "path": "phase12_virtio_net_survey.zig",
        },
    ],
    "module_imports": [
        {
            "module": "virtio_net_queue_resume_root_module",
            "import_name": "virtio_net_queue_resume",
            "imported_module": "virtio_net_queue_resume_module",
        },
        {
            "module": "virtio_net_transmit_recycle_root_module",
            "import_name": "virtio_net_transmit_recycle",
            "imported_module": "virtio_net_transmit_recycle_module",
        },
        {
            "module": "virtio_net_receive_refill_replay_root_module",
            "import_name": "virtio_net_receive_refill_replay",
            "imported_module": "virtio_net_receive_refill_replay_module",
        },
        {
            "module": "virtio_net_post_reset_replay_root_module",
            "import_name": "virtio_net_post_reset_replay",
            "imported_module": "virtio_net_post_reset_replay_module",
        },
        {
            "module": "virtio_net_throughput_parity_root_module",
            "import_name": "virtio_net_throughput_parity",
            "imported_module": "virtio_net_throughput_parity_module",
        },
    ],
    "test_root_modules": [
        {
            "test": "phase12-virtio-net-queue-resume-tests",
            "root_module": "virtio_net_queue_resume_root_module",
        },
        {
            "test": "phase12-virtio-net-transmit-recycle-tests",
            "root_module": "virtio_net_transmit_recycle_root_module",
        },
        {
            "test": "phase12-virtio-net-receive-refill-replay-tests",
            "root_module": "virtio_net_receive_refill_replay_root_module",
        },
        {
            "test": "phase12-virtio-net-post-reset-replay-tests",
            "root_module": "virtio_net_post_reset_replay_root_module",
        },
        {
            "test": "phase12-virtio-net-throughput-parity-tests",
            "root_module": "virtio_net_throughput_parity_root_module",
        },
        {
            "test": "phase12-virtio-net-survey-tests",
            "root_module": "virtio_net_survey_root_module",
        },
    ],
}


def write_fixture_root(root: Path) -> None:
    (root / BUILD_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / FIXTURE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / BUILD_PATH).write_text(CURRENT_BUILD_TEXT, encoding="utf-8")
    (root / FIXTURE_PATH).write_text(
        json.dumps(CURRENT_FIXTURE, indent=2) + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-build-inventory-"))
    try:
        write_fixture_root(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture should pass: {failures!r}")

        bad_fixture = base / FIXTURE_PATH
        data = load_json(bad_fixture)
        data["build_test_names"] = data["build_test_names"][:-1]
        bad_fixture.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        failures = validate(base)
        if "phase12_build_inventory_mismatch" not in failures:
            raise SystemExit(f"expected mismatch failure, got {failures!r}")

        write_fixture_root(base)
        (base / BUILD_PATH).unlink()
        failures = validate(base)
        if f"missing_file:{BUILD_PATH.as_posix()}" not in failures:
            raise SystemExit(f"expected missing build failure, got {failures!r}")

        write_fixture_root(base)
        (base / BUILD_PATH).write_text(
            "const std = @import(\"std\");\n"
            "pub fn build(b: *std.Build) void {\n"
            "    _ = b;\n"
            "}\n",
            encoding="utf-8",
        )
        failures = validate(base)
        if "phase12_build_inventory_missing_tests" not in failures:
            raise SystemExit(f"expected missing tests failure, got {failures!r}")

        print("PHASE12_BUILD_INVENTORY_SELF_TEST=pass")
        print("PHASE12_BUILD_INVENTORY_SELF_TEST_CASE_COUNT=4")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 12 shared-build inventory fixture matches the live build packet structure."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE12_BUILD_INVENTORY=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE12_BUILD_INVENTORY=pass")
    print(f"PHASE12_BUILD_INVENTORY_TEST_COUNT={len(CURRENT_FIXTURE['build_test_names'])}")
    print(
        "PHASE12_BUILD_INVENTORY_MODULE_COUNT="
        f"{len(CURRENT_FIXTURE['module_root_source_files'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

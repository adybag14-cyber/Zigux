#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path(".")
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
STEP_RE = re.compile(
    r'const\s+([A-Za-z0-9_]+)\s*=\s*b\.step\(\s*'
    r'"([^"]+)"\s*,\s*"([^"]+)"\s*,?\s*\);',
    re.S,
)
SMOKE_DEPEND_RE = re.compile(r"smoke_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
TEST_DEPEND_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
THROUGHPUT_DEPEND_RE = re.compile(
    r"throughput_parity_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);"
)


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
    steps = STEP_RE.findall(build_text)
    return {
        "build_test_names": [test_name for _, test_name, _ in tests],
        "shared_smoke_depend_steps": SMOKE_DEPEND_RE.findall(build_text),
        "shared_test_depend_steps": TEST_DEPEND_RE.findall(build_text),
        "throughput_anchor_depend_steps": THROUGHPUT_DEPEND_RE.findall(build_text),
        "module_root_source_files": modules,
        "module_imports": imports,
        "test_root_modules": [
            {"test": test_name, "root_module": root_module}
            for _, test_name, root_module in tests
        ],
        "build_step_catalog": [
            {"variable": variable_name, "step": step_name, "description": description}
            for variable_name, step_name, description in steps
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
    shared_smoke_depend_steps = actual["shared_smoke_depend_steps"]
    shared_test_depend_steps = actual["shared_test_depend_steps"]
    throughput_anchor_depend_steps = actual["throughput_anchor_depend_steps"]
    build_step_catalog = actual["build_step_catalog"]
    test_root_modules = actual["test_root_modules"]

    if not build_test_names:
        failures.append("phase12_build_inventory_missing_tests")
    if not build_step_catalog:
        failures.append("phase12_build_inventory_missing_steps")
    if len(build_test_names) != len(shared_smoke_depend_steps):
        failures.append("phase12_build_inventory_smoke_depend_step_count_mismatch")
    if len(build_test_names) != len(shared_test_depend_steps):
        failures.append("phase12_build_inventory_test_depend_step_count_mismatch")
    if len(build_test_names) != len(test_root_modules):
        failures.append("phase12_build_inventory_test_root_count_mismatch")
    if len(set(build_test_names)) != len(build_test_names):
        failures.append("phase12_build_inventory_duplicate_test_name")
    if len(throughput_anchor_depend_steps) != 1:
        failures.append("phase12_build_inventory_throughput_anchor_depend_step_mismatch")

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
    const throughput_parity_tests = run_virtio_net_throughput_parity_tests;

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

    const throughput_parity_step = b.step("phase12-virtio-net-throughput-parity", "Run the Phase 12 virtio_net throughput parity checks");
    throughput_parity_step.dependOn(&throughput_parity_tests.step);
}
"""


def current_fixture() -> dict[str, object]:
    return render_inventory(CURRENT_BUILD_TEXT)


def write_fixture_root(root: Path) -> None:
    (root / BUILD_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / FIXTURE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / BUILD_PATH).write_text(CURRENT_BUILD_TEXT, encoding="utf-8")
    (root / FIXTURE_PATH).write_text(
        json.dumps(current_fixture(), indent=2) + "\n",
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
        data["build_step_catalog"] = data["build_step_catalog"][:-1]
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
            'const std = @import("std");\n'
            "pub fn build(b: *std.Build) void {\n"
            "    _ = b;\n"
            "}\n",
            encoding="utf-8",
        )
        failures = validate(base)
        if "phase12_build_inventory_missing_tests" not in failures:
            raise SystemExit(f"expected missing tests failure, got {failures!r}")
        if "phase12_build_inventory_missing_steps" not in failures:
            raise SystemExit(f"expected missing steps failure, got {failures!r}")

        write_fixture_root(base)
        (base / BUILD_PATH).write_text(
            (base / BUILD_PATH)
            .read_text(encoding="utf-8")
            .replace(
                "    throughput_parity_step.dependOn(&throughput_parity_tests.step);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate(base)
        if "phase12_build_inventory_throughput_anchor_depend_step_mismatch" not in failures:
            raise SystemExit(
                f"expected throughput anchor mismatch failure, got {failures!r}"
            )

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

    actual = render_inventory((args.root / BUILD_PATH).read_text(encoding="utf-8"))
    print("PHASE12_BUILD_INVENTORY=pass")
    print(f"PHASE12_BUILD_INVENTORY_TEST_COUNT={len(actual['build_test_names'])}")
    print(
        "PHASE12_BUILD_INVENTORY_MODULE_COUNT="
        f"{len(actual['module_root_source_files'])}"
    )
    print(
        "PHASE12_BUILD_INVENTORY_STEP_COUNT="
        f"{len(actual['build_step_catalog'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

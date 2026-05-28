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
SYNTAX_BUILD_PATH = Path("zigux/tests/phase12_virtio_net_syntax_lab_build.zig")
SYNTAX_SOURCE_PATH = Path("zigux/tests/phase12_virtio_net_syntax_lab.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

MODULE_RE = re.compile(r'const\s+([A-Za-z0-9_]+)\s*=\s*b\.createModule\(\.\{\s*\.root_source_file\s*=\s*b\.path\("([^"]+)"\)', re.S)
IMPORT_RE = re.compile(r'([A-Za-z0-9_]+)\.addImport\(\s*"([^"]+)"\s*,\s*([A-Za-z0-9_]+)\s*,?\s*\);', re.S)
TEST_RE = re.compile(r'const\s+([A-Za-z0-9_]+)\s*=\s*b\.addTest\(\.\{\s*\.name\s*=\s*"([^"]+)"\s*,\s*\.root_module\s*=\s*([A-Za-z0-9_]+)\s*,', re.S)
STEP_RE = re.compile(r'const\s+([A-Za-z0-9_]+)\s*=\s*b\.step\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,?\s*\);', re.S)
SMOKE_DEPEND_RE = re.compile(r"smoke_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
TEST_DEPEND_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
THROUGHPUT_DEPEND_RE = re.compile(r"throughput_parity_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")

EXPECTED_SYNTAX_LAB_INVENTORY = {
    "build_test_names": ["phase12-virtio-net-syntax-lab-tests"],
    "shared_smoke_depend_steps": ["run_syntax_lab_tests"],
    "shared_test_depend_steps": ["run_syntax_lab_tests"],
    "throughput_anchor_depend_steps": [],
    "module_root_source_files": [
        {"module": "virtio_module", "path": "../../drivers/virtio/virtio.zig"},
        {"module": "queue_resume_module", "path": "../../drivers/net/virtio_net_queue_resume.zig"},
        {"module": "receive_refill_replay_module", "path": "../../drivers/net/virtio_net_receive_refill_replay.zig"},
        {"module": "transmit_recycle_module", "path": "../../drivers/net/virtio_net_transmit_recycle.zig"},
        {"module": "post_reset_replay_module", "path": "../../drivers/net/virtio_net_post_reset_replay.zig"},
        {"module": "throughput_parity_module", "path": "../../drivers/net/virtio_net_throughput_parity.zig"},
        {"module": "syntax_lab_module", "path": "phase12_virtio_net_syntax_lab.zig"},
    ],
    "module_imports": [
        {"module": "syntax_lab_module", "import_name": "virtio", "imported_module": "virtio_module"},
        {"module": "syntax_lab_module", "import_name": "virtio_net_queue_resume", "imported_module": "queue_resume_module"},
        {"module": "syntax_lab_module", "import_name": "virtio_net_receive_refill_replay", "imported_module": "receive_refill_replay_module"},
        {"module": "syntax_lab_module", "import_name": "virtio_net_transmit_recycle", "imported_module": "transmit_recycle_module"},
        {"module": "syntax_lab_module", "import_name": "virtio_net_post_reset_replay", "imported_module": "post_reset_replay_module"},
        {"module": "syntax_lab_module", "import_name": "virtio_net_throughput_parity", "imported_module": "throughput_parity_module"},
    ],
    "test_root_modules": [{"test": "phase12-virtio-net-syntax-lab-tests", "root_module": "syntax_lab_module"}],
    "build_step_catalog": [
        {"variable": "smoke_step", "step": "smoke", "description": "Run the Phase 12 virtio_net syntax-lab smoke tests"},
        {"variable": "test_step", "step": "test", "description": "Run the Phase 12 virtio_net syntax-lab tests"},
    ],
}

REQUIRED_MAKEFILE_MARKERS = [
    "phase12-smoke:",
    "$(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12-test:",
    "$(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12-virtio-net-syntax-lab-test:",
    "$(ZIG) build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all",
    "phase12: phase12-validate phase12-smoke phase12-test",
]

FORBIDDEN_MAKEFILE_MARKERS = [
    "phase12: phase12-validate phase12-smoke phase12-test phase12-virtio-net-syntax-lab-test",
    "phase12-smoke: phase12-virtio-net-syntax-lab-test",
]


def render_inventory(build_text: str) -> dict[str, object]:
    modules = [{"module": a, "path": b} for a, b in MODULE_RE.findall(build_text)]
    imports = [{"module": a, "import_name": b, "imported_module": c} for a, b, c in IMPORT_RE.findall(build_text)]
    tests = TEST_RE.findall(build_text)
    steps = STEP_RE.findall(build_text)
    return {
        "build_test_names": [test_name for _, test_name, _ in tests],
        "shared_smoke_depend_steps": SMOKE_DEPEND_RE.findall(build_text),
        "shared_test_depend_steps": TEST_DEPEND_RE.findall(build_text),
        "throughput_anchor_depend_steps": THROUGHPUT_DEPEND_RE.findall(build_text),
        "module_root_source_files": modules,
        "module_imports": imports,
        "test_root_modules": [{"test": test_name, "root_module": root_module} for _, test_name, root_module in tests],
        "build_step_catalog": [{"variable": a, "step": b, "description": c} for a, b, c in steps],
    }


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (BUILD_PATH, FIXTURE_PATH, SYNTAX_BUILD_PATH, SYNTAX_SOURCE_PATH, MAKEFILE_PATH):
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel.as_posix()}")
    if failures:
        return failures

    expected = json.loads((root / FIXTURE_PATH).read_text(encoding="utf-8"))
    actual = render_inventory((root / BUILD_PATH).read_text(encoding="utf-8"))
    syntax_actual = render_inventory((root / SYNTAX_BUILD_PATH).read_text(encoding="utf-8"))
    makefile_text = (root / MAKEFILE_PATH).read_text(encoding="utf-8")

    if expected != actual:
        failures.append("phase12_build_inventory_mismatch")
    if syntax_actual != EXPECTED_SYNTAX_LAB_INVENTORY:
        failures.append("phase12_syntax_lab_inventory_mismatch")
    if len(actual["build_test_names"]) != len(actual["shared_smoke_depend_steps"]):
        failures.append("phase12_build_inventory_smoke_depend_step_count_mismatch")
    if len(actual["build_test_names"]) != len(actual["shared_test_depend_steps"]):
        failures.append("phase12_build_inventory_test_depend_step_count_mismatch")
    if actual["throughput_anchor_depend_steps"] != expected.get("throughput_anchor_depend_steps"):
        failures.append("phase12_build_inventory_throughput_anchor_depend_step_mismatch")
    for marker in REQUIRED_MAKEFILE_MARKERS:
        if marker not in makefile_text:
            failures.append(f"phase12_makefile_missing_marker:{marker}")
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        if marker in makefile_text:
            failures.append(f"phase12_makefile_forbidden_marker:{marker}")
    return failures


def write_fixture_root(root: Path) -> None:
    for rel in (BUILD_PATH, FIXTURE_PATH, SYNTAX_SOURCE_PATH):
        source_path = ROOT / rel
        if not source_path.exists():
            raise SystemExit(f"missing source fixture input: {source_path}")

    current_build = (ROOT / BUILD_PATH).read_text(encoding="utf-8")
    current_fixture = (ROOT / FIXTURE_PATH).read_text(encoding="utf-8")
    syntax_source = (ROOT / SYNTAX_SOURCE_PATH).read_text(encoding="utf-8")
    syntax_build = """const std = @import(\"std\");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_module = b.createModule(.{ .root_source_file = b.path(\"../../drivers/virtio/virtio.zig\"), .target = target, .optimize = optimize });
    const queue_resume_module = b.createModule(.{ .root_source_file = b.path(\"../../drivers/net/virtio_net_queue_resume.zig\"), .target = target, .optimize = optimize });
    const receive_refill_replay_module = b.createModule(.{ .root_source_file = b.path(\"../../drivers/net/virtio_net_receive_refill_replay.zig\"), .target = target, .optimize = optimize });
    const transmit_recycle_module = b.createModule(.{ .root_source_file = b.path(\"../../drivers/net/virtio_net_transmit_recycle.zig\"), .target = target, .optimize = optimize });
    const post_reset_replay_module = b.createModule(.{ .root_source_file = b.path(\"../../drivers/net/virtio_net_post_reset_replay.zig\"), .target = target, .optimize = optimize });
    const throughput_parity_module = b.createModule(.{ .root_source_file = b.path(\"../../drivers/net/virtio_net_throughput_parity.zig\"), .target = target, .optimize = optimize });
    const syntax_lab_module = b.createModule(.{ .root_source_file = b.path(\"phase12_virtio_net_syntax_lab.zig\"), .target = target, .optimize = optimize });
    syntax_lab_module.addImport(\"virtio\", virtio_module);
    syntax_lab_module.addImport(\"virtio_net_queue_resume\", queue_resume_module);
    syntax_lab_module.addImport(\"virtio_net_receive_refill_replay\", receive_refill_replay_module);
    syntax_lab_module.addImport(\"virtio_net_transmit_recycle\", transmit_recycle_module);
    syntax_lab_module.addImport(\"virtio_net_post_reset_replay\", post_reset_replay_module);
    syntax_lab_module.addImport(\"virtio_net_throughput_parity\", throughput_parity_module);
    const syntax_lab_tests = b.addTest(.{
        .name = \"phase12-virtio-net-syntax-lab-tests\",
        .root_module = syntax_lab_module,
    });
    const run_syntax_lab_tests = b.addRunArtifact(syntax_lab_tests);
    const smoke_step = b.step(\"smoke\", \"Run the Phase 12 virtio_net syntax-lab smoke tests\");
    smoke_step.dependOn(&run_syntax_lab_tests.step);
    const test_step = b.step(\"test\", \"Run the Phase 12 virtio_net syntax-lab tests\");
    test_step.dependOn(&run_syntax_lab_tests.step);
}
"""
    makefile_text = """phase12-smoke:
	cd $(ZIGUX_ROOT) && $(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all

phase12-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all

phase12-virtio-net-syntax-lab-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all

phase12: phase12-validate phase12-smoke phase12-test
"""
    for rel, text in (
        (BUILD_PATH, current_build),
        (FIXTURE_PATH, current_fixture),
        (SYNTAX_BUILD_PATH, syntax_build),
        (SYNTAX_SOURCE_PATH, syntax_source),
        (MAKEFILE_PATH, makefile_text),
    ):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-build-inventory-"))
    try:
        write_fixture_root(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture should pass: {failures!r}")

        write_fixture_root(base)
        (base / FIXTURE_PATH).write_text("{}\n", encoding="utf-8")
        if "phase12_build_inventory_mismatch" not in validate(base):
            raise SystemExit("expected inventory mismatch")

        write_fixture_root(base)
        (base / BUILD_PATH).write_text('const std = @import("std");\npub fn build(b: *std.Build) void { _ = b; }\n', encoding="utf-8")
        failures = validate(base)
        if "phase12_build_inventory_mismatch" not in failures:
            raise SystemExit("expected build mismatch")

        write_fixture_root(base)
        (base / BUILD_PATH).write_text(
            (base / BUILD_PATH).read_text(encoding="utf-8").replace(
                "throughput_parity_step.dependOn(&throughput_parity_tests.step);",
                "throughput_parity_step.dependOn(&run_virtio_net_survey_tests.step);",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate(base)
        if "phase12_build_inventory_throughput_anchor_depend_step_mismatch" not in failures:
            raise SystemExit("expected throughput-anchor dependency mismatch")

        write_fixture_root(base)
        (base / SYNTAX_SOURCE_PATH).unlink()
        failures = validate(base)
        if f"missing_file:{SYNTAX_SOURCE_PATH.as_posix()}" not in failures:
            raise SystemExit("expected syntax-lab source missing-file failure")

        write_fixture_root(base)
        (base / SYNTAX_BUILD_PATH).unlink()
        failures = validate(base)
        if f"missing_file:{SYNTAX_BUILD_PATH.as_posix()}" not in failures:
            raise SystemExit("expected syntax-lab build missing-file failure")

        write_fixture_root(base)
        (base / SYNTAX_BUILD_PATH).write_text('const std = @import("std");\npub fn build(b: *std.Build) void { _ = b; }\n', encoding="utf-8")
        failures = validate(base)
        if "phase12_syntax_lab_inventory_mismatch" not in failures:
            raise SystemExit("expected syntax-lab inventory mismatch")

        write_fixture_root(base)
        (base / MAKEFILE_PATH).write_text(
            "phase12-test:\n"
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all\n",
            encoding="utf-8",
        )
        failures = validate(base)
        if "phase12_makefile_missing_marker:phase12-virtio-net-syntax-lab-test:" not in failures:
            raise SystemExit("expected syntax-lab makefile marker failure")

        write_fixture_root(base)
        (base / MAKEFILE_PATH).write_text(
            (base / MAKEFILE_PATH).read_text(encoding="utf-8")
            + "phase12: phase12-validate phase12-smoke phase12-test phase12-virtio-net-syntax-lab-test\n",
            encoding="utf-8",
        )
        failures = validate(base)
        if (
            "phase12_makefile_forbidden_marker:"
            "phase12: phase12-validate phase12-smoke phase12-test phase12-virtio-net-syntax-lab-test"
        ) not in failures:
            raise SystemExit("expected forbidden syntax-lab aggregation marker")

        print("PHASE12_BUILD_INVENTORY_SELF_TEST=pass")
        print("PHASE12_BUILD_INVENTORY_SELF_TEST_CASE_COUNT=9")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the Phase 12 shared-build inventory fixture matches the live build packet structure.")
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
    syntax_actual = render_inventory((args.root / SYNTAX_BUILD_PATH).read_text(encoding="utf-8"))
    print("PHASE12_BUILD_INVENTORY=pass")
    print(f"PHASE12_BUILD_INVENTORY_TEST_COUNT={len(actual['build_test_names'])}")
    print(f"PHASE12_BUILD_INVENTORY_MODULE_COUNT={len(actual['module_root_source_files'])}")
    print(f"PHASE12_BUILD_INVENTORY_STEP_COUNT={len(actual['build_step_catalog'])}")
    print(f"PHASE12_SYNTAX_LAB_BUILD_INVENTORY_TEST_COUNT={len(syntax_actual['build_test_names'])}")
    print(f"PHASE12_SYNTAX_LAB_BUILD_INVENTORY_MODULE_COUNT={len(syntax_actual['module_root_source_files'])}")
    print(f"PHASE12_SYNTAX_LAB_BUILD_INVENTORY_STEP_COUNT={len(syntax_actual['build_step_catalog'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

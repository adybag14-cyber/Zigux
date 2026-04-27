const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow_unsafe_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    const atomic_helpers_module = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });
    const barrier_helpers_module = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });
    const mmio_helpers_module = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio_helpers_module.addImport("abi_bindings", abi_bindings_module);
    mmio_helpers_module.addImport("narrow_unsafe", narrow_unsafe_module);

    const low_level_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_low_level_wrappers.zig"),
        .target = target,
        .optimize = optimize,
    });
    low_level_root_module.addImport("abi_bindings", abi_bindings_module);
    low_level_root_module.addImport("atomic_helpers", atomic_helpers_module);
    low_level_root_module.addImport("barrier_helpers", barrier_helpers_module);
    low_level_root_module.addImport("mmio_helpers", mmio_helpers_module);
    low_level_root_module.addImport("narrow_unsafe", narrow_unsafe_module);

    const low_level_tests = b.addTest(.{
        .name = "phase3-low-level-wrapper-tests",
        .root_module = low_level_root_module,
    });
    const run_low_level_tests = b.addRunArtifact(low_level_tests);
    const low_level_step = b.step(
        "phase3-low-level-wrappers-test",
        "Run focused Phase 3 low-level wrapper tests",
    );
    low_level_step.dependOn(&run_low_level_tests.step);
}

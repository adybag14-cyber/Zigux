const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    abi_bindings.addImport("notifier_abi.zig", notifier_abi);

    const atomic_helper = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });
    const barrier_helper = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });
    const mmio_helper = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow_unsafe = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_unsafe.addImport("abi_bindings", abi_bindings);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_low_level_wrappers.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);
    root_module.addImport("atomic_helper", atomic_helper);
    root_module.addImport("barrier_helper", barrier_helper);
    root_module.addImport("mmio_helper", mmio_helper);
    root_module.addImport("narrow_unsafe", narrow_unsafe);

    const tests = b.addTest(.{
        .name = "phase3-low-level-wrappers-test",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step(
        "phase3-low-level-wrappers-test",
        "Run the focused Phase 3 low-level wrapper replay",
    );
    test_step.dependOn(&run_tests.step);
}

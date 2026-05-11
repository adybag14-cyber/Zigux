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
    narrow_unsafe_module.addImport("abi_bindings", abi_bindings_module);

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

    const allocator_policy_helpers_module = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy_helpers_module.addImport("abi_bindings", abi_bindings_module);

    const panic_policy_helpers_module = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_helpers_module.addImport("abi_bindings", abi_bindings_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_low_level_wrappers.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings_module);
    root_module.addImport("atomic_helpers", atomic_helpers_module);
    root_module.addImport("barrier_helpers", barrier_helpers_module);
    root_module.addImport("mmio_helpers", mmio_helpers_module);
    root_module.addImport("narrow_unsafe", narrow_unsafe_module);
    root_module.addImport("allocator_policy_helpers", allocator_policy_helpers_module);
    root_module.addImport("panic_policy_helpers", panic_policy_helpers_module);

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

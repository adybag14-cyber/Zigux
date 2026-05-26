const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const narrow_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_module.addImport("abi_bindings", abi_bindings_module);

    const unsafe_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy_module.addImport("abi_bindings", abi_bindings_module);
    unsafe_policy_module.addImport("narrow", narrow_module);

    const mmio_module = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio_module.addImport("abi_bindings", abi_bindings_module);
    mmio_module.addImport("unsafe_policy", unsafe_policy_module);

    const tests = b.addTest(.{
        .name = "phase3-mmio-test",
        .root_module = mmio_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const phase3_mmio_step = b.step(
        "phase3-mmio-test",
        "Run the focused Phase 3 mmio helper tests",
    );
    phase3_mmio_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the focused Phase 3 mmio helper tests",
    );
    test_step.dependOn(&run_tests.step);
}

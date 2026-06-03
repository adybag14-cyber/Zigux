const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const atomic_module = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });

    const abi_tests = b.addTest(.{
        .name = "phase3_abi_pair_tests",
        .root_module = abi_bindings_module,
    });
    const atomic_tests = b.addTest(.{
        .name = "phase3_atomic_pair_tests",
        .root_module = atomic_module,
    });

    const run_abi_tests = b.addRunArtifact(abi_tests);
    const run_atomic_tests = b.addRunArtifact(atomic_tests);

    const test_step = b.step(
        "phase3-abi-atomic-pair-test",
        "Run the focused Phase 3 ABI bindings and atomic helper pair replay",
    );
    test_step.dependOn(&run_abi_tests.step);
    test_step.dependOn(&run_atomic_tests.step);
}

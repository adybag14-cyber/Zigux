const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const barrier_module = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });

    const abi_tests = b.addTest(.{
        .name = "phase3_abi_pair_tests",
        .root_module = abi_bindings_module,
    });
    const barrier_tests = b.addTest(.{
        .name = "phase3_barrier_pair_tests",
        .root_module = barrier_module,
    });

    const run_abi_tests = b.addRunArtifact(abi_tests);
    const run_barrier_tests = b.addRunArtifact(barrier_tests);

    const test_step = b.step(
        "phase3-abi-barrier-pair-test",
        "Run the focused Phase 3 ABI bindings and barrier helper pair replay",
    );
    test_step.dependOn(&run_abi_tests.step);
    test_step.dependOn(&run_barrier_tests.step);
}

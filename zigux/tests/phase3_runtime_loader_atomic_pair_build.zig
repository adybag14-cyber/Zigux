const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const atomic_tests = b.addTest(.{
        .name = "phase3_atomic_pair_tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../helpers/atomic.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_loader_contract_tests = b.addTest(.{
        .name = "phase3_runtime_loader_contract_pair_tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_atomic_tests = b.addRunArtifact(atomic_tests);
    const run_runtime_loader_contract_tests = b.addRunArtifact(runtime_loader_contract_tests);

    const pair_test_step = b.step(
        "phase3-runtime-loader-atomic-pair-test",
        "Run the focused Phase 3 runtime-loader/atomic pair replay",
    );
    pair_test_step.dependOn(&run_atomic_tests.step);
    pair_test_step.dependOn(&run_runtime_loader_contract_tests.step);
}

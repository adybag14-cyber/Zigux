const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const panic_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_module.addImport("abi_bindings", abi_bindings_module);

    const barrier_module = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });

    const panic_policy_tests = b.addTest(.{
        .root_module = panic_policy_module,
        .name = "phase3_panic_policy_barrier_pair_panic_policy_tests",
    });
    const barrier_tests = b.addTest(.{
        .root_module = barrier_module,
        .name = "phase3_panic_policy_barrier_pair_barrier_tests",
    });

    const run_panic_policy_tests = b.addRunArtifact(panic_policy_tests);
    const run_barrier_tests = b.addRunArtifact(barrier_tests);

    const pair_test = b.step(
        "phase3-panic-policy-barrier-pair-test",
        "Run the Phase 3 panic-policy and barrier helper packets together.",
    );
    pair_test.dependOn(&run_panic_policy_tests.step);
    pair_test.dependOn(&run_barrier_tests.step);
}

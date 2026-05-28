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

    const atomic_module = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });

    const panic_policy_tests = b.addTest(.{
        .root_module = panic_policy_module,
        .name = "phase3_panic_policy_pair_tests",
    });
    const atomic_tests = b.addTest(.{
        .root_module = atomic_module,
        .name = "phase3_atomic_pair_tests",
    });

    const run_panic_policy_tests = b.addRunArtifact(panic_policy_tests);
    const run_atomic_tests = b.addRunArtifact(atomic_tests);

    const pair_test = b.step(
        "phase3-panic-policy-atomic-pair-test",
        "Run the standalone Phase 3 panic-policy and atomic pair replay.",
    );
    pair_test.dependOn(&run_panic_policy_tests.step);
    pair_test.dependOn(&run_atomic_tests.step);
}

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

    const abi_tests = b.addTest(.{
        .name = "phase3_abi_pair_tests",
        .root_module = abi_bindings_module,
    });
    const panic_policy_tests = b.addTest(.{
        .name = "phase3_panic_policy_pair_tests",
        .root_module = panic_policy_module,
    });

    const run_abi_tests = b.addRunArtifact(abi_tests);
    const run_panic_policy_tests = b.addRunArtifact(panic_policy_tests);

    const test_step = b.step(
        "phase3-abi-panic-policy-pair-test",
        "Run the focused Phase 3 ABI bindings and panic policy helper pair replay",
    );
    test_step.dependOn(&run_abi_tests.step);
    test_step.dependOn(&run_panic_policy_tests.step);
}

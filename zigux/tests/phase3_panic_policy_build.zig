const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const panic_policy_helpers_module = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_helpers_module.addImport("abi_bindings", abi_bindings_module);

    const tests = b.addTest(.{
        .name = "phase3-panic-policy-test",
        .root_module = panic_policy_helpers_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase3-panic-policy-test",
        "Run the focused Phase 3 panic policy helper tests",
    );
    test_step.dependOn(&run_tests.step);
}

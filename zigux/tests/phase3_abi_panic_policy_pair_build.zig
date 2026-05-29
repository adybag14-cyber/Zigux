const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const panic_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy.addImport("abi_bindings", abi_bindings);

    const abi_tests = b.addTest(.{
        .name = "phase3_abi_pair_tests",
        .root_module = abi_bindings,
    });
    const panic_policy_tests = b.addTest(.{
        .name = "phase3_panic_policy_pair_tests",
        .root_module = panic_policy,
    });

    const abi_run = b.addRunArtifact(abi_tests);
    const panic_policy_run = b.addRunArtifact(panic_policy_tests);

    const pair_step = b.step(
        "phase3-abi-panic-policy-pair-test",
        "Run the focused Phase 3 ABI bindings and panic policy helper pair replay.",
    );
    pair_step.dependOn(&abi_run.step);
    pair_step.dependOn(&panic_policy_run.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const allocator_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy.addImport("abi_bindings", abi_bindings);

    const abi_tests = b.addTest(.{
        .name = "phase3_abi_allocator_pair_abi_tests",
        .root_module = abi_bindings,
    });
    const allocator_policy_tests = b.addTest(.{
        .name = "phase3_abi_allocator_pair_allocator_policy_tests",
        .root_module = allocator_policy,
    });

    const abi_run = b.addRunArtifact(abi_tests);
    const allocator_policy_run = b.addRunArtifact(allocator_policy_tests);

    const pair_step = b.step(
        "phase3-abi-allocator-policy-pair-test",
        "Run the focused Phase 3 ABI bindings and allocator policy helper pair replay.",
    );
    pair_step.dependOn(&abi_run.step);
    pair_step.dependOn(&allocator_policy_run.step);
}

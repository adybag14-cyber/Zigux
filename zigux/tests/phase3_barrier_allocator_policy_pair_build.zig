const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const barrier = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });
    const allocator_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy.addImport("abi_bindings", abi_bindings);

    const barrier_tests = b.addTest(.{
        .name = "phase3_barrier_pair_tests",
        .root_module = barrier,
    });
    const allocator_policy_tests = b.addTest(.{
        .name = "phase3_allocator_policy_pair_tests",
        .root_module = allocator_policy,
    });

    const barrier_run = b.addRunArtifact(barrier_tests);
    const allocator_policy_run = b.addRunArtifact(allocator_policy_tests);

    const pair_step = b.step(
        "phase3-barrier-allocator-policy-pair-test",
        "Run the Phase 3 barrier and allocator_policy helper packets together.",
    );
    pair_step.dependOn(&barrier_run.step);
    pair_step.dependOn(&allocator_policy_run.step);
}

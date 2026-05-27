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

    const tests = b.addTest(.{
        .name = "phase3-allocator-policy-test",
        .root_module = allocator_policy,
    });
    const run = b.addRunArtifact(tests);

    const phase3_allocator_policy_step = b.step(
        "phase3-allocator-policy-test",
        "Run the standalone Phase 3 allocator-policy helper tests",
    );
    phase3_allocator_policy_step.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the standalone Phase 3 allocator-policy helper tests",
    );
    test_step.dependOn(&run.step);
}

const std = @import("std");

fn addAllocatorPolicyTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);

    const tests = b.addTest(.{
        .name = "phase3-allocator-policy-test",
        .root_module = root_module,
    });

    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const allocator_policy = addAllocatorPolicyTest(b, target, optimize);

    const allocator_policy_step = b.step(
        "phase3-allocator-policy-test",
        "Run the focused Phase 3 allocator-policy ABI replay",
    );
    allocator_policy_step.dependOn(&allocator_policy.step);
}

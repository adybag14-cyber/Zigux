const std = @import("std");

fn addUnsafePolicyTest(
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
        .root_source_file = b.path("../phase3_unsafe_policy_test_root.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);

    const tests = b.addTest(.{
        .name = "phase3-unsafe-policy-test",
        .root_module = root_module,
    });

    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unsafe_policy = addUnsafePolicyTest(b, target, optimize);

    const unsafe_policy_step = b.step(
        "phase3-unsafe-policy-test",
        "Run the focused Phase 3 unsafe-policy ABI replay",
    );
    unsafe_policy_step.dependOn(&unsafe_policy.step);
}

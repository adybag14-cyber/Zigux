const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_step = addContractRun(b, target, optimize);
    b.step("phase2-cross-policy-sha-scope-contract", "Run the Phase 2 cross policy SHA scope contract").dependOn(contract_step);

    const test_step = addContractRun(b, target, optimize);
    b.step("test", "Run the Phase 2 cross policy SHA scope contract tests").dependOn(test_step);
}

fn addContractRun(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step {
    const module = b.createModule(.{
        .root_source_file = b.path("phase2_cross_policy_sha_scope_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{ .root_module = module });
    const run = b.addRunArtifact(tests);
    return &run.step;
}

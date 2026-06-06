const std = @import("std");

fn addContractTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_closure_string_casecmp_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase1-closure-string-casecmp-contract",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = addContractTest(b, target, optimize);

    const contract_step = b.step(
        "phase1-closure-string-casecmp-contract",
        "Run the Phase 1 closure string case-insensitive compare marker contract",
    );
    contract_step.dependOn(&contract_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 1 closure string case-insensitive compare marker contract",
    );
    test_step.dependOn(&contract_tests.step);
}

const std = @import("std");

fn addContractTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_closure_bench_expectations_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase1-closure-bench-expectations-contract",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);
    run.setCwd(b.path("../.."));
    return run;
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = addContractTest(b, target, optimize);

    const contract_step = b.step(
        "phase1-closure-bench-expectations-contract",
        "Run the Phase 1 closure bench expectations contract",
    );
    contract_step.dependOn(&contract.step);

    const test_step = b.step("test", "Run the Phase 1 closure bench expectations contract");
    test_step.dependOn(&contract.step);

    b.default_step.dependOn(&contract.step);
}

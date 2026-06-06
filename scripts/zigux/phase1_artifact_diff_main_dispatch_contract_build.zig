const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase1_artifact_diff_main_dispatch_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "phase1-artifact-diff-main-dispatch-contract",
        .root_module = contract_module,
    });

    const run_contract = b.addRunArtifact(contract_tests);
    const contract_step = b.step("phase1-artifact-diff-main-dispatch-contract", "Run the artifact diff main dispatch contract");
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the artifact diff main dispatch contract");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}

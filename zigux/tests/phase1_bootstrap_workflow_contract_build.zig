const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_bootstrap_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-bootstrap-workflow-contract",
        "Run the Phase 1 bootstrap workflow contract witness",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Phase 1 bootstrap workflow contract tests");
    test_step.dependOn(&run_tests.step);
}

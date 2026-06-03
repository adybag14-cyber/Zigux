const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane17_phase1_bench_workflow_publish_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step("lane17-phase1-bench-workflow-publish-contract", "Validate the Lane 17 Phase 1 bench workflow publish splice");
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 17 Phase 1 bench workflow publish contract tests");
    test_step.dependOn(&run_tests.step);
}

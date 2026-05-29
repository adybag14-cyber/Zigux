const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "lane17-phase1-bench-workflow-gap-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane17_phase1_bench_workflow_gap_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const lane_step = b.step(
        "lane17-phase1-bench-workflow-gap-contract",
        "Run the Lane 17 Phase 1 bench workflow gap contract.",
    );
    lane_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 1 bench workflow gap contract.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane17_phase1_bench_live_guard_workflow_cluster.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const named_step = b.step(
        "lane17-phase1-bench-live-guard-workflow-cluster",
        "Run the Lane 17 Phase 1 bench live-guard workflow cluster contract",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 17 Phase 1 bench live-guard workflow cluster contract",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(named_step);
}

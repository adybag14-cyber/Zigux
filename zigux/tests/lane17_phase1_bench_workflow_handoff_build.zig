const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_step = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane17_phase1_bench_workflow_handoff.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(test_step);

    const named_step = b.step(
        "lane17-phase1-bench-workflow-handoff",
        "Run the Lane 17 Phase 1 bench workflow handoff contract",
    );
    named_step.dependOn(&run_tests.step);

    const default_test_step = b.step("test", "Run Lane 17 Phase 1 bench workflow handoff contract tests");
    default_test_step.dependOn(&run_tests.step);
}

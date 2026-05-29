const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane17_phase1_bench_workflow_live_check_window.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const named_step = b.step(
        "lane17-phase1-bench-workflow-live-check-window",
        "Run the Lane 17 Phase 1 bench workflow live-check window contract",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 17 Phase 1 bench workflow live-check window contract",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(named_step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const context_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_bench_live_step_context.zig"),
        .target = target,
        .optimize = optimize,
    });

    const context_tests = b.addTest(.{
        .name = "lane17-phase1-bench-live-step-context-tests",
        .root_module = context_module,
    });
    const run_context_tests = b.addRunArtifact(context_tests);

    const focused_step = b.step(
        "lane17-phase1-bench-live-step-context",
        "Run the Lane 17 Phase 1 bench live-step workflow context contract.",
    );
    focused_step.dependOn(&run_context_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 1 bench live-step workflow context tests.");
    test_step.dependOn(&run_context_tests.step);

    b.default_step.dependOn(test_step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const summary_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_checker_summary_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_summary_tests = b.addRunArtifact(summary_tests);

    const summary_step = b.step(
        "phase2-cross-checker-summary-contract",
        "Run the Phase 2 cross checker summary contract.",
    );
    summary_step.dependOn(&run_summary_tests.step);

    const test_step = b.step("test", "Run the Phase 2 cross checker summary contract tests.");
    test_step.dependOn(&run_summary_tests.step);
}

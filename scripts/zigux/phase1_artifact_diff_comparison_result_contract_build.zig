const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_artifact_diff_comparison_result_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const step = b.step(
        "phase1-artifact-diff-comparison-result-contract",
        "Run the Lane 09 artifact diff ComparisonResult source contract",
    );
    step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 09 artifact diff ComparisonResult source contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase2-artifact-diff-docs-contract-test",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_artifact_diff_docs_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase2-artifact-diff-docs-contract-test",
        "Run the Phase 2 artifact-diff documentation contract",
    );
    test_step.dependOn(&run_tests.step);

    const default_step = b.step("test", "Run the default Phase 2 artifact-diff documentation contract");
    default_step.dependOn(&run_tests.step);
}

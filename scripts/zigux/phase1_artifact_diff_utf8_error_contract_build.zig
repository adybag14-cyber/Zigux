const std = @import("std");

pub fn build(b: *std.Build) void {
    const test_module = b.createModule(.{
        .root_source_file = b.path("phase1_artifact_diff_utf8_error_contract.zig"),
        .target = b.graph.host,
    });
    const tests = b.addTest(.{ .root_module = test_module });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-artifact-diff-utf8-error-contract",
        "Run the Phase 1 artifact-diff UTF-8 error source contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 artifact-diff UTF-8 error contract tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}

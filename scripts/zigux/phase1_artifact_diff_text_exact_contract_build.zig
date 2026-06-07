const std = @import("std");

pub fn build(b: *std.Build) void {
    const test_step = b.step(
        "phase1-artifact-diff-text-exact-contract",
        "Run the Lane 09 artifact-diff text exactness contract",
    );
    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_artifact_diff_text_exact_contract.zig"),
            .target = b.graph.host,
        }),
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    test_step.dependOn(&run_unit_tests.step);

    const default_test_step = b.step("test", "Run artifact-diff text exactness contract tests");
    default_test_step.dependOn(&run_unit_tests.step);
    b.default_step.dependOn(&run_unit_tests.step);
}

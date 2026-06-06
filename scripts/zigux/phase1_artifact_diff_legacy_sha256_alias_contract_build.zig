const std = @import("std");

pub fn build(b: *std.Build) void {
    const test_module = b.createModule(.{
        .root_source_file = b.path("phase1_artifact_diff_legacy_sha256_alias_contract.zig"),
        .target = b.graph.host,
    });
    const tests = b.addTest(.{ .root_module = test_module });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-artifact-diff-legacy-sha256-alias-contract",
        "Run the Phase 1 artifact-diff legacy sha256 alias source contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 artifact-diff legacy sha256 alias contract tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}

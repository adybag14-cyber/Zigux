const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_artifact_diff_json_utf8_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase1-artifact-diff-json-utf8-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step("phase1-artifact-diff-json-utf8-contract", "Run the Phase 1 artifact diff JSON UTF-8 contract");
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 artifact diff JSON UTF-8 contract tests");
    test_step.dependOn(&run_tests.step);
}

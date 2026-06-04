const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("artifact_diff_json_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "artifact-diff-json-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "artifact-diff-json-contract",
        "Run the artifact_diff.py JSON canonicalization contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the artifact_diff.py JSON canonicalization contract");
    test_step.dependOn(&run_tests.step);
}

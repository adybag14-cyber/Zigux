const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("artifact_diff_nonfile_path_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "artifact-diff-nonfile-path-contract",
        "Validate artifact_diff.py non-file path diagnostic gate markers",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run artifact diff non-file path contract tests");
    test_step.dependOn(&run_contract_tests.step);
}

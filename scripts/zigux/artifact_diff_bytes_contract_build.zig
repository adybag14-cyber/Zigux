const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("artifact_diff_bytes_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "artifact-diff-bytes-contract-tests",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const contract_step = b.step("artifact-diff-bytes-contract", "Run artifact_diff.py bytes-mode contract");
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run artifact_diff.py bytes-mode contract");
    test_step.dependOn(&run_contract_tests.step);
}

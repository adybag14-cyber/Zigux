const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane18_stage_source_checkonly_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const contract_tests = b.addTest(.{
        .name = "lane18-stage-source-checkonly-contract-tests",
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    const contract_step = b.step(
        "lane18-stage-source-checkonly-contract",
        "Run the Lane 18 stage-pinned Zig archive source check-only contract.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 18 stage-pinned Zig archive source check-only contract tests.",
    );
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}

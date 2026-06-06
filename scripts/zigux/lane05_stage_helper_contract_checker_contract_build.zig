const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane05_stage_helper_contract_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane05-stage-helper-contract-checker-contract-tests",
        .root_module = contract_module,
    });
    const run_contract = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane05-stage-helper-contract-checker-contract",
        "Run the Lane 05 stage helper contract checker source contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run Lane 05 stage helper contract checker source tests");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}

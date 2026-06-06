const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_toolchain_policy_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    const contract_step = b.step(
        "lane05-toolchain-policy-workflow-contract",
        "Run the Lane 05 toolchain policy/workflow contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 05 toolchain policy/workflow contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}

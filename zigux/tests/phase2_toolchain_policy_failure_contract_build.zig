const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .name = "phase2-toolchain-policy-failure-contract-test",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_toolchain_policy_failure_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const test_step = b.step("test", "Run Phase 2 toolchain policy failure contract tests");
    test_step.dependOn(&run_contract_tests.step);

    const named_test_step = b.step("phase2-toolchain-policy-failure-contract-test", "Run Phase 2 toolchain policy failure contract tests");
    named_test_step.dependOn(&run_contract_tests.step);
}

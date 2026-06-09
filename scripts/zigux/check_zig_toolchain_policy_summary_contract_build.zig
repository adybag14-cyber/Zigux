const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("check_zig_toolchain_policy_summary_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const contract_tests = b.addTest(.{
        .name = "check-zig-toolchain-policy-summary-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract = b.addExecutable(.{
        .name = "check-zig-toolchain-policy-summary-contract",
        .root_module = contract_module,
    });
    const run_contract = b.addRunArtifact(contract);

    const contract_step = b.step(
        "check-zig-toolchain-policy-summary-contract",
        "Validate the check-zig-toolchain policy-only summary source contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the check-zig-toolchain policy-only summary contract tests");
    test_step.dependOn(&run_contract_tests.step);
    b.default_step.dependOn(&run_contract_tests.step);
}

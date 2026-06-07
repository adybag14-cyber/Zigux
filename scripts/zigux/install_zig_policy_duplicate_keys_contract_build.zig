const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("install_zig_policy_duplicate_keys_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const contract_tests = b.addTest(.{
        .name = "install-zig-policy-duplicate-keys-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "install-zig-policy-duplicate-keys-contract",
        "Run the Lane 18 install-zig policy duplicate-keys contract.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 18 install-zig policy duplicate-keys contract tests.");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}

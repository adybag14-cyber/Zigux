const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("check_zig_toolchain_policy_validation_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "check-zig-toolchain-policy-validation-contract-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "check-zig-toolchain-policy-validation-contract",
        "Run the Lane 18 check-zig-toolchain policy validation contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 18 check-zig-toolchain policy validation contract tests.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}

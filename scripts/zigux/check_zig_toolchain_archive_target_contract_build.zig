const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("check_zig_toolchain_archive_target_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "check-zig-toolchain-archive-target-contract",
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    const test_step = b.step(
        "check-zig-toolchain-archive-target-contract",
        "Run the check-zig-toolchain explicit archive target contract.",
    );
    test_step.dependOn(&run_contract_tests.step);

    const default_test_step = b.step(
        "test",
        "Run the check-zig-toolchain explicit archive target contract tests.",
    );
    default_test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .name = "phase15-lane01-readme-charter-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase15_lane01_readme_charter_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    const test_step = b.step("phase15-lane01-readme-charter-contract", "Run the Lane 01 README charter contract tests.");
    test_step.dependOn(&run_contract_tests.step);

    const default_test_step = b.step("test", "Run the Lane 01 README charter contract tests.");
    default_test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}

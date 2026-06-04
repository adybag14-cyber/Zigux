const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane01_non_negotiable_rules_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const named_step = b.step(
        "lane01-non-negotiable-rules-contract",
        "Run the Lane 01 non-negotiable product rules contract",
    );
    named_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run Lane 01 non-negotiable product rules contract tests");
    test_step.dependOn(&run_contract_tests.step);
}

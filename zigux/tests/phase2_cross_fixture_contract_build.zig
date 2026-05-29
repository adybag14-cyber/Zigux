const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const fixture_contract_module = b.createModule(.{
        .root_source_file = b.path("phase2_cross_fixture_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const fixture_contract_tests = b.addTest(.{
        .name = "phase2-cross-fixture-contract-tests",
        .root_module = fixture_contract_module,
    });
    const run_fixture_contract_tests = b.addRunArtifact(fixture_contract_tests);

    const contract_step = b.step("phase2-cross-fixture-contract", "Run the Phase 2 cross fixture contract tests");
    contract_step.dependOn(&run_fixture_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 2 cross fixture contract tests");
    test_step.dependOn(&run_fixture_contract_tests.step);

    b.default_step.dependOn(test_step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_cmdline_fixture_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase1-cmdline-fixture-contract-tests",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-cmdline-fixture-contract",
        "Run the Phase 1 cmdline fixture contract tests",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 cmdline fixture contract tests");
    test_step.dependOn(&run_tests.step);
}

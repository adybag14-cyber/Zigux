const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_module = b.createModule(.{
        .root_source_file = b.path("phase1_cmdline_fixture_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .root_module = test_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase1-cmdline-fixture-contract",
        "Run the Lane 09 Phase 1 cmdline fixture contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 09 Phase 1 cmdline fixture contract test alias",
    );
    test_step.dependOn(&run_tests.step);
}

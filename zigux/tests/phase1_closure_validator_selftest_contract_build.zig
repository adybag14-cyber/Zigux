const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_closure_validator_selftest_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase1-closure-validator-selftest-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "phase1-closure-validator-selftest-contract",
        "Run the Phase 1 closure validator self-test contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 closure validator self-test contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}

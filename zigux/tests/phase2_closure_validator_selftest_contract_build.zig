const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_closure_validator_selftest_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase2-closure-validator-selftest-contract-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase2-closure-validator-selftest-contract",
        "Run the Phase 2 closure validator self-test contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const default_test_step = b.step("test", "Run the Phase 2 closure validator self-test contract.");
    default_test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(default_test_step);
}

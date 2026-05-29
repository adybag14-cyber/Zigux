const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_root_module = b.createModule(.{
        .root_source_file = b.path("phase2_cross_failure_codes_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "phase2-cross-failure-codes-contract-tests",
        .root_module = contract_root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase2-cross-failure-codes-contract",
        "Run the Lane 21 Phase 2 cross failure-code contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 21 Phase 2 cross failure-code contract");
    test_step.dependOn(&run_contract_tests.step);
}

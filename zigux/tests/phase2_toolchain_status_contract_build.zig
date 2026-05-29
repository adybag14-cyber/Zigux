const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase2_toolchain_status_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "phase2-toolchain-status-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const test_step = b.step(
        "phase2-toolchain-status-contract-test",
        "Run the Phase 2 toolchain status/archive output contract",
    );
    test_step.dependOn(&run_contract_tests.step);
}

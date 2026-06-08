const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const atomic_module = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_atomic_order_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("atomic_helpers", atomic_module);

    const contract_tests = b.addTest(.{
        .name = "phase3-abi-atomic-order-contract-test",
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    const contract_step = b.step(
        "phase3-abi-atomic-order-contract",
        "Run the Lane 26 Phase 3 ABI atomic order contract.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 26 Phase 3 ABI atomic order contract tests.");
    test_step.dependOn(contract_step);

    b.default_step.dependOn(&run_contract_tests.step);
}

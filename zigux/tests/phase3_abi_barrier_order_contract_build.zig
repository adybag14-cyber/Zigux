const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const barrier_helpers = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract = b.createModule(.{
        .root_source_file = b.path("phase3_abi_barrier_order_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract.addImport("barrier_helpers", barrier_helpers);

    const contract_tests = b.addTest(.{
        .name = "phase3_abi_barrier_order_contract",
        .root_module = contract,
    });
    const run_contract = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-barrier-order-contract",
        "Run the Phase 3 ABI barrier order contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Phase 3 ABI barrier order contract");
    test_step.dependOn(contract_step);
}

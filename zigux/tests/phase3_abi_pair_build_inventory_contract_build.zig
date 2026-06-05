const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addTest(.{
        .name = "phase3_abi_pair_build_inventory_contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_abi_pair_build_inventory_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract = b.addRunArtifact(contract);

    const contract_step = b.step(
        "phase3-abi-pair-build-inventory-contract",
        "Check the Phase 3 ABI pair-build shard inventory",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Phase 3 ABI pair-build inventory contract");
    test_step.dependOn(contract_step);
}

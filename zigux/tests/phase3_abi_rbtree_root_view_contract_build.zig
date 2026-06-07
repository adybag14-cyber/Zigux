const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_rbtree_root_view_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("abi_bindings", abi_bindings_module);

    const contract_tests = b.addTest(.{
        .name = "phase3-abi-rbtree-root-view-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-rbtree-root-view-contract",
        "Run the Phase 3 ABI rbtree root view contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI rbtree root view contract");
    test_step.dependOn(contract_step);

    b.default_step.dependOn(&run_contract_tests.step);
}

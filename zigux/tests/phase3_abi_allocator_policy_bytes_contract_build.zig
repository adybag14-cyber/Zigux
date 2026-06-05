const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const allocator_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });

    allocator_policy_module.addImport("abi_bindings", abi_bindings_module);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_allocator_policy_bytes_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("abi_bindings", abi_bindings_module);
    contract_module.addImport("allocator_policy", allocator_policy_module);

    const contract_tests = b.addTest(.{
        .name = "phase3-abi-allocator-policy-bytes-contract",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-allocator-policy-bytes-contract",
        "Run the Phase 3 allocator policy ABI byte contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 3 allocator policy ABI byte contract");
    test_step.dependOn(contract_step);
}

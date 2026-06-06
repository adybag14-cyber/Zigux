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

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_allocator_policy_reserved_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings_module);
    root_module.addImport("allocator_policy", allocator_policy_module);

    const tests = b.addTest(.{
        .name = "phase3_abi_allocator_policy_reserved_contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase3-abi-allocator-policy-reserved-contract",
        "Run the Phase 3 ABI allocator-policy reserved-byte contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 3 ABI allocator-policy reserved-byte contract tests.",
    );
    test_step.dependOn(contract_step);
}

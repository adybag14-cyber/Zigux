const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const panic_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_module.addImport("abi_bindings", abi_bindings_module);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_panic_policy_bytes_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("abi_bindings", abi_bindings_module);
    contract_module.addImport("panic_policy", panic_policy_module);

    const contract_tests = b.addTest(.{
        .name = "phase3-abi-panic-policy-bytes-contract",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-panic-policy-bytes-contract",
        "Run the Phase 3 panic-policy ABI byte contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 3 panic-policy ABI byte contract");
    test_step.dependOn(contract_step);
}

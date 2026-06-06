const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "path to zigux/bindings/abi.zig",
    ) orelse "../bindings/abi.zig";
    const panic_policy_path = b.option(
        []const u8,
        "panic-policy-path",
        "path to zigux/helpers/panic_policy.zig",
    ) orelse "../helpers/panic_policy.zig";

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    const panic_policy_module = b.createModule(.{
        .root_source_file = b.path(panic_policy_path),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_module.addImport("abi_bindings", abi_bindings_module);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_panic_policy_status_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("abi_bindings", abi_bindings_module);
    contract_module.addImport("panic_policy_helpers", panic_policy_module);

    const contract_tests = b.addTest(.{
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-panic-policy-status-contract",
        "Run the Phase 3 ABI panic-policy status/action contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_contract_tests.step);
}

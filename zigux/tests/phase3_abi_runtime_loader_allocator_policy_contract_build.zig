const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const runtime_loader_contract_path = b.option(
        []const u8,
        "runtime-loader-contract-path",
        "Path to runtime_loader_contract.zig",
    ) orelse "../kernel/runtime_loader_contract.zig";
    const allocator_policy_path = b.option(
        []const u8,
        "allocator-policy-path",
        "Path to allocator_policy.zig",
    ) orelse "../helpers/allocator_policy.zig";
    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to abi.zig",
    ) orelse "../bindings/abi.zig";

    const runtime_loader_contract_module = b.createModule(.{
        .root_source_file = b.path(runtime_loader_contract_path),
        .target = target,
        .optimize = optimize,
    });
    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    const allocator_policy_module = b.createModule(.{
        .root_source_file = b.path(allocator_policy_path),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy_module.addImport("abi_bindings", abi_bindings_module);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_runtime_loader_allocator_policy_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("runtime_loader_contract", runtime_loader_contract_module);
    contract_module.addImport("allocator_policy", allocator_policy_module);

    const contract_tests = b.addTest(.{
        .name = "phase3-abi-runtime-loader-allocator-policy-contract-tests",
        .root_module = contract_module,
    });
    const run_contract = b.addRunArtifact(contract_tests);
    run_contract.setCwd(b.path("../.."));

    const contract_step = b.step(
        "phase3-abi-runtime-loader-allocator-policy-contract",
        "Run the Lane 26 runtime-loader allocator-policy ABI contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Lane 26 runtime-loader allocator-policy ABI contract");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}

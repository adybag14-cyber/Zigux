const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const runtime_loader_contract_path = b.option(
        []const u8,
        "runtime-loader-contract-path",
        "Path to the runtime loader contract module",
    ) orelse "../kernel/runtime_loader_contract.zig";

    const runtime_loader_contract_module = b.createModule(.{
        .root_source_file = b.path(runtime_loader_contract_path),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_runtime_loader_policy_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("runtime_loader_contract", runtime_loader_contract_module);

    const tests = b.addTest(.{
        .name = "phase3-abi-runtime-loader-policy-contract",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-abi-runtime-loader-policy-contract",
        "Run the Phase 3 ABI runtime loader policy contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI runtime loader policy contract");
    test_step.dependOn(&run_tests.step);
}

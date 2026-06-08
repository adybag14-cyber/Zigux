const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const runtime_loader_path = b.option(
        []const u8,
        "runtime-loader-contract-path",
        "path to zigux/kernel/runtime_loader_contract.zig",
    ) orelse "../kernel/runtime_loader_contract.zig";

    const runtime_loader_module = b.createModule(.{
        .root_source_file = b.path(runtime_loader_path),
        .target = target,
        .optimize = optimize,
    });
    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_runtime_loader_field_boundary_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("runtime_loader_contract", runtime_loader_module);

    const contract_tests = b.addTest(.{
        .root_module = contract_module,
    });
    const run_contract = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-runtime-loader-field-boundary-contract",
        "Run the Phase 3 runtime-loader LoadPlan field-boundary ABI contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Phase 3 runtime-loader field-boundary contract");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}

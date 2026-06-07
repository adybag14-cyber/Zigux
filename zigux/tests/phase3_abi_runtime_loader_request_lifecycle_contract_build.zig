const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const runtime_loader_path = b.option(
        []const u8,
        "runtime-loader-path",
        "path to the runtime loader module under test",
    ) orelse "../kernel/runtime_loader.zig";
    const runtime_loader_contract_path = b.option(
        []const u8,
        "runtime-loader-contract-path",
        "path to the runtime loader contract module under test",
    ) orelse "../kernel/runtime_loader_contract.zig";

    const contract_module = b.createModule(.{
        .root_source_file = b.path(runtime_loader_contract_path),
        .target = target,
        .optimize = optimize,
    });
    const runtime_loader_module = b.createModule(.{
        .root_source_file = b.path(runtime_loader_path),
        .target = target,
        .optimize = optimize,
    });
    runtime_loader_module.addImport("runtime_loader_contract", contract_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_runtime_loader_request_lifecycle_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("runtime_loader", runtime_loader_module);

    const tests = b.addTest(.{
        .name = "phase3-abi-runtime-loader-request-lifecycle-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase3-abi-runtime-loader-request-lifecycle-contract",
        "Run the Phase 3 runtime-loader request lifecycle ABI contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 runtime-loader request lifecycle ABI contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}

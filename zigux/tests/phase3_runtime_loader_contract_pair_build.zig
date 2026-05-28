const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const runtime_loader_contract_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_loader_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_loader_module.addImport("runtime_loader_contract", runtime_loader_contract_module);

    const runtime_loader_contract_tests = b.addTest(.{
        .name = "phase3_runtime_loader_contract_pair_tests",
        .root_module = runtime_loader_contract_module,
    });

    const runtime_loader_tests = b.addTest(.{
        .name = "phase3_runtime_loader_pair_tests",
        .root_module = runtime_loader_module,
    });

    const run_runtime_loader_contract_tests = b.addRunArtifact(runtime_loader_contract_tests);
    const run_runtime_loader_tests = b.addRunArtifact(runtime_loader_tests);
    const test_step = b.step(
        "phase3-runtime-loader-contract-pair-test",
        "Run the focused Phase 3 runtime loader contract pair replay",
    );
    test_step.dependOn(&run_runtime_loader_contract_tests.step);
    test_step.dependOn(&run_runtime_loader_tests.step);
}

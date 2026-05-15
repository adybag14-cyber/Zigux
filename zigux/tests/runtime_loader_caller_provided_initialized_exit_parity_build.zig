const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

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

    const parity_tests_module = b.createModule(.{
        .root_source_file = b.path("runtime_loader_caller_provided_initialized_exit_parity.zig"),
        .target = target,
        .optimize = optimize,
    });
    parity_tests_module.addImport("runtime_loader", runtime_loader_module);

    const parity_tests = b.addTest(.{
        .root_module = parity_tests_module,
    });

    const run_parity_tests = b.addRunArtifact(parity_tests);
    const test_step = b.step(
        "test",
        "Run runtime loader caller-provided initialized exit parity tests",
    );
    test_step.dependOn(&run_parity_tests.step);
}

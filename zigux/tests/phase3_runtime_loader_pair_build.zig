const std = @import("std");

fn addRuntimeLoaderContractTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const runtime_loader_contract_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase3-runtime-loader-contract-module-test",
        .root_module = runtime_loader_contract_module,
    });

    return b.addRunArtifact(tests);
}

fn addRuntimeLoaderTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
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

    const tests = b.addTest(.{
        .name = "phase3-runtime-loader-module-test",
        .root_module = runtime_loader_module,
    });

    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const runtime_loader_contract_tests = addRuntimeLoaderContractTest(
        b,
        target,
        optimize,
    );
    const runtime_loader_tests = addRuntimeLoaderTest(
        b,
        target,
        optimize,
    );

    const runtime_loader_contract_step = b.step(
        "phase3-runtime-loader-contract-test",
        "Run the focused Phase 3 runtime-loader contract replay",
    );
    runtime_loader_contract_step.dependOn(&runtime_loader_contract_tests.step);

    const runtime_loader_step = b.step(
        "phase3-runtime-loader-test",
        "Run the focused Phase 3 runtime-loader replay",
    );
    runtime_loader_step.dependOn(&runtime_loader_tests.step);

    const runtime_loader_pair_step = b.step(
        "phase3-runtime-loader-pair-test",
        "Run the focused Phase 3 runtime-loader pair replay",
    );
    runtime_loader_pair_step.dependOn(&runtime_loader_contract_tests.step);
    runtime_loader_pair_step.dependOn(&runtime_loader_tests.step);
}

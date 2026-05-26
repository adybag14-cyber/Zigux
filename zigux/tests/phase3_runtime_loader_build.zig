const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const runtime_loader_contract = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_loader = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_loader.addImport("runtime_loader_contract", runtime_loader_contract);

    const tests = b.addTest(.{
        .name = "phase3-runtime-loader-test",
        .root_module = runtime_loader,
    });
    const run = b.addRunArtifact(tests);

    const runtime_loader_step = b.step(
        "phase3-runtime-loader-test",
        "Run the standalone Phase 3 runtime-loader helper tests",
    );
    runtime_loader_step.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the standalone Phase 3 runtime-loader helper tests",
    );
    test_step.dependOn(&run.step);
}

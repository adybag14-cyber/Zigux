const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const runtime_loader_contract = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_loader_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("../kernel/runtime_loader.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{
                    .name = "runtime_loader_contract",
                    .module = runtime_loader_contract,
                },
            },
        }),
        .name = "runtime_loader_tests",
    });

    const runtime_loader_contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
        .name = "runtime_loader_contract_tests",
    });

    const run_runtime_loader_tests = b.addRunArtifact(runtime_loader_tests);
    const run_runtime_loader_contract_tests = b.addRunArtifact(runtime_loader_contract_tests);

    const phase3_runtime_loader_test = b.step(
        "phase3-runtime-loader-test",
        "Run the standalone Phase 3 runtime loader contract replay.",
    );
    phase3_runtime_loader_test.dependOn(&run_runtime_loader_contract_tests.step);
    phase3_runtime_loader_test.dependOn(&run_runtime_loader_tests.step);
}

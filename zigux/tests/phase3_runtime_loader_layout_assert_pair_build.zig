const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const layout_assert_tests = b.addTest(.{
        .name = "phase3_layout_assert_pair_tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../helpers/layout_assert.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    layout_assert_tests.root_module.addImport("abi_bindings", abi_bindings);

    const runtime_loader_contract_tests = b.addTest(.{
        .name = "phase3_runtime_loader_contract_pair_tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_layout_assert_tests = b.addRunArtifact(layout_assert_tests);
    const run_runtime_loader_contract_tests = b.addRunArtifact(runtime_loader_contract_tests);

    const pair_test_step = b.step(
        "phase3-runtime-loader-layout-assert-pair-test",
        "Run the focused Phase 3 runtime-loader/layout-assert pair replay",
    );
    pair_test_step.dependOn(&run_layout_assert_tests.step);
    pair_test_step.dependOn(&run_runtime_loader_contract_tests.step);
}

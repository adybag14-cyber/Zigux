const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow.addImport("abi_bindings", abi_bindings);

    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy.addImport("abi_bindings", abi_bindings);
    unsafe_policy.addImport("narrow", narrow);

    const mmio_tests = b.addTest(.{
        .name = "phase3_mmio_pair_tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../helpers/mmio.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    mmio_tests.root_module.addImport("abi_bindings", abi_bindings);
    mmio_tests.root_module.addImport("narrow", narrow);
    mmio_tests.root_module.addImport("narrow_unsafe", narrow);
    mmio_tests.root_module.addImport("unsafe_policy", unsafe_policy);

    const runtime_loader_contract_tests = b.addTest(.{
        .name = "phase3_runtime_loader_contract_pair_tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_mmio_tests = b.addRunArtifact(mmio_tests);
    const run_runtime_loader_contract_tests = b.addRunArtifact(runtime_loader_contract_tests);

    const pair_test_step = b.step(
        "phase3-runtime-loader-mmio-pair-test",
        "Run the focused Phase 3 runtime-loader/MMIO pair replay",
    );
    pair_test_step.dependOn(&run_mmio_tests.step);
    pair_test_step.dependOn(&run_runtime_loader_contract_tests.step);
}

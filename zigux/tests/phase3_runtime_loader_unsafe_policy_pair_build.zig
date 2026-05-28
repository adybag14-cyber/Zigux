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

    const unsafe_policy_tests = b.addTest(.{
        .name = "phase3_unsafe_policy_pair_tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../helpers/unsafe_policy.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    unsafe_policy_tests.root_module.addImport("abi_bindings", abi_bindings);
    unsafe_policy_tests.root_module.addImport("narrow", narrow);

    const runtime_loader_contract_tests = b.addTest(.{
        .name = "phase3_runtime_loader_contract_pair_tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_unsafe_policy_tests = b.addRunArtifact(unsafe_policy_tests);
    const run_runtime_loader_contract_tests = b.addRunArtifact(runtime_loader_contract_tests);

    const pair_test_step = b.step(
        "phase3-runtime-loader-unsafe-policy-pair-test",
        "Run the focused Phase 3 runtime-loader/unsafe-policy pair replay",
    );
    pair_test_step.dependOn(&run_unsafe_policy_tests.step);
    pair_test_step.dependOn(&run_runtime_loader_contract_tests.step);
}

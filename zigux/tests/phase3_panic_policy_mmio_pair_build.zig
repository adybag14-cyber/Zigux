const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy.addImport("abi_bindings", abi_bindings);

    const panic_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy.addImport("abi_bindings", abi_bindings);

    const mmio = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio.addImport("abi_bindings", abi_bindings);
    mmio.addImport("unsafe_policy", unsafe_policy);
    mmio.addImport("narrow_unsafe", unsafe_policy);

    const panic_policy_tests = b.addTest(.{
        .name = "phase3_panic_policy_pair_tests",
        .root_module = panic_policy,
    });
    const mmio_tests = b.addTest(.{
        .name = "phase3_mmio_pair_tests",
        .root_module = mmio,
    });

    const panic_policy_run = b.addRunArtifact(panic_policy_tests);
    const mmio_run = b.addRunArtifact(mmio_tests);

    const pair_step = b.step(
        "phase3-panic-policy-mmio-pair-test",
        "Run the Phase 3 panic_policy and MMIO helper packets together.",
    );
    pair_step.dependOn(&panic_policy_run.step);
    pair_step.dependOn(&mmio_run.step);
}

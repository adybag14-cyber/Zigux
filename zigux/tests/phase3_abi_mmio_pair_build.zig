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

    const mmio = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio.addImport("abi_bindings", abi_bindings);
    mmio.addImport("unsafe_policy", unsafe_policy);
    mmio.addImport("narrow_unsafe", unsafe_policy);

    const abi_tests = b.addTest(.{
        .name = "phase3_abi_pair_tests",
        .root_module = abi_bindings,
    });
    const mmio_tests = b.addTest(.{
        .name = "phase3_mmio_pair_tests",
        .root_module = mmio,
    });

    const abi_run = b.addRunArtifact(abi_tests);
    const mmio_run = b.addRunArtifact(mmio_tests);

    const pair_step = b.step(
        "phase3-abi-mmio-pair-test",
        "Run the focused Phase 3 ABI bindings and MMIO helper pair replay.",
    );
    pair_step.dependOn(&abi_run.step);
    pair_step.dependOn(&mmio_run.step);
}

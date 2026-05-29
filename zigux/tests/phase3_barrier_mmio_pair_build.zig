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

    const barrier = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });

    const mmio = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio.addImport("abi_bindings", abi_bindings);
    mmio.addImport("unsafe_policy", unsafe_policy);
    mmio.addImport("narrow_unsafe", unsafe_policy);

    const barrier_tests = b.addTest(.{
        .name = "phase3_barrier_pair_tests",
        .root_module = barrier,
    });
    const mmio_tests = b.addTest(.{
        .name = "phase3_mmio_pair_tests",
        .root_module = mmio,
    });

    const barrier_run = b.addRunArtifact(barrier_tests);
    const mmio_run = b.addRunArtifact(mmio_tests);

    const pair_step = b.step(
        "phase3-barrier-mmio-pair-test",
        "Run the Phase 3 barrier and MMIO helper packets together.",
    );
    pair_step.dependOn(&barrier_run.step);
    pair_step.dependOn(&mmio_run.step);
}

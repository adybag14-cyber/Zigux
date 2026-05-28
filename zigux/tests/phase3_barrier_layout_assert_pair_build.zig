const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const barrier = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });
    const layout_assert = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert.addImport("abi_bindings", abi_bindings);

    const barrier_tests = b.addTest(.{
        .name = "phase3_barrier_pair_tests",
        .root_module = barrier,
    });
    const layout_assert_tests = b.addTest(.{
        .name = "phase3_layout_assert_pair_tests",
        .root_module = layout_assert,
    });

    const barrier_run = b.addRunArtifact(barrier_tests);
    const layout_assert_run = b.addRunArtifact(layout_assert_tests);

    const pair_step = b.step(
        "phase3-barrier-layout-assert-pair-test",
        "Run the Phase 3 barrier and layout_assert helper packets together.",
    );
    pair_step.dependOn(&barrier_run.step);
    pair_step.dependOn(&layout_assert_run.step);
}

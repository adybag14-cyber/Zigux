const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const atomic = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });

    const layout_assert = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert.addImport("abi_bindings", abi_bindings);

    const atomic_tests = b.addTest(.{
        .name = "phase3_atomic_pair_tests",
        .root_module = atomic,
    });
    const layout_assert_tests = b.addTest(.{
        .name = "phase3_layout_assert_pair_tests",
        .root_module = layout_assert,
    });

    const atomic_run = b.addRunArtifact(atomic_tests);
    const layout_assert_run = b.addRunArtifact(layout_assert_tests);

    const pair_step = b.step(
        "phase3-atomic-layout-assert-pair-test",
        "Run the Phase 3 atomic and layout assertion helper packets together.",
    );
    pair_step.dependOn(&atomic_run.step);
    pair_step.dependOn(&layout_assert_run.step);
}

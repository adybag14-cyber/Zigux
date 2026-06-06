const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_module = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cpumask_module = b.createModule(.{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpumask_module.addImport("bitmap_view", bitmap_module);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_bitmap_cpumask_boundary_collapse_replay.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("bitmap_view", bitmap_module);
    tests.root_module.addImport("cpumask_view", cpumask_module);

    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step(
        "phase3-bitmap-cpumask-boundary-collapse-replay",
        "Run the Phase 3 bitmap/cpumask boundary-collapse replay",
    );
    test_step.dependOn(&run_tests.step);

    const alias_step = b.step("test", "Run this standalone Phase 3 bitmap/cpumask replay");
    alias_step.dependOn(&run_tests.step);
}

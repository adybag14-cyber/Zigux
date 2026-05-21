const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_mod = b.addModule("bitmap_view", .{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cpumask_mod = b.addModule("cpumask_view", .{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpumask_mod.addImport("bitmap_view", bitmap_mod);

    const test_mod = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_bookend_gap_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_mod.addImport("bitmap_view", bitmap_mod);
    test_mod.addImport("cpumask_view", cpumask_mod);

    const tests = b.addTest(.{
        .root_module = test_mod,
    });

    const run_tests = b.addRunArtifact(tests);

    const step = b.step(
        "phase3-bitmap-cpumask-bookend-gap-replay",
        "Run the Phase 3 bitmap/cpumask bookend-gap replay.",
    );
    step.dependOn(&run_tests.step);
}

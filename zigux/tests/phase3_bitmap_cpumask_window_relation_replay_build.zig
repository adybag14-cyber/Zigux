const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cpumask_view = b.createModule(.{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpumask_view.addImport("bitmap_view", bitmap_view);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_window_relation_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap_view", bitmap_view);
    root_module.addImport("cpumask_view", cpumask_view);

    const tests = b.addTest(.{
        .name = "phase3-bitmap-cpumask-window-relation-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const replay = b.step(
        "phase3-bitmap-cpumask-window-relation-replay",
        "Run the Lane 27 bitmap/cpumask window relation replay.",
    );
    replay.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the Lane 27 bitmap/cpumask window relation replay tests.",
    );
    test_step.dependOn(&run.step);
}

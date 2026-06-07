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

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_braid_checkpoint_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("bitmap_view", bitmap_view);
    replay_module.addImport("cpumask_view", cpumask_view);

    const replay_tests = b.addTest(.{
        .root_module = replay_module,
    });

    const run_tests = b.addRunArtifact(replay_tests);

    const named = b.step("phase3-bitmap-cpumask-braid-checkpoint-replay", "Run the Lane 27 bitmap/cpumask braid checkpoint replay");
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 27 bitmap/cpumask braid checkpoint replay");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}

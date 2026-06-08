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

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_foldback_delta_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("bitmap_view", bitmap_module);
    replay_module.addImport("cpumask_view", cpumask_module);

    const replay_tests = b.addTest(.{
        .root_module = replay_module,
    });
    const run_replay = b.addRunArtifact(replay_tests);

    const named = b.step("phase3-bitmap-cpumask-foldback-delta-replay", "Run the Phase 3 bitmap/cpumask foldback delta replay");
    named.dependOn(&run_replay.step);

    const test_step = b.step("test", "Run the Phase 3 bitmap/cpumask foldback delta replay");
    test_step.dependOn(&run_replay.step);

    b.default_step.dependOn(&run_replay.step);
}

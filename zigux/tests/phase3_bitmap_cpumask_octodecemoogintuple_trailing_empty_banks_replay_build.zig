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
        .root_source_file = b.path("phase3_bitmap_cpumask_octodecemoogintuple_trailing_empty_banks_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("bitmap_view", bitmap_module);
    replay_module.addImport("cpumask_view", cpumask_module);

    const replay_tests = b.addTest(.{
        .name = "phase3-bitmap-cpumask-octodecemoogintuple-trailing-empty-banks-replay-tests",
        .root_module = replay_module,
    });

    const run_replay_tests = b.addRunArtifact(replay_tests);

    const replay_step = b.step(
        "phase3-bitmap-cpumask-octodecemoogintuple-trailing-empty-banks-replay",
        "Run the Phase 3 bitmap/cpumask octodecemoogintuple trailing-empty-banks replay.",
    );
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the focused Phase 3 bitmap/cpumask octodecemoogintuple replay tests.");
    test_step.dependOn(&run_replay_tests.step);

    b.default_step.dependOn(test_step);
}

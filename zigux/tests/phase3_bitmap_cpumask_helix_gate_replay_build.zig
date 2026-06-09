const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_view_mod = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cpumask_view_mod = b.createModule(.{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpumask_view_mod.addImport("bitmap_view", bitmap_view_mod);

    const replay_mod = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_helix_gate_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_mod.addImport("bitmap_view", bitmap_view_mod);
    replay_mod.addImport("cpumask_view", cpumask_view_mod);

    const tests = b.addTest(.{
        .root_module = replay_mod,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase3-bitmap-cpumask-helix-gate-replay",
        "Run the Lane 27 helix-gate bitmap/cpumask replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 27 helix-gate replay tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}

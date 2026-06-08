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

    const test_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_zigzag_handoff_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("bitmap_view", bitmap_view);
    test_module.addImport("cpumask_view", cpumask_view);

    const tests = b.addTest(.{
        .root_module = test_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const named_step = b.step("phase3-bitmap-cpumask-zigzag-handoff-replay", "Run the Lane 27 bitmap/cpumask zigzag handoff replay");
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 27 bitmap/cpumask zigzag handoff replay");
    test_step.dependOn(named_step);

    b.default_step.dependOn(test_step);
}

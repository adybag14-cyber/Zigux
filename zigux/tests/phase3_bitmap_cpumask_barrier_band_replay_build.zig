const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_barrier_band_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
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
    root_module.addImport("bitmap_view", bitmap_view);
    root_module.addImport("cpumask_view", cpumask_view);

    const tests = b.addTest(.{
        .name = "phase3-bitmap-cpumask-barrier-band-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const named_step = b.step("phase3-bitmap-cpumask-barrier-band-replay", "Run the Phase 3 bitmap/cpumask barrier-band replay");
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 bitmap/cpumask barrier-band replay");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}

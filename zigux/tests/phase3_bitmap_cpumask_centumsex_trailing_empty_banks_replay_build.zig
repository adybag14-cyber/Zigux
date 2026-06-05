const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cpumask_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpumask_view_module.addImport("bitmap_view", bitmap_view_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_centumsex_trailing_empty_banks_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap_view", bitmap_view_module);
    root_module.addImport("cpumask_view", cpumask_view_module);

    const tests = b.addTest(.{
        .name = "phase3-bitmap-cpumask-centumsex-trailing-empty-banks-replay",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const replay_step = b.step(
        "phase3-bitmap-cpumask-centumsex-trailing-empty-banks-replay",
        "Run the Lane 27 centumsex trailing-empty-banks replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 27 centumsex replay test alias");
    test_step.dependOn(&run_tests.step);
}

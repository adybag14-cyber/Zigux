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
        .root_source_file = b.path("phase3_bitmap_cpumask_partial_tail_double_bank_empty_valid_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap_view", bitmap_view_module);
    root_module.addImport("cpumask_view", cpumask_view_module);

    const tests = b.addTest(.{
        .name = "phase3-bitmap-cpumask-partial-tail-double-bank-empty-valid-replay",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase3-bitmap-cpumask-partial-tail-double-bank-empty-valid-replay",
        "Run the focused Phase 3 bitmap/cpumask double-bank empty-valid replay",
    );
    test_step.dependOn(&run_tests.step);
}

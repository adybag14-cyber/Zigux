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

    const test_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_pivot_ladder_exchange_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("bitmap_view", bitmap_module);
    test_module.addImport("cpumask_view", cpumask_module);

    const tests = b.addTest(.{
        .root_module = test_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step(
        "phase3-bitmap-cpumask-pivot-ladder-exchange-replay",
        "Run the Phase 3 bitmap/cpumask pivot ladder exchange replay",
    );
    test_step.dependOn(&run_tests.step);

    const default_test_step = b.step("test", "Run the Phase 3 bitmap/cpumask pivot ladder exchange replay");
    default_test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}

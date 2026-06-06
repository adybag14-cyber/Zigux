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

    const tests_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_symmetric_difference_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    tests_module.addImport("bitmap_view", bitmap_module);
    tests_module.addImport("cpumask_view", cpumask_module);

    const unit_tests = b.addTest(.{
        .root_module = tests_module,
    });
    const run_tests = b.addRunArtifact(unit_tests);

    const route = b.step(
        "phase3-bitmap-cpumask-symmetric-difference-replay",
        "Run the Phase 3 bitmap/cpumask symmetric difference replay",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 bitmap/cpumask symmetric difference replay");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(test_step);
}

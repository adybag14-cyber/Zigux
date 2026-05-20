const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_three_cluster_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_module = b.createModule(.{
        .root_source_file = b.path("bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cpumask_module = b.createModule(.{
        .root_source_file = b.path("cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpumask_module.addImport("bitmap_view", bitmap_module);
    root_module.addImport("bitmap_view", bitmap_module);
    root_module.addImport("cpumask_view", cpumask_module);

    const tests = b.addTest(.{
        .name = "phase3-bitmap-cpumask-three-cluster-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const step = b.step(
        "phase3-bitmap-cpumask-three-cluster-replay",
        "Run the standalone Lane 27 three-cluster bitmap/cpumask replay",
    );
    step.dependOn(&run_tests.step);
}

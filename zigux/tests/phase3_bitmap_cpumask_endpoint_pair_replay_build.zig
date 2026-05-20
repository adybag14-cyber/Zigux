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

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_endpoint_pair_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap_view", bitmap_module);
    root_module.addImport("cpumask_view", cpumask_module);

    const tests = b.addTest(.{
        .name = "phase3-bitmap-cpumask-endpoint-pair-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase3-bitmap-cpumask-endpoint-pair-replay",
        "Run the Lane 27 endpoint-pair bitmap/cpumask replay",
    );
    step.dependOn(&run.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const devres = b.createModule(.{
        .root_source_file = b.path("../../lib/devres.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase13_devres_dmam_alloc_zero_size_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("devres", devres);

    const tests = b.addTest(.{
        .name = "phase13-devres-dmam-alloc-zero-size-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);
    const step = b.step(
        "phase13-devres-dmam-alloc-zero-size-replay",
        "Run the Phase 13 devres zero-size replay",
    );
    step.dependOn(&run.step);
}

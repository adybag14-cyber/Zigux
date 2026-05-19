const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_slab_reclaim_edges.zig"),
        .target = target,
        .optimize = optimize,
    });
    const slab_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("slab", slab_module);

    const tests = b.addTest(.{
        .name = "phase1-slab-reclaim-edges",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-slab-reclaim-edges",
        "Run the focused Phase 1 slab replay from zigux/tests",
    );
    replay_step.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the focused Phase 1 slab replay from zigux/tests",
    );
    test_step.dependOn(&run.step);
}

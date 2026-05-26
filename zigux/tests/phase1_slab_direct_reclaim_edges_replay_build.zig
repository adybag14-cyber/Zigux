const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_slab_direct_reclaim_edges_replay.zig"),
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
        .name = "phase1-slab-direct-reclaim-edges-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-slab-direct-reclaim-edges-replay",
        "Run the standalone Lane 07 slab direct-reclaim edge replay",
    );
    replay_step.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the standalone Lane 07 slab direct-reclaim edge replay",
    );
    test_step.dependOn(&run.step);
}

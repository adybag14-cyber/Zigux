const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_rbtree_cached_reseed_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("rbtree", rbtree_module);

    const unit_tests = b.addTest(.{
        .name = "phase1-rbtree-cached-reseed-replay",
        .root_module = root_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const replay_step = b.step(
        "phase1-rbtree-cached-reseed-replay",
        "Run the Lane 06 cached-root reseed replay",
    );
    replay_step.dependOn(&run_unit_tests.step);
}

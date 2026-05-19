const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const rbtree_dep = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_rbtree_cached_match_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "rbtree", .module = rbtree_dep },
            },
        }),
    });

    const run_replay_tests = b.addRunArtifact(replay_tests);
    const replay_step = b.step(
        "phase1-rbtree-cached-match-replay",
        "Run the Lane 06 Phase 1 rbtree cached-match replay tests",
    );
    replay_step.dependOn(&run_replay_tests.step);
}

const std = @import("std");

fn addReplayTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const list_view = b.createModule(.{
        .root_source_file = b.path("../helpers/list_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hlist_view = b.createModule(.{
        .root_source_file = b.path("../helpers/hlist_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_cross_fold_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_view", list_view);
    root_module.addImport("hlist_view", hlist_view);

    const tests = b.addTest(.{
        .name = "phase3-list-hlist-cross-fold-replay",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const replay = addReplayTest(b, target, optimize);

    const replay_step = b.step(
        "phase3-list-hlist-cross-fold-replay",
        "Run the Lane 28 Phase 3 list/hlist cross-fold replay.",
    );
    replay_step.dependOn(&replay.step);

    const test_step = b.step(
        "test",
        "Run the Lane 28 Phase 3 list/hlist cross-fold replay tests.",
    );
    test_step.dependOn(&replay.step);
}

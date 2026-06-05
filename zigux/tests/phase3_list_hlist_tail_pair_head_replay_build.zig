const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_tail_pair_head_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("list_view", list_view);
    replay_module.addImport("hlist_view", hlist_view);

    const tests = b.addTest(.{
        .name = "phase3-list-hlist-tail-pair-head-replay-tests",
        .root_module = replay_module,
    });

    const run = b.addRunArtifact(tests);
    const replay_step = b.step(
        "phase3-list-hlist-tail-pair-head-replay",
        "Run the Lane 28 list/hlist tail-pair head replay",
    );
    replay_step.dependOn(&run.step);

    const test_step = b.step("test", "Run the Lane 28 list/hlist tail-pair head replay tests");
    test_step.dependOn(&run.step);
}

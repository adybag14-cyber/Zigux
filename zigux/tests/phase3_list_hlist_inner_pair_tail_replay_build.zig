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
        .root_source_file = b.path("phase3_list_hlist_inner_pair_tail_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("list_view", list_view);
    replay_module.addImport("hlist_view", hlist_view);

    const replay_tests = b.addTest(.{
        .name = "phase3-list-hlist-inner-pair-tail-replay",
        .root_module = replay_module,
    });

    const run_replay = b.addRunArtifact(replay_tests);
    const replay_step = b.step("phase3-list-hlist-inner-pair-tail-replay", "Run the Phase 3 list/hlist inner-pair tail replay");
    replay_step.dependOn(&run_replay.step);

    const test_step = b.step("test", "Run the Phase 3 list/hlist inner-pair tail replay");
    test_step.dependOn(&run_replay.step);
}

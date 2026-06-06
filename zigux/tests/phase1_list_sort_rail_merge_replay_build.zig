const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_root_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_rail_merge_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root_module.addImport("list_sort", list_sort_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-list-sort-rail-merge-replay-tests",
        .root_module = replay_root_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);
    run_replay_tests.setCwd(b.path("../.."));

    const replay_step = b.step("phase1-list-sort-rail-merge-replay", "Run the Phase 1 list_sort rail merge replay");
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the Phase 1 list_sort rail merge replay");
    test_step.dependOn(&run_replay_tests.step);
}

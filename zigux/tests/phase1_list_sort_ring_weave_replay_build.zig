const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_sort = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_ring_weave_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("list_sort", list_sort);

    const replay = b.addTest(.{
        .name = "phase1-list-sort-ring-weave-replay",
        .root_module = replay_module,
    });

    const run_replay = b.addRunArtifact(replay);
    const replay_step = b.step("phase1-list-sort-ring-weave-replay", "Run the Lane 12 list_sort ring-weave replay");
    replay_step.dependOn(&run_replay.step);

    const test_step = b.step("test", "Run Lane 12 list_sort ring-weave replay tests");
    test_step.dependOn(&run_replay.step);
}

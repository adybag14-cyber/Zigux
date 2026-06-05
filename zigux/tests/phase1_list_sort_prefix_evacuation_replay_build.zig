const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_prefix_evacuation_replay.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "list_sort", .module = list_sort_module },
        },
    });

    const replay_tests = b.addTest(.{ .root_module = replay_module });
    const run_replay = b.addRunArtifact(replay_tests);

    const replay_step = b.step(
        "phase1-list-sort-prefix-evacuation-replay",
        "Run the Phase 1 list_sort prefix evacuation replay",
    );
    replay_step.dependOn(&run_replay.step);

    const test_step = b.step("test", "Run the Phase 1 list_sort prefix evacuation replay tests");
    test_step.dependOn(&run_replay.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const list_sort = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_nested_staging_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_sort", list_sort);

    const replay = b.addTest(.{
        .name = "phase1-list-sort-nested-staging-replay",
        .root_module = root_module,
    });

    const run_replay = b.addRunArtifact(replay);
    const replay_step = b.step("phase1-list-sort-nested-staging-replay", "Run the Lane 12 nested staging list_sort replay");
    replay_step.dependOn(&run_replay.step);

    const test_step = b.step("test", "Run the Lane 12 nested staging list_sort replay");
    test_step.dependOn(&run_replay.step);
}

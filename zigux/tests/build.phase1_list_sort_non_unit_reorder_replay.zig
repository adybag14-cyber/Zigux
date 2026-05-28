const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });
    const replay_root = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_non_unit_reorder_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root.addImport("list_sort", list_sort_module);

    const tests = b.addTest(.{
        .name = "phase1-list-sort-non-unit-reorder-replay",
        .root_module = replay_root,
    });
    const run_tests = b.addRunArtifact(tests);
    const step = b.step(
        "phase1-list-sort-non-unit-reorder-replay",
        "Run the Lane 12 non-unit reorder list_sort replay",
    );
    step.dependOn(&run_tests.step);
}

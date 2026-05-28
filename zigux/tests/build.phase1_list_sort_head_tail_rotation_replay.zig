const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_head_tail_rotation_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_sort", list_sort_module);

    const tests = b.addTest(.{
        .name = "phase1-list-sort-head-tail-rotation-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-list-sort-head-tail-rotation-replay",
        "Run the Lane 12 head-tail rotation list_sort replay",
    );
    replay_step.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the Lane 12 head-tail rotation list_sort replay",
    );
    test_step.dependOn(&run.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_non_unit_context_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_sort", list_sort_module);

    const tests = b.addTest(.{
        .name = "phase1-list-sort-non-unit-context-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-list-sort-non-unit-context-replay",
        "Run the standalone Phase 1 list_sort non-unit comparator-context replay",
    );
    replay_step.dependOn(&run.step);
}

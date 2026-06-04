const std = @import("std");

fn addReplay(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_priority_context_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_sort", list_sort_module);

    const tests = b.addTest(.{
        .name = "phase1-list-sort-priority-context-replay",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const replay = addReplay(b, target, optimize);

    const replay_step = b.step(
        "phase1-list-sort-priority-context-replay",
        "Run the Lane 12 Phase 1 list_sort priority-context replay",
    );
    replay_step.dependOn(&replay.step);

    const test_step = b.step(
        "test",
        "Run the Lane 12 Phase 1 list_sort priority-context replay",
    );
    test_step.dependOn(&replay.step);
}

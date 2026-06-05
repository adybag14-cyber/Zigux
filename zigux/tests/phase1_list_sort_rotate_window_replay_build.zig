const std = @import("std");

fn addRotateWindowReplay(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_rotate_window_replay.zig"),
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
        .name = "phase1-list-sort-rotate-window-replay",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const replay = addRotateWindowReplay(b, target, optimize);
    const replay_step = b.step(
        "phase1-list-sort-rotate-window-replay",
        "Run the Phase 1 list_sort rotate-window replay",
    );
    replay_step.dependOn(&replay.step);

    const test_step = b.step("test", "Run the Phase 1 list_sort rotate-window replay tests");
    test_step.dependOn(&replay.step);
}

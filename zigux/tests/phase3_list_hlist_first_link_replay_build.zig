const std = @import("std");

fn addFirstLinkReplay(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const list_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/list_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hlist_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/hlist_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_first_link_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_view", list_view_module);
    root_module.addImport("hlist_view", hlist_view_module);

    const tests = b.addTest(.{
        .name = "phase3-list-hlist-first-link-replay",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const replay = addFirstLinkReplay(b, target, optimize);
    const replay_step = b.step("phase3-list-hlist-first-link-replay", "Run the Phase 3 list/hlist first-link replay");
    replay_step.dependOn(&replay.step);

    const test_step = b.step("test", "Run the Phase 3 list/hlist first-link replay");
    test_step.dependOn(&replay.step);
}

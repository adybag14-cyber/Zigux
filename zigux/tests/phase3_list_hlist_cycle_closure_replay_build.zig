const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_view_mod = b.createModule(.{
        .root_source_file = b.path("../helpers/list_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hlist_view_mod = b.createModule(.{
        .root_source_file = b.path("../helpers/hlist_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const replay_mod = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_cycle_closure_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_mod.addImport("list_view", list_view_mod);
    replay_mod.addImport("hlist_view", hlist_view_mod);

    const tests = b.addTest(.{ .root_module = replay_mod });
    const run_tests = b.addRunArtifact(tests);
    if (b.args) |args| {
        run_tests.addArgs(args);
    }

    const replay_step = b.step("phase3-list-hlist-cycle-closure-replay", "Run the Phase 3 list/hlist cycle closure replay");
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 list/hlist cycle closure replay");
    test_step.dependOn(&run_tests.step);
}

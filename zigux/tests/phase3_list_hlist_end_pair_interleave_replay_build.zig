const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_end_pair_interleave_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
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
    root_module.addImport("list_view", list_view_module);
    root_module.addImport("hlist_view", hlist_view_module);

    const tests = b.addTest(.{
        .name = "phase3-list-hlist-end-pair-interleave-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step("phase3-list-hlist-end-pair-interleave-replay", "Run Phase 3 list/hlist end-pair interleave replay");
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Phase 3 list/hlist end-pair interleave replay tests");
    test_step.dependOn(&run_tests.step);
}

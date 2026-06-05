const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_view = b.createModule(.{
        .root_source_file = b.path("../helpers/list_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hlist_view = b.createModule(.{
        .root_source_file = b.path("../helpers/hlist_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_head_transplant_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root.addImport("list_view", list_view);
    root.addImport("hlist_view", hlist_view);

    const tests = b.addTest(.{ .root_module = root });
    const run_tests = b.addRunArtifact(tests);

    const named = b.step("phase3-list-hlist-head-transplant-replay", "Run Lane 28 head transplant replay");
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 28 head transplant replay");
    test_step.dependOn(&run_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_list_hlist_inner_block_front_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "list_view", .module = list_view_module },
                .{ .name = "hlist_view", .module = hlist_view_module },
            },
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const replay_step = b.step(
        "phase3-list-hlist-inner-block-front-replay",
        "Run Lane 28 Phase 3 list/hlist inner-block front replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 28 Phase 3 list/hlist inner-block front replay tests");
    test_step.dependOn(&run_tests.step);
}

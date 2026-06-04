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

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_list_hlist_middle_excision_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "list_view", .module = list_view_mod },
                .{ .name = "hlist_view", .module = hlist_view_mod },
            },
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase3-list-hlist-middle-excision-replay",
        "Run the Phase 3 list/hlist middle-excision replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 list/hlist middle-excision replay");
    test_step.dependOn(&run_tests.step);
}

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
    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_hexatetraconta_bridge_braid_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("list_view", list_view_module);
    replay_module.addImport("hlist_view", hlist_view_module);

    const replay_tests = b.addTest(.{
        .root_module = replay_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);

    const replay_step = b.step(
        "phase3-list-hlist-hexatetraconta-bridge-braid-replay",
        "Run the Lane 28 Phase 3 list/hlist hexatetraconta bridge-braid replay.",
    );
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 28 Phase 3 list/hlist hexatetraconta bridge-braid replay tests.",
    );
    test_step.dependOn(&run_replay_tests.step);
    b.default_step.dependOn(&run_replay_tests.step);
}

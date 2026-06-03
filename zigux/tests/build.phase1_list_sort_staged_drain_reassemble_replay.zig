const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const replay_root_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_staged_drain_reassemble_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root_module.addImport("list_sort", list_sort_module);

    const replay_tests = b.addTest(.{
        .root_module = replay_root_module,
    });

    const run_replay_tests = b.addRunArtifact(replay_tests);
    const replay_step = b.step(
        "phase1-list-sort-staged-drain-reassemble-replay",
        "Run the Phase 1 list_sort staged drain reassemble replay",
    );
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the Phase 1 list_sort staged drain reassemble replay tests");
    test_step.dependOn(&run_replay_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_tail_splice_bucket_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("list_sort", list_sort_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-list-sort-tail-splice-bucket-replay-tests",
        .root_module = replay_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);
    run_replay_tests.setCwd(b.path("../.."));

    const replay_step = b.step(
        "phase1-list-sort-tail-splice-bucket-replay",
        "Run the Phase 1 list_sort tail-splice bucket replay",
    );
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the Phase 1 list_sort tail-splice bucket replay");
    test_step.dependOn(replay_step);
}

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
        .root_source_file = b.path("phase1_list_sort_tail_drain_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("list_sort", list_sort_module);

    const tests = b.addTest(.{
        .name = "phase1-list-sort-tail-drain-replay-tests",
        .root_module = replay_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-list-sort-tail-drain-replay",
        "Run the Lane 12 list_sort tail-drain replay.",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 12 list_sort tail-drain replay tests.",
    );
    test_step.dependOn(&run_tests.step);
}

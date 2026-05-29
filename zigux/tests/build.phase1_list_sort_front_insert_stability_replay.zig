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
        .root_source_file = b.path("phase1_list_sort_front_insert_stability_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("list_sort", list_sort_module);

    const tests = b.addTest(.{
        .name = "phase1-list-sort-front-insert-stability-replay",
        .root_module = replay_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const replay_step = b.step("phase1-list-sort-front-insert-stability-replay", "Run the Phase 1 list_sort front-insert stability replay");
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 list_sort front-insert stability replay");
    test_step.dependOn(&run_tests.step);
}

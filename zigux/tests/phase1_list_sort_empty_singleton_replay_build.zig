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
        .root_source_file = b.path("phase1_list_sort_empty_singleton_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("list_sort", list_sort_module);

    const tests = b.addTest(.{
        .name = "phase1-list-sort-empty-singleton-replay",
        .root_module = replay_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const replay_step = b.step(
        "phase1-list-sort-empty-singleton-replay",
        "Run the Phase 1 list_sort empty/singleton replay.",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Phase 1 list_sort empty/singleton replay.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}

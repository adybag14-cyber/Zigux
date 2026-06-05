const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_sort_module = b.addModule("list_sort", .{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
    });

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_even_odd_roundtrip_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("list_sort", list_sort_module);

    const replay_tests = b.addTest(.{
        .root_module = replay_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);

    const replay_step = b.step(
        "phase1-list-sort-even-odd-roundtrip-replay",
        "Run the Phase 1 list_sort even/odd roundtrip replay",
    );
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the Phase 1 list_sort even/odd roundtrip replay");
    test_step.dependOn(&run_replay_tests.step);
}

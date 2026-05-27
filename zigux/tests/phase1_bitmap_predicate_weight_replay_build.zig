const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_module.addImport("find_bit", find_bit_module);

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_bitmap_predicate_weight_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("bitmap", bitmap_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-bitmap-predicate-weight-replay",
        .root_module = replay_module,
    });

    const run_replay = b.addRunArtifact(replay_tests);
    const replay_step = b.step(
        "phase1-bitmap-predicate-weight-replay",
        "Run the standalone Phase 1 bitmap predicate and weight replay",
    );
    replay_step.dependOn(&run_replay.step);

    const test_step = b.step("test", "Run the standalone Phase 1 bitmap predicate and weight replay");
    test_step.dependOn(&run_replay.step);
}

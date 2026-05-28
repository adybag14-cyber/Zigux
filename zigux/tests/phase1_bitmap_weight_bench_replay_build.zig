const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{ .preferred_optimize_mode = .ReleaseSafe });

    const find_bit_module = b.addModule("find_bit", .{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });

    const bitmap_module = b.addModule("bitmap", .{
        .root_source_file = b.path("../../tools/lib/bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_module.addImport("find_bit", find_bit_module);

    const replay_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_bitmap_weight_bench_replay.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    replay_tests.root_module.addImport("bitmap", bitmap_module);
    replay_tests.root_module.addImport("find_bit", find_bit_module);

    const run_replay_tests = b.addRunArtifact(replay_tests);

    const replay_step = b.step("phase1-bitmap-weight-bench-replay", "Run the Phase 1 bitmap.weight bench replay");
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the Phase 1 bitmap.weight bench replay");
    test_step.dependOn(&run_replay_tests.step);
}

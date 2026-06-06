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
        .root_source_file = b.path("phase1_bitmap_window_tail_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("bitmap", bitmap_module);
    replay_module.addImport("find_bit", find_bit_module);

    const tests = b.addTest(.{
        .name = "phase1-bitmap-window-tail-replay",
        .root_module = replay_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step("phase1-bitmap-window-tail-replay", "Run Phase 1 bitmap window tail replay");
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Phase 1 bitmap window tail replay");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}

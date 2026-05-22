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

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_bitmap_weight_tail_window_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap", bitmap_module);

    const tests = b.addTest(.{
        .name = "phase1-bitmap-weight-tail-window-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-bitmap-weight-tail-window-replay",
        "Run the Phase 1 bitmap weighted-count and tail-window replay",
    );
    step.dependOn(&run.step);
}

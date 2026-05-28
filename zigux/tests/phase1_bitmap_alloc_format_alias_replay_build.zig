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
        .root_source_file = b.path("phase1_bitmap_alloc_format_alias_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap", bitmap_module);

    const tests = b.addTest(.{
        .name = "phase1-bitmap-alloc-format-alias-replay",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase1-bitmap-alloc-format-alias-replay",
        "Run the focused Phase 1 bitmap alloc-format alias replay",
    );
    test_step.dependOn(&run_tests.step);
}

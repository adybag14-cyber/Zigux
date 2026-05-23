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
        .root_source_file = b.path("phase1_bitmap_helper_smoke.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("find_bit", find_bit_module);
    root_module.addImport("bitmap", bitmap_module);

    const tests = b.addTest(.{
        .name = "phase1-bitmap-helper-smoke",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-bitmap-helper-smoke",
        "Run the standalone Phase 1 bitmap helper smoke shard",
    );
    step.dependOn(&run_tests.step);
}

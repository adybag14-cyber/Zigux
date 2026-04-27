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

    const diff_root = b.createModule(.{
        .root_source_file = b.path("bitmap_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    diff_root.addImport("bitmap", bitmap_module);
    diff_root.addImport("find_bit", find_bit_module);

    const diff_tests = b.addTest(.{
        .name = "phase1-bitmap-diff",
        .root_module = diff_root,
    });

    const run_diff_tests = b.addRunArtifact(diff_tests);
    const test_step = b.step("test", "Run focused bitmap diff checks");
    test_step.dependOn(&run_diff_tests.step);
}

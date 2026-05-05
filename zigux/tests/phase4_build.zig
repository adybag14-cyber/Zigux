const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const atomic_module = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_atomic64_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_atomic64.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_sample_module.addImport("atomic", atomic_module);
    const atomic64_diff_module = b.createModule(.{
        .root_source_file = b.path("atomic64_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    atomic64_diff_module.addImport("runtime_atomic64_sample", runtime_atomic64_sample_module);
    const bitmap_diff_module = b.createModule(.{
        .root_source_file = b.path("bitmap_diff.zig"),
        .target = target,
        .optimize = optimize,
    });

    const atomic64_diff_tests = b.addTest(.{
        .name = "phase4-runtime-atomic64-diff-tests",
        .root_module = atomic64_diff_module,
    });
    const run_atomic64_diff_tests = b.addRunArtifact(atomic64_diff_tests);

    const bitmap_diff_tests = b.addTest(.{
        .name = "phase4-bitmap-diff-tests",
        .root_module = bitmap_diff_module,
    });
    const run_bitmap_diff_tests = b.addRunArtifact(bitmap_diff_tests);

    const test_step = b.step("test", "Run Phase 4 differential validation tests");
    test_step.dependOn(&run_atomic64_diff_tests.step);
    test_step.dependOn(&run_bitmap_diff_tests.step);
}

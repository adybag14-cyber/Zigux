const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const atomic_module = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_atomic64_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_atomic64.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_sample_module.addImport("atomic", atomic_module);
    const runtime_bitmap_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_sample_module.addImport("bitmap_view", bitmap_view_module);
    const runtime_kretprobe_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_kretprobe.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_atomic64_diff_module = b.createModule(.{
        .root_source_file = b.path("runtime_atomic64_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_diff_module.addImport("runtime_atomic64_sample", runtime_atomic64_sample_module);
    const runtime_bitmap_diff_module = b.createModule(.{
        .root_source_file = b.path("runtime_bitmap_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_diff_module.addImport("runtime_bitmap_sample", runtime_bitmap_sample_module);
    const runtime_kretprobe_diff_module = b.createModule(.{
        .root_source_file = b.path("runtime_kretprobe_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_kretprobe_diff_module.addImport("runtime_kretprobe_sample", runtime_kretprobe_sample_module);

    const runtime_atomic64_diff_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-diff-tests",
        .root_module = runtime_atomic64_diff_module,
    });
    const run_runtime_atomic64_diff_tests = b.addRunArtifact(runtime_atomic64_diff_tests);
    const runtime_bitmap_diff_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-diff-tests",
        .root_module = runtime_bitmap_diff_module,
    });
    const run_runtime_bitmap_diff_tests = b.addRunArtifact(runtime_bitmap_diff_tests);
    const runtime_kretprobe_diff_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-diff-tests",
        .root_module = runtime_kretprobe_diff_module,
    });
    const run_runtime_kretprobe_diff_tests = b.addRunArtifact(runtime_kretprobe_diff_tests);

    const runtime_diff_step = b.step(
        "phase9-runtime-diff-test",
        "Run the focused Phase 9 runtime differential gates",
    );
    runtime_diff_step.dependOn(&run_runtime_atomic64_diff_tests.step);
    runtime_diff_step.dependOn(&run_runtime_bitmap_diff_tests.step);
    runtime_diff_step.dependOn(&run_runtime_kretprobe_diff_tests.step);

    const test_step = b.step("test", "Run the focused Phase 9 runtime differential gates");
    test_step.dependOn(runtime_diff_step);
    b.default_step.dependOn(test_step);
}

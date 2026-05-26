const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_bitmap_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_sample_module.addImport("bitmap_view", bitmap_view_module);

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

    const runtime_kretprobe_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_kretprobe.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_first_loadable_parity_behavior_module = b.createModule(.{
        .root_source_file = b.path("runtime_first_loadable_parity_behavior.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_first_loadable_parity_behavior_module.addImport(
        "runtime_atomic64_sample",
        runtime_atomic64_sample_module,
    );
    runtime_first_loadable_parity_behavior_module.addImport(
        "runtime_bitmap_sample",
        runtime_bitmap_sample_module,
    );
    runtime_first_loadable_parity_behavior_module.addImport(
        "runtime_kretprobe_sample",
        runtime_kretprobe_sample_module,
    );

    const runtime_first_loadable_parity_behavior_tests = b.addTest(.{
        .name = "phase9-first-loadable-runtime-module-parity-behavior-tests",
        .root_module = runtime_first_loadable_parity_behavior_module,
    });

    const run_runtime_first_loadable_parity_behavior_tests = b.addRunArtifact(
        runtime_first_loadable_parity_behavior_tests,
    );

    const test_step = b.step(
        "test",
        "Run focused Phase 9 first-loadable runtime-module parity behavior tests.",
    );
    test_step.dependOn(&run_runtime_first_loadable_parity_behavior_tests.step);
}

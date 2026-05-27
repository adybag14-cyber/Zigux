const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const runtime_kretprobe_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_kretprobe.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_kretprobe_diff_module = b.createModule(.{
        .root_source_file = b.path("runtime_kretprobe_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_kretprobe_diff_module.addImport(
        "runtime_kretprobe_sample",
        runtime_kretprobe_sample_module,
    );

    const runtime_kretprobe_diff_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-diff-tests",
        .root_module = runtime_kretprobe_diff_module,
    });

    const run_runtime_kretprobe_diff_tests = b.addRunArtifact(runtime_kretprobe_diff_tests);

    const phase9_runtime_kretprobe_diff = b.step(
        "phase9-runtime-kretprobe-diff-tests",
        "Run the Phase 9 runtime kretprobe differential replay tests.",
    );
    phase9_runtime_kretprobe_diff.dependOn(&run_runtime_kretprobe_diff_tests.step);
}

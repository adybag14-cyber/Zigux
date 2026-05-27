const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const guard_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig"),
        .target = target,
        .optimize = optimize,
    });

    const guard_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-initialized-snapshot-guard-tests",
        .root_module = guard_module,
    });

    const run_guard_tests = b.addRunArtifact(guard_tests);

    const guard_step = b.step(
        "phase9-runtime-kretprobe-initialized-snapshot-guard-tests",
        "Run the Phase 9 runtime kretprobe initialized-snapshot guard tests.",
    );
    guard_step.dependOn(&run_guard_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 9 runtime kretprobe initialized-snapshot guard tests.",
    );
    test_step.dependOn(&run_guard_tests.step);
}

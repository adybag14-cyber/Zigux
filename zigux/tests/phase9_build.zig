const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const runtime_atomic64_diff_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-diff-tests",
        .root_source_file = b.path("runtime_atomic64_diff.zig"),
        .target = target,
        .optimize = optimize,
    });

    const run_runtime_atomic64_diff_tests = b.addRunArtifact(runtime_atomic64_diff_tests);

    const phase9_runtime_atomic64_diff = b.step(
        "phase9-runtime-atomic64-diff",
        "Run the Phase 9 runtime atomic64 differential replay tests.",
    );
    phase9_runtime_atomic64_diff.dependOn(&run_runtime_atomic64_diff_tests.step);
}

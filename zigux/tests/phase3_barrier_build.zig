const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const barrier_helpers_module = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase3-barrier-test",
        .root_module = barrier_helpers_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase3-barrier-test",
        "Run the focused Phase 3 barrier helper replay",
    );
    test_step.dependOn(&run_tests.step);
}

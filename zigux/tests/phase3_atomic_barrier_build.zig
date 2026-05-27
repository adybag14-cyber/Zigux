const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const atomic_module = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });
    const barrier_module = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });

    const atomic_tests = b.addTest(.{
        .name = "phase3-atomic-test",
        .root_module = atomic_module,
    });
    const run_atomic_tests = b.addRunArtifact(atomic_tests);

    const barrier_tests = b.addTest(.{
        .name = "phase3-barrier-test",
        .root_module = barrier_module,
    });
    const run_barrier_tests = b.addRunArtifact(barrier_tests);

    const test_step = b.step(
        "phase3-atomic-barrier-test",
        "Run the focused Phase 3 atomic and barrier helper replays",
    );
    test_step.dependOn(&run_atomic_tests.step);
    test_step.dependOn(&run_barrier_tests.step);
}

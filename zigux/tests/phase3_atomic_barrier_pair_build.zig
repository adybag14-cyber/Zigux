const std = @import("std");

fn addModuleTest(
    b: *std.Build,
    name: []const u8,
    root_source_file: []const u8,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path(root_source_file),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = name,
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const atomic_tests = addModuleTest(
        b,
        "phase3_atomic_pair_tests",
        "../helpers/atomic.zig",
        target,
        optimize,
    );
    const barrier_tests = addModuleTest(
        b,
        "phase3_barrier_pair_tests",
        "../helpers/barrier.zig",
        target,
        optimize,
    );

    const pair_step = b.step(
        "phase3-atomic-barrier-pair-test",
        "Run the phase3 atomic and barrier helper tests together",
    );
    pair_step.dependOn(&atomic_tests.step);
    pair_step.dependOn(&barrier_tests.step);
}

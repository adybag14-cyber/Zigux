const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const hweight_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    });
    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_hweight_strided_planes_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("hweight", hweight_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-hweight-strided-planes-replay-tests",
        .root_module = replay_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);

    const replay_step = b.step("phase1-hweight-strided-planes-replay", "Run the Phase 1 hweight strided-planes replay.");
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the focused Phase 1 hweight strided-planes replay.");
    test_step.dependOn(replay_step);

    b.default_step.dependOn(test_step);
}

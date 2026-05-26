const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const hweight_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_root = b.createModule(.{
        .root_source_file = b.path("phase1_hweight_complement_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root.addImport("hweight", hweight_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-hweight-complement-replay",
        .root_module = replay_root,
    });

    const run_replay = b.addRunArtifact(replay_tests);
    const replay_step = b.step(
        "phase1-hweight-complement-replay",
        "Run the Lane 08 hweight complement replay",
    );
    replay_step.dependOn(&run_replay.step);

    const test_step = b.step("test", "Run the Lane 08 hweight complement replay");
    test_step.dependOn(&run_replay.step);
}

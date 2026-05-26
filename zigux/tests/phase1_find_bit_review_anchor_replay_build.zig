const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_find_bit_review_anchor_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("find_bit", find_bit_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-find-bit-review-anchor-replay",
        .root_module = root_module,
    });

    const run_replay_tests = b.addRunArtifact(replay_tests);
    const replay_step = b.step(
        "phase1-find-bit-review-anchor-replay",
        "Run the focused Phase 1 find_bit review-anchor replay.",
    );
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the focused Phase 1 find_bit review-anchor replay.");
    test_step.dependOn(&run_replay_tests.step);

    b.default_step.dependOn(test_step);
}

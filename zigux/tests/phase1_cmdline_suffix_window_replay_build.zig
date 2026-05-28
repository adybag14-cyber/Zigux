const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_cmdline_suffix_window_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("cmdline", cmdline_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-cmdline-suffix-window-replay-tests",
        .root_module = replay_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);

    const replay_step = b.step("phase1-cmdline-suffix-window-replay", "Run Phase 1 cmdline suffix-window replay tests");
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run Phase 1 cmdline suffix-window replay tests");
    test_step.dependOn(replay_step);
}

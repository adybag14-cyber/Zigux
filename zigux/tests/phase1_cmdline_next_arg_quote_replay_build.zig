const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    const replay_root_module = b.createModule(.{
        .root_source_file = b.path("phase1_cmdline_next_arg_quote_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root_module.addImport("cmdline", cmdline_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-cmdline-next-arg-quote-replay-tests",
        .root_module = replay_root_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);
    const replay_step = b.step(
        "phase1-cmdline-next-arg-quote-replay",
        "Run the Phase 1 cmdline nextArg quoted-token replay",
    );
    replay_step.dependOn(&run_replay_tests.step);
}

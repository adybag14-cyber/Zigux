const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const replay_root = b.createModule(.{
        .root_source_file = b.path("phase1_cmdline_option_memparse_edges.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root.addImport("cmdline", cmdline_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-cmdline-option-memparse-edges",
        .root_module = replay_root,
    });

    const run_replay = b.addRunArtifact(replay_tests);

    const replay_step = b.step(
        "phase1-cmdline-option-memparse-edges",
        "Run the Phase 1 cmdline option and memparse edges replay.",
    );
    replay_step.dependOn(&run_replay.step);
}

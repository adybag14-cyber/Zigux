const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_string_memchr_bounded_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("string", string_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-string-memchr-bounded-replay",
        .root_module = replay_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);

    const replay_step = b.step("phase1-string-memchr-bounded-replay", "Run the focused Phase 1 string memchr/bounded replay.");
    replay_step.dependOn(&run_replay_tests.step);
    b.default_step.dependOn(replay_step);
}

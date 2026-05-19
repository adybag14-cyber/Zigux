const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const string_dep = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_string_memchr_memparse_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "string", .module = string_dep },
            },
        }),
    });

    const run_replay_tests = b.addRunArtifact(replay_tests);
    const replay_step = b.step(
        "phase1-string-memchr-memparse-replay",
        "Run the Lane 06 Phase 1 string memchr and memparse replay tests",
    );
    replay_step.dependOn(&run_replay_tests.step);
}

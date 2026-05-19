const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const find_bit_dep = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_find_bit_clump8_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "find_bit", .module = find_bit_dep },
            },
        }),
    });

    const run_replay_tests = b.addRunArtifact(replay_tests);
    const replay_step = b.step(
        "phase1-find-bit-clump8-replay",
        "Run the Lane 06 Phase 1 find_bit clump8 replay tests",
    );
    replay_step.dependOn(&run_replay_tests.step);
}

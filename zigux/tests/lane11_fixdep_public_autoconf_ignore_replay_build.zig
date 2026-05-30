const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const fixdep_module = b.createModule(.{
        .root_source_file = b.path("../../scripts/zigux/fixdep.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_module = b.createModule(.{
        .root_source_file = b.path("lane11_fixdep_public_autoconf_ignore_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("fixdep", fixdep_module);

    const replay_tests = b.addTest(.{
        .name = "lane11-fixdep-public-autoconf-ignore-replay-tests",
        .root_module = replay_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);
    run_replay_tests.setCwd(b.path("../.."));

    const test_step = b.step("test", "Run Lane 11 fixdep public autoconf ignore replay");
    test_step.dependOn(&run_replay_tests.step);
}

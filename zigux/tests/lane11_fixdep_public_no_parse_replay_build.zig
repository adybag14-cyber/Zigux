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
        .root_source_file = b.path("lane11_fixdep_public_no_parse_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("fixdep", fixdep_module);

    const tests = b.addTest(.{
        .name = "lane11-fixdep-public-no-parse-replay-tests",
        .root_module = replay_module,
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const test_step = b.step("test", "Run Lane 11 fixdep public no-parse replay tests");
    test_step.dependOn(&run_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_b_numeric_token_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("argv_split", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    }));
    replay_module.addImport("cmdline", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    }));
    replay_module.addImport("ctype", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/ctype.zig"),
        .target = target,
        .optimize = optimize,
    }));
    replay_module.addImport("hweight", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    }));

    const replay_tests = b.addTest(.{
        .name = "phase1-helper-ports-b-numeric-token-replay-tests",
        .root_module = replay_module,
    });

    const run_replay_tests = b.addRunArtifact(replay_tests);

    const replay_step = b.step(
        "phase1-helper-ports-b-numeric-token-replay",
        "Run the Lane 08 helper ports B numeric token replay tests.",
    );
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the Lane 08 helper ports B numeric token replay tests.");
    test_step.dependOn(&run_replay_tests.step);

    b.default_step.dependOn(test_step);
}

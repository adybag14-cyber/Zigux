const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const genksyms_module = b.createModule(.{
        .root_source_file = b.path("../../scripts/zigux/genksyms.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase2_genksyms_wrapper_version_json_escape_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("genksyms", genksyms_module);

    const replay_tests = b.addTest(.{
        .name = "phase2-genksyms-wrapper-version-json-escape-replay-tests",
        .root_module = replay_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);
    run_replay_tests.setCwd(b.path("../.."));

    const replay_step = b.step(
        "phase2-genksyms-wrapper-version-json-escape-replay",
        "Run the Phase 2 genksyms wrapper version JSON escape replay.",
    );
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the Phase 2 genksyms wrapper version JSON escape replay.");
    test_step.dependOn(&run_replay_tests.step);
}

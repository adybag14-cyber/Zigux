const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_root = b.createModule(.{
        .root_source_file = b.path("phase1_string_strlcat_casecmp_terminator_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root.addImport("string", string_module);

    const tests = b.addTest(.{
        .name = "phase1-string-strlcat-casecmp-terminator-replay",
        .root_module = replay_root,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase1-string-strlcat-casecmp-terminator-replay",
        "Run the Lane 06 string strlcat/casecmp/terminator replay",
    );
    test_step.dependOn(&run_tests.step);
}

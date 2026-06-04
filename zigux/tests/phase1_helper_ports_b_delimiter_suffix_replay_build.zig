const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests_mod = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_b_delimiter_suffix_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    tests_mod.addImport("argv_split", b.createModule(.{ .root_source_file = b.path("../../tools/lib/argv_split.zig") }));
    tests_mod.addImport("cmdline", b.createModule(.{ .root_source_file = b.path("../../tools/lib/cmdline.zig") }));
    tests_mod.addImport("ctype", b.createModule(.{ .root_source_file = b.path("../../tools/lib/ctype.zig") }));
    tests_mod.addImport("hweight", b.createModule(.{ .root_source_file = b.path("../../tools/lib/hweight.zig") }));

    const tests = b.addTest(.{
        .root_module = tests_mod,
    });

    const run_tests = b.addRunArtifact(tests);
    const replay_step = b.step(
        "phase1-helper-ports-b-delimiter-suffix-replay",
        "Run the Lane 08 delimiter and suffix replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 08 delimiter and suffix replay tests");
    test_step.dependOn(&run_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_string_compare_substring_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("string", string_module);

    const tests = b.addTest(.{
        .name = "phase1-string-compare-substring-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay = b.step(
        "phase1-string-compare-substring-replay",
        "Run the focused Phase 1 string compare-and-substring replay from zigux/tests",
    );
    replay.dependOn(&run_tests.step);
}

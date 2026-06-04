const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });
    string_module.addImport("cmdline", cmdline_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_string_compare_terminator_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("string", string_module);

    const tests = b.addTest(.{
        .name = "phase1-string-compare-terminator-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay = b.step(
        "phase1-string-compare-terminator-replay",
        "Run the focused Phase 1 string comparison terminator replay",
    );
    replay.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Phase 1 string comparison terminator replay");
    test_step.dependOn(&run_tests.step);
}

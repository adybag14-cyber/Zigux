const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_string_bool_memparse_basename_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
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
    root_module.addImport("string", string_module);

    const tests = b.addTest(.{
        .name = "phase1-string-bool-memparse-basename-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-string-bool-memparse-basename-replay",
        "Run the Phase 1 string bool/memparse/basename replay",
    );
    replay_step.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the Phase 1 string bool/memparse/basename replay",
    );
    test_step.dependOn(&run.step);
}

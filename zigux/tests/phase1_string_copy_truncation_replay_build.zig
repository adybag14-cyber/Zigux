const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_string_copy_truncation_replay.zig"),
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
        .name = "phase1-string-copy-truncation-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-string-copy-truncation-replay",
        "Run the Phase 1 string copy/truncation replay",
    );
    replay_step.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the Phase 1 string copy/truncation replay",
    );
    test_step.dependOn(&run.step);
}

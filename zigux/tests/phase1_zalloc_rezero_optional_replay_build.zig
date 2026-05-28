const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const zalloc_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests_root = b.createModule(.{
        .root_source_file = b.path("phase1_zalloc_rezero_optional_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    tests_root.addImport("zalloc", zalloc_module);

    const tests = b.addTest(.{
        .name = "phase1-zalloc-rezero-optional-replay",
        .root_module = tests_root,
    });

    const run = b.addRunArtifact(tests);

    const replay = b.step(
        "phase1-zalloc-rezero-optional-replay",
        "Run the Lane 07 zalloc rezero and optional reset replay.",
    );
    replay.dependOn(&run.step);

    const test_alias = b.step("test", "Alias for the Lane 07 zalloc replay.");
    test_alias.dependOn(&run.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests_root = b.createModule(.{
        .root_source_file = b.path("phase1_string_whitespace_scan_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    tests_root.addImport("string", string_module);

    const tests = b.addTest(.{
        .name = "phase1-string-whitespace-scan-replay",
        .root_module = tests_root,
    });

    const run = b.addRunArtifact(tests);

    const replay = b.step(
        "phase1-string-whitespace-scan-replay",
        "Run the Lane 07 string whitespace and scan replay.",
    );
    replay.dependOn(&run.step);

    const test_alias = b.step("test", "Alias for the Lane 07 string whitespace replay.");
    test_alias.dependOn(&run.step);
}

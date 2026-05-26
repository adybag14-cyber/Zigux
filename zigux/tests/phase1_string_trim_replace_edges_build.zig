const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_string_trim_replace_edges.zig"),
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
        .name = "phase1-string-trim-replace-edges",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const replay = b.step(
        "phase1-string-trim-replace-edges",
        "Run the Phase 1 string trim and replace edge replay",
    );
    replay.dependOn(&run.step);

    const test_step = b.step("test", "Run the Phase 1 string trim and replace edge replay");
    test_step.dependOn(&run.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_string_copy_bool_edges.zig"),
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
        .name = "phase1-string-copy-bool-edges",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const replay = b.step(
        "phase1-string-copy-bool-edges",
        "Run the Phase 1 string copy and bool edge replay",
    );
    replay.dependOn(&run.step);
}

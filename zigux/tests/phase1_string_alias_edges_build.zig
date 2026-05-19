const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_string_alias_edges.zig"),
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
        .name = "phase1-string-alias-edges",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-string-alias-edges",
        "Run the standalone Phase 1 string alias edge replay from zigux/tests",
    );
    step.dependOn(&run.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_string_compare_span_replay.zig"),
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
        .name = "phase1-string-compare-span-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-string-compare-span-replay",
        "Run the Lane 07 Phase 1 string compare-and-span replay",
    );
    step.dependOn(&run.step);
}

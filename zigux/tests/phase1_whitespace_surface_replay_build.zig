const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_whitespace_surface_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("cmdline", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    }));
    root_module.addImport("ctype", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/ctype.zig"),
        .target = target,
        .optimize = optimize,
    }));
    root_module.addImport("string", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    }));

    const tests = b.addTest(.{
        .name = "phase1-whitespace-surface-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-whitespace-surface-replay",
        "Run the Phase 1 whitespace surface replay from zigux/tests",
    );
    step.dependOn(&run.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_ctype_ascii_window_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const ctype_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/ctype.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("ctype", ctype_module);

    const tests = b.addTest(.{
        .name = "phase1-ctype-ascii-window-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-ctype-ascii-window-replay",
        "Run the standalone Phase 1 ctype ASCII-window replay from zigux/tests",
    );
    step.dependOn(&run_tests.step);
}

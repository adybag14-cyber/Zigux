const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_str_error_r_helper_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const str_error_r_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("str_error_r", str_error_r_module);

    const tests = b.addTest(.{
        .name = "phase1-str-error-r-helper-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-str-error-r-helper-replay",
        "Run the standalone Phase 1 str_error_r helper replay from zigux/tests",
    );
    step.dependOn(&run.step);
}

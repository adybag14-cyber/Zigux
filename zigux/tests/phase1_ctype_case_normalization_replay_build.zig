const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const ctype_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/ctype.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_ctype_case_normalization_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("ctype", ctype_module);

    const tests = b.addTest(.{
        .name = "phase1-ctype-case-normalization-replay",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase1-ctype-case-normalization-replay",
        "Run the Lane 08 ctype case-normalization replay",
    );
    test_step.dependOn(&run_tests.step);
}

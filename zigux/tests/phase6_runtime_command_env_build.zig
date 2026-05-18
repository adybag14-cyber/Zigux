const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase6_runtime_command_env.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    const argv_split_module = b.createModule(.{
        .root_source_file = b.path("../../lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });
    const string_helpers_module = b.createModule(.{
        .root_source_file = b.path("../../lib/string_helpers.zig"),
        .target = target,
        .optimize = optimize,
    });

    root_module.addImport("cmdline", cmdline_module);
    root_module.addImport("argv_split", argv_split_module);
    root_module.addImport("string_helpers", string_helpers_module);

    const tests = b.addTest(.{
        .name = "phase6-runtime-command-env",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const phase6_step = b.step(
        "phase6-runtime-command-env",
        "Run the Phase 6 runtime command and environment helper control surface",
    );
    phase6_step.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the Phase 6 runtime command and environment helper control surface",
    );
    test_step.dependOn(&run.step);
}

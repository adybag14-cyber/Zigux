const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_argv_split_whitespace_reset_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const argv_split_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("argv_split", argv_split_module);

    const tests = b.addTest(.{
        .name = "phase1-argv-split-whitespace-reset-replay",
        .root_module = root_module,
    });

    const run = b.addRunArtifact(tests);

    const main_step = b.step(
        "phase1-argv-split-whitespace-reset-replay",
        "Run the Phase 1 argv_split whitespace and reset replay.",
    );
    main_step.dependOn(&run.step);

    const test_step = b.step("test", "Alias for phase1-argv-split-whitespace-reset-replay.");
    test_step.dependOn(&run.step);
}

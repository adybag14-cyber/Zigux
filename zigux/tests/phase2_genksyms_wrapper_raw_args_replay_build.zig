const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const genksyms_module = b.createModule(.{
        .root_source_file = b.path("../../scripts/zigux/genksyms.zig"),
        .target = target,
        .optimize = optimize,
    });
    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase2_genksyms_wrapper_raw_args_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("genksyms", genksyms_module);

    const tests = b.addTest(.{
        .name = "phase2-genksyms-wrapper-raw-args-replay-tests",
        .root_module = replay_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase2-genksyms-wrapper-raw-args-replay",
        "Run the focused Phase 2 genksyms wrapper raw-args replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Phase 2 genksyms wrapper raw-args replay");
    test_step.dependOn(&run_tests.step);
}

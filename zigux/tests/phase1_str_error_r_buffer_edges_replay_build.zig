const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const str_error_r_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_str_error_r_buffer_edges_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("str_error_r", str_error_r_module);

    const tests = b.addTest(.{
        .name = "phase1-str-error-r-buffer-edges-replay",
        .root_module = replay_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step("phase1-str-error-r-buffer-edges-replay", "Run Phase 1 str_error_r buffer edge replay");
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Phase 1 str_error_r buffer edge replay");
    test_step.dependOn(&run_tests.step);
}

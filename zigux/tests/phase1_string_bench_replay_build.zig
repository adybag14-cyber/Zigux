const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_string_bench_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("string", string_module);

    const tests = b.addTest(.{
        .name = "phase1-string-bench-replay",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-string-bench-replay",
        "Run the focused Phase 1 string bench replay from zigux/tests",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Phase 1 string bench replay.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const str_error_r_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_str_error_r_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("str_error_r", str_error_r_module);

    const tests = b.addTest(.{
        .name = "phase1-str-error-r-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const phase1_step = b.step(
        "phase1-str-error-r-replay",
        "Run the dedicated Phase 1 str_error_r replay shard",
    );
    phase1_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the dedicated Phase 1 str_error_r replay shard");
    test_step.dependOn(&run_tests.step);
}

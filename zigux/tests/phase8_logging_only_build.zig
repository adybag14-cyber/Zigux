const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const logging_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/logging.zig"),
        .target = target,
        .optimize = optimize,
    });
    const logging_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_logging.zig"),
        .target = target,
        .optimize = optimize,
    });
    logging_root_module.addImport("logging", logging_module);

    const logging_tests = b.addTest(.{
        .name = "phase8-logging-tests",
        .root_module = logging_root_module,
    });
    const run_logging_tests = b.addRunArtifact(logging_tests);

    const test_step = b.step("test", "Run focused Phase 8 logging tests");
    test_step.dependOn(&run_logging_tests.step);
}

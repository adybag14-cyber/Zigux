const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const help_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/subcmd/help.zig"),
        .target = target,
        .optimize = optimize,
    });

    const help_tests = b.addTest(.{
        .name = "phase8-help-only-tests",
        .root_module = help_module,
    });

    const run_help_tests = b.addRunArtifact(help_tests);

    const test_step = b.step("test", "Run the focused Phase 8 help-only tests.");
    test_step.dependOn(&run_help_tests.step);

    b.default_step.dependOn(test_step);
}

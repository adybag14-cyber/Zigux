const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abbreviated_help_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("genksyms_abbreviated_help_executable_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_abbreviated_help_tests = b.addRunArtifact(abbreviated_help_tests);

    const abbreviated_help_step = b.step(
        "lane23-genksyms-abbreviated-help-executable",
        "Run Lane 23 genksyms abbreviated help executable proof",
    );
    abbreviated_help_step.dependOn(&run_abbreviated_help_tests.step);

    const test_step = b.step("test", "Run Lane 23 genksyms abbreviated help executable proof");
    test_step.dependOn(&run_abbreviated_help_tests.step);
    b.default_step.dependOn(&run_abbreviated_help_tests.step);
}

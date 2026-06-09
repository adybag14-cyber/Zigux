const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const required_terminator_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("genksyms_required_terminator_argument_executable_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_required_terminator_tests = b.addRunArtifact(required_terminator_tests);

    const required_terminator_step = b.step(
        "lane23-genksyms-required-terminator-argument-executable",
        "Run Lane 23 genksyms required terminator-argument executable proof",
    );
    required_terminator_step.dependOn(&run_required_terminator_tests.step);

    const test_step = b.step("test", "Run Lane 23 genksyms required terminator-argument executable proof");
    test_step.dependOn(&run_required_terminator_tests.step);
    b.default_step.dependOn(&run_required_terminator_tests.step);
}

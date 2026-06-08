const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unexpected_inline_long_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("genksyms_unexpected_inline_long_executable_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_unexpected_inline_long_tests = b.addRunArtifact(unexpected_inline_long_tests);

    const unexpected_inline_long_step = b.step(
        "lane23-genksyms-unexpected-inline-long-executable",
        "Run Lane 23 genksyms unexpected inline-long executable proof",
    );
    unexpected_inline_long_step.dependOn(&run_unexpected_inline_long_tests.step);

    const test_step = b.step("test", "Run Lane 23 genksyms unexpected inline-long executable proof");
    test_step.dependOn(&run_unexpected_inline_long_tests.step);
    b.default_step.dependOn(&run_unexpected_inline_long_tests.step);
}

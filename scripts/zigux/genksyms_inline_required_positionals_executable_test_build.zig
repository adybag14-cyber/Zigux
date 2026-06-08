const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const inline_required_positionals_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("genksyms_inline_required_positionals_executable_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_inline_required_positionals_tests = b.addRunArtifact(inline_required_positionals_tests);

    const inline_required_positionals_step = b.step(
        "lane23-genksyms-inline-required-positionals-executable",
        "Run Lane 23 genksyms inline-required positionals executable proof",
    );
    inline_required_positionals_step.dependOn(&run_inline_required_positionals_tests.step);

    const test_step = b.step("test", "Run Lane 23 genksyms inline-required positionals executable proof");
    test_step.dependOn(&run_inline_required_positionals_tests.step);
    b.default_step.dependOn(&run_inline_required_positionals_tests.step);
}

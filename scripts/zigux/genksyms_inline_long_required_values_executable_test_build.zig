const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const inline_long_required_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("genksyms_inline_long_required_values_executable_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_inline_long_required_tests = b.addRunArtifact(inline_long_required_tests);
    run_inline_long_required_tests.setCwd(b.path("../.."));

    const route_step = b.step(
        "lane23-genksyms-inline-long-required-values-executable",
        "Run the Lane 23 genksyms inline long required values executable proof.",
    );
    route_step.dependOn(&run_inline_long_required_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 23 genksyms inline long required values executable proof.",
    );
    test_step.dependOn(&run_inline_long_required_tests.step);

    b.default_step.dependOn(&run_inline_long_required_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("genksyms_version_before_ambiguous_inline_long_option_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "genksyms-version-before-ambiguous-inline-long-option-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route = b.step(
        "genksyms-version-before-ambiguous-inline-long-option",
        "Run genksyms ambiguous inline long-option version tests",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run genksyms ambiguous inline long-option version tests");
    test_step.dependOn(&run_tests.step);
}

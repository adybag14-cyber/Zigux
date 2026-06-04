const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("genksyms_empty_separate_long_after_positionals_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "genksyms-empty-separate-long-after-positionals-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route = b.step(
        "genksyms-empty-separate-long-after-positionals",
        "Run genksyms empty separate long after positionals tests",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run genksyms empty separate long after positionals tests");
    test_step.dependOn(&run_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const escaped_dependency_dedupe_module = b.createModule(.{
        .root_source_file = b.path("fixdep_escaped_dependency_dedupe_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const escaped_dependency_dedupe_tests = b.addTest(.{
        .name = "fixdep-escaped-dependency-dedupe-tests",
        .root_module = escaped_dependency_dedupe_module,
    });
    const run_escaped_dependency_dedupe_tests = b.addRunArtifact(escaped_dependency_dedupe_tests);
    run_escaped_dependency_dedupe_tests.setCwd(b.path("../.."));

    const escaped_dependency_dedupe_step = b.step(
        "fixdep-escaped-dependency-dedupe",
        "Run the Lane 11 fixdep escaped-dependency de-dupe proof",
    );
    escaped_dependency_dedupe_step.dependOn(&run_escaped_dependency_dedupe_tests.step);

    const test_step = b.step("test", "Run the Lane 11 fixdep escaped-dependency de-dupe proof");
    test_step.dependOn(&run_escaped_dependency_dedupe_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const test_module = b.createModule(.{
        .root_source_file = b.path("fixdep_escaped_space_public_entry_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "fixdep-escaped-space-public-entry-tests",
        .root_module = test_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step("fixdep-escaped-space-public-entry", "Run the focused fixdep escaped-space public-entry proof.");
    test_step.dependOn(&run_tests.step);

    const default_test_step = b.step("test", "Run the focused fixdep escaped-space public-entry proof.");
    default_test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}

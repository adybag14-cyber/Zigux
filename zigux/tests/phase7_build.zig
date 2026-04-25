const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const string_helpers_module = b.createModule(.{
        .root_source_file = b.path("../../lib/string_helpers.zig"),
        .target = target,
        .optimize = optimize,
    });
    const string_helpers_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_string_helpers.zig"),
        .target = target,
        .optimize = optimize,
    });
    string_helpers_root_module.addImport("string_helpers", string_helpers_module);

    const string_helpers_tests = b.addTest(.{
        .name = "phase7-string-helpers-tests",
        .root_module = string_helpers_root_module,
    });
    const run_string_helpers_tests = b.addRunArtifact(string_helpers_tests);

    const test_step = b.step("test", "Run Phase 7 string helper tests");
    test_step.dependOn(&run_string_helpers_tests.step);
}

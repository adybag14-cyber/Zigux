const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const source_directory_module = b.createModule(.{
        .root_source_file = b.path("fixdep_source_directory_public_entry_test.zig"),
        .target = target,
        .optimize = optimize,
    });
    const source_directory_tests = b.addTest(.{
        .name = "fixdep-source-directory-public-entry-tests",
        .root_module = source_directory_module,
    });
    const run_source_directory_tests = b.addRunArtifact(source_directory_tests);

    const source_directory_step = b.step(
        "fixdep-source-directory-public-entry",
        "Run the fixdep public-entry source directory proof.",
    );
    source_directory_step.dependOn(&run_source_directory_tests.step);

    const test_step = b.step("test", "Run the fixdep source directory public-entry tests.");
    test_step.dependOn(&run_source_directory_tests.step);

    b.default_step.dependOn(test_step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const directory_dependency_module = b.createModule(.{
        .root_source_file = b.path("fixdep_directory_dependency_public_entry_test.zig"),
        .target = target,
        .optimize = optimize,
    });
    const directory_dependency_tests = b.addTest(.{
        .name = "fixdep-directory-dependency-public-entry-tests",
        .root_module = directory_dependency_module,
    });
    const run_directory_dependency_tests = b.addRunArtifact(directory_dependency_tests);

    const directory_dependency_step = b.step(
        "fixdep-directory-dependency-public-entry",
        "Run the fixdep public-entry directory dependency proof.",
    );
    directory_dependency_step.dependOn(&run_directory_dependency_tests.step);

    const test_step = b.step("test", "Run the fixdep directory dependency public-entry tests.");
    test_step.dependOn(&run_directory_dependency_tests.step);

    b.default_step.dependOn(test_step);
}

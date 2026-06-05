const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("fixdep_missing_later_dependency_public_entry_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const named_step = b.step(
        "fixdep-missing-later-dependency-public-entry",
        "Run the fixdep missing-later-dependency public-entry proof",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_tests.step);
}

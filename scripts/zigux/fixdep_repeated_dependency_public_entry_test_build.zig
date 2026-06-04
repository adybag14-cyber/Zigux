const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("fixdep_repeated_dependency_public_entry_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const route = b.step("fixdep-repeated-dependency-public-entry", "Run the repeated dependency fixdep public-entry proof");
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run this standalone fixdep proof");
    test_step.dependOn(&run_tests.step);
}

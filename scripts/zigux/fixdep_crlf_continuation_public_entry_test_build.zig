const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_module = b.createModule(.{
        .root_source_file = b.path("fixdep_crlf_continuation_public_entry_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "fixdep-crlf-continuation-public-entry-tests",
        .root_module = test_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const route = b.step("fixdep-crlf-continuation-public-entry", "Run the fixdep CRLF continuation public-entry proof");
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the fixdep CRLF continuation public-entry proof");
    test_step.dependOn(&run_tests.step);
}

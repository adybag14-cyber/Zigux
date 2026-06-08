const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const reference_limit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("genksyms_reference_limit_executable_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_reference_limit_tests = b.addRunArtifact(reference_limit_tests);

    const reference_limit_step = b.step(
        "lane23-genksyms-reference-limit-executable",
        "Run Lane 23 genksyms reference-limit executable proof",
    );
    reference_limit_step.dependOn(&run_reference_limit_tests.step);

    const test_step = b.step("test", "Run Lane 23 genksyms reference-limit executable proof");
    test_step.dependOn(&run_reference_limit_tests.step);
    b.default_step.dependOn(&run_reference_limit_tests.step);
}

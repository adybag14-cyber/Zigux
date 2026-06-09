const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("genksyms_positionals_before_version_executable_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(unit_tests);

    const named_step = b.step(
        "lane23-genksyms-positionals-before-version-executable",
        "Run Lane 23 genksyms positionals-before-version executable proof",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 23 genksyms positionals-before-version executable proof");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}

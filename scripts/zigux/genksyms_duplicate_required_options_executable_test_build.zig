const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_step = b.step(
        "lane23-genksyms-duplicate-required-options-executable",
        "Run Lane 23 genksyms duplicate required-options executable proof",
    );

    const executable_test = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("genksyms_duplicate_required_options_executable_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_executable_test = b.addRunArtifact(executable_test);
    run_executable_test.cwd = b.path("../..");
    test_step.dependOn(&run_executable_test.step);
    b.default_step.dependOn(test_step);
    b.step("test", "Run Lane 23 genksyms duplicate required-options executable proof").dependOn(test_step);
}

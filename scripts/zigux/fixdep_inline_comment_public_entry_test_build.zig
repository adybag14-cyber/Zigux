const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("fixdep_inline_comment_public_entry_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const named_step = b.step(
        "fixdep-inline-comment-public-entry",
        "Run fixdep inline-comment public-entry proof",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run fixdep inline-comment public-entry proof");
    test_step.dependOn(&run_tests.step);
}

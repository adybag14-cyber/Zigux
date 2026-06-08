const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("rbtree_plain_erase_alias_followup_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step("rbtree-plain-erase-alias-followup-test", "Run rbtree plain erase alias follow-up contract");
    test_step.dependOn(&run_tests.step);

    const default_test_step = b.step("test", "Run rbtree plain erase alias follow-up contract");
    default_test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}

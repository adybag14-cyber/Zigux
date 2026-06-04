const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_step = b.step(
        "fixdep-rlib-no-parse-public-entry",
        "Run the fixdep .rlib no-parse public-entry proof",
    );

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("fixdep_rlib_no_parse_public_entry_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    test_step.dependOn(&b.addRunArtifact(tests).step);
    b.default_step.dependOn(test_step);

    const alias = b.step("test", "Run the fixdep .rlib no-parse public-entry proof");
    alias.dependOn(test_step);
}

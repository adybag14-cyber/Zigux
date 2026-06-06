const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("fixdep_cmdline_leading_trailing_space_public_entry_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const space_step = b.step(
        "fixdep-cmdline-leading-trailing-space-public-entry",
        "Run the Lane 11 fixdep leading/trailing-space cmdline public-entry proof",
    );
    space_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Lane 11 fixdep leading/trailing-space cmdline public-entry proof");
    test_step.dependOn(&run_unit_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("fixdep_cmdline_so_public_entry_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_unit_tests = b.addRunArtifact(tests);

    const test_step = b.step("fixdep-cmdline-so-public-entry", "Run the fixdep SO cmdline public-entry proof");
    test_step.dependOn(&run_unit_tests.step);

    const alias_step = b.step("test", "Run fixdep SO cmdline public-entry tests");
    alias_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("fixdep_cmdline_dc3_public_entry_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const dc3_step = b.step("fixdep-cmdline-dc3-public-entry", "Run the fixdep DC3 cmdline public-entry proof");
    dc3_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_tests.step);
}

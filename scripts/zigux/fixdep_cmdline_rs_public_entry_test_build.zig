const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("fixdep_cmdline_rs_public_entry_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const rs_step = b.step(
        "fixdep-cmdline-rs-public-entry",
        "Run the Lane 11 fixdep RS cmdline public-entry proof",
    );
    rs_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Lane 11 fixdep RS cmdline public-entry proof");
    test_step.dependOn(&run_unit_tests.step);
}

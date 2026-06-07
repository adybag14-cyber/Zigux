const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("fixdep_cmdline_tilde_public_entry_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "fixdep-cmdline-tilde-public-entry",
        "Run the fixdep command-line tilde public-entry proof",
    );
    test_step.dependOn(&run_unit_tests.step);

    const default_test_step = b.step("test", "Run the fixdep command-line tilde public-entry proof");
    default_test_step.dependOn(&run_unit_tests.step);
    b.default_step.dependOn(&run_unit_tests.step);
}

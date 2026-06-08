const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("fixdep_cmdline_si_public_entry_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "fixdep-cmdline-si-public-entry-tests",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const public_entry_step = b.step(
        "fixdep-cmdline-si-public-entry",
        "Run the fixdep SI savedcmd public-entry proof",
    );
    public_entry_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the fixdep SI public-entry proof");
    test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}

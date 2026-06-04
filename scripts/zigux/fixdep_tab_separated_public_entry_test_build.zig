const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tab_separated_module = b.createModule(.{
        .root_source_file = b.path("fixdep_tab_separated_public_entry_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tab_separated_tests = b.addTest(.{
        .name = "fixdep-tab-separated-public-entry-tests",
        .root_module = tab_separated_module,
    });
    const run_tab_separated_tests = b.addRunArtifact(tab_separated_tests);
    run_tab_separated_tests.setCwd(b.path("../.."));

    const tab_separated_step = b.step(
        "fixdep-tab-separated-public-entry",
        "Run the Lane 11 fixdep tab-separated public-entry proof",
    );
    tab_separated_step.dependOn(&run_tab_separated_tests.step);

    const test_step = b.step("test", "Run the Lane 11 fixdep tab-separated public-entry proof");
    test_step.dependOn(&run_tab_separated_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const ignored_autoconf_public_entry_module = b.createModule(.{
        .root_source_file = b.path("fixdep_ignored_autoconf_public_entry_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const ignored_autoconf_public_entry_tests = b.addTest(.{
        .name = "fixdep-ignored-autoconf-public-entry-tests",
        .root_module = ignored_autoconf_public_entry_module,
    });
    const run_ignored_autoconf_public_entry_tests = b.addRunArtifact(ignored_autoconf_public_entry_tests);
    run_ignored_autoconf_public_entry_tests.setCwd(b.path("../.."));

    const ignored_autoconf_public_entry_step = b.step(
        "fixdep-ignored-autoconf-public-entry",
        "Run the Lane 11 fixdep ignored-autoconf public-entry proof",
    );
    ignored_autoconf_public_entry_step.dependOn(&run_ignored_autoconf_public_entry_tests.step);

    const test_step = b.step("test", "Run the Lane 11 fixdep ignored-autoconf public-entry proof");
    test_step.dependOn(&run_ignored_autoconf_public_entry_tests.step);
}

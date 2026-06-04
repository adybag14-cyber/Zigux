const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_module = b.createModule(.{
        .root_source_file = b.path("fixdep_embedded_nul_public_entry_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const fixdep_module = b.createModule(.{
        .root_source_file = b.path("fixdep.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("fixdep.zig", fixdep_module);

    const tests = b.addTest(.{
        .name = "fixdep-embedded-nul-public-entry-tests",
        .root_module = test_module,
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const route_step = b.step("fixdep-embedded-nul-public-entry", "Run the Lane 11 embedded-NUL fixdep public-entry proof");
    route_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 11 embedded-NUL fixdep public-entry proof");
    test_step.dependOn(&run_tests.step);
}

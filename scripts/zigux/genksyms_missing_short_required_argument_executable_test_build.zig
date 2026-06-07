const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("genksyms_missing_short_required_argument_executable_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const route_step = b.step(
        "lane23-genksyms-missing-short-required-argument-executable",
        "Run the Lane 23 genksyms missing short required-argument executable proof.",
    );
    route_step.dependOn(&run_unit_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 23 genksyms missing short required-argument executable proof.",
    );
    test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}

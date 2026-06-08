const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_module = b.createModule(.{
        .root_source_file = b.path("genksyms_short_required_option_arguments_executable_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .root_module = test_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const lane_step = b.step(
        "lane23-genksyms-short-required-option-arguments-executable",
        "Run the Lane 23 genksyms short required option argument executable proof",
    );
    lane_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Lane 23 genksyms short required option argument executable proof");
    test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}

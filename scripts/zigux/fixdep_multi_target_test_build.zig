const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const multi_target_module = b.createModule(.{
        .root_source_file = b.path("fixdep_multi_target_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const multi_target_tests = b.addTest(.{
        .name = "fixdep-multi-target-tests",
        .root_module = multi_target_module,
    });
    const run_multi_target_tests = b.addRunArtifact(multi_target_tests);
    run_multi_target_tests.setCwd(b.path("../.."));

    const multi_target_step = b.step(
        "fixdep-multi-target",
        "Run the Lane 11 fixdep multi-target public-entry proof",
    );
    multi_target_step.dependOn(&run_multi_target_tests.step);

    const test_step = b.step("test", "Run the Lane 11 fixdep multi-target public-entry proof");
    test_step.dependOn(&run_multi_target_tests.step);
}

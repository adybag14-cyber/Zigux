const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const patch_applier_module = b.createModule(.{
        .root_source_file = b.path("phase2_genksyms_survey_route_patch_applier.zig"),
        .target = target,
        .optimize = optimize,
    });

    const patch_applier_tests = b.addTest(.{
        .name = "phase2-genksyms-survey-route-patch-applier-tests",
        .root_module = patch_applier_module,
    });

    const run_patch_applier_tests = b.addRunArtifact(patch_applier_tests);

    const test_step = b.step("test", "Run the focused Phase 2 genksyms survey route patch-applier tests.");
    test_step.dependOn(&run_patch_applier_tests.step);

    b.default_step.dependOn(test_step);
}

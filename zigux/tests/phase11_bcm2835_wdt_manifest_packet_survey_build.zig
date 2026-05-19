const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const survey_module = b.createModule(.{
        .root_source_file = b.path("phase11_bcm2835_wdt_manifest_packet_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const survey_tests = b.addTest(.{
        .name = "phase11-bcm2835-wdt-manifest-packet-survey-tests",
        .root_module = survey_module,
    });

    const run_survey_tests = b.addRunArtifact(survey_tests);
    const test_step = b.step("test", "Run the focused Phase 11 bcm2835 watchdog manifest packet survey");
    test_step.dependOn(&run_survey_tests.step);
}

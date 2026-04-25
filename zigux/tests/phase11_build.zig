const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const phase11_gpio_wdt_survey_module = b.createModule(.{
        .root_source_file = b.path("phase11_gpio_wdt_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase11_gpio_wdt_survey_tests = b.addTest(.{
        .name = "phase11-gpio-wdt-survey-tests",
        .root_module = phase11_gpio_wdt_survey_module,
    });
    const run_phase11_gpio_wdt_survey_tests = b.addRunArtifact(phase11_gpio_wdt_survey_tests);

    const test_step = b.step("test", "Run Phase 11 gpio_wdt survey tests");
    test_step.dependOn(&run_phase11_gpio_wdt_survey_tests.step);
}

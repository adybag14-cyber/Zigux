const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const gpio_wdt_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/gpio_wdt.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase11_gpio_wdt_module = b.createModule(.{
        .root_source_file = b.path("phase11_gpio_wdt.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase11_gpio_wdt_module.addImport("gpio_wdt", gpio_wdt_module);
    const phase11_gpio_wdt_survey_module = b.createModule(.{
        .root_source_file = b.path("phase11_gpio_wdt_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bcm2835_wdt_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/bcm2835_wdt.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase11_bcm2835_wdt_module = b.createModule(.{
        .root_source_file = b.path("phase11_bcm2835_wdt.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase11_bcm2835_wdt_module.addImport("bcm2835_wdt", bcm2835_wdt_module);
    const phase11_bcm2835_wdt_survey_module = b.createModule(.{
        .root_source_file = b.path("phase11_bcm2835_wdt_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const dw_wdt_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/dw_wdt.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase11_dw_wdt_module = b.createModule(.{
        .root_source_file = b.path("phase11_dw_wdt.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase11_dw_wdt_module.addImport("dw_wdt", dw_wdt_module);
    const phase11_dw_wdt_survey_module = b.createModule(.{
        .root_source_file = b.path("phase11_dw_wdt_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hvc_console_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/tty/hvc/hvc_console.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase11_hvc_console_module = b.createModule(.{
        .root_source_file = b.path("phase11_hvc_console.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase11_hvc_console_module.addImport("hvc_console", hvc_console_module);
    const phase11_hvc_console_survey_module = b.createModule(.{
        .root_source_file = b.path("phase11_hvc_console_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase11_gpio_wdt_tests = b.addTest(.{
        .name = "phase11-gpio-wdt-tests",
        .root_module = phase11_gpio_wdt_module,
    });
    const run_phase11_gpio_wdt_tests = b.addRunArtifact(phase11_gpio_wdt_tests);
    const phase11_gpio_wdt_survey_tests = b.addTest(.{
        .name = "phase11-gpio-wdt-survey-tests",
        .root_module = phase11_gpio_wdt_survey_module,
    });
    const run_phase11_gpio_wdt_survey_tests = b.addRunArtifact(phase11_gpio_wdt_survey_tests);
    const phase11_bcm2835_wdt_tests = b.addTest(.{
        .name = "phase11-bcm2835-wdt-tests",
        .root_module = phase11_bcm2835_wdt_module,
    });
    const run_phase11_bcm2835_wdt_tests = b.addRunArtifact(phase11_bcm2835_wdt_tests);
    const phase11_bcm2835_wdt_survey_tests = b.addTest(.{
        .name = "phase11-bcm2835-wdt-survey-tests",
        .root_module = phase11_bcm2835_wdt_survey_module,
    });
    const run_phase11_bcm2835_wdt_survey_tests = b.addRunArtifact(phase11_bcm2835_wdt_survey_tests);
    const phase11_dw_wdt_tests = b.addTest(.{
        .name = "phase11-dw-wdt-tests",
        .root_module = phase11_dw_wdt_module,
    });
    const run_phase11_dw_wdt_tests = b.addRunArtifact(phase11_dw_wdt_tests);
    const phase11_dw_wdt_survey_tests = b.addTest(.{
        .name = "phase11-dw-wdt-survey-tests",
        .root_module = phase11_dw_wdt_survey_module,
    });
    const run_phase11_dw_wdt_survey_tests = b.addRunArtifact(phase11_dw_wdt_survey_tests);
    const phase11_hvc_console_tests = b.addTest(.{
        .name = "phase11-hvc-console-tests",
        .root_module = phase11_hvc_console_module,
    });
    const run_phase11_hvc_console_tests = b.addRunArtifact(phase11_hvc_console_tests);
    const phase11_hvc_console_survey_tests = b.addTest(.{
        .name = "phase11-hvc-console-survey-tests",
        .root_module = phase11_hvc_console_survey_module,
    });
    const run_phase11_hvc_console_survey_tests = b.addRunArtifact(phase11_hvc_console_survey_tests);

    const test_step = b.step("test", "Run Phase 11 starter and survey tests");
    test_step.dependOn(&run_phase11_gpio_wdt_tests.step);
    test_step.dependOn(&run_phase11_gpio_wdt_survey_tests.step);
    test_step.dependOn(&run_phase11_bcm2835_wdt_tests.step);
    test_step.dependOn(&run_phase11_bcm2835_wdt_survey_tests.step);
    test_step.dependOn(&run_phase11_dw_wdt_tests.step);
    test_step.dependOn(&run_phase11_dw_wdt_survey_tests.step);
    test_step.dependOn(&run_phase11_hvc_console_tests.step);
    test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);
}

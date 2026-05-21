const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const gpio_wdt = b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/gpio_wdt.zig"),
        .target = target,
        .optimize = optimize,
    });

    const test_root = b.createModule(.{
        .root_source_file = b.path("phase11_gpio_wdt_register_device_glue_review.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_root.addImport("gpio_wdt", gpio_wdt);

    const unit_tests = b.addTest(.{
        .root_module = test_root,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase11-gpio-wdt-register-device-glue-review-test",
        "Run the bounded gpio_wdt register-device glue review packet",
    );
    test_step.dependOn(&run_unit_tests.step);
}

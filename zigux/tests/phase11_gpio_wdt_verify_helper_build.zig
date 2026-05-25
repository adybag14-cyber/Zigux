const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_source_file = b.path("../../drivers/watchdog/gpio_wdt_verify.zig"),
        .target = target,
        .optimize = optimize,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase11-gpio-wdt-verify-helper-test",
        "Run the driver-backed gpio_wdt verify helper packet",
    );
    test_step.dependOn(&run_unit_tests.step);
}

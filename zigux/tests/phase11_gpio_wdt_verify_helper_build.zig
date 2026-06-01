const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const verify_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/gpio_wdt_verify.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .root_module = verify_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "test",
        "Run the driver-backed gpio_wdt verify helper packet",
    );
    test_step.dependOn(&run_unit_tests.step);

    const named_step = b.step(
        "phase11-gpio-wdt-verify-helper-test",
        "Run the driver-backed gpio_wdt verify helper packet",
    );
    named_step.dependOn(&run_unit_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const gpio_wdt_verify_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/gpio_wdt_verify.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hvc_console_verify_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/tty/hvc/hvc_console_verify.zig"),
        .target = target,
        .optimize = optimize,
    });

    const gpio_wdt_verify_tests = b.addTest(.{
        .name = "phase11-gpio-wdt-verify-tests",
        .root_module = gpio_wdt_verify_module,
    });
    const run_gpio_wdt_verify_tests = b.addRunArtifact(gpio_wdt_verify_tests);

    const hvc_console_verify_tests = b.addTest(.{
        .name = "phase11-hvc-console-verify-tests",
        .root_module = hvc_console_verify_module,
    });
    const run_hvc_console_verify_tests = b.addRunArtifact(hvc_console_verify_tests);

    const test_step = b.step("test", "Run Phase 11 simple-driver verification replays");
    test_step.dependOn(&run_gpio_wdt_verify_tests.step);
    test_step.dependOn(&run_hvc_console_verify_tests.step);

    const gpio_wdt_verify_step = b.step(
        "phase11-gpio-wdt-verify",
        "Run the Phase 11 gpio watchdog verification replay",
    );
    gpio_wdt_verify_step.dependOn(&run_gpio_wdt_verify_tests.step);

    const hvc_console_verify_step = b.step(
        "phase11-hvc-console-verify",
        "Run the Phase 11 HVC console verification replay",
    );
    hvc_console_verify_step.dependOn(&run_hvc_console_verify_tests.step);

    const phase11_simple_drivers_step = b.step(
        "phase11-simple-drivers",
        "Run the bounded Phase 11 simple-driver verification replays",
    );
    phase11_simple_drivers_step.dependOn(&run_gpio_wdt_verify_tests.step);
    phase11_simple_drivers_step.dependOn(&run_hvc_console_verify_tests.step);
}

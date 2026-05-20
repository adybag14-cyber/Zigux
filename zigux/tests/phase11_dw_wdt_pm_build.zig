const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const dw_wdt_pm_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/dw_wdt_pm.zig"),
        .target = target,
        .optimize = optimize,
    });

    const dw_wdt_pm_tests = b.addTest(.{
        .name = "phase11-dw-wdt-pm-tests",
        .root_module = dw_wdt_pm_module,
    });
    const run_dw_wdt_pm_tests = b.addRunArtifact(dw_wdt_pm_tests);

    const test_step = b.step(
        "test",
        "Run the focused Phase 11 DesignWare watchdog PM helper replay",
    );
    test_step.dependOn(&run_dw_wdt_pm_tests.step);

    const pm_step = b.step(
        "phase11-dw-wdt-pm-test",
        "Run the focused Phase 11 DesignWare watchdog PM helper replay",
    );
    pm_step.dependOn(&run_dw_wdt_pm_tests.step);
}

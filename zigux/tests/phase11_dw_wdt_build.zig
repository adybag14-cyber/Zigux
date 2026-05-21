const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const registration_scaffold_module = b.createModule(.{
        .root_source_file = b.path("phase11_dw_wdt_registration_scaffold.zig"),
        .target = target,
        .optimize = optimize,
    });
    const pm_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/dw_wdt_pm.zig"),
        .target = target,
        .optimize = optimize,
    });

    const registration_scaffold_tests = b.addTest(.{
        .name = "phase11-dw-wdt-registration-scaffold-tests",
        .root_module = registration_scaffold_module,
    });
    const run_registration_scaffold_tests = b.addRunArtifact(registration_scaffold_tests);

    const pm_tests = b.addTest(.{
        .name = "phase11-dw-wdt-pm-tests",
        .root_module = pm_module,
    });
    const run_pm_tests = b.addRunArtifact(pm_tests);

    const test_step = b.step(
        "test",
        "Run the focused Phase 11 DesignWare watchdog scaffold packet",
    );
    test_step.dependOn(&run_registration_scaffold_tests.step);
    test_step.dependOn(&run_pm_tests.step);
}

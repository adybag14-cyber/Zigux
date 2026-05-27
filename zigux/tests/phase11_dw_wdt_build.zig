const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const registration_scaffold_module = b.createModule(.{
        .root_source_file = b.path("phase11_dw_wdt_registration_scaffold.zig"),
        .target = target,
        .optimize = optimize,
    });
    const live_mmio_review_module = b.createModule(.{
        .root_source_file = b.path("phase11_dw_wdt_live_mmio_review.zig"),
        .target = target,
        .optimize = optimize,
    });
    live_mmio_review_module.addImport("dw_wdt", b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/dw_wdt.zig"),
        .target = target,
        .optimize = optimize,
    }));
    live_mmio_review_module.addImport("dw_wdt_pm", b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/dw_wdt_pm.zig"),
        .target = target,
        .optimize = optimize,
    }));
    const pm_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/dw_wdt_pm.zig"),
        .target = target,
        .optimize = optimize,
    });
    const restart_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/dw_wdt_restart.zig"),
        .target = target,
        .optimize = optimize,
    });
    const verify_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/dw_wdt_verify.zig"),
        .target = target,
        .optimize = optimize,
    });

    const registration_scaffold_tests = b.addTest(.{
        .name = "phase11-dw-wdt-registration-scaffold-tests",
        .root_module = registration_scaffold_module,
    });
    const run_registration_scaffold_tests = b.addRunArtifact(registration_scaffold_tests);

    const live_mmio_review_tests = b.addTest(.{
        .name = "phase11-dw-wdt-live-mmio-review-tests",
        .root_module = live_mmio_review_module,
    });
    const run_live_mmio_review_tests = b.addRunArtifact(live_mmio_review_tests);

    const pm_tests = b.addTest(.{
        .name = "phase11-dw-wdt-pm-tests",
        .root_module = pm_module,
    });
    const run_pm_tests = b.addRunArtifact(pm_tests);

    const restart_tests = b.addTest(.{
        .name = "phase11-dw-wdt-restart-tests",
        .root_module = restart_module,
    });
    const run_restart_tests = b.addRunArtifact(restart_tests);

    const verify_tests = b.addTest(.{
        .name = "phase11-dw-wdt-verify-tests",
        .root_module = verify_module,
    });
    const run_verify_tests = b.addRunArtifact(verify_tests);

    const test_step = b.step(
        "test",
        "Run the focused Phase 11 DesignWare watchdog scaffold and verify packet",
    );
    test_step.dependOn(&run_registration_scaffold_tests.step);
    test_step.dependOn(&run_live_mmio_review_tests.step);
    test_step.dependOn(&run_pm_tests.step);
    test_step.dependOn(&run_restart_tests.step);
    test_step.dependOn(&run_verify_tests.step);
}

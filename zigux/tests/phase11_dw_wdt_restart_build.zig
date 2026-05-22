const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const restart_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/dw_wdt_restart.zig"),
        .target = target,
        .optimize = optimize,
    });

    const restart_tests = b.addTest(.{
        .name = "phase11-dw-wdt-restart-tests",
        .root_module = restart_module,
    });

    const run_restart_tests = b.addRunArtifact(restart_tests);
    const test_step = b.step("test", "Run the focused Phase 11 DesignWare watchdog restart replay");
    test_step.dependOn(&run_restart_tests.step);
}

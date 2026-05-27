const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bcm2835_wdt_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/bcm2835_wdt.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase11_bcm2835_wdt.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bcm2835_wdt", bcm2835_wdt_module);

    const unit_tests = b.addTest(.{
        .name = "phase11-bcm2835-wdt-direct-replay",
        .root_module = root_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    const test_step = b.step("test", "Run the focused Phase 11 bcm2835 watchdog direct replay.");
    test_step.dependOn(&run_unit_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const hvc_console_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/tty/hvc/hvc_console.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase11_hvc_console_verify.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("hvc_console", hvc_console_module);

    const unit_tests = b.addTest(.{
        .name = "phase11-hvc-console-verify",
        .root_module = root_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    const test_step = b.step("test", "Run the bounded Phase 11 HVC console verification replay.");
    test_step.dependOn(&run_unit_tests.step);
}

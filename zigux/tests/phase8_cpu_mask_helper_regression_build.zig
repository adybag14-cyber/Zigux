const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const cpu_mask_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/cpu_mask.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase8_cpu_mask_helper_regression.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("cpu_mask", cpu_mask_module);

    const unit_tests = b.addTest(.{
        .name = "phase8-cpu-mask-helper-regression-tests",
        .root_module = root_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    const test_step = b.step(
        "test",
        "Run focused Phase 8 cpu-mask helper regression tests",
    );
    test_step.dependOn(&run_unit_tests.step);
}

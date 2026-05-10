const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const cpu_mask_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/cpu_mask.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cpu_mask_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_cpu_mask.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpu_mask_root_module.addImport("cpu_mask", cpu_mask_module);

    const cpu_mask_tests = b.addTest(.{
        .name = "phase8-cpu-mask-tests",
        .root_module = cpu_mask_root_module,
    });
    const run_cpu_mask_tests = b.addRunArtifact(cpu_mask_tests);

    const test_step = b.step("test", "Run focused Phase 8 cpu mask tests");
    test_step.dependOn(&run_cpu_mask_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const runtime_loader_contract_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_kretprobe_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_kretprobe.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_kretprobe_loader_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_kretprobe_loader.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_kretprobe_loader_module.addImport("runtime_kretprobe_sample", runtime_kretprobe_sample_module);
    runtime_kretprobe_loader_module.addImport("runtime_loader", runtime_loader_contract_module);
    const runtime_kretprobe_module = b.createModule(.{
        .root_source_file = b.path("runtime_kretprobe_module.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_kretprobe_module.addImport("runtime_kretprobe_sample", runtime_kretprobe_sample_module);
    const runtime_kretprobe_diff_module = b.createModule(.{
        .root_source_file = b.path("runtime_kretprobe_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_kretprobe_diff_module.addImport("runtime_kretprobe_sample", runtime_kretprobe_sample_module);

    const runtime_kretprobe_sample_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-sample-tests",
        .root_module = runtime_kretprobe_sample_module,
    });
    const run_runtime_kretprobe_sample_tests = b.addRunArtifact(runtime_kretprobe_sample_tests);
    const runtime_kretprobe_module_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-module-tests",
        .root_module = runtime_kretprobe_module,
    });
    const run_runtime_kretprobe_module_tests = b.addRunArtifact(runtime_kretprobe_module_tests);
    const runtime_kretprobe_diff_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-diff-tests",
        .root_module = runtime_kretprobe_diff_module,
    });
    const run_runtime_kretprobe_diff_tests = b.addRunArtifact(runtime_kretprobe_diff_tests);
    const runtime_kretprobe_loader_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-loader-tests",
        .root_module = runtime_kretprobe_loader_module,
    });
    const run_runtime_kretprobe_loader_tests = b.addRunArtifact(runtime_kretprobe_loader_tests);

    const test_step = b.step("test", "Run focused Phase 9 runtime kretprobe sample, module, diff, and loader tests");
    test_step.dependOn(&run_runtime_kretprobe_sample_tests.step);
    test_step.dependOn(&run_runtime_kretprobe_module_tests.step);
    test_step.dependOn(&run_runtime_kretprobe_diff_tests.step);
    test_step.dependOn(&run_runtime_kretprobe_loader_tests.step);
}

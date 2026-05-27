const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const atomic_module = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });

    const bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_loader_contract_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_loader_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_loader_module.addImport("runtime_loader_contract", runtime_loader_contract_module);

    const runtime_atomic64_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_atomic64.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_sample_module.addImport("atomic", atomic_module);

    const runtime_bitmap_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_sample_module.addImport("bitmap_view", bitmap_view_module);

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
    runtime_kretprobe_loader_module.addImport(
        "runtime_kretprobe_sample",
        runtime_kretprobe_sample_module,
    );
    runtime_kretprobe_loader_module.addImport("runtime_loader", runtime_loader_module);

    const handoff_parity_module = b.createModule(.{
        .root_source_file = b.path("runtime_first_loadable_loader_handoff_parity.zig"),
        .target = target,
        .optimize = optimize,
    });
    handoff_parity_module.addImport(
        "runtime_atomic64_sample",
        runtime_atomic64_sample_module,
    );
    handoff_parity_module.addImport(
        "runtime_bitmap_sample",
        runtime_bitmap_sample_module,
    );
    handoff_parity_module.addImport(
        "runtime_kretprobe_sample",
        runtime_kretprobe_sample_module,
    );
    handoff_parity_module.addImport(
        "runtime_kretprobe_loader",
        runtime_kretprobe_loader_module,
    );
    handoff_parity_module.addImport("runtime_loader", runtime_loader_module);

    const handoff_parity_tests = b.addTest(.{
        .name = "phase9-first-loadable-runtime-loader-handoff-parity-tests",
        .root_module = handoff_parity_module,
    });

    const run_handoff_parity_tests = b.addRunArtifact(handoff_parity_tests);
    const handoff_parity_step = b.step(
        "phase9-first-loadable-runtime-loader-handoff-parity-tests",
        "Run the first-loadable runtime loader handoff parity tests",
    );
    handoff_parity_step.dependOn(&run_handoff_parity_tests.step);
}

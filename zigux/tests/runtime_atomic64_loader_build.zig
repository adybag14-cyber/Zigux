const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const atomic_module = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_atomic64_sample_module = b.createModule(.{
        .root_source_file = b.path("../samples/zigux/runtime_atomic64.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_sample_module.addImport("atomic", atomic_module);

    const runtime_atomic64_loader_module = b.createModule(.{
        .root_source_file = b.path("../samples/zigux/runtime_atomic64_loader.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_loader_module.addImport(
        "runtime_atomic64_sample",
        runtime_atomic64_sample_module,
    );

    const runtime_atomic64_loader_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-loader-tests",
        .root_module = runtime_atomic64_loader_module,
    });

    const run_runtime_atomic64_loader_tests = b.addRunArtifact(
        runtime_atomic64_loader_tests,
    );

    const phase9_runtime_atomic64_loader = b.step(
        "phase9-runtime-atomic64-loader-tests",
        "Run the Phase 9 runtime atomic64 loader-facing lifecycle tests.",
    );
    phase9_runtime_atomic64_loader.dependOn(&run_runtime_atomic64_loader_tests.step);
}

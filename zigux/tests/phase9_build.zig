const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const runtime_atomic64_diff_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-diff-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("runtime_atomic64_diff.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_bitmap_sample_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-sample-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../../samples/zigux/runtime_bitmap.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_bitmap_module_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-module-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("runtime_bitmap_module.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_bitmap_diff_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-diff-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("runtime_bitmap_diff.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_bitmap_loader_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-loader-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../../samples/zigux/runtime_bitmap_loader.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_bitmap_survey_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-survey-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("runtime_bitmap_survey.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_bitmap_top_bit_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-top-bit-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../../samples/zigux/runtime_bitmap_top_bit_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_loader_selftest_complete_exit_parity_tests = b.addTest(.{
        .name = "phase9-runtime-loader-selftest-complete-exit-parity-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("runtime_loader_selftest_complete_exit_parity.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_runtime_atomic64_diff_tests = b.addRunArtifact(runtime_atomic64_diff_tests);
    const run_runtime_bitmap_sample_tests = b.addRunArtifact(runtime_bitmap_sample_tests);
    const run_runtime_bitmap_module_tests = b.addRunArtifact(runtime_bitmap_module_tests);
    const run_runtime_bitmap_diff_tests = b.addRunArtifact(runtime_bitmap_diff_tests);
    const run_runtime_bitmap_loader_tests = b.addRunArtifact(runtime_bitmap_loader_tests);
    const run_runtime_bitmap_survey_tests = b.addRunArtifact(runtime_bitmap_survey_tests);
    const run_runtime_bitmap_top_bit_tests = b.addRunArtifact(runtime_bitmap_top_bit_tests);
    const run_runtime_loader_selftest_complete_exit_parity_tests = b.addRunArtifact(runtime_loader_selftest_complete_exit_parity_tests);

    const phase9_runtime_atomic64_diff = b.step(
        "phase9-runtime-atomic64-diff",
        "Run the Phase 9 runtime atomic64 differential replay tests.",
    );
    phase9_runtime_atomic64_diff.dependOn(&run_runtime_atomic64_diff_tests.step);

    const phase9_runtime_bitmap_top_bit = b.step(
        "phase9-runtime-bitmap-top-bit-tests",
        "Run the Phase 9 runtime bitmap top-bit contract tests.",
    );
    phase9_runtime_bitmap_top_bit.dependOn(&run_runtime_bitmap_top_bit_tests.step);

    const phase9_runtime_bitmap = b.step(
        "phase9-runtime-bitmap-tests",
        "Run the Phase 9 runtime bitmap sample, module, diff, loader, and survey tests.",
    );
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_sample_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_module_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_diff_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_loader_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_survey_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_top_bit_tests.step);

    const phase9_runtime_loader_shared = b.step(
        "phase9-runtime-loader-shared-tests",
        "Run the shared Phase 9 runtime loader handoff parity tests.",
    );
    phase9_runtime_loader_shared.dependOn(&run_runtime_bitmap_loader_tests.step);
    phase9_runtime_loader_shared.dependOn(&run_runtime_loader_selftest_complete_exit_parity_tests.step);
}

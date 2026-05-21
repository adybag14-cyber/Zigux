const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_bitmap_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_sample_module.addImport("bitmap_view", bitmap_view_module);

    const runtime_bitmap_loader_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_bitmap_loader.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_loader_module.addImport("runtime_bitmap_sample", runtime_bitmap_sample_module);

    const atomic_module = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_atomic64_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_atomic64.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_sample_module.addImport("atomic", atomic_module);

    const runtime_atomic64_diff_module = b.createModule(.{
        .root_source_file = b.path("runtime_atomic64_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_diff_module.addImport(
        "runtime_atomic64_sample",
        runtime_atomic64_sample_module,
    );

    const runtime_atomic64_diff_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-diff-tests",
        .root_module = runtime_atomic64_diff_module,
    });

    const runtime_atomic64_module_tests_module = b.createModule(.{
        .root_source_file = b.path("runtime_atomic64_module.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_module_tests_module.addImport(
        "runtime_atomic64_sample",
        runtime_atomic64_sample_module,
    );

    const runtime_atomic64_module_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-module-tests",
        .root_module = runtime_atomic64_module_tests_module,
    });

    const runtime_loader_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_loader_contract_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_loader_command_env_boundary_guard_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader_command_env_boundary_guard.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_atomic64_sample_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-sample-tests",
        .root_module = runtime_atomic64_sample_module,
    });

    const runtime_bitmap_sample_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-sample-tests",
        .root_module = runtime_bitmap_sample_module,
    });

    const runtime_bitmap_loader_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-loader-tests",
        .root_module = runtime_bitmap_loader_module,
    });

    const runtime_bitmap_survey_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-survey-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("runtime_bitmap_survey.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_bitmap_top_bit_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_bitmap_top_bit_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_top_bit_module.addImport("runtime_bitmap_sample", runtime_bitmap_sample_module);

    const runtime_bitmap_top_bit_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-top-bit-tests",
        .root_module = runtime_bitmap_top_bit_module,
    });

    const runtime_loader_allocator_init_flow_module = b.createModule(.{
        .root_source_file = b.path("runtime_loader_allocator_init_flow.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_loader_allocator_init_flow_module.addImport("runtime_loader", runtime_loader_module);
    runtime_loader_allocator_init_flow_module.addImport(
        "runtime_loader_contract",
        runtime_loader_contract_module,
    );

    const runtime_loader_allocator_init_flow_tests = b.addTest(.{
        .name = "phase9-runtime-loader-allocator-init-flow-tests",
        .root_module = runtime_loader_allocator_init_flow_module,
    });

    const runtime_loader_command_env_boundary_guard_tests = b.addTest(.{
        .name = "phase9-runtime-loader-command-env-boundary-guard-tests",
        .root_module = runtime_loader_command_env_boundary_guard_module,
    });

    const runtime_first_loadable_parity_survey_tests = b.addTest(.{
        .name = "phase9-first-loadable-runtime-module-parity-survey-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("runtime_first_loadable_parity_survey.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_runtime_atomic64_diff_tests = b.addRunArtifact(runtime_atomic64_diff_tests);
    const run_runtime_atomic64_module_tests = b.addRunArtifact(runtime_atomic64_module_tests);
    const run_runtime_atomic64_sample_tests = b.addRunArtifact(runtime_atomic64_sample_tests);
    const run_runtime_bitmap_sample_tests = b.addRunArtifact(runtime_bitmap_sample_tests);
    const run_runtime_bitmap_loader_tests = b.addRunArtifact(runtime_bitmap_loader_tests);
    const run_runtime_bitmap_survey_tests = b.addRunArtifact(runtime_bitmap_survey_tests);
    const run_runtime_bitmap_top_bit_tests = b.addRunArtifact(runtime_bitmap_top_bit_tests);
    const run_runtime_loader_allocator_init_flow_tests = b.addRunArtifact(
        runtime_loader_allocator_init_flow_tests,
    );
    const run_runtime_loader_command_env_boundary_guard_tests = b.addRunArtifact(
        runtime_loader_command_env_boundary_guard_tests,
    );
    const run_runtime_first_loadable_parity_survey_tests = b.addRunArtifact(
        runtime_first_loadable_parity_survey_tests,
    );

    const phase9_runtime_atomic64_diff = b.step(
        "phase9-runtime-atomic64-diff",
        "Run the Phase 9 runtime atomic64 differential replay tests.",
    );
    phase9_runtime_atomic64_diff.dependOn(&run_runtime_atomic64_diff_tests.step);

    const phase9_runtime_atomic64_module = b.step(
        "phase9-runtime-atomic64-module-tests",
        "Run the Phase 9 runtime atomic64 module lifecycle tests.",
    );
    phase9_runtime_atomic64_module.dependOn(&run_runtime_atomic64_module_tests.step);

    const phase9_runtime_atomic64 = b.step(
        "phase9-runtime-atomic64-tests",
        "Run the Phase 9 runtime atomic64 lifecycle and differential replay tests.",
    );
    phase9_runtime_atomic64.dependOn(&run_runtime_atomic64_diff_tests.step);
    phase9_runtime_atomic64.dependOn(&run_runtime_atomic64_module_tests.step);

    const phase9_runtime_atomic64_sample = b.step(
        "phase9-runtime-atomic64-sample-tests",
        "Run the Phase 9 runtime atomic64 sample lifecycle tests.",
    );
    phase9_runtime_atomic64_sample.dependOn(&run_runtime_atomic64_sample_tests.step);

    const phase9_runtime_bitmap_loader = b.step(
        "phase9-runtime-bitmap-loader-tests",
        "Run the Phase 9 runtime bitmap loader-input and lifecycle tests.",
    );
    phase9_runtime_bitmap_loader.dependOn(&run_runtime_bitmap_loader_tests.step);

    const phase9_runtime_bitmap_top_bit = b.step(
        "phase9-runtime-bitmap-top-bit-tests",
        "Run the Phase 9 runtime bitmap top-bit contract tests.",
    );
    phase9_runtime_bitmap_top_bit.dependOn(&run_runtime_bitmap_top_bit_tests.step);

    const phase9_runtime_bitmap = b.step(
        "phase9-runtime-bitmap-tests",
        "Run the Phase 9 runtime bitmap sample, loader, survey, and top-bit tests.",
    );
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_sample_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_loader_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_survey_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_top_bit_tests.step);

    const phase9_runtime_loader_command_env_boundary_guard = b.step(
        "phase9-runtime-loader-command-env-boundary-guard-tests",
        "Run the Phase 9 shared runtime loader command/environment boundary guard tests.",
    );
    phase9_runtime_loader_command_env_boundary_guard.dependOn(
        &run_runtime_loader_command_env_boundary_guard_tests.step,
    );

    const phase9_runtime_loader_shared = b.step(
        "phase9-runtime-loader-shared-tests",
        "Run the shared Phase 9 runtime loader handoff parity tests.",
    );
    phase9_runtime_loader_shared.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);
    phase9_runtime_loader_shared.dependOn(
        &run_runtime_loader_command_env_boundary_guard_tests.step,
    );
    phase9_runtime_loader_shared.dependOn(&run_runtime_bitmap_loader_tests.step);

    const phase9_first_loadable_runtime_module_parity = b.step(
        "phase9-first-loadable-runtime-module-parity-survey-tests",
        "Run the Phase 9 first-loadable runtime-module parity survey tests.",
    );
    phase9_first_loadable_runtime_module_parity.dependOn(
        &run_runtime_first_loadable_parity_survey_tests.step,
    );
}

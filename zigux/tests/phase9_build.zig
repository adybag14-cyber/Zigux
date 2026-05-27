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

    const runtime_atomic64_loader_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_atomic64_loader.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_loader_module.addImport(
        "runtime_atomic64_sample",
        runtime_atomic64_sample_module,
    );

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
    runtime_loader_module.addImport("runtime_loader_contract", runtime_loader_contract_module);

    const runtime_loader_kernel_tests = b.addTest(.{
        .name = "phase9-runtime-loader-kernel-tests",
        .root_module = runtime_loader_module,
    });
    const runtime_loader_contract_tests = b.addTest(.{
        .name = "phase9-runtime-loader-contract-tests",
        .root_module = runtime_loader_contract_module,
    });

    const runtime_loader_command_env_boundary_guard_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader_command_env_boundary_guard.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_trace_events_loader_substrate_drift_module = b.createModule(.{
        .root_source_file = b.path("runtime_trace_events_loader_substrate_drift.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_trace_events_loader_substrate_drift_module.addImport("runtime_loader", runtime_loader_module);

    const runtime_atomic64_sample_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-sample-tests",
        .root_module = runtime_atomic64_sample_module,
    });

    const runtime_atomic64_loader_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-loader-tests",
        .root_module = runtime_atomic64_loader_module,
    });

    const runtime_bitmap_sample_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-sample-tests",
        .root_module = runtime_bitmap_sample_module,
    });

    const runtime_bitmap_direct_init_contract_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_bitmap_direct_init_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_direct_init_contract_module.addImport(
        "runtime_bitmap_sample",
        runtime_bitmap_sample_module,
    );

    const runtime_bitmap_direct_init_contract_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-direct-init-contract-tests",
        .root_module = runtime_bitmap_direct_init_contract_module,
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

    const runtime_bitmap_module = b.createModule(.{
        .root_source_file = b.path("runtime_bitmap_module.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_module.addImport("runtime_bitmap_sample", runtime_bitmap_sample_module);

    const runtime_bitmap_module_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-module-tests",
        .root_module = runtime_bitmap_module,
    });

    const runtime_bitmap_diff_module = b.createModule(.{
        .root_source_file = b.path("runtime_bitmap_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_diff_module.addImport("runtime_bitmap_sample", runtime_bitmap_sample_module);

    const runtime_bitmap_diff_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-diff-tests",
        .root_module = runtime_bitmap_diff_module,
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

    const runtime_bitmap_cold_stage_guard_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_bitmap_cold_stage_guard.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_cold_stage_guard_module.addImport(
        "runtime_bitmap_sample",
        runtime_bitmap_sample_module,
    );

    const runtime_bitmap_cold_stage_guard_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-cold-stage-guard-tests",
        .root_module = runtime_bitmap_cold_stage_guard_module,
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

    const runtime_trace_events_loader_substrate_drift_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-loader-substrate-drift-tests",
        .root_module = runtime_trace_events_loader_substrate_drift_module,
    });

    const runtime_trace_events_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_trace_events.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_trace_events_sample_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-sample-tests",
        .root_module = runtime_trace_events_sample_module,
    });

    const runtime_trace_events_survey_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-survey-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("runtime_trace_events_survey.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_kretprobe_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_kretprobe.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_first_loadable_parity_survey_tests = b.addTest(.{
        .name = "phase9-first-loadable-runtime-module-parity-survey-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("runtime_first_loadable_parity_survey.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const runtime_first_loadable_parity_behavior_module = b.createModule(.{
        .root_source_file = b.path("runtime_first_loadable_parity_behavior.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_first_loadable_parity_behavior_module.addImport(
        "runtime_atomic64_sample",
        runtime_atomic64_sample_module,
    );
    runtime_first_loadable_parity_behavior_module.addImport(
        "runtime_bitmap_sample",
        runtime_bitmap_sample_module,
    );
    runtime_first_loadable_parity_behavior_module.addImport(
        "runtime_kretprobe_sample",
        runtime_kretprobe_sample_module,
    );

    const runtime_first_loadable_parity_behavior_tests = b.addTest(.{
        .name = "phase9-first-loadable-runtime-module-parity-behavior-tests",
        .root_module = runtime_first_loadable_parity_behavior_module,
    });

    const runtime_kretprobe_sample_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-sample-tests",
        .root_module = runtime_kretprobe_sample_module,
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

    const runtime_kretprobe_loader_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-loader-tests",
        .root_module = runtime_kretprobe_loader_module,
    });

    const runtime_kretprobe_initialized_snapshot_guard_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-initialized-snapshot-guard-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../../samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_kretprobe_registration_reentry_gate_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_kretprobe_registration_reentry_gate.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_kretprobe_registration_reentry_gate_module.addImport(
        "runtime_kretprobe_sample",
        runtime_kretprobe_sample_module,
    );

    const runtime_kretprobe_registration_reentry_gate_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-registration-reentry-gate-tests",
        .root_module = runtime_kretprobe_registration_reentry_gate_module,
    });

    const runtime_kretprobe_reinit_reexit_guard_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-reinit-reexit-guard-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../../samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_kretprobe_survey_module = b.createModule(.{
        .root_source_file = b.path("runtime_kretprobe_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_kretprobe_survey_module.addImport(
        "runtime_kretprobe_sample",
        runtime_kretprobe_sample_module,
    );

    const runtime_kretprobe_survey_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-survey-tests",
        .root_module = runtime_kretprobe_survey_module,
    });

    const runtime_kretprobe_module_tests_module = b.createModule(.{
        .root_source_file = b.path("runtime_kretprobe_module.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_kretprobe_module_tests_module.addImport(
        "runtime_kretprobe_sample",
        runtime_kretprobe_sample_module,
    );

    const runtime_kretprobe_module_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-module-tests",
        .root_module = runtime_kretprobe_module_tests_module,
    });

    const runtime_trace_events_module_tests_module = b.createModule(.{
        .root_source_file = b.path("runtime_trace_events_module.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_trace_events_module_tests_module.addImport(
        "runtime_trace_events_sample",
        runtime_trace_events_sample_module,
    );

    const runtime_trace_events_module_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-module-tests",
        .root_module = runtime_trace_events_module_tests_module,
    });

    const runtime_trace_events_unregistered_gate_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-unregistered-gate-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../../samples/zigux/runtime_trace_events_unregistered_gate.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_trace_events_exit_rollback_guard_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-exit-rollback-guard-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../../samples/zigux/runtime_trace_events_exit_rollback_guard.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_trace_events_registration_reentry_gate_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-registration-reentry-gate-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../../samples/zigux/runtime_trace_events_registration_reentry_gate.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_trace_events_reinit_rollback_guard_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-reinit-rollback-guard-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../../samples/zigux/runtime_trace_events_reinit_rollback_guard.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const runtime_trace_events_reinit_reexit_guard_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-reinit-reexit-guard-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../../samples/zigux/runtime_trace_events_reinit_reexit_guard.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_runtime_atomic64_diff_tests = b.addRunArtifact(runtime_atomic64_diff_tests);
    const run_runtime_atomic64_module_tests = b.addRunArtifact(runtime_atomic64_module_tests);
    const run_runtime_loader_kernel_tests = b.addRunArtifact(runtime_loader_kernel_tests);
    const run_runtime_loader_contract_tests = b.addRunArtifact(runtime_loader_contract_tests);
    const run_runtime_atomic64_sample_tests = b.addRunArtifact(runtime_atomic64_sample_tests);
    const run_runtime_atomic64_loader_tests = b.addRunArtifact(runtime_atomic64_loader_tests);
    const run_runtime_bitmap_sample_tests = b.addRunArtifact(runtime_bitmap_sample_tests);
    const run_runtime_bitmap_direct_init_contract_tests = b.addRunArtifact(
        runtime_bitmap_direct_init_contract_tests,
    );
    const run_runtime_bitmap_loader_tests = b.addRunArtifact(runtime_bitmap_loader_tests);
    const run_runtime_bitmap_survey_tests = b.addRunArtifact(runtime_bitmap_survey_tests);
    const run_runtime_bitmap_module_tests = b.addRunArtifact(runtime_bitmap_module_tests);
    const run_runtime_bitmap_diff_tests = b.addRunArtifact(runtime_bitmap_diff_tests);
    const run_runtime_bitmap_top_bit_tests = b.addRunArtifact(runtime_bitmap_top_bit_tests);
    const run_runtime_bitmap_cold_stage_guard_tests = b.addRunArtifact(
        runtime_bitmap_cold_stage_guard_tests,
    );
    const run_runtime_loader_allocator_init_flow_tests = b.addRunArtifact(
        runtime_loader_allocator_init_flow_tests,
    );
    const run_runtime_loader_command_env_boundary_guard_tests = b.addRunArtifact(
        runtime_loader_command_env_boundary_guard_tests,
    );
    const run_runtime_trace_events_loader_substrate_drift_tests = b.addRunArtifact(
        runtime_trace_events_loader_substrate_drift_tests,
    );
    const run_runtime_trace_events_sample_tests = b.addRunArtifact(
        runtime_trace_events_sample_tests,
    );
    const run_runtime_trace_events_survey_tests = b.addRunArtifact(
        runtime_trace_events_survey_tests,
    );
    const run_runtime_kretprobe_sample_tests = b.addRunArtifact(
        runtime_kretprobe_sample_tests,
    );
    const run_runtime_kretprobe_loader_tests = b.addRunArtifact(
        runtime_kretprobe_loader_tests,
    );
    const run_runtime_kretprobe_initialized_snapshot_guard_tests = b.addRunArtifact(
        runtime_kretprobe_initialized_snapshot_guard_tests,
    );
    const run_runtime_kretprobe_registration_reentry_gate_tests = b.addRunArtifact(
        runtime_kretprobe_registration_reentry_gate_tests,
    );
    const run_runtime_kretprobe_reinit_reexit_guard_tests = b.addRunArtifact(
        runtime_kretprobe_reinit_reexit_guard_tests,
    );
    const run_runtime_kretprobe_survey_tests = b.addRunArtifact(
        runtime_kretprobe_survey_tests,
    );
    const run_runtime_kretprobe_module_tests = b.addRunArtifact(
        runtime_kretprobe_module_tests,
    );
    const run_runtime_trace_events_module_tests = b.addRunArtifact(
        runtime_trace_events_module_tests,
    );
    const run_runtime_trace_events_unregistered_gate_tests = b.addRunArtifact(
        runtime_trace_events_unregistered_gate_tests,
    );
    const run_runtime_trace_events_exit_rollback_guard_tests = b.addRunArtifact(
        runtime_trace_events_exit_rollback_guard_tests,
    );
    const run_runtime_trace_events_registration_reentry_gate_tests = b.addRunArtifact(
        runtime_trace_events_registration_reentry_gate_tests,
    );
    const run_runtime_trace_events_reinit_rollback_guard_tests = b.addRunArtifact(
        runtime_trace_events_reinit_rollback_guard_tests,
    );
    const run_runtime_trace_events_reinit_reexit_guard_tests = b.addRunArtifact(
        runtime_trace_events_reinit_reexit_guard_tests,
    );
    const run_runtime_first_loadable_parity_survey_tests = b.addRunArtifact(
        runtime_first_loadable_parity_survey_tests,
    );
    const run_runtime_first_loadable_parity_behavior_tests = b.addRunArtifact(
        runtime_first_loadable_parity_behavior_tests,
    );

    const phase9_runtime_atomic64_diff = b.step(
        "phase9-runtime-atomic64-diff",
        "Run the Phase 9 runtime atomic64 differential replay tests.",
    );
    phase9_runtime_atomic64_diff.dependOn(&run_runtime_atomic64_diff_tests.step);

    const phase9_runtime_atomic64_loader = b.step(
        "phase9-runtime-atomic64-loader-tests",
        "Run the Phase 9 runtime atomic64 loader lifecycle tests.",
    );
    phase9_runtime_atomic64_loader.dependOn(&run_runtime_atomic64_loader_tests.step);

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
    phase9_runtime_atomic64.dependOn(&run_runtime_atomic64_sample_tests.step);
    phase9_runtime_atomic64.dependOn(&run_runtime_atomic64_loader_tests.step);

    const phase9_runtime_atomic64_sample = b.step(
        "phase9-runtime-atomic64-sample-tests",
        "Run the Phase 9 runtime atomic64 sample lifecycle tests.",
    );
    phase9_runtime_atomic64_sample.dependOn(&run_runtime_atomic64_sample_tests.step);

    const phase9_runtime_bitmap_direct_init_contract = b.step(
        "phase9-runtime-bitmap-direct-init-contract-tests",
        "Run the Phase 9 runtime bitmap direct-init normalization contract tests.",
    );
    phase9_runtime_bitmap_direct_init_contract.dependOn(
        &run_runtime_bitmap_direct_init_contract_tests.step,
    );

    const phase9_runtime_bitmap_loader = b.step(
        "phase9-runtime-bitmap-loader-tests",
        "Run the Phase 9 runtime bitmap loader-input and lifecycle tests.",
    );
    phase9_runtime_bitmap_loader.dependOn(&run_runtime_bitmap_loader_tests.step);

    const phase9_runtime_bitmap_module = b.step(
        "phase9-runtime-bitmap-module-tests",
        "Run the Phase 9 runtime bitmap module-boundary lifecycle tests.",
    );
    phase9_runtime_bitmap_module.dependOn(&run_runtime_bitmap_module_tests.step);

    const phase9_runtime_bitmap_diff = b.step(
        "phase9-runtime-bitmap-diff-tests",
        "Run the Phase 9 runtime bitmap differential replay tests.",
    );
    phase9_runtime_bitmap_diff.dependOn(&run_runtime_bitmap_diff_tests.step);

    const phase9_runtime_bitmap_top_bit = b.step(
        "phase9-runtime-bitmap-top-bit-tests",
        "Run the Phase 9 runtime bitmap top-bit contract tests.",
    );
    phase9_runtime_bitmap_top_bit.dependOn(&run_runtime_bitmap_top_bit_tests.step);

    const phase9_runtime_bitmap_cold_stage_guard = b.step(
        "phase9-runtime-bitmap-cold-stage-guard-tests",
        "Run the Phase 9 runtime bitmap cold-stage selftest, exit, and mutation guard tests.",
    );
    phase9_runtime_bitmap_cold_stage_guard.dependOn(
        &run_runtime_bitmap_cold_stage_guard_tests.step,
    );

    const phase9_runtime_bitmap = b.step(
        "phase9-runtime-bitmap-tests",
        "Run the Phase 9 runtime bitmap sample, direct-init contract, loader, module, cold-stage guard, survey, diff, and top-bit tests.",
    );
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_sample_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_direct_init_contract_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_loader_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_module_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_cold_stage_guard_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_survey_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_diff_tests.step);
    phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_top_bit_tests.step);

    const phase9_runtime_loader_kernel = b.step(
        "phase9-runtime-loader-kernel-tests",
        "Run the Phase 9 shared runtime loader kernel-contract tests.",
    );
    phase9_runtime_loader_kernel.dependOn(&run_runtime_loader_kernel_tests.step);

    const phase9_runtime_loader_contract = b.step(
        "phase9-runtime-loader-contract-tests",
        "Run the Phase 9 shared runtime loader contract tests.",
    );
    phase9_runtime_loader_contract.dependOn(&run_runtime_loader_contract_tests.step);

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
    phase9_runtime_loader_shared.dependOn(&run_runtime_loader_kernel_tests.step);
    phase9_runtime_loader_shared.dependOn(&run_runtime_loader_contract_tests.step);
    phase9_runtime_loader_shared.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);
    phase9_runtime_loader_shared.dependOn(
        &run_runtime_loader_command_env_boundary_guard_tests.step,
    );
    phase9_runtime_loader_shared.dependOn(
        &run_runtime_trace_events_loader_substrate_drift_tests.step,
    );
    phase9_runtime_loader_shared.dependOn(&run_runtime_atomic64_loader_tests.step);
    phase9_runtime_loader_shared.dependOn(&run_runtime_bitmap_loader_tests.step);
    phase9_runtime_loader_shared.dependOn(&run_runtime_kretprobe_loader_tests.step);

    const phase9_runtime_trace_events = b.step(
        "phase9-runtime-trace-events-tests",
        "Run the Phase 9 trace-events runtime sample, survey, module, and lifecycle companion tests.",
    );
    phase9_runtime_trace_events.dependOn(&run_runtime_trace_events_sample_tests.step);
    phase9_runtime_trace_events.dependOn(&run_runtime_trace_events_survey_tests.step);
    phase9_runtime_trace_events.dependOn(&run_runtime_trace_events_module_tests.step);
    phase9_runtime_trace_events.dependOn(
        &run_runtime_trace_events_unregistered_gate_tests.step,
    );
    phase9_runtime_trace_events.dependOn(
        &run_runtime_trace_events_exit_rollback_guard_tests.step,
    );
    phase9_runtime_trace_events.dependOn(
        &run_runtime_trace_events_registration_reentry_gate_tests.step,
    );
    phase9_runtime_trace_events.dependOn(
        &run_runtime_trace_events_reinit_rollback_guard_tests.step,
    );
    phase9_runtime_trace_events.dependOn(
        &run_runtime_trace_events_reinit_reexit_guard_tests.step,
    );

    const phase9_runtime_kretprobe_sample = b.step(
        "phase9-runtime-kretprobe-sample-tests",
        "Run the Phase 9 runtime kretprobe sample lifecycle tests.",
    );
    phase9_runtime_kretprobe_sample.dependOn(&run_runtime_kretprobe_sample_tests.step);

    const phase9_runtime_kretprobe_loader = b.step(
        "phase9-runtime-kretprobe-loader-tests",
        "Run the Phase 9 runtime kretprobe loader handoff and blocked shared-request tests.",
    );
    phase9_runtime_kretprobe_loader.dependOn(&run_runtime_kretprobe_loader_tests.step);

    const phase9_runtime_kretprobe_initialized_snapshot_guard = b.step(
        "phase9-runtime-kretprobe-initialized-snapshot-guard-tests",
        "Run the Phase 9 runtime kretprobe initialized-snapshot guard tests.",
    );
    phase9_runtime_kretprobe_initialized_snapshot_guard.dependOn(
        &run_runtime_kretprobe_initialized_snapshot_guard_tests.step,
    );

    const phase9_runtime_kretprobe_registration_reentry_gate = b.step(
        "phase9-runtime-kretprobe-registration-reentry-gate-tests",
        "Run the Phase 9 runtime kretprobe registration-reentry gate tests.",
    );
    phase9_runtime_kretprobe_registration_reentry_gate.dependOn(
        &run_runtime_kretprobe_registration_reentry_gate_tests.step,
    );

    const phase9_runtime_kretprobe_reinit_reexit_guard = b.step(
        "phase9-runtime-kretprobe-reinit-reexit-guard-tests",
        "Run the Phase 9 runtime kretprobe paired re-init and re-exit rollback guard tests.",
    );
    phase9_runtime_kretprobe_reinit_reexit_guard.dependOn(
        &run_runtime_kretprobe_reinit_reexit_guard_tests.step,
    );

    const phase9_runtime_kretprobe_survey = b.step(
        "phase9-runtime-kretprobe-survey-tests",
        "Run the Phase 9 runtime kretprobe survey tests.",
    );
    phase9_runtime_kretprobe_survey.dependOn(&run_runtime_kretprobe_survey_tests.step);

    const phase9_runtime_kretprobe_module = b.step(
        "phase9-runtime-kretprobe-module-tests",
        "Run the Phase 9 runtime kretprobe module lifecycle tests.",
    );
    phase9_runtime_kretprobe_module.dependOn(&run_runtime_kretprobe_module_tests.step);

    const phase9_runtime_kretprobe = b.step(
        "phase9-runtime-kretprobe-tests",
        "Run the Phase 9 runtime kretprobe sample, loader, initialized-snapshot guard, registration-reentry gate, reinit-reexit guard, survey, and module lifecycle tests.",
    );
    phase9_runtime_kretprobe.dependOn(&run_runtime_kretprobe_sample_tests.step);
    phase9_runtime_kretprobe.dependOn(&run_runtime_kretprobe_loader_tests.step);
    phase9_runtime_kretprobe.dependOn(
        &run_runtime_kretprobe_initialized_snapshot_guard_tests.step,
    );
    phase9_runtime_kretprobe.dependOn(
        &run_runtime_kretprobe_registration_reentry_gate_tests.step,
    );
    phase9_runtime_kretprobe.dependOn(
        &run_runtime_kretprobe_reinit_reexit_guard_tests.step,
    );
    phase9_runtime_kretprobe.dependOn(&run_runtime_kretprobe_survey_tests.step);
    phase9_runtime_kretprobe.dependOn(&run_runtime_kretprobe_module_tests.step);

    const phase9_runtime_trace_events_module = b.step(
        "phase9-runtime-trace-events-module-tests",
        "Run the Phase 9 trace-events module-boundary lifecycle tests.",
    );
    phase9_runtime_trace_events_module.dependOn(
        &run_runtime_trace_events_module_tests.step,
    );

    const phase9_first_loadable_runtime_module_parity_survey = b.step(
        "phase9-first-loadable-runtime-module-parity-survey-tests",
        "Run the Phase 9 first-loadable runtime-module parity survey tests.",
    );
    phase9_first_loadable_runtime_module_parity_survey.dependOn(
        &run_runtime_first_loadable_parity_survey_tests.step,
    );

    const phase9_first_loadable_runtime_module_parity_behavior = b.step(
        "phase9-first-loadable-runtime-module-parity-behavior-tests",
        "Run the Phase 9 first-loadable runtime-module parity behavior tests.",
    );
    phase9_first_loadable_runtime_module_parity_behavior.dependOn(
        &run_runtime_first_loadable_parity_behavior_tests.step,
    );

    const phase9_first_loadable_runtime_module_parity = b.step(
        "phase9-first-loadable-runtime-module-parity-tests",
        "Run the Phase 9 first-loadable runtime-module parity survey and behavior tests together.",
    );
    phase9_first_loadable_runtime_module_parity.dependOn(
        &run_runtime_first_loadable_parity_survey_tests.step,
    );
    phase9_first_loadable_runtime_module_parity.dependOn(
        &run_runtime_first_loadable_parity_behavior_tests.step,
    );
}

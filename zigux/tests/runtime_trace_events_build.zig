const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const runtime_trace_events_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_trace_events.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_trace_events_sample_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-sample-tests",
        .root_module = runtime_trace_events_sample_module,
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

    const run_runtime_trace_events_sample_tests = b.addRunArtifact(
        runtime_trace_events_sample_tests,
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

    const test_step = b.step(
        "test",
        "Run focused Phase 9 runtime trace-events sample, module, and lifecycle companion tests.",
    );
    test_step.dependOn(&run_runtime_trace_events_sample_tests.step);
    test_step.dependOn(&run_runtime_trace_events_module_tests.step);
    test_step.dependOn(&run_runtime_trace_events_unregistered_gate_tests.step);
    test_step.dependOn(&run_runtime_trace_events_exit_rollback_guard_tests.step);
    test_step.dependOn(&run_runtime_trace_events_registration_reentry_gate_tests.step);
    test_step.dependOn(&run_runtime_trace_events_reinit_rollback_guard_tests.step);
    test_step.dependOn(&run_runtime_trace_events_reinit_reexit_guard_tests.step);
}
